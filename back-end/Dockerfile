FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production && npm install -D typescript ts-node @types/node

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["node", "dist/index.js"] 