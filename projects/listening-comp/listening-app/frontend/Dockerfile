# Use Node.js as the base image for building the frontend
FROM node:18-slim as build

# Set the working directory
WORKDIR /app

# Copy package.json for dependency installation
COPY ./frontend/package.json ./

# Install dependencies
RUN npm install --quiet

# Copy the rest of the frontend source code
COPY ./frontend/ ./

# Build the frontend
RUN npm run build

# Use Nginx as the base image for serving the frontend
FROM nginx:stable-alpine

# Copy the built frontend files to the Nginx HTML directory
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 for the frontend
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]