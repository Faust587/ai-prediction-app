import { Request, Response } from 'express';
import { PredictionService } from '../services/predictionService';
import { log } from 'console';

export class PredictionController {
  private predictionService: PredictionService;

  constructor() {
    this.predictionService = new PredictionService();
  }

  getCurrencyPairs = async (req: Request, res: Response) => {
    try {
      const currencyPairs = await this.predictionService.getCurrencyPairs();
      res.json(currencyPairs);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch currency pairs' });
    }
  };

  getPrediction = async (req: Request, res: Response) => {
    try {
      const { currencyPairId } = req.params;
      const prediction = await this.predictionService.getPrediction(currencyPairId);
      res.json(prediction);
    } catch (error) {
      console.log(error);
      if (error instanceof Error && error.message === 'Currency pair not found') {
        res.status(404).json({ error: 'Currency pair not found' });
      } else {
        res.status(500).json({ error: 'Failed to fetch prediction' });
      }
    }
  };
} 