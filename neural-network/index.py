import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from progress_bar import VisualProgressBar
from model_trainer import train_model, load_saved_model
from gpu_utils import check_gpu_availability
import os
import time
from datetime import datetime, timedelta

# Check GPU availability
print("[>] Checking GPU availability...")
gpu_available = check_gpu_availability()

# Налаштування параметрів навчання
DATA_DIR = './data'           # Директорія з даними
FILE_PREFIX = 'BTCUSD_1.csv'           # Префікс файлів для обробки
N_DAYS = 30                 # Кількість днів для прогнозування
EPOCHS = 20                   # Кількість епох навчання
WINDOW_SIZE = 1000             # Розмір вікна для послідовностей
BATCH_SIZE = 32             # Розмір батчу
TEST_SIZE = 0.2              # Частка тестових даних
MODEL_PATH = './models'      # Шлях для збереження моделі

# Отримуємо список всіх відповідних файлів
matching_files = [
    os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR)
    if f.endswith(FILE_PREFIX)
]

if not matching_files:
    print(f"[!] Не знайдено файлів з префіксом '{FILE_PREFIX}' в директорії {DATA_DIR}")
    sys.exit(1)

print(f"[>] Знайдено {len(matching_files)} файлів для обробки")

# Перевіряємо чи існує модель
model_exists = os.path.exists(os.path.join(MODEL_PATH, 'model.h5'))
if model_exists:
    print("[>] Знайдено існуючу модель, продовжуємо навчання")
else:
    print("[>] Створюємо нову модель")

# Обробляємо кожен файл
for i, file_path in enumerate(matching_files, 1):
    print(f"\n[>] Обробка файлу {i}/{len(matching_files)}: {file_path}")
    
    # Запам'ятовуємо час початку обробки
    start_time = time.time()
    
    try:
        # Навчання моделі
        model, history, accuracy = train_model(
            data_path=file_path,
            n_days=N_DAYS,
            epochs=EPOCHS,
            window_size=WINDOW_SIZE,
            batch_size=BATCH_SIZE,
            test_size=TEST_SIZE,
            show_plot=True,
            save_model=True,
            model_path=MODEL_PATH,
            continue_training=model_exists  # Продовжуємо навчання, якщо модель існує
        )
        
        # Після першого файлу модель вже існує
        model_exists = True
        
        # Розраховуємо час виконання
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Форматуємо час виконання
        if execution_time < 60:
            time_str = f"{execution_time:.1f} секунд"
        else:
            minutes = int(execution_time // 60)
            seconds = execution_time % 60
            time_str = f"{minutes} хвилин {seconds:.1f} секунд"
            
        print(f"[✓] Файл оброблено за {time_str}")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"[!] Помилка при обробці файлу {file_path}: {str(e)}")
        continue
    except Exception as e:
        print(f"[!] Неочікувана помилка при обробці файлу {file_path}: {str(e)}")
        continue

print("\n[✓] Навчання завершено для всіх файлів")