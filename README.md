# Trading Prediction App

Application for predicting cryptocurrency prices using neural networks.

## Architecture

The project consists of three main components:

- **Python API** - FastAPI service for price prediction using TensorFlow
- **Backend** - Node.js/Express service for working with Binance data
- **Frontend** - React application with Material-UI

## Running with Docker

### Prerequisites

- Docker
- Docker Compose

### Quick Start

#### Method 1: Using scripts (recommended)

1. Clone the repository and navigate to the project directory:

```bash
cd trading-prediction-app
```

2. Start the application:

```bash
./start.sh
```

3. Stop the application:

```bash
./stop.sh
```

#### Method 2: Using Docker Compose directly

1. Clone the repository and navigate to the project directory:

```bash
cd trading-prediction-app
```

2. Build and run all services:

```bash
docker compose up --build
```

Or run in the background:

```bash
docker compose up -d --build
```

3. The application will be available at:
   - **Frontend**: http://localhost
   - **Backend API**: http://localhost:3000
   - **Python API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

### Useful Commands

#### View container status

```bash
docker compose ps
```

#### View logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs frontend
docker compose logs backend
docker compose logs python-api

# Follow logs in real-time
docker compose logs -f
```

#### Stop services

```bash
docker compose down
```

#### Stop services and remove volumes

```bash
docker compose down -v
```

#### Rebuild specific service

```bash
docker compose build frontend
docker compose build backend
docker compose build python-api
```

#### Restart service

```bash
docker compose restart frontend
docker compose restart backend
docker compose restart python-api
```

## Project Structure

```
trading-prediction-app/
├── python-api/          # FastAPI service for ML predictions
│   ├── api.py
│   ├── model/
│   │   └── model.keras  # Trained LSTM model
│   ├── Dockerfile
│   └── requirements.txt
├── back-end/            # Node.js/Express backend
│   ├── src/
│   │   ├── controllers/
│   │   ├── routes/
│   │   └── services/
│   ├── Dockerfile
│   └── package.json
├── front-end/           # React frontend
│   ├── src/
│   │   ├── components/
│   │   └── services/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── neural-network/      # Code for model training
│   ├── model_trainer.py
│   ├── config.py
│   └── data/
├── docker-compose.yml   # Orchestration of all services
├── README.md
├── DOCKER_SETUP.md      # Detailed Docker documentation
└── NEURAL_NETWORK.md    # Neural network explanation
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                    http://localhost:80                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Currency     │  │ Prediction   │  │ Chart        │      │
│  │ Selector     │  │ Display      │  │ Component    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                   Backend (Node.js/Express)                  │
│                    http://localhost:3000                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Prediction   │  │ Binance      │  │ Prediction   │      │
│  │ Controller   │→ │ Service      │→ │ Service      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         │                  ↓                  ↓              │
│         │          Binance API      Python API (internal)   │
└─────────┴──────────────────┴──────────────────┬─────────────┘
                                                 │ HTTP/REST
                                                 ↓
┌─────────────────────────────────────────────────────────────┐
│                   Python API (FastAPI)                       │
│                    http://localhost:8000                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ FastAPI      │→ │ Crypto       │→ │ LSTM Model   │      │
│  │ Endpoint     │  │ Predictor    │  │ (TensorFlow) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                              ↑                │
│                                              │                │
│                                       model.keras             │
└─────────────────────────────────────────────────────────────┘

Data flow for prediction:
1. User selects cryptocurrency pair in Frontend
2. Frontend → Backend: prediction request
3. Backend → Binance API: get historical data (30+ points)
4. Backend → Python API: send data for analysis
5. Python API → LSTM Model: prediction
6. Python API → Backend: result (probability of price increase)
7. Backend → Frontend: formatted prediction
8. Frontend: display result and chart
```

## How the Neural Network Works

For detailed explanation of the architecture and operation of the LSTM model for cryptocurrency prediction, see [NEURAL_NETWORK.md](NEURAL_NETWORK.md).

Briefly:

- **Model**: LSTM (Long Short-Term Memory) neural network
- **Input data**: 30 time points × 5 features (open, high, low, close, volume)
- **Output**: probability of price increase (0-1)
- **Framework**: TensorFlow/Keras
- **Accuracy**: depends on training data

## Development

### Local development without Docker

#### Python API

```bash
cd python-api
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

#### Backend

```bash
cd back-end
npm install
npm run dev
```

#### Frontend

```bash
cd front-end
npm install
npm run dev
```

## Configuration

### Environment Variables

You can configure environment variables in `docker-compose.yml`:

#### Backend

- `NODE_ENV` - Node.js environment (default: `production`)
- `PYTHON_API_URL` - Python API URL (default: `http://python-api:8000`)
- `PORT` - server port (default: `3000`)

#### Python API

- `PYTHONUNBUFFERED` - disable Python output buffering

For local development without Docker, create `.env` files:

- `back-end/.env` - for backend (use `PYTHON_API_URL=http://localhost:8000`)
- `python-api/.env` - for Python API

### Ports

The following ports are used by default:

- Frontend: 80
- Backend: 3000
- Python API: 8000

To change ports, edit `docker-compose.yml`.

## Troubleshooting

### Container won't start

Check logs:

```bash
docker compose logs [service-name]
```

### Port already in use

Change ports in `docker-compose.yml` or stop the process using the port.

### Build issues

Clear Docker cache:

```bash
docker compose down
docker system prune -a
docker compose build --no-cache
```

## License

MIT
