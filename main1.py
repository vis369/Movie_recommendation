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
    # Query MongoDB to find movie by title
    movie_data = collection.find_one({'title': movie_title})  # Replace 'title' with the actual field name
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
    background: rgba(255, 255, 255, 0.2); /* Semi-transparent white */
    border: 1px solid rgba(255, 255, 255, 0.3); /* Light border */
    border-radius: 15px;
    backdrop-filter: blur(10px); /* Blur the background */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25); /* Subtle shadow */
    padding: 20px; /* Add some space inside */
    margin-bottom: 20px; /* Space between recommendations */
}
</style>
"""
st.markdown(glass_css, unsafe_allow_html=True)



# Adding styles to Text Input
custom_css = """
<style>
input[type="text"] {
    padding: 10px;
    border: 2px solid #6da0d3;
    border-radius: 5px;
    font-size: 16px;
}
input[type="text"]:focus {
    box-shadow: 0px 0px 7px #6da0d3;
    border-color: #6da0d3;
}
input[type="text"]:hover {
    border: 1px solid #6da0d3;
    border-radius: 5px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Adding styles to Buttons
m = st.markdown(""" 
<style>
div.stButton > button:first-child {
    background-color: #316ba5;
    color: white;
    height: 2em;
    width: 12em;
    border-radius:10px;
    border:3px solid #000000;
    font-size:15px;
    font-weight: bold;
    margin: auto;
    display: block;
}

div.stButton > button:hover {
	background:linear-gradient(to bottom, #316ba5 5%, #183552 100%);
	background-color:#316ba5;
}

div.stButton > button:active {
	position:relative;
	top:3px;
}

</style>""", unsafe_allow_html=True)

# Font
st.markdown("""
<link href='https://fonts.googleapis.com/css?family=Merriweather' rel='stylesheet'>
<style>
body {
    font-family: 'Merriweather', serif;
    font-size: 13px; 
    line-height: 1.15;
    font-weight:300
}
</style>
""", unsafe_allow_html=True)

# TMDB API
TMDB_API_KEY = 'e09fea0e16abbb609056fc75d68caf69'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

# Load the NLP model and TFIDF vectorizer
filename = 'nlp_model.pkl'
clf = pickle.load(open(filename, 'rb'))
vectorizer = pickle.load(open('tranform.pkl', 'rb'))

# Fetching Movie Details from TMDB website
def fetch_movie_details(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    return response.json()

def fetch_movie_posters(movie_titles):
    posters = []
    for title in movie_titles:
        url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={title}"
        try:
            response = requests.get(url, timeout=10)  # Add timeout here
            response.raise_for_status()  # Raise an error for bad responses
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
    # title Font
    center_heading_css = """
    <link href='https://fonts.googleapis.com/css?family=Merriweather' rel='stylesheet'>
    <style>
       h1 {
       text-align: center;
       font-size:50px;
       margin-bottom:40px
       font-family: 'Merriweather', serif;
       font-weight: 700;
       white-space: nowrap;
       }
    </style>
              """
    st.markdown(center_heading_css, unsafe_allow_html=True)
    st.title("Movie Recommendation System")
    if 'input' not in st.session_state:
       st.session_state['input'] = ''
    if 'page' not in st.session_state:
       st.session_state['page'] = 'home'
    if 'recommendations' not in st.session_state:
       st.session_state['recommendations'] = []

    if st.session_state['page'] == 'home':
        movie_name = st.text_input("Enter The Movie Name:", "", key="custom")
        if movie_name:
            st.session_state['input'] = movie_name
        else:
            st.session_state['input'] = ""

    # Recommendations   
    if st.button("Recommend Movies"):
        if st.session_state['input']:
            recommendations = rcmd(st.session_state['input'])
            if isinstance(recommendations, str):
                st.error(recommendations)
            else:
                st.session_state['recommendations'] = recommendations
                st.success("Recommendations:")
                show_recommendations()
        else:
            st.error("Please enter a movie name.")
        if st.button("Back to Home"):
            st.session_state['page'] = 'home'

    # Reset functionality
    if st.button("Reset"):
        st.session_state.clear()  # Clear all session states
        st.session_state['page'] = 'home'  # Set the page to 'home'
        st.session_state['recommendations'] = []  # Reset recommendations

    st.markdown('<p></p>', unsafe_allow_html = True)

    # Reviews
    if st.button("View Reviews"):
        fetch_reviews_page()

    # Reviews page
    if st.session_state['page'] == 'reviews':
       st.write(f"Fetching reviews for: {st.session_state['input']}")
       col1, col2 = st.columns([1, 3])
       movie_data = fetch_movie_data_from_mongo(st.session_state['input'])
       if movie_data:
           st.write(f"Movie Data from MongoDB for {st.session_state['input']}:")
           st.write(movie_data)  # Displaying movie data from MongoDB
       else:
           st.error(f"Movie data not found in MongoDB for {st.session_state['input']}")

       st.markdown("<hr>", unsafe_allow_html=True)
       display_reviews(st.session_state['input'])

       if st.button("Back to Home"):
        st.session_state['page'] = 'home'


def show_recommendations():
    if 'recommendations' in st.session_state:
        recommendations = st.session_state['recommendations']
        posters = fetch_movie_posters(recommendations)
        
        for i, movie in enumerate(recommendations):
            # Start glass effect container
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            
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
            
            # End glass effect container
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.write("No recommendations to show. Please enter a movie name above.")




if __name__ == "__main__":
    main()
