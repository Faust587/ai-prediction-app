import pandas as pd
import os

data_dir = './data'        # Папка з CSV-файлами
N = 60                    # Кількість годин у майбутнє для прогнозу
expected_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']
file_prefix = ''        # Префікс файлів для обробки (наприклад, '_1' для файлів '_1.csv')

# === Проходження по кожному файлу ===
for filename in os.listdir(data_dir):
    # Перевіряємо чи файл відповідає префіксу та має розширення .csv
    if filename.endswith(file_prefix + '_1.csv'):
        file_path = os.path.join(data_dir, filename)
        print(f"[>] Обробка: {file_path}")

        try:
            # === 1. Пробуємо прочитати файл з заголовками ===
            df = pd.read_csv(file_path)

            # === 2. Якщо перший рядок виглядає як дані, а не заголовки — додаємо заголовки ===
            if not set(expected_columns).issubset(df.columns):
                print("   [i] Додаємо заголовки...")
                df = pd.read_csv(file_path, header=None)
                df.columns = expected_columns
                df['date'] = pd.to_datetime(df['timestamp'], unit='s')
            else:
                if 'date' not in df.columns:
                    df['date'] = pd.to_datetime(df['timestamp'], unit='s')

            # === 3. Сортуємо по часу (важливо для послідовностей) ===
            df = df.sort_values('date')

            # === 4. Додаємо future_close і target ===
            df['future_close'] = df['close'].shift(-N)
            df['target'] = (df['future_close'] > df['close']).astype(int)

            # === 5. Видаляємо порожні значення ===
            df = df.dropna()

            # === 6. Зберігаємо файл (перезаписуємо) ===
            df.to_csv(file_path, index=False)
            print(f"[✓] Оновлено успішно.")

        except Exception as e:
            print(f"   [!] Помилка при обробці {filename}: {e}")
