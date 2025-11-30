export interface CurrencyPair {
  id: string;
  name: string;
  baseCurrency: string;
  quoteCurrency: string;
}

export interface PriceData {
  timestamp: number;
  price: number;
}

export interface PredictionData {
  currencyPair: CurrencyPair;
  historicalData: PriceData[];
  prediction: {
    willRise: boolean;
    confidence: number;
    predictedPrice: number;
  };
} 