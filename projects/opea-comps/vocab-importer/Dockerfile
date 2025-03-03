FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

# Print Python version and installed packages for debugging
RUN python --version
RUN pip list

# Use -u flag for unbuffered output and add more verbosity
CMD ["python", "-u", "app.py"]