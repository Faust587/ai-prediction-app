import { Router } from 'express';
import { PredictionController } from '../controllers/predictionController';

const router = Router();
const predictionController = new PredictionController();

router.get('/currency-pairs', predictionController.getCurrencyPairs);
router.get('/prediction/:currencyPairId', predictionController.getPrediction);

export default router; 