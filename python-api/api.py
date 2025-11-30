from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import sys
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
import os
sys.path.append("../neural-network")

app = FastAPI()

# Дозволяємо CORS для локальної розробки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CryptoPredictor:
    def __init__(self, model_path: str = 'model/model.keras'):
        """
        Ініціалізація предиктора.
        
        Args:
            model_path (str): Шлях до збереженої моделі
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Модель не знайдено за шляхом: {model_path}")
            
        self.model = keras.models.load_model(model_path)
        self.scaler = MinMaxScaler()
        self.window_size = 30  # Змінено на 30, щоб відповідати вхідним даним
        print(f"Ініціалізовано CryptoPredictor з window_size={self.window_size}")
        
    def prepare_data(self, df: pd.DataFrame) -> np.ndarray:
        """
        Підготовка даних для прогнозування.
        
        Args:
            df (pd.DataFrame): DataFrame з даними
            
        Returns:
            np.ndarray: Підготовлені дані для моделі
        """
        print(f"prepare_data: отримано {len(df)} рядків даних")
        print(f"prepare_data: window_size={self.window_size}")
        
        if len(df) < self.window_size:
            raise ValueError(f"Недостатньо даних. Потрібно мінімум {self.window_size} точок, отримано {len(df)}")
            
        # Вибір потрібних колонок
        feature_cols = ['open', 'high', 'low', 'close', 'volume']
        print(f"prepare_data: використовуємо колонки {feature_cols}")
        
        # Нормалізація даних
        scaled_data = self.scaler.fit_transform(df[feature_cols])
        print(f"prepare_data: розмір scaled_data={scaled_data.shape}")
        
        # Створення послідовності для прогнозування
        try:
            X = scaled_data[-self.window_size:].reshape(1, self.window_size, len(feature_cols))
            print(f"prepare_data: успішно створено X з розміром {X.shape}")
            return X
        except Exception as e:
            print(f"Помилка при reshape: {str(e)}")
            print(f"Розмір scaled_data: {scaled_data.shape}")
            print(f"Спроба reshape в: (1, {self.window_size}, {len(feature_cols)})")
            raise
    
    def predict(self, df: pd.DataFrame) -> float:
        """
        Прогнозування на основі даних.
        
        Args:
            df (pd.DataFrame): DataFrame з даними
            
        Returns:
            float: Прогнозована ціна
        """
        print("predict: початок прогнозування")
        # Підготовка даних
        X = self.prepare_data(df)
        
        # Прогнозування
        prediction = self.model.predict(X)
        print(f"predict: отримано прогноз {prediction}")
        
        return float(prediction[0][0])

# Створюємо глобальний екземпляр предиктора
predictor = CryptoPredictor()

@app.post("/predict")
async def predict(request: Request):
    print("=== Початок запиту ===")
    data = await request.json()
    print(data)
    # Отримуємо дані
    symbol = data.get("symbol", "unknown")
    prices_data = data.get("prices", [])
    print(f"Символ: {symbol}")
    print(f"Кількість точок даних: {len(prices_data)}")
    
    try:
        # Створюємо DataFrame з даними
        df = pd.DataFrame(prices_data)
        print(f"Створено DataFrame з розміром {df.shape}")
        
        # Перевіряємо наявність всіх необхідних колонок
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Відсутня колонка {col} в даних")
        
        # Перевіряємо кількість даних
        if len(df) < predictor.window_size:
            raise ValueError(f"Недостатньо даних. Потрібно мінімум {predictor.window_size} точок, отримано {len(df)}")
        
        # Отримання прогнозу
        predicted_price = predictor.predict(df)

        return {
            "prediction": {
                "willRise": predicted_price,
                "currencyPair": {
                    "name": symbol
                }
            }
        }
        
        # Отримання останньої ціни
        # last_price = df["close"].iloc[-1]
        
        # # Визначення напрямку руху ціни
        # will_rise = predicted_price > last_price
        
        # # Розрахунок відсоткової зміни
        # price_change_percent = ((predicted_price - last_price) / last_price) * 100
        
        # # Розрахунок впевненості на основі відсоткової зміни
        # confidence = min(abs(price_change_percent) / 2, 0.95)  # Максимум 95% впевненості
        
        # result = {
        #     "prediction": {
        #         "willRise": will_rise,
        #         "confidence": confidence,
        #         "predictedPrice": round(float(predicted_price), 2),
        #         "priceChangePercent": round(price_change_percent, 2),
        #         "lastPrice": round(float(last_price), 2)
        #     }
        # }
        # print("Результат:", result)
        # return result
        
    except Exception as e:
        print("Помилка при обробці даних:", str(e))
        return {"prediction": {"error": f"Error processing data: {str(e)}"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 