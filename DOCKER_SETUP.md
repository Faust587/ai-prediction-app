# Docker Setup - Налаштування Docker

## Що було зроблено

### 1. Створено Dockerfile для кожного сервісу

#### Python API (`python-api/Dockerfile`)

- Базовий образ: `python:3.11-slim`
- Встановлено залежності з `requirements.txt`
- Виправлено залежності TensorFlow (замінено macOS-специфічні пакети на стандартні)
- Запуск через uvicorn на порту 8000

#### Backend (`back-end/Dockerfile`)

- Базовий образ: `node:20-slim`
- Встановлено залежності та зібрано TypeScript проект
- Запуск скомпільованого JavaScript файлу

#### Frontend (`front-end/Dockerfile`)

- Multi-stage build:
  - Stage 1: Збірка React додатку з Node.js
  - Stage 2: Сервування через Nginx
- Налаштовано nginx для proxy до backend та python-api

### 2. Створено docker-compose.yml

Оркестрація всіх трьох сервісів:

- **python-api**: порт 8000
- **backend**: порт 3000
- **frontend**: порт 80

Всі сервіси підключені до спільної мережі `app-network`.

### 3. Створено конфігураційні файли

- `front-end/nginx.conf` - конфігурація Nginx для фронтенду
- `.dockerignore` файли для кожного сервісу
- `README.md` - документація проекту
- `DOCKER_SETUP.md` - цей файл

### 4. Виправлено помилки

#### Python API

- Виправлено CMD в Dockerfile: `main:app` → `api:app`
- Замінено `tensorflow-macos` та `tensorflow-metal` на стандартний `tensorflow`

#### Frontend

- Виправлено TypeScript помилки в `PredictionChart.tsx`
- Налаштовано alias `@` в `vite.config.ts`
- Видалено невикористані змінні

#### Backend

- Налаштовано правильний шлях до скомпільованого файлу
- Видалено volume mounts, які перезаписували зібраний код
- **Виправлено підключення до Python API**: змінено `localhost:8000` на `python-api:8000` (використання Docker service name)
- Додано змінну середовища `PYTHON_API_URL` для гнучкого налаштування

## Структура файлів Docker

```
trading-prediction-app/
├── docker-compose.yml           # Головний файл оркестрації
├── python-api/
│   ├── Dockerfile              # Dockerfile для Python API
│   ├── .dockerignore           # Ігноровані файли
│   └── requirements.txt        # Python залежності
├── back-end/
│   ├── Dockerfile              # Dockerfile для Backend
│   ├── .dockerignore           # Ігноровані файли
│   └── package.json            # Node.js залежності
└── front-end/
    ├── Dockerfile              # Dockerfile для Frontend
    ├── nginx.conf              # Конфігурація Nginx
    ├── .dockerignore           # Ігноровані файли
    └── package.json            # Node.js залежності
```

## Використання

### Запуск всіх сервісів

```bash
docker compose up -d
```

### Зупинка всіх сервісів

```bash
docker compose down
```

### Перезбудова та запуск

```bash
docker compose up --build -d
```

### Перегляд логів

```bash
docker compose logs -f
```

### Перевірка статусу

```bash
docker compose ps
```

## Доступ до сервісів

- **Frontend**: http://localhost
- **Backend API**: http://localhost:3000
- **Python API**: http://localhost:8000
- **Python API Docs**: http://localhost:8000/docs

## Мережа

Всі сервіси підключені до мережі `app-network`, що дозволяє їм комунікувати між собою за іменами сервісів:

- `python-api:8000` - Python API сервіс
- `backend:3000` - Node.js backend
- `frontend:80` - React frontend з Nginx

**Важливо**: В Docker контейнерах використовуйте імена сервісів (наприклад, `http://python-api:8000`) замість `localhost`, оскільки `localhost` всередині контейнера вказує на сам контейнер, а не на хост машину.

## Особливості

1. **Multi-stage build для Frontend** - зменшує розмір фінального образу
2. **Nginx як reverse proxy** - ефективне сервування статичних файлів та проксування API запитів
3. **Restart policy** - автоматичний перезапуск контейнерів при падінні
4. **Оптимізація build context** - використання `.dockerignore` для виключення непотрібних файлів

## Troubleshooting

### Помилка "port already in use"

```bash
# Знайти процес, що використовує порт
lsof -i :80
lsof -i :3000
lsof -i :8000

# Або змінити порти в docker-compose.yml
```

### Контейнер падає при запуску

```bash
# Перегляньте логи
docker compose logs [service-name]

# Перезберіть образ без кешу
docker compose build --no-cache [service-name]
```

### Зміни в коді не застосовуються

```bash
# Перезберіть образи
docker compose build
docker compose up -d
```

## Продакшн

Для продакшн середовища рекомендується:

1. Використовувати `.env` файли для конфігурації
2. Налаштувати SSL/TLS сертифікати
3. Додати health checks
4. Налаштувати logging та monitoring
5. Використовувати Docker secrets для чутливих даних
6. Налаштувати resource limits

Приклад з resource limits:

```yaml
services:
  python-api:
    deploy:
      resources:
        limits:
          cpus: "1"
          memory: 2G
        reservations:
          cpus: "0.5"
          memory: 1G
```
