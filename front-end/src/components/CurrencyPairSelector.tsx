import { useState, useEffect } from 'react';
import { 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  CircularProgress,
  Box
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material/Select';
import type { CurrencyPair } from '@/types';
import { api } from '@/services/api';

interface CurrencyPairSelectorProps {
  onSelect: (currencyPairId: string) => void;
}

export const CurrencyPairSelector = ({ onSelect }: CurrencyPairSelectorProps) => {
  const [currencyPairs, setCurrencyPairs] = useState<CurrencyPair[]>([]);
  const [selectedPair, setSelectedPair] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCurrencyPairs = async () => {
      try {
        const pairs = await api.getCurrencyPairs();
        setCurrencyPairs(pairs);
      } catch (error) {
        console.error('Error fetching currency pairs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCurrencyPairs();
  }, []);

  const handleChange = (event: SelectChangeEvent) => {
    const value = event.target.value;
    setSelectedPair(value);
    onSelect(value);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={2}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <FormControl fullWidth>
      <InputLabel id="currency-pair-select-label">Currency Pair</InputLabel>
      <Select
        labelId="currency-pair-select-label"
        id="currency-pair-select"
        value={selectedPair}
        label="Currency Pair"
        onChange={handleChange}
      >
        {currencyPairs.map((pair) => (
          <MenuItem key={pair.id} value={pair.id}>
            {pair.name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}; 