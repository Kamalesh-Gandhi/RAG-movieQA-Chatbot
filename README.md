# Movie QA Chatbot with RAG 🎬🤖          
    
## Project Description

This project develops an intelligent question-answering chatbot that provides accurate and contextually relevant answers to user queries about movies. Leveraging a Retrieval Augmented Generation (RAG) architecture, the chatbot goes beyond standard Large Language Models (LLMs) by retrieving information from a dedicated knowledge base (PostgreSQL and Pinecone Vector Database) to inform its responses, ensuring up-to-date and specific movie details. The application is built with Streamlit for an interactive user interface and deployed using Docker on AWS EC2 for scalability and accessibility.

---

## Features ✨

- **Contextual Movie QA** - Answers questions about movie plots, cast, directors, release dates, reviews, and more by retrieving precise information. 🎬
- **Retrieval Augmented Generation (RAG)** - Combines the power of a Generative AI model (Groq's Gemma2) with a structured knowledge base for factual accuracy. 🧠
- **Vector Database Integration (Pinecone)** - Efficiently stores and retrieves movie embeddings for semantic search and relevant context retrieval. 🔍
- **Relational Database (PostgreSQL)** - Manages structured movie metadata. 🗃️
- **Modern LLM Integration (Groq)** - Utilizes Groq's high-speed inference for quick and relevant answer generation. ⚡
- **Sentence Embeddings (HuggingFace)** - Transforms movie data into dense vector representations for semantic similarity search. 📊
- **Interactive User Interface (Streamlit)** - Provides a user-friendly web interface for asking questions and viewing responses. 🖥️
- **Containerized Deployment (Docker)** - Ensures portability and consistent environment across different deployment targets. 🚢
- **Cloud Deployment (AWS EC2)** - Scalable and accessible deployment of the chatbot as a web service. ☁️

---

## Technologies Used 🛠️

- **Frontend** - Streamlit 📊
- **Backend/Logic** - Python 🐍
- **LLM** - Groq (Gemma2) 💬
- **Vector Database** - Pinecone 🌲
- **Embedding Model** - sentence-transformers/all-MiniLM-L6-v2 (from HuggingFace) 🤗
- **Traditional Database** - PostgreSQL 🐘
- **Orchestration** - LangChain 🔗
- **Containerization** - Docker 🐳
- **Cloud Platform** - AWS EC2 ☁️
- **Environment Management** - python-dotenv 🔑

---

## Architecture Overview 🏗️

The system operates as follows:

1. User submits a query via the Streamlit interface. 💬
2. The query is embedded into a vector representation. ➡️
3. This vector is used to perform a similarity search in the Pinecone vector database to retrieve relevant movie context. 🔍
4. Optionally, specific movie details might be retrieved from PostgreSQL based on keywords or IDs found. 📚
5. The retrieved context (from Pinecone and/or PostgreSQL) is combined with the user's original query. 🤝
6. This augmented prompt is sent to the Groq LLM. 🚀
7. The LLM generates a comprehensive answer based on the provided context. ✅
8. The answer is displayed to the user in the Streamlit app. 🌟

---

## Setup and Local Development 💻

**Prerequisites**
1. Python 3.9+ 🐍
2. Docker Desktop 🐳
3. A Groq API Key 🔑
4. A Pinecone API Key and Environment 🌲
5. A running PostgreSQL instance (local or remote) 🐘
6. Necessary AWS credentials (for EC2 deployment) ☁️

#### 1. Clone the Repository
```bash
git clone https://github.com/Kamalesh-Gandhi/RAG-movieQA-Chatbot.git
cd your_repo_name

```

#### 2. Set Up Environment Variables
Create a .env file in the root of your project directory with the following variables:
```
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=your_pinecone_index_name_here
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=your_postgres_host # e.g., localhost or your RDS endpoint
POSTGRES_PORT=5432
POSTGRES_DB=your_postgres_db_name

```

#### 3. Install Dependencies (for local testing, if needed)
```bash
pip install -r requirements.txt
```

#### 4. Prepare your Knowledge Base (Pinecone & PostgreSQL)
- **PostgreSQL** - Ensure your PostgreSQL database is running and accessible with the provided credentials. You will need to load your movie data into it. 🎥
- **Pinecone** -
  - Create an index in Pinecone with the specified PINECONE_INDEX_NAME and correct dimension for all-MiniLM-L6-v2 embeddings (384 dimensions). 📏
  - You will need to have a script or process to generate embeddings from your movie data and upload them to this Pinecone index. This often involves reading data from PostgreSQL, embedding it, and upserting. ⬆️

#### 5. Run Locally (for testing)
```bash
streamlit run rag_pipeline/app.py
```

---

## Docker Deployment (AWS EC2) 🚀

This project is designed for robust deployment using Docker on AWS EC2.

##### 1. Build the Docker Image
From the root of your project directory:
```bash
docker build -t image-name .
```
#### 2. Push to Docker Hub (or your preferred registry)
```bash
docker push dockerhub-repo:version
```
#### 3. AWS EC2 Setup
- **Launch EC2 Instance** - Choose an instance type with sufficient RAM (e.g., t2.medium, t3.medium, or larger) to avoid Out-of-Memory (OOM) errors, especially when loading embedding models. 💾
- **Security Group** -  Ensure your EC2 instance's Security Group allows inbound traffic on:
  - Port 22 (SSH) from your IP. 🔑
  - Port 8501 (for Streamlit) from 0.0.0.0/0 (for public access) or a specific IP range. 🌐
- **SSH into EC2** - Connect to your instance using your .pem key. 🔗

#### 4. Install Docker on EC2
```bash
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
exit # Log out and log back in for group changes to apply
```
#### 5. Transfer .env File to EC2
From your local machine's terminal (where your .env and .pem are):
```bash
scp -i your_pem_file_name.pem .env ec2-user@YOUR_EC2_PUBLIC_IP:~
```
#### 6. Pull and Run Docker Container on EC2
Once logged back into your EC2 instance:
```bash
docker pull docker-repo:version
docker run -d -p 8501:8501 --env-file /home/ec2-user/.env dockerhub-repo:version
```
#### 7. Access the Application
Open your web browser and navigate to:
```
http://YOUR_EC2_PUBLIC_IP:8501
```







