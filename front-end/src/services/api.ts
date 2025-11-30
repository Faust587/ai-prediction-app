import type { CurrencyPair, PredictionData } from '@/types';

const API_BASE_URL = 'http://localhost:3000/api';

export const api = {
  getCurrencyPairs: async (): Promise<CurrencyPair[]> => {
    const response = await fetch(`${API_BASE_URL}/currency-pairs`);
    if (!response.ok) {
      throw new Error('Failed to fetch currency pairs');
    }
    return response.json();
  },

  getPrediction: async (currencyPairId: string): Promise<PredictionData> => {
    const response = await fetch(`${API_BASE_URL}/prediction/${currencyPairId}`);
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Currency pair not found');
      }
      throw new Error('Failed to fetch prediction');
    }
    return response.json();
  },
}; 