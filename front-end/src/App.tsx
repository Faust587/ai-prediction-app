import { useState } from 'react'
import { Container, Box, Typography, Paper } from '@mui/material'
import { CurrencyPairSelector } from './components/CurrencyPairSelector'
import { PredictionChart } from './components/PredictionChart'
import './App.css'

function App() {
  const [selectedPairId, setSelectedPairId] = useState<string>('')

  return (
    <Container maxWidth="lg">
      <Box py={4}>
        <Typography color='grayimage.png' variant="h4" component="h1" gutterBottom align="center">
          Trading Price Prediction
        </Typography>
        
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <CurrencyPairSelector onSelect={setSelectedPairId} />
        </Paper>

        {selectedPairId && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <PredictionChart currencyPairId={selectedPairId} />
          </Paper>
        )}
      </Box>
    </Container>
  )
}

export default App
