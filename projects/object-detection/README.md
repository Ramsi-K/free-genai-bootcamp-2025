# Korean Object Detection App

## Setup Instructions

1. **Prerequisites**:

   - Docker installed
   - Docker Compose installed

2. **Run the app**:

   ```bash
   docker-compose up -d
   ```

3. **Access the app**:

   - On your computer: http://localhost:8080
   - On your phone:
     1. Connect to the same WiFi network as your computer
     2. Find your computer's local IP address:
        - Mac/Linux: Run `ifconfig | grep "inet "`
        - Windows: Run `ipconfig`
     3. Visit: http://[YOUR_COMPUTER_IP]:8080

4. **Stop the app**:
   ```bash
   docker-compose down
   ```

## Features

- Real-time object detection using MediaPipe
- Korean labels for detected objects
- Mobile-optimized interface
