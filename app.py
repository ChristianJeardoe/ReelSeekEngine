import pandas as pd
from collections import defaultdict
import math

### This is the main program that will take user input and recommend movies based on the input ###

# Load the CSV file
file_path = 'processed_data/condensed_movies_with_cast.csv'

movies_df = pd.read_csv(file_path, dtype={'startYear': str})
movies_df = movies_df[movies_df['primaryName'].notna()]

# Preserve original title for display purposes
movies_df['primaryTitle_original'] = movies_df['primaryTitle']

# Preprocess columns for indexing
movies_df['primaryTitle_processed'] = movies_df['primaryTitle'].str.lower().str.strip()
movies_df['genres'] = movies_df['genres'].replace("\\N", "")
movies_df['primaryName'] = movies_df['primaryName'].replace("\\N", "")

# Split and normalize genres and names
movies_df['genre_list'] = movies_df['genres'].apply(lambda x: x.split(',') if pd.notna(x) else [])
movies_df['name_list'] = movies_df['primaryName'].apply(lambda x: x.split(',') if pd.notna(x) else [])
movies_df['genre_list'] = movies_df['genre_list'].apply(lambda genres: [genre.strip().lower() for genre in genres])

# Join first and last names
movies_df['name_list'] = movies_df['name_list'].apply(lambda names: [name.replace(" ", "").lower() for name in names])

# Combine text for indexing
movies_df['Combined_Text'] = movies_df.apply(
    lambda row: f"{row['primaryTitle_processed']} {' '.join(row['genre_list'])} {' '.join(row['name_list'])}",
    axis=1
)

# Create an inverted index to map terms to documents
inverted_index = defaultdict(set)
for idx, row in movies_df.iterrows():
    terms = row['Combined_Text'].split()
    for term in terms:
        inverted_index[term].add(idx)

# BM25 parameters
# k1: term frequency parameter
# b: length normalization parameter
k1 = 1.5
b = 0.75

# Compute document lengths and average document length
movies_df['doc_length'] = movies_df['Combined_Text'].apply(lambda x: len(x.split()))
avg_doc_length = movies_df['doc_length'].mean()

# Normalize ratings and votes for hybrid scoring
max_rating = movies_df['averageRating'].max()
max_votes = movies_df['numVotes'].max()
movies_df['normalized_rating'] = movies_df['averageRating'] / max_rating
movies_df['normalized_votes'] = movies_df['numVotes'] / max_votes

def calculate_idf(term):
    doc_frequency = len(inverted_index[term])
    return math.log((len(movies_df) - doc_frequency + 0.5) / (doc_frequency + 0.5) + 1)

def calculate_bm25(term, doc_id):
    tf = movies_df.loc[doc_id, 'Combined_Text'].split().count(term)
    doc_length = movies_df.loc[doc_id, 'doc_length']
    idf = calculate_idf(term)

    numerator = tf * (k1 + 1)
    denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
    return idf * (numerator / denominator)

# Hybrid scoring function
# alpha: BM25 weight
# beta: normalized rating weight
# gamma: normalized votes weight
def search_movies_bm25_hybrid(query, exclude_ids=set(), alpha=0.55, beta=0.35, gamma=0.1):
    query = query.lower()
    query_terms = query.split()
    doc_scores = defaultdict(float)
    
    # Calculate BM25 score for each document that contains each query term
    for term in query_terms:
        if term in inverted_index:
            for doc_id in inverted_index[term]:
                if doc_id not in exclude_ids:  # Exclude document IDs of users movies
                    bm25_score = calculate_bm25(term, doc_id)
                    doc_scores[doc_id] += bm25_score

    hybrid_scores = []
    for doc_id, bm25_score in doc_scores.items():
        rating_score = movies_df.loc[doc_id, 'normalized_rating']
        votes_score = movies_df.loc[doc_id, 'normalized_votes']
        hybrid_score = (alpha * bm25_score) + (beta * rating_score) + (gamma * votes_score)
        hybrid_scores.append((doc_id, hybrid_score))

    # Sort documents by score
    sorted_docs = sorted(hybrid_scores, key=lambda x: x[1], reverse=True)
    return sorted_docs

# Function to collect user input for favorite movies and ensure they are found in the dataset
def get_user_favorite_movies():
    user_movies = []
    
    print("Please enter 3 to 10 movies you like. Once you have entered at least 3 movies, you can press Enter to stop.")

    while len(user_movies) < 10:
        title = input(f"Enter the title of movie {len(user_movies) + 1}: ").strip().lower()
        if not title and len(user_movies) >= 3:
            break
        year = input(f"Enter the release year of '{title}': ").strip()

        # Check if the movie exists in the dataset
        matching_movies = movies_df[(movies_df['primaryTitle_processed'] == title) & (movies_df['startYear'] == year)]
        if matching_movies.empty:
            print(f"Sorry, '{title}' ({year}) was not found in the dataset. Please try again.")
        else:
            user_movies.append((title, year))
            if len(user_movies) >= 10:  # Stop after 10 movies
                break

    return user_movies


# Construct query from users movies and identify their IDs
def construct_query_from_favorites(user_movies):
    query_terms = []
    exclude_ids = set()
    for title, year in user_movies:
        matching_movies = movies_df[(movies_df['primaryTitle_processed'] == title) & (movies_df['startYear'] == year)]
        if not matching_movies.empty:
            query_terms.extend(matching_movies['Combined_Text'].iloc[0].split())
            exclude_ids.update(matching_movies.index)
    return " ".join(query_terms), exclude_ids


def main():
    user_movies = get_user_favorite_movies()

    # Construct query and get IDs of movies to exclude
    query, exclude_ids = construct_query_from_favorites(user_movies)

    # Perform the search using BM25 hybrid, excluding user given movie IDs
    results = search_movies_bm25_hybrid(query, exclude_ids=exclude_ids)

    # Display the top 10 results (I made one type for basic information and one for detailed information to help yall see the things that went into the scoring)
    output_type = int(input("\nEnter 1 to display basic movie information, or 2 to display detailed information: "))
    print("\nTop 10 Recommended Movies:")
    if output_type == 1:
        for idx, (doc_id, score) in enumerate(results[:10], 1):
            title = movies_df.loc[doc_id, 'primaryTitle_original']
            year = movies_df.loc[doc_id, 'startYear']
            print(f"{idx}. Title: {title} | Year: {year}")
    elif output_type == 2:
        for idx, (doc_id, score) in enumerate(results[:10], 1):
            title = movies_df.loc[doc_id, 'primaryTitle_original']
            genres = movies_df.loc[doc_id, 'genres']
            names = movies_df.loc[doc_id, 'primaryName']
            rating = movies_df.loc[doc_id, 'averageRating']
            votes = movies_df.loc[doc_id, 'numVotes']
            print(f"{idx}. Title: {title} | Genres: {genres} | Names: {names} | Rating: {rating} | Votes: {votes} | Score: {score:.4f}")
    

if __name__ == "__main__":
    main()
