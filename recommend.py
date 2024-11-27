import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
import streamlit as st


# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI if needed
db = client['movienames']  # Replace 'movienames' with your database name
collection = db['movie_data']  # Replace 'movie_data' with your collection name

# Fetch movie data from MongoDB
def fetch_movie_data():
    # Retrieve all movie documents from the collection
    movies = collection.find()  # Adjust query if you need to filter or sort data
    # Convert the MongoDB cursor to a pandas DataFrame
    data = pd.DataFrame(list(movies))
    return data

# Training similarity learning model - Cosine Similarity
def create_similarity():
    data = fetch_movie_data()  # Get movie data from MongoDB
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])  # Assuming 'comb' is a column in your MongoDB documents
    similarity = cosine_similarity(count_matrix)
    return data, similarity

# Recommendation function
def rcmd(m):
    m = m.lower()
    try:
        data.head() 
        similarity.shape
    except:
        data, similarity = create_similarity()

    # Check if the movie is in the database
    if m not in data['movie_title'].unique():
        return 'Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movie.'
    else:
        # Find the index of the movie
        i = data.loc[data['movie_title'] == m].index[0]
        # Get the similarity scores for the movie
        lst = list(enumerate(similarity[i]))
        # Sort by similarity score in descending order
        lst = sorted(lst, key=lambda x: x[1], reverse=True)
        lst = lst[1:6]  # Get top 5 similar movies
        # Get movie titles for the recommended movies
        l = [data['movie_title'][i[0]] for i in lst]
        return l
