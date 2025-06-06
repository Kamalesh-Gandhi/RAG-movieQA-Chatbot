import pandas as pd
from bson import ObjectId

def flatten_comments(comments_raw):
    """
    Flattens the comments data by extracting relevant fields and converting it to a DataFrame.
    
    Args:
        comments_raw (list): List of raw comment dictionaries.
        
    Returns:
        pd.DataFrame: DataFrame containing flattened comment data.
    """
    df = pd.json_normalize(comments_raw)
    df["_id"] = df["_id"].astype(str)
    df["movie_id"] = df["movie_id"].astype(str)
    df['name'] = df.get('name', '')
    df['email'] = df.get('email', '')
    df['text'] = df.get('text', '')
    df["date"] = df["date"].astype(str)

    return df 

def flatten_users(users_raw):
    """
    Flattens the users data by extracting relevant fields and converting it to a DataFrame.
    
    Args:
        users_raw (list): List of raw user dictionaries.
        
    Returns:
        pd.DataFrame: DataFrame containing flattened user data.
    """
    df = pd.json_normalize(users_raw)
    df["_id"] = df["_id"].astype(str)

    return df[["_id", "name", "email"]]

def flatten_movies(movies_raw):
    """
    Flattens the movies data by extracting relevant fields and converting it to a DataFrame.
    
    Args:
        movies_raw (list): List of raw movie dictionaries.
        
    Returns:
        pd.DataFrame: DataFrame containing flattened movie data.
    """
    df = pd.json_normalize(movies_raw)
    df["_id"] = df["_id"].astype(str)

    df['plot'] = df.get('plot', '')
    df['runtime'] = df.get('runtime', None)
    df['rated'] = df.get('rated', '')
    df['title'] = df.get('title', '')
    df['fullplot'] = df.get('fullplot', '')
    df['awards'] = df.get('awards.text', '')
    df['released'] = df.get('released', None)
    df['imdb_rating'] = df.get('imdb.rating', None)
    df['imdb_votes'] = df.get('imdb.votes', None)

    df['genres'] = df.get('genres', []).apply(lambda x: ','.join(x) if isinstance(x,list) else "")
    df['cast'] = df.get('cast', []).apply(lambda x: ','.join(x) if isinstance(x,list) else "")
    df['languages'] = df.get('languages', []).apply(lambda x: ','.join(x) if isinstance(x,list) else "")
    df['directors'] = df.get('directors', []).apply(lambda x: ','.join(x) if isinstance(x,list) else "")
    df['countries'] = df.get('countries', []).apply(lambda x: ','.join(x) if isinstance(x,list) else "")    

    # Convert to numeric types safely
    df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
    df['imdb_votes'] = pd.to_numeric(df['imdb_votes'], errors='coerce')
    df['imdb_rating'] = pd.to_numeric(df['imdb_rating'], errors='coerce')

    return df[["_id", "title", "plot", "genres", "cast", "languages",
                "directors", "countries", "fullplot", "runtime", "rated",
                "awards", "released", "imdb_rating", "imdb_votes"]]


def flatten_embeddedmovies(movies_raw):
    """
    Flattens the movies data by extracting relevant fields and converting it to a DataFrame.
    
    Args:
        movies_raw (list): List of raw movie dictionaries.
        
    Returns:
        pd.DataFrame: DataFrame containing flattened movie data.
    """
    df = pd.json_normalize(movies_raw)
    df["_id"] = df["_id"].astype(str)

    df['plot'] = df.get('plot', '')
    df['runtime'] = df.get('runtime', None)
    df['rated'] = df.get('rated', '')
    df['title'] = df.get('title', '')
    df['fullplot'] = df.get('fullplot', '')
    df['awards'] = df.get('awards.text', '')
    df['released'] = df.get('released', None)
    df['imdb_rating'] = df.get('imdb.rating', None)
    df['imdb_votes'] = df.get('imdb.votes', None)
    df['writers'] = df['writers'].apply(lambda x: ','.join(x) if isinstance(x, list) else "")
    df['production'] = df.get('production', '')

    df['genres'] = df.get('genres', []).apply(lambda x: ','.join(x) if isinstance(x,list) else "")
    df['cast'] = df.get('cast', []).apply(lambda x: ','.join(x) if isinstance(x,list) else "")
    df['languages'] = df.get('languages', []).apply(lambda x: ','.join(x) if isinstance(x,list) else "")
    df['directors'] = df.get('directors', []).apply(lambda x: ','.join(x) if isinstance(x,list) else "")
    df['countries'] = df.get('countries', []).apply(lambda x: ','.join(x) if isinstance(x,list) else "")    

    # Convert to numeric types safely
    df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
    df['imdb_votes'] = pd.to_numeric(df['imdb_votes'], errors='coerce')
    df['imdb_rating'] = pd.to_numeric(df['imdb_rating'], errors='coerce')


    return df[["_id", "title", "plot", "genres", "cast", "languages",
                "directors", "countries", "fullplot", "runtime", "rated",
                "awards", "released", "imdb_rating", "imdb_votes"]]

def flatten_theaters(theaters_raw):
    """
    Flattens the theaters data by extracting relevant fields and converting it to a DataFrame.
    
    Args:
        theaters_raw (list): List of raw theater dictionaries.
        
    Returns:
        pd.DataFrame: DataFrame containing flattened theater data.
    """
    df = pd.json_normalize(theaters_raw)
    df["_id"] = df["_id"].astype(str)
    df['theater_id'] = df["theaterId"].astype(str)
    df['theater_city'] = df.get('location.address.city', '')
    df['theater_state'] = df.get('location.address.state', '')

    return df[["_id", "theater_id", "theater_city", "theater_state"]]

def flatten_sessions(raw):
    df = pd.json_normalize(raw)
    df["_id"] = df["_id"].astype(str)
    df["user_id"] = df["user_id"].astype(str)
    return df[["_id", "user_id", "jwt"]]

def transform_data(raw_data: dict):
    """
    Transforms raw data extracted from MongoDB into structured DataFrames.
    
    Args:
        raw_data (dict): Dictionary containing raw data from MongoDB.
        
    Returns:
        dict: Dictionary containing transformed DataFrames.
    """
    movies_df = flatten_movies(raw_data["movies"])
    embedded_movies_df = flatten_embeddedmovies(raw_data["embedded_movies"])

    all_movies_df = pd.concat([movies_df, embedded_movies_df], ignore_index=True)
    all_movies_df.drop_duplicates(subset="_id", inplace=True)

    return {
        "movies": all_movies_df,
        "comments": flatten_comments(raw_data["comments"]),
        "users": flatten_users(raw_data["users"]),
        "theaters": flatten_theaters(raw_data["theaters"]),
        "sessions": flatten_sessions(raw_data["sessions"])
    }

if __name__ == "__main__":
    from extract import extract_from_mongodb
    raw = extract_from_mongodb()
    transformed = transform_data(raw)

    for key in transformed:
        print(f"\n📂 {key} - Transformed Rows: {len(transformed[key])}")
        print(transformed[key].head(1))


