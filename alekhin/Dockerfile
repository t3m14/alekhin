FROM python:3.12-slim
# Set the working directory
WORKDIR /app
# Copy the requirements file into the container
COPY requirements.txt /app/
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the application code into the container
COPY . /app/
# Expose the port the app runs on
EXPOSE 8000
# Set the environment variable for Django settings
ENV DJANGO_SETTINGS_MODULE=alekhin.settings
# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# Use the default command to start the application