import { useEffect, useState } from 'react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart,
} from 'recharts';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Chip,
  useTheme,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import type { PredictionData } from '@/types';
import { api } from '@/services/api';

interface PredictionChartProps {
  currencyPairId: string;
}

export const PredictionChart = ({ currencyPairId }: PredictionChartProps) => {
  const [predictionData, setPredictionData] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const theme = useTheme();

  useEffect(() => {
    const fetchPrediction = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getPrediction(currencyPairId);
        setPredictionData(data);
      } catch (err) {
        setError('Failed to fetch prediction data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (currencyPairId) {
      fetchPrediction();
    }
  }, [currencyPairId]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  if (!predictionData) {
    return null;
  }

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString();
  };

  const formatPrice = (price: number | undefined | null): string => {
    if (price === undefined || price === null) {
      return 'N/A';
    }
    return `$${price.toFixed(2)}`;
  };

  // Calculate min and max for Y axis
  const prices = predictionData.historicalData
    .map(d => d.price)
    .filter((price): price is number => price !== undefined && price !== null);

  if (prices.length === 0) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <Typography color="error">No valid price data available</Typography>
      </Box>
    );
  }

  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;
  const yAxisMin = minPrice - priceRange * 0.1;
  const yAxisMax = maxPrice + priceRange * 0.1;

  // Get the last price from historical data
  const lastPrice = predictionData.historicalData[predictionData.historicalData.length - 1]?.price;

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            {predictionData.currencyPair.name} Price Prediction
          </Typography>
          <Chip
            icon={predictionData.prediction.willRise ? <TrendingUpIcon /> : <TrendingDownIcon />}
            label={`${predictionData.prediction.willRise ? 'Will Rise' : 'Will Fall'}`}
            color={predictionData.prediction.willRise ? 'success' : 'error'}
          />
        </Box>
        
        <Box height={400}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={predictionData.historicalData}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={theme.palette.divider}
                vertical={false}
              />
              <XAxis
                dataKey="timestamp"
                tickFormatter={formatDate}
                stroke={theme.palette.text.secondary}
                tick={{ fill: theme.palette.text.secondary }}
              />
              <YAxis
                domain={[yAxisMin, yAxisMax]}
                tickFormatter={formatPrice}
                stroke={theme.palette.text.secondary}
                tick={{ fill: theme.palette.text.secondary }}
              />
              <Tooltip
                labelFormatter={formatDate}
                formatter={(value: number) => [formatPrice(value), 'Price']}
                contentStyle={{
                  backgroundColor: theme.palette.background.paper,
                  border: `1px solid ${theme.palette.divider}`,
                  borderRadius: theme.shape.borderRadius,
                }}
              />
              <Area
                type="monotone"
                dataKey="price"
                stroke={theme.palette.primary.main}
                fillOpacity={1}
                fill="url(#colorPrice)"
                strokeWidth={2}
              />
              {predictionData.prediction.predictedPrice && (
                <ReferenceLine
                  y={predictionData.prediction.predictedPrice}
                  stroke={theme.palette.secondary.main}
                  strokeDasharray="3 3"
                  label={{
                    value: 'Predicted',
                    position: 'right',
                    fill: theme.palette.secondary.main,
                  }}
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        </Box>

        <Box mt={2} display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="body2" color="text.secondary">
            Current Price: {formatPrice(lastPrice)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Predicted Price: {formatPrice(predictionData.prediction.predictedPrice)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Confidence: {predictionData.prediction.confidence 
              ? `${(predictionData.prediction.confidence * 100).toFixed(1)}%`
              : 'N/A'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}; 