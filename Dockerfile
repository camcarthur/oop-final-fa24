# Use the official Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt (contains the Python dependencies)
COPY requirements.txt .

# Install the required Python modules
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the Flask app port
EXPOSE 5000

# Set the default command to run the app
CMD ["flask", "run", "--host=0.0.0.0"]
