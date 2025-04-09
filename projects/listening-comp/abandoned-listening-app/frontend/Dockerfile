# Build stage
FROM node:18.19-slim

WORKDIR /app

# Copy package files
COPY ./frontend/package.json ./

# Install dependencies
RUN npm install

# Copy frontend code
COPY ./frontend/ ./

# Build React app
RUN npm run build

# Serve with Node
EXPOSE 80
CMD ["npm", "start"]