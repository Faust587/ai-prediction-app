import { CurrencyPair, HistoricalDataPoint, PredictionData } from '../types';
import { BinanceService } from './binanceService';
import fetch from 'node-fetch'; // npm install node-fetch@2

interface HistoricalData {
    timestamp: number;
    symbol: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    trades: number;
}

interface PythonPrediction {
    willRise: boolean;
    confidence: number;
    predictedPrice: number;
    currencyPair: {
        name: string;
    }
}

export class PredictionService {
  private binanceService: BinanceService;

  constructor() {
    this.binanceService = new BinanceService();
  }

  async getCurrencyPairs(): Promise<CurrencyPair[]> {
    return this.binanceService.getCurrencyPairs();
  }

  async getPrediction(currencyPairId: string): Promise<PredictionData> {
    // Отримуємо історичні дані з Binance
    const historicalData = await this.binanceService.getHistoricalData(currencyPairId);

    // Викликаємо Python FastAPI для справжнього prediction
    const pythonPrediction = await this.getPredictionFromPython(historicalData);

    // Формуємо історичні дані для графіка
    const chartData: HistoricalDataPoint[] = historicalData.map(data => ({
      timestamp: data.timestamp,
      price: data.close
    }));

    // Отримуємо інформацію про валютну пару
    const currencyPair = await this.binanceService.getCurrencyPairInfo(currencyPairId);

    return {
      currencyPair,
      historicalData: chartData,
      prediction: {
        willRise: pythonPrediction.willRise,
        confidence: pythonPrediction.confidence,
        predictedPrice: pythonPrediction.predictedPrice,
        priceChangePercent: 0, // Це значення буде розраховано в Python API
        lastPrice: historicalData[historicalData.length - 1].close
      }
    };
  }

  private async getPredictionFromPython(data: HistoricalData[]): Promise<PythonPrediction> {
    try {
      // Форматуємо дані для Python API
      const formattedData = {
        symbol: data[0].symbol,
        prices: data.map(price => ({
          timestamp: price.timestamp,
          open: parseFloat(price.open.toString()),
          high: parseFloat(price.high.toString()),
          low: parseFloat(price.low.toString()),
          close: parseFloat(price.close.toString()),
          volume: parseFloat(price.volume.toString()),
          trades: parseFloat(price.trades.toString())
        }))
      };

      console.log('Sending data to Python API:', formattedData);

      const pythonApiUrl = process.env.PYTHON_API_URL || 'http://python-api:8000';
      const response = await fetch(`${pythonApiUrl}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formattedData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.prediction?.error || 'Failed to get prediction');
      }

      const result = await response.json();
      console.log('Received prediction:', result);
      return result.prediction;
    } catch (error) {
      console.error('Error getting prediction:', error);
      throw error;
    }
  }
} 