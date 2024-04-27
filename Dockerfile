# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /bot

# Copy the current directory contents into the container at /usr/src/app
COPY . /bot/

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the bot runs on
EXPOSE 8080

# Run the bot when the container launches
CMD ["python", "main.py"]
