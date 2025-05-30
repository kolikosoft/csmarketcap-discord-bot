# Use the official Python base image
FROM python:3.11-slim


# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to run the application
CMD ["python", "bot.py"]
