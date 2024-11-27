import pandas as pd
from pymongo import MongoClient

# Load the CSV file
df = pd.read_csv('main_data.csv')  # Replace with your actual CSV file path

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Ensure MongoDB is running locally
db = client['movienames']  # Your database name (replace with your desired database name)

try:
    # List all databases
    databases = client.list_database_names()
    print("Connected to MongoDB. Databases:", databases)
except Exception as e:
    print("Failed to connect to MongoDB:", e)

# Create or access a collection within the database
collection = db['movie_data']  # Replace 'movie_data' with your desired collection name

# Convert DataFrame to a list of dictionaries (MongoDB documents)
data = df.to_dict(orient='records')

# Insert data into MongoDB
collection.insert_many(data)

# Verify the insertion by printing the first document
document = collection.find_one()  # Find one document to verify
print(document)
