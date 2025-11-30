# Trading Prediction App

Додаток для прогнозування цін криптовалют з використанням нейронних мереж.

## Архітектура

Проект складається з трьох основних компонентів:

- **Python API** - FastAPI сервіс для прогнозування цін з використанням TensorFlow
- **Backend** - Node.js/Express сервіс для роботи з даними Binance
- **Frontend** - React додаток з Material-UI

## Запуск з Docker

### Передумови

- Docker
- Docker Compose

### Швидкий старт

#### Метод 1: Використання скриптів (рекомендовано)

1. Клонуйте репозиторій та перейдіть до директорії проекту:

```bash
cd trading-prediction-app
```

2. Запустіть додаток:

```bash
./start.sh
```

3. Зупиніть додаток:

```bash
./stop.sh
```

#### Метод 2: Використання Docker Compose напряму

1. Клонуйте репозиторій та перейдіть до директорії проекту:

```bash
cd trading-prediction-app
```

2. Зберіть та запустіть всі сервіси:

```bash
docker compose up --build
```

Або запустіть у фоновому режимі:

```bash
docker compose up -d --build
```

3. Додаток буде доступний за адресами:
   - **Frontend**: http://localhost
   - **Backend API**: http://localhost:3000
   - **Python API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

### Корисні команди

#### Переглянути статус контейнерів

```bash
docker compose ps
```

#### Переглянути логи

```bash
# Всі сервіси
docker compose logs

# Конкретний сервіс
docker compose logs frontend
docker compose logs backend
docker compose logs python-api

# Слідкувати за логами в реальному часі
docker compose logs -f
```

#### Зупинити сервіси

```bash
docker compose down
```

#### Зупинити сервіси та видалити volumes

```bash
docker compose down -v
```

#### Перезбудувати конкретний сервіс

```bash
docker compose build frontend
docker compose build backend
docker compose build python-api
```

#### Перезапустити сервіс

```bash
docker compose restart frontend
docker compose restart backend
docker compose restart python-api
```

## Структура проекту

```
trading-prediction-app/
├── python-api/          # FastAPI сервіс для ML прогнозів
│   ├── api.py
│   ├── model/
│   │   └── model.keras  # Навчена LSTM модель
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
├── neural-network/      # Код для навчання моделі
│   ├── model_trainer.py
│   ├── config.py
│   └── data/
├── docker-compose.yml   # Оркестрація всіх сервісів
├── README.md
├── DOCKER_SETUP.md      # Детальна документація Docker
└── NEURAL_NETWORK.md    # Пояснення роботи нейронної мережі
```

## Архітектура системи

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

Потік даних для прогнозування:
1. Користувач вибирає криптовалютну пару у Frontend
2. Frontend → Backend: запит прогнозу
3. Backend → Binance API: отримання історичних даних (30+ точок)
4. Backend → Python API: відправка даних для аналізу
5. Python API → LSTM Model: прогнозування
6. Python API → Backend: результат (ймовірність зростання)
7. Backend → Frontend: відформатований прогноз
8. Frontend: відображення результату та графіка
```

## Як працює нейронна мережа

Детальне пояснення архітектури та роботи LSTM моделі для прогнозування криптовалют дивіться в [NEURAL_NETWORK.md](NEURAL_NETWORK.md).

Коротко:

- **Модель**: LSTM (Long Short-Term Memory) нейронна мережа
- **Вхідні дані**: 30 часових точок × 5 ознак (open, high, low, close, volume)
- **Вихід**: ймовірність зростання ціни (0-1)
- **Фреймворк**: TensorFlow/Keras
- **Точність**: залежить від навчальних даних

## Розробка

### Локальна розробка без Docker

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

## Налаштування

### Змінні середовища

Ви можете налаштувати змінні середовища в `docker-compose.yml`:

#### Backend

- `NODE_ENV` - середовище Node.js (за замовчуванням: `production`)
- `PYTHON_API_URL` - URL Python API (за замовчуванням: `http://python-api:8000`)
- `PORT` - порт сервера (за замовчуванням: `3000`)

#### Python API

- `PYTHONUNBUFFERED` - вимкнення буферизації Python виводу

Для локальної розробки без Docker створіть `.env` файли:

- `back-end/.env` - для backend (використовуйте `PYTHON_API_URL=http://localhost:8000`)
- `python-api/.env` - для Python API

### Порти

За замовчуванням використовуються наступні порти:

- Frontend: 80
- Backend: 3000
- Python API: 8000

Щоб змінити порти, відредагуйте `docker-compose.yml`.

## Troubleshooting

### Контейнер не запускається

Перевірте логи:

```bash
docker compose logs [service-name]
```

### Порт вже зайнятий

Змініть порти в `docker-compose.yml` або зупиніть процес, що використовує порт.

### Проблеми з build

Очистіть Docker cache:

```bash
docker compose down
docker system prune -a
docker compose build --no-cache
```

## Ліцензія

MIT
