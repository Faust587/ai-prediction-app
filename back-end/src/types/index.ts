export interface CurrencyPair {
  id: string;
  name: string;
  baseCurrency: string;
  quoteCurrency: string;
}

export interface HistoricalDataPoint {
  timestamp: number;
  price: number;
}

export interface Prediction {
  willRise: boolean;
  confidence: number;
  predictedPrice: number;
  priceChangePercent: number;
  lastPrice: number;
}

export interface PredictionData {
  currencyPair: CurrencyPair;
  historicalData: HistoricalDataPoint[];
  prediction: Prediction;
} 