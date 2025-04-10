# Use official Nginx image
FROM nginx:alpine

# Copy your HTML file
COPY app/index.html /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]