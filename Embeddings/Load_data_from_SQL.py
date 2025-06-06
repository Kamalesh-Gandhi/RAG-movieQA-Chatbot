# Embeddings/build_vectorstore.py

from sqlalchemy import create_engine
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()



# DB Connection
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")   
port = os.getenv("POSTGRES_PORT")
db_name = os.getenv("POSTGRES_DB")
db_uri = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(db_uri)


# SQL → Sentences
def load_and_prepare_sentences():
    df_movies = pd.read_sql("SELECT * FROM movies", engine)
    df_comments = pd.read_sql("SELECT * FROM comments", engine)
    df_users = pd.read_sql("SELECT * FROM users", engine)
    df_theaters = pd.read_sql("SELECT * FROM theaters", engine)
    df_sessions = pd.read_sql("SELECT * FROM sessions", engine)

    def movie_to_sentences(row):
        return (
        f"'{row['title']}' is a {row['genres']} movie released on {row['released']}. "
        f"It was directed by {row['directors']} and stars {row['cast']}. "
        f"The main plot: {row['plot']} Full story: {row['fullplot']}. "
        f"The film is available in {row['languages']} and was produced in {row['countries']}. "
        f"It runs for {row['runtime']} minutes and is rated '{row['rated']}'. "
        f"IMDb rating: {row['imdb_rating']} based on {row['imdb_votes']} votes. "
        f"Awards received: {row['awards']}."
    )

    def comment_to_sentences(row):
        return (
        f"On {row['date']}, {row['name']} commented on movie ID {row['movie_id']}: "
        f"\"{row['text']}\". Contact email: {row['email']}."
    )

    def user_to_sentences(row):
        return (
        f"This is the user profile of {row['name']} with the email address {row['email']}."
    )

    def theater_to_sentences(row):
        return f"Theater located in {row['theater_city']}, {row['theater_state']}."

    def session_to_sentences(row):
        return f"Session ID {row['_id']} was created by user ID {row['user_id']}."

    all_sentences = (
        df_movies.apply(movie_to_sentences, axis=1).tolist() +
        df_comments.apply(comment_to_sentences, axis=1).tolist() +
        df_users.apply(user_to_sentences, axis=1).tolist() +
        df_theaters.apply(theater_to_sentences, axis=1).tolist() +
        df_sessions.apply(session_to_sentences, axis=1).tolist()
    )

    return [s.strip() for s in all_sentences if isinstance(s, str) and len(s.strip()) > 10]

# Build vectorstore & save
def build_and_save_vectorstore():
    # ✅ Pinecone connection
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "rag-movies-qa"
    pinecone_index_obj = pc.Index(index_name)


    sentences = load_and_prepare_sentences()
    print(f"Loaded {len(sentences)} sentences from SQL database.")

    docs = [Document(page_content=s) for s in sentences]
    print(f"Converted to {len(docs)} Document objects.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)
    print(f"Split into {len(split_docs)} chunks.")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


    # # ✅ Pinecone vectorstore and upload
    # vectorstore = Pinecone(index, embeddings, text_key="page_content")
    # vectorstore.add_documents(split_docs)

    # ⬇️ Instantiate PineconeVectorStore directly
    vectorstore = PineconeVectorStore(
        index=pinecone_index_obj,    # Pass your Pinecone Index object here
        embedding=embeddings,
        text_key="text"              # Pinecone typically uses "text" as the default key for content.
                                     # Document.page_content will be mapped to this key.
    )

    #  Add documents to the vectorstore
    print(f"Uploading {len(split_docs)} chunks to Pinecone...")
    vectorstore.add_documents(split_docs)

    print("✅ Embeddings successfully uploaded to Pinecone!")

if __name__ == "__main__":
    build_and_save_vectorstore()
