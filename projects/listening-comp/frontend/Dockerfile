# Build stage
FROM node:18-slim AS build

WORKDIR /app

# Copy package.json first for better caching
COPY frontend/package*.json ./

RUN npm install

# Then copy the rest of the frontend files
COPY frontend/ .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
