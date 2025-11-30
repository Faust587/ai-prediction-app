import pandas as pd
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
import os

class CryptoPredictor:
    def __init__(self, model_path: str = 'models/model.keras'):
        """
        Ініціалізація предиктора.
        
        Args:
            model_path (str): Шлях до збереженої моделі
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Модель не знайдено за шляхом: {model_path}")
            
        self.model = keras.models.load_model(model_path)
        self.scaler = MinMaxScaler()
        self.window_size = 120  # Розмір вікна для прогнозування
        
    def prepare_data(self, df: pd.DataFrame) -> np.ndarray:
        """
        Підготовка даних для прогнозування.
        
        Args:
            df (pd.DataFrame): DataFrame з даними
            
        Returns:
            np.ndarray: Підготовлені дані для моделі
        """
        # Вибір потрібних колонок
        feature_cols = ['open', 'high', 'low', 'close', 'volume']
        
        # Нормалізація даних
        scaled_data = self.scaler.fit_transform(df[feature_cols])
        
        # Створення послідовностей
        X = []
        for i in range(self.window_size, len(scaled_data)):
            X.append(scaled_data[i - self.window_size:i])
            
        return np.array(X)
    
    def predict(self, df: pd.DataFrame) -> tuple:
        """
        Прогнозування на основі даних.
        
        Args:
            df (pd.DataFrame): DataFrame з даними
            
        Returns:
            tuple: (прогнози, ймовірності)
        """
        # Підготовка даних
        X = self.prepare_data(df)
        
        # Прогнозування
        predictions = self.model.predict(X)
        
        # Отримання останніх дат
        dates = df['timestamp'].iloc[self.window_size:].values
        
        return dates, predictions
    
    def analyze_predictions(self, dates: np.ndarray, predictions: np.ndarray, threshold: float = 0.5) -> pd.DataFrame:
        """
        Аналіз прогнозів.
        
        Args:
            dates (np.ndarray): Масив дат
            predictions (np.ndarray): Масив прогнозів
            threshold (float): Поріг для класифікації
            
        Returns:
            pd.DataFrame: DataFrame з результатами аналізу
        """
        # Перетворення predictions в одновимірний масив
        predictions_flat = predictions.flatten()
        
        results = pd.DataFrame({
            'timestamp': dates,
            'probability': predictions_flat,
            'prediction': (predictions_flat > threshold).astype(int)
        })
        
        # Додавання інтерпретації
        results['interpretation'] = results['prediction'].map({
            1: 'Ріст',
            0: 'Падіння'
        })
        
        return results

def main():
    try:
        # Створення предиктора
        predictor = CryptoPredictor()
        
        # Завантаження даних
        data_file = 'data/BTCUSDT_1h_20250531_220101.csv'  # Оновлений шлях до файлу
        if not os.path.exists(data_file):
            print(f"Файл {data_file} не знайдено!")
            return
            
        df = pd.read_csv(data_file)
        
        # Прогнозування
        dates, predictions = predictor.predict(df)
        
        # Аналіз результатів
        results = predictor.analyze_predictions(dates, predictions)
        
        # Виведення результатів
        print("\nОстанні 5 прогнозів:")
        print(results.tail())
        
        # Статистика
        total_predictions = len(results)
        growth_predictions = (results['prediction'] == 1).sum()
        fall_predictions = (results['prediction'] == 0).sum()
        
        print(f"\nСтатистика прогнозів:")
        print(f"Всього прогнозів: {total_predictions}")
        print(f"Прогнозів росту: {growth_predictions} ({growth_predictions/total_predictions*100:.1f}%)")
        print(f"Прогнозів падіння: {fall_predictions} ({fall_predictions/total_predictions*100:.1f}%)")
        
    except Exception as e:
        print(f"Помилка: {str(e)}")

if __name__ == "__main__":
    main() 