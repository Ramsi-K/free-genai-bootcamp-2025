# Build stage
FROM node:18-slim AS build

WORKDIR /app

# Copy package files first for better caching
COPY frontend/package*.json ./

# Install dependencies - use npm install instead of npm ci since package-lock.json might not exist
RUN npm install --quiet

# Copy frontend source code
COPY frontend/ .

# Debugging: List files before running npm build
RUN ls -la /app

# Debugging: Print Node.js and npm versions
RUN node -v && npm -v

# Build the app
RUN npm run build

# Production stage with minimal image
FROM nginx:stable-alpine
# Copy build artifacts from the build stage
COPY --from=build /app/build /usr/share/nginx/html

# Add nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
