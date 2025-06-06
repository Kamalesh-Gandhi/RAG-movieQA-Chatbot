# Use minimal Python image 
FROM python:3.10-slim

# Set env vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy only necessary files
COPY requirements.txt ./
COPY rag_pipeline/ ./rag_pipeline/

# Install system dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "rag_pipeline/app.py"]