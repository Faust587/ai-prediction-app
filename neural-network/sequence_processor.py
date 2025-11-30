import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os
import glob
from pathlib import Path

def get_sequence_file_path(data_path: str, window_size: int) -> str:
    """
    Генерує шлях до файлу з послідовностями на основі шляху до даних та розміру вікна.
    
    Args:
        data_path (str): Шлях до оригінального файлу з даними
        window_size (int): Розмір вікна для послідовностей
        
    Returns:
        str: Шлях до файлу з послідовностями
    """
    data_path = Path(data_path)
    return str(data_path.parent / f"{data_path.stem}_sequences_{window_size}.npz")

def generate_and_save_sequences(data_path: str, window_size: int) -> tuple:
    """
    Генерує послідовності для LSTM моделі та зберігає їх у файл.
    
    Args:
        data_path (str): Шлях до CSV файлу з даними
        window_size (int): Розмір вікна для послідовностей
        
    Returns:
        tuple: (X, y, scaler) - послідовності, цільові значення та скалер
    """
    # Перевірка файлу
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Файл не знайдено: {data_path}")
    
    if os.path.getsize(data_path) == 0:
        raise ValueError(f"Файл порожній: {data_path}")

    # === 1. Завантаження CSV ===
    try:
        df = pd.read_csv(data_path)
        if df.empty:
            raise ValueError(f"Файл не містить даних: {data_path}")
    except pd.errors.EmptyDataError:
        raise ValueError(f"Файл порожній або має неправильний формат: {data_path}")
    except Exception as e:
        raise ValueError(f"Помилка при читанні файлу {data_path}: {str(e)}")

    df['date'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df.sort_values('date')

    # === 2. Масштабування ознак ===
    feature_cols = ['open', 'high', 'low', 'close', 'volume']
    scaler = MinMaxScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    df = df[feature_cols + ['target']]

    # === 3. Послідовності для LSTM ===
    X = []
    y = []
    total = len(df) - window_size

    for i in range(window_size, len(df)):
        X.append(df[feature_cols].iloc[i - window_size:i].values)
        y.append(df['target'].iloc[i])

        # Вивід прогресу на кожному кроці
        current = i - window_size + 1
        percentage = (current / total) * 100
        print(f"\r🔄 Прогрес: {percentage:.3f}%", end="", flush=True)

    print("\n✅ Генерація завершена.")
    
    # Конвертуємо в numpy масиви
    X = np.array(X)
    y = np.array(y)
    
    # Зберігаємо результати
    sequence_file = get_sequence_file_path(data_path, window_size)
    np.savez(sequence_file, X=X, y=y, scaler_min=scaler.min_, scaler_scale=scaler.scale_)
    print(f"[✓] Послідовності збережено в {sequence_file}")
    
    return X, y, scaler

def load_sequences(data_path: str, window_size: int) -> tuple:
    """
    Завантажує збережені послідовності або генерує нові, якщо вони не існують.
    
    Args:
        data_path (str): Шлях до CSV файлу з даними
        window_size (int): Розмір вікна для послідовностей
        
    Returns:
        tuple: (X, y, scaler) - послідовності, цільові значення та скалер
    """
    sequence_file = get_sequence_file_path(data_path, window_size)
    
    if os.path.exists(sequence_file):
        print(f"[>] Завантаження збережених послідовностей з {sequence_file}")
        data = np.load(sequence_file)
        X = data['X']
        y = data['y']
        
        # Відновлюємо скалер
        scaler = MinMaxScaler()
        scaler.min_ = data['scaler_min']
        scaler.scale_ = data['scaler_scale']
        
        print("[✓] Послідовності успішно завантажено")
        return X, y, scaler
    else:
        print(f"[>] Файл з послідовностями не знайдено. Генеруємо нові послідовності...")
        return generate_and_save_sequences(data_path, window_size)

def process_all_sequence_files(data_dir: str, window_sizes: list) -> None:
    """
    Обробляє всі CSV файли в директорії та генерує для них послідовності.
    
    Args:
        data_dir (str): Шлях до директорії з CSV файлами
        window_sizes (list): Список розмірів вікон для генерації послідовностей
    """
    # Знаходимо всі CSV файли в директорії
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    if not csv_files:
        print(f"[!] CSV файли не знайдено в директорії {data_dir}")
        return
    
    print(f"[>] Знайдено {len(csv_files)} CSV файлів")
    
    # Обробляємо кожен файл
    for csv_file in csv_files:
        print(f"\n[>] Обробка файлу: {csv_file}")
        for window_size in window_sizes:
            print(f"\n[>] Генерація послідовностей для вікна розміром {window_size}")
            try:
                load_sequences(csv_file, window_size)
            except Exception as e:
                print(f"[!] Помилка при обробці файлу {csv_file} з вікном {window_size}: {str(e)}")
                continue 