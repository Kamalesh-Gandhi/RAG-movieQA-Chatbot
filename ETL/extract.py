from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()

def extract_from_mongodb():

    try:
        """
        Extracts data from MongoDB and returns it as a list of dictionaries.
        """
        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client["sample_mflix"]

        movies = list(db.movies.find())
        embedded_movies = list(db.embedded_movies.find())
        comments = list(db.comments.find())
        sessions = list(db.sessions.find())
        users = list(db.users.find())
        theaters = list(db.theaters.find())

        print(f"Extracted {len(movies)} movies, {len(embedded_movies)} embedded movies, "
            f"{len(comments)} comments, {len(sessions)} sessions, {len(users)} users, {len(theaters)} theaters.")
        
        return{
            "movies" :movies,
            "embedded_movies" :embedded_movies, 
            "comments" :comments,
            "sessions" :sessions,   
            "users" : users,
            "theaters" : theaters
        }
    except Exception as e:
        print(f"An error occured while extracting data from mongodb: {str(e)}")

        return None
    
if __name__ == "__main__":
    data = extract_from_mongodb()
    if data:
        for key in data:
            if len(data[key]) > 0:
                 print(f"\n📂 {key} - First Document:\n{data[key][0]}\n")
            else:
                print(f"\n📂 {key} - No documents found.\n")
    
