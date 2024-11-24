from flask import Flask, render_template, request, jsonify
import pandas as pd
from collections import defaultdict
import math


### This is the main program that will take user input and recommend movies based on the input ###

app = Flask(__name__)

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
                if doc_id not in exclude_ids:
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


@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    if request.method == 'POST':

        # Extract user provided favorite movies
        user_movies = []
        for i in range(1, 6):
            title = request.form.get(f'title{i}', '').strip().lower()
            year = request.form.get(f'year{i}', '').strip()
            if title and year:
                user_movies.append((title.lower(), year))

        # Construct query from user provided favorite movies and identify their IDs
        if len(user_movies) >= 3:
            query_terms = []
            exclude_ids = set()
            for title, year in user_movies:
                matching_movies = movies_df[(movies_df['primaryTitle'].str.lower() == title) & (movies_df['startYear'] == year)]
                if not matching_movies.empty:
                    query_terms.extend(matching_movies['Combined_Text'].iloc[0].split())
                    exclude_ids.update(matching_movies.index)  # Add movie index to exclude set
            query = " ".join(query_terms)

            # Perform the search using BM25 hybrid, excluding user fav movie IDs
            results = search_movies_bm25_hybrid(query, exclude_ids=exclude_ids)

            # Get the top 10 recommendations
            for idx, (doc_id, _) in enumerate(results[:10], 1):
                title = movies_df.loc[doc_id, 'primaryTitle'].title()
                year = movies_df.loc[doc_id, 'startYear']
                recommendations.append(
                    f"{idx}. Title: {title} | Year: {year}"
                )

    return render_template('index.html', recommendations=recommendations)

# Autocomplete
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    term = request.args.get('term', '').strip().lower()
    year = request.args.get('year', '').strip()
    if year:
        matching_movies = movies_df[(movies_df['primaryTitle'].str.contains(term, case=False, na=False)) & (movies_df['startYear'] == year)].copy()
    else:
        matching_movies = movies_df[movies_df['primaryTitle'].str.contains(term, case=False, na=False)].copy()
    matching_movies['match_priority'] = matching_movies['primaryTitle'].apply(lambda x: x.startswith(term))
    matching_movies = matching_movies.sort_values(by='match_priority', ascending=False).head(10)
    suggestions = []
    for _, row in matching_movies.iterrows():
        suggestions.append({
            'label': f"{row['primaryTitle'].title()} ({row['startYear']})",
            'value': row['primaryTitle'],
            'year': row['startYear']
        })
    return jsonify(suggestions)


if __name__ == '__main__':
    app.run(debug=True)
