from sqlalchemy import Table, Column, String, Integer, MetaData, ForeignKey

metadata = MetaData()

# Define the 'movies' table schema
movies_table = Table(
    'movies', metadata,
    Column('_id', String, primary_key=True),
    Column('title', String, nullable=False),
    Column('plot', String, nullable=True),
    Column('genres', String, nullable=True),
    Column('cast', String, nullable=True),
    Column('languages', String, nullable=True),
    Column('directors', String, nullable=True),
    Column('countries', String, nullable=True),
    Column('fullplot', String, nullable=True),
    Column('runtime', Integer, nullable=True),
    Column('rated', String, nullable=True),
    Column('awards', String, nullable=True),
    Column('released', String, nullable=True),
    Column('imdb_rating', Integer, nullable=True),
    Column('imdb_votes', Integer, nullable=True)
)

# Define the 'comments' table schema    
comments_table = Table(
    'comments', metadata,
    Column('_id', String, primary_key=True),
    Column('movie_id', String,nullable=False),
    Column('name', String, nullable=True),
    Column('email', String, nullable=True),
    Column('text', String, nullable=True),
    Column('date', String, nullable=True)
)

# Define the 'users' table schema
users_table = Table(
    'users', metadata,
    Column('_id', String, primary_key=True),
    Column('name', String, nullable=False),
    Column('email', String, nullable=False)
)

# Define the 'sessions' table schema    
sessions_table = Table(
    'sessions', metadata,
    Column('_id', String, primary_key=True),
    Column('user_id', String, nullable=False),
    Column('jwt', String, nullable=False),

)

# Define the 'theaters' table schema
theaters_table = Table(
    'theaters', metadata,
    Column('_id', String, primary_key=True),
    Column('theater_id', String, nullable=False),
    Column('theater_city', String, nullable=True),
    Column('theater_state', String, nullable=True)
)