import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta
import os
from typing import Optional, Tuple
import time

class CryptoDataFetcher:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Ініціалізація фетчера даних криптовалюти.
        
        Args:
            api_key (str, optional): API ключ Binance
            api_secret (str, optional): API секрет Binance
        """
        self.client = Client(api_key, api_secret)
        
    def get_historical_klines(
        self,
        symbol: str,
        interval: str = '1h',
        start_str: Optional[str] = None,
        end_str: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Отримання історичних даних для вказаної криптовалюти.
        
        Args:
            symbol (str): Символ криптовалюти (наприклад, 'BTCUSDT')
            interval (str): Інтервал часу ('1m', '5m', '15m', '1h', '4h', '1d', тощо)
            start_str (str, optional): Початкова дата у форматі 'YYYY-MM-DD'
            end_str (str, optional): Кінцева дата у форматі 'YYYY-MM-DD'
            limit (int): Максимальна кількість записів
            
        Returns:
            pd.DataFrame: DataFrame з даними у форматі, придатному для моделі
        """
        # Встановлення часових меж
        if not start_str:
            start_str = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_str:
            end_str = datetime.now().strftime('%Y-%m-%d')
            
        # Отримання даних
        klines = self.client.get_historical_klines(
            symbol,
            interval,
            start_str,
            end_str,
            limit=limit
        )
        
        # Створення DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # Конвертація timestamp з мілісекунд в секунди
        df['timestamp'] = df['timestamp'].astype(int) // 1000
        
        # Конвертація типів даних
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
            
        # Додавання колонки trades (використовуємо number_of_trades)
        df['trades'] = df['number_of_trades'].astype(int)
        
        # Вибір потрібних колонок у правильному порядку
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']]
        
        return df
    
    def save_data(self, df: pd.DataFrame, symbol: str, interval: str, output_dir: str = 'data') -> str:
        """
        Збереження даних у CSV файл.
        
        Args:
            df (pd.DataFrame): DataFrame з даними
            symbol (str): Символ криптовалюти
            interval (str): Інтервал часу
            output_dir (str): Директорія для збереження
            
        Returns:
            str: Шлях до збереженого файлу
        """
        # Створення директорії, якщо вона не існує
        os.makedirs(output_dir, exist_ok=True)
        
        # Формування імені файлу
        filename = f"{symbol}_{interval}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Збереження даних
        df.to_csv(filepath, index=False)
        print(f"Дані збережено у файл: {filepath}")
        
        return filepath

def main():
    # Приклад використання
    fetcher = CryptoDataFetcher()
    
    # Встановлюємо часові межі для отримання рівно 300 записів
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=300)  # 300 хвилин для 1-хвилинних інтервалів
    
    # Отримання даних для BTC/USDT
    df = fetcher.get_historical_klines(
        symbol='BTCUSDT',
        interval='1m',
        start_str=start_time.strftime('%Y-%m-%d %H:%M:%S'),
        end_str=end_time.strftime('%Y-%m-%d %H:%M:%S'),
        limit=300
    )
    
    # Збереження даних
    filepath = fetcher.save_data(df, 'BTCUSDT', '1m')
    print(f"Розмір датасету: {len(df)} рядків")
    print("\nПерші 5 рядків даних:")
    print(df.head())

if __name__ == "__main__":
    main() 