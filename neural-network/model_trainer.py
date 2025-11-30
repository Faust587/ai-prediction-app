import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from progress_bar import VisualProgressBar
import os
import tensorflow as tf
import json
from pathlib import Path
import multiprocessing
from sequence_processor import load_sequences

# Disable multi-threading
os.environ['TF_NUM_INTEROP_THREADS'] = '2'
os.environ['TF_NUM_INTRAOP_THREADS'] = '2'

# Disable multi-core processing
tf.config.threading.set_inter_op_parallelism_threads(2)
tf.config.threading.set_intra_op_parallelism_threads(2)

# Disable XLA compilation
os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices=false'

# Disable GPU memory growth
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# Налаштування для паралельного виконання
tf.config.optimizer.set_jit(True)  # XLA оптимізація

# Увімкнення eager execution
tf.config.run_functions_eagerly(True)
# Увімкнення debug режиму для tf.data
tf.data.experimental.enable_debug_mode()

def get_processed_files_path():
    """Returns the path to the processed files JSON."""
    return os.path.join('./models', 'processed_files.json')

def load_processed_files():
    """Load the list of processed files from JSON."""
    processed_files_path = get_processed_files_path()
    if os.path.exists(processed_files_path):
        with open(processed_files_path, 'r') as f:
            return json.load(f)
    return []

def save_processed_file(file_path):
    """Add a file to the processed files list and save it."""
    processed_files = load_processed_files()
    if file_path not in processed_files:
        processed_files.append(file_path)
        os.makedirs('./models', exist_ok=True)
        with open(get_processed_files_path(), 'w') as f:
            json.dump(processed_files, f, indent=2)

def is_file_processed(file_path):
    """Check if a file has been processed before."""
    return file_path in load_processed_files()

def save_trained_model(model, model_path: str = './models'):
    """
    Зберігає модель та її ваги.

    Args:
        model: Навчена модель
        model_path (str): Шлях для збереження моделі
    """
    # Створюємо директорію, якщо її немає
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    
    # Зберігаємо модель у новому форматі .keras
    model_save_path = os.path.join(model_path, 'model.keras')
    model.save(model_save_path)
    print(f"[✓] Модель збережено в {model_save_path}")

def load_saved_model(model_path: str = './models/model.keras'):
    """
    Завантажує збережену модель.

    Args:
        model_path (str): Шлях до збереженої моделі

    Returns:
        model: Завантажена модель
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Модель не знайдено за шляхом: {model_path}")
    
    model = load_model(model_path)
    print(f"[✓] Модель завантажено з {model_path}")
    return model

def generate_lstm_sequences(data_path: str, window_size: int) -> tuple:
    """
    Генерує послідовності для LSTM моделі.

    Args:
        data_path (str): Шлях до CSV файлу з даними
        window_size (int): Розмір вікна для послідовностей

    Returns:
        tuple: (X, y, scaler) - послідовності, цільові значення та скалер
    """
    return load_sequences(data_path, window_size)

def train_model(
    data_path: str,
    n_days: int = 10,
    epochs: int = 20,
    window_size: int = 30,
    batch_size: int = 32,
    test_size: float = 0.2,
    show_plot: bool = True,
    save_model: bool = True,
    model_path: str = './models',
    continue_training: bool = False,
    lstm_units: int = 128,
    pre_generated_data: tuple = None
) -> tuple:
    """
    Навчає LSTM модель для прогнозування руху ціни.

    Args:
        data_path (str): Шлях до CSV файлу з даними
        n_days (int): Кількість днів для прогнозування
        epochs (int): Кількість епох навчання
        window_size (int): Розмір вікна для послідовностей
        batch_size (int): Розмір батчу для навчання
        test_size (float): Частка тестових даних
        show_plot (bool): Чи показувати графік навчання
        save_model (bool): Чи зберігати модель після навчання
        model_path (str): Шлях для збереження моделі
        continue_training (bool): Чи продовжити навчання існуючої моделі
        lstm_units (int): Кількість нейронів у LSTM шарі
        pre_generated_data (tuple): Попередньо згенеровані дані (X, y, scaler)

    Returns:
        tuple: (model, history, test_accuracy)
    """
    # Перевірка чи файл вже був оброблений
    if is_file_processed(data_path):
        print(f"[!] Файл {data_path} вже був оброблений раніше. Пропускаємо.")
        return None, None, None

    # === 1. Отримання даних ===
    if pre_generated_data is not None:
        X, y, scaler = pre_generated_data
    else:
        X, y, scaler = generate_lstm_sequences(data_path, window_size)

    # === 2. Розділення ===
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False
    )

    # === 3. Створення або завантаження моделі ===
    if continue_training and os.path.exists(os.path.join(model_path, 'model.keras')):
        print("[>] Продовжуємо навчання існуючої моделі...")
        model = load_saved_model(os.path.join(model_path, 'model.keras'))
    else:
        print("[>] Створюємо нову модель...")
        model = Sequential([
            Input(shape=(X_train.shape[1], X_train.shape[2])),
            LSTM(units=lstm_units, return_sequences=False),
            Dropout(0.2),
            Dense(1, activation='sigmoid')
        ])
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy'],
            jit_compile=False,  # Відключення XLA компіляції
            run_eagerly=True  # Відключення графового режиму
        )
        print("[>] Модель створена")

    # === 4. Навчання ===
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        verbose=1
    )

    # === 5. Оцінка ===
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f'\n\n[✓] Test Accuracy for N={n_days} → {accuracy:.4f}')

    # === 6. Збереження моделі ===
    if save_model:
        save_trained_model(model, model_path)
        # Зберігаємо інформацію про оброблений файл
        save_processed_file(data_path)

    # === 7. Графік ===
    if show_plot:
        plt.figure(figsize=(10, 6))
        plt.plot(history.history['accuracy'], label='Train Accuracy')
        plt.plot(history.history['val_accuracy'], label='Test Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.title(f'LSTM Accuracy (N={n_days} days)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return model, history, accuracy 