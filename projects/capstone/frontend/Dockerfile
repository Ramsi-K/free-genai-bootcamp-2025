FROM node:18-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Add environment variables
ENV NODE_ENV=development
ENV VITE_API_URL=http://localhost:8000/api

EXPOSE 5173

# Start development server with correct host and port
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
