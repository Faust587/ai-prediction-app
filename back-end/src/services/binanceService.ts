import Binance from 'binance-api-node';
import { CurrencyPair } from '../types';

export class BinanceService {
  private client: ReturnType<typeof Binance>;

  constructor() {
    // Initialize Binance client without authentication for public endpoints
    this.client = Binance();
  }

  async getCurrencyPairs(): Promise<CurrencyPair[]> {
    try {
      // Get exchange info which contains all trading pairs
      const exchangeInfo = await this.client.exchangeInfo();
      
      // Filter for USDT pairs and map to our format
      const currencyPairs: CurrencyPair[] = exchangeInfo.symbols
        .filter((symbol: any) => 
          symbol.status === 'TRADING' && 
          symbol.quoteAsset === 'USDT' &&
          !symbol.symbol.includes('DOWN') &&
          !symbol.symbol.includes('UP')
        )
        .map((symbol: any) => ({
          id: symbol.symbol,
          name: symbol.symbol,
          baseCurrency: symbol.baseAsset,
          quoteCurrency: symbol.quoteAsset
        }))
        .slice(0, 10); // Limit to top 10 pairs for now

      return currencyPairs;
    } catch (error) {
      console.error('Error fetching currency pairs from Binance:', error);
      throw new Error('Failed to fetch currency pairs from Binance');
    }
  }

  async getCurrencyPairInfo(symbol: string): Promise<CurrencyPair> {
    try {
      // Get exchange info which contains all trading pairs
      const exchangeInfo = await this.client.exchangeInfo();
      
      // Find the specific symbol
      const symbolInfo = exchangeInfo.symbols.find((s: any) => s.symbol === symbol);
      
      if (!symbolInfo) {
        throw new Error('Currency pair not found');
      }

      return {
        id: symbolInfo.symbol,
        name: symbolInfo.symbol,
        baseCurrency: symbolInfo.baseAsset,
        quoteCurrency: symbolInfo.quoteAsset
      };
    } catch (error) {
      console.error('Error fetching currency pair info from Binance:', error);
      throw new Error('Failed to fetch currency pair info from Binance');
    }
  }

  async getHistoricalData(
    symbol: string,
    interval: '1m' | '3m' | '5m' | '15m' | '30m' | '1h' | '2h' | '4h' | '6h' | '8h' | '12h' | '1d' | '3d' | '1w' | '1M' = '1d',
    limit: number = 30
  ) {
    try {
      const candles = await this.client.candles({
        symbol,
        interval: '1m',
        limit: 30
      });
      
      return candles.map((candle: any) => ({
        timestamp: candle.openTime,
        symbol,
        open: parseFloat(candle.open),
        high: parseFloat(candle.high),
        low: parseFloat(candle.low),
        close: parseFloat(candle.close),
        volume: parseFloat(candle.volume),
        trades: parseFloat(candle.trades)
      }));
    } catch (error) {
      console.error('Error fetching historical data from Binance:', error);
      throw new Error('Failed to fetch historical data from Binance');
    }
  }
} 