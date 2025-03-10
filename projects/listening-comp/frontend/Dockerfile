# Build stage
FROM node:18-slim AS build

WORKDIR /app

# Copy package files (fixed path)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source files (fixed path)
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
