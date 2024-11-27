import streamlit as st
from pymongo import MongoClient
import requests
import pickle
from recommend import rcmd
import base64
from reviews import display_reviews

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')  # Ensure MongoDB is running locally
db = client['movienames']  # Your database name (replace with your desired database name)
collection = db['movie_data']  # Replace 'movie_data' with your desired collection name

# Function to fetch movie data from MongoDB
def fetch_movie_data_from_mongo(movie_title):
    movie_data = collection.find_one({'title': movie_title})
    return movie_data

# Setting the background
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        min-height: 100%;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-size: cover;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

set_png_as_page_bg('movie_recommendation4.jpg')

# Glass Effect CSS
glass_css = """
<style>
.glass {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
    padding: 20px;
    margin-bottom: 20px;
}
</style>
"""
st.markdown(glass_css, unsafe_allow_html=True)

# Button Styling (improved for responsiveness)
button_css = """
<style>
div.stButton > button:first-child {
  background-color: #316ba5;
  color: white;
  padding: 10px 20px;
  border-radius: 10px;
  border: 2px solid #000000;
  font-size: 16px;
  font-weight: bold;
  margin: 0.2em;
  display: block;
  transition: all 0.3s ease;
  width: 100%;  /* Make buttons responsive */
}

div.stButton > button:hover {
  background: linear-gradient(to bottom, #4a90e2 5%, #316ba5 100%);
  border-color: #4a90e2;
  transform: scale(1.05);
  cursor: pointer;
}

div.stButton > button:active {
  position: relative;
  top: 2px;
}
</style>
"""
st.markdown(button_css, unsafe_allow_html=True)

# TMDB API
TMDB_API_KEY = 'e09fea0e16abbb609056fc75d68caf69'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

# Load NLP model and vectorizer
filename = 'nlp_model.pkl'
clf = pickle.load(open(filename, 'rb'))
vectorizer = pickle.load(open('tranform.pkl', 'rb'))

def fetch_movie_details(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    return response.json()

def fetch_movie_posters(movie_titles):
    posters = []
    for title in movie_titles:
        url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={title}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data['results']:
                poster_path = data['results'][0]['poster_path']
                posters.append(f"https://image.tmdb.org/t/p/original{poster_path}")
            else:
                posters.append(None)
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching poster for {title}: {e}")
            posters.append(None)
    return posters

def fetch_movie_id(movie_title):
    url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        return data['results'][0]['id']
    return None

def display_movie_details(details):
    st.write(f"**Title:** {details['original_title']}")
    st.write(f"**Overview:** {details['overview']}")
    st.write(f"**Genres:** {', '.join([genre['name'] for genre in details['genres']])}")
    st.write(f"**Rating:** {details['vote_average']} ({details['vote_count']} votes)")
    st.write(f"**Release Date:** {details['release_date']}")
    st.write(f"**Runtime:** {details['runtime']} minutes")

def fetch_reviews_page():
    st.session_state['page'] = 'reviews'

def main():
    st.title("Movie Recommendation System")

    # Responsive layout for inputs and buttons
    col1, col2 = st.columns([2, 1])
    with col1:
        movie_name = st.text_input("Enter The Movie Name:", st.session_state.get('input', ''), key="custom")
    with col2:
        if st.button("Recommend Movies"):
            if movie_name:
                st.session_state['input'] = movie_name
                recommendations = rcmd(movie_name)
                if isinstance(recommendations, str):
                    st.error(recommendations)
                else:
                    st.session_state['recommendations'] = recommendations
                    st.success("Recommendations fetched!")
                    st.session_state['page'] = 'recommendations'
            else:
                st.error("Please enter a movie name.")

    # Navigation bar (improved for responsiveness)
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
    with nav_col1:
        if st.button("Reset"):
            st.session_state.clear()
            st.session_state['page'] = 'home'
    with nav_col2:
        if st.button("View Reviews"):
            fetch_reviews_page()
    with nav_col3:
        if st.session_state.get('page') != 'home' and st.button("Back to Home"):
            st.session_state['page'] = 'home'

    if st.session_state.get('page') == 'recommendations':
        show_recommendations()
    elif st.session_state.get('page') == 'reviews':
        fetch_reviews_page()

def show_recommendations():
    if 'recommendations' in st.session_state:
        recommendations = st.session_state['recommendations']
        posters = fetch_movie_posters(recommendations)

        for i, movie in enumerate(recommendations):
            st.markdown('<div class="glass">', unsafe_allow_html=True)

            with st.container():
                col1, col2 = st.columns([1, 3])

                with col1:
                    if posters[i]:
                        st.image(posters[i], width=150)

                with col2:
                    movie_id = fetch_movie_id(movie)
                    if movie_id:
                        details = fetch_movie_details(movie_id)
                        display_movie_details(details)
                    else:
                        st.error("Could not fetch movie details.")
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.write("No recommendations to show. Please enter a movie name above.")
if __name__ == "__main__":
    main()