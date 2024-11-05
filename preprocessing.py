import pandas as pd
from tqdm import tqdm

### This script is used to preprocess the multiple raw IMDb data files and merge them into a single CSV file ###
### This script takes quite a while to run due to the large size of the IMDb datasets (It took me about 45 mins to an hour) ###

# File paths for IMDb datasets
name_file = 'raw_data/name.basics.tsv'
title_file = 'raw_data/title.basics.tsv'
principals_file = 'raw_data/title.principals.tsv'
ratings_file = 'raw_data/title.ratings.tsv'

# Set chunk size (process 100,000 rows at a time for memory efficiency)
chunksize = 10**5

# Initialize empty DataFrames to store the final results
movies_df = pd.DataFrame()
names_df = pd.DataFrame()
principals_df = pd.DataFrame()
ratings_df = pd.DataFrame()

# Function to get total number of lines for progress bar
def get_total_lines(file_path):
    with open(file_path, 'r') as f:
        total_lines = sum(1 for _ in f) - 1 
    return total_lines

# Read and process 'name.basics.tsv' in chunks with progress bar
print("Processing 'name.basics.tsv'")
total_lines = get_total_lines(name_file)
for chunk in tqdm(pd.read_csv(name_file, sep='\t', dtype=str, chunksize=chunksize), total=total_lines//chunksize):
    names_df = pd.concat([names_df, chunk])

# Read and process 'title.basics.tsv' in chunks with progress bar
print("Processing 'title.basics.tsv'")
total_lines = get_total_lines(title_file)
for chunk in tqdm(pd.read_csv(title_file, sep='\t', dtype=str, chunksize=chunksize), total=total_lines//chunksize):
    movies_df = pd.concat([movies_df, chunk])

# Read and process 'title.principals.tsv' in chunks with progress bar
print("Processing 'title.principals.tsv'")
total_lines = get_total_lines(principals_file)
for chunk in tqdm(pd.read_csv(principals_file, sep='\t', dtype=str, chunksize=chunksize), total=total_lines//chunksize):
    principals_df = pd.concat([principals_df, chunk])

# Read and process 'title.ratings.tsv' in chunks with progress bar
print("Processing 'title.ratings.tsv'")
total_lines = get_total_lines(ratings_file)
for chunk in tqdm(pd.read_csv(ratings_file, sep='\t', dtype=str, chunksize=chunksize), total=total_lines//chunksize):
    ratings_df = pd.concat([ratings_df, chunk])

# Filter movies only
movies_df = movies_df[movies_df['titleType'] == 'movie']

# Merge movies with ratings
final_movies_df = pd.merge(movies_df, ratings_df, on='tconst', how='left')

# Merge movies with principals to get directors and cast
final_movies_df = pd.merge(final_movies_df, principals_df, on='tconst', how='left')

# Merge with names to get director and cast names
final_movies_df = pd.merge(final_movies_df, names_df, left_on='nconst', right_on='nconst', how='left')

# Cleaning and selecting relevant columns (optional)
final_movies_df = final_movies_df[['tconst', 'primaryTitle', 'originalTitle', 'startYear', 'genres', 'averageRating', 'numVotes', 'primaryName']]

# Save the final DataFrame to CSV
final_movies_df.to_csv('processed_data/movies_with_cast.csv', index=False)
print("Saved 'movies_with_cast.csv'")
