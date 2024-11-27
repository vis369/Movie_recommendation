import streamlit as st
import requests
import numpy as np
import pickle
import matplotlib.pyplot as plt


TMDB_API_KEY = 'c623f238e0338705296c4af77125f967'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

# Fetch movie details using TMDB API 
def fetch_movie_posters(movie_titles):
    posters = []
    for title in movie_titles:
        url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={title}"
        response = requests.get(url)
        data = response.json()
        if data['results']:
            poster_path = data['results'][0]['poster_path']
            posters.append(f"https://image.tmdb.org/t/p/original{poster_path}")
        else:
            posters.append(None)
    return posters

def fetch_movie_id(movie_title):
    url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        return data['results'][0]['id']
    return None

def fetch_movie_details(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    return response.json()


# Load the NLP model and TFIDF vectorizer 
filename = 'nlp_model.pkl'
clf = pickle.load(open(filename, 'rb'))
vectorizer = pickle.load(open('tranform.pkl', 'rb'))

def fetch_tmdb_reviews(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}'
    response = requests.get(url)
    reviews_result = response.json().get('results', [])
    
    reviews_list = [] 
    reviews_status = []  
    for review in reviews_result:
        content = review.get('content')
        if content:
            reviews_list.append(content)
            # Passing the reviews to our model
            movie_review_list = np.array([content])
            movie_vector = vectorizer.transform(movie_review_list)
            pred = clf.predict(movie_vector)
            reviews_status.append('Good' if pred else 'Bad')

    movie_reviews = {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))}
    return movie_reviews

def display_reviews(movie_name):
    details = get_movie_details(movie_name)
    if details:
        movie_id = fetch_movie_id(movie_name)
        if movie_id:
            reviews = fetch_tmdb_reviews(movie_id)
            word_limit_per_review = 100

            st.write("User Reviews:")
            for review, status in reviews.items():
                limited_review = ' '.join(review.split()[:word_limit_per_review])
                st.write(f"Review: {limited_review}\n\nStatus: {status}")
                st.markdown("<hr>", unsafe_allow_html=True)

            # plotting pie chart  
            good_count = sum(1 for status in reviews.values() if status == 'Good')
            bad_count = sum(1 for status in reviews.values() if status == 'Bad')

            # Handle edge cases where there are no valid reviews or only one type of review
            if good_count == 0 and bad_count == 0:
                st.warning("No valid reviews found for sentiment analysis.")
                return
            
            # If there is only one type of sentiment, we can't generate a pie chart
            if good_count == 0 or bad_count == 0:
                st.warning("Not enough variety in reviews to generate a pie chart.")
                return
            
            labels = ['Good', 'Bad']
            sizes = [good_count, bad_count]
            colors = ['#4CAF50', '#FF5252']
            explode = (0.1, 0)  # explode 1st slice

            # Create a pie chart
            fig1, ax1 = plt.subplots(figsize=(6, 6))  # Ensure proper figure size
            ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            st.pyplot(fig1)  
        else:
            st.error("TMDB ID not found for this movie.")
    else:
        st.error("Movie details not found.")

def get_movie_details(movie_title):
    my_api_key = 'c623f238e0338705296c4af77125f967'
    url = f'https://api.themoviedb.org/3/search/movie?api_key={my_api_key}&query={movie_title}'
    response = requests.get(url)
    if response.status_code == 200:
        movie = response.json()
        if movie['results']:
            movie_id = movie['results'][0]['id']
            return fetch_movie_details(movie_id)
        else:
            st.error("Movie not found.")
    else:
        st.error("Failed to fetch movie details.")
