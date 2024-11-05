import pandas as pd

#### This script is used to clean and condense the movie data AFTER it was removed from its orginal .tsv file ####

# Load the CSV file
movies_df = pd.read_csv('processed_data/movies_with_cast.csv', low_memory=False)

# Remove rows with missing values in 'averageRating', 'numVotes', or 'startYear'
movies_df = movies_df.dropna(subset=['averageRating', 'numVotes', 'startYear'])

# Convert columns to appropriate dtypes
movies_df['averageRating'] = movies_df['averageRating'].astype(float)
movies_df['numVotes'] = movies_df['numVotes'].astype(int)
movies_df['startYear'] = movies_df['startYear'].astype(str)

# Check if primaryTitle is the same as originalTitle if it is, replace it with 'N/A'
movies_df['originalTitle'] = movies_df.apply(
    lambda row: "N/A" if row['primaryTitle'] == row['originalTitle'] else row['originalTitle'], axis=1)

# Group by 'tconst' (IMDb ID) to condense multiple rows into one per movie
# Group primary names into a quoted string and handle duplicates
condensed_df = movies_df.groupby(
    ['tconst', 'primaryTitle', 'originalTitle', 'startYear', 'genres', 'averageRating', 'numVotes'], as_index=False
).agg({
    'primaryName': lambda x: ', '.join(f'"{name}"' for name in sorted(x.unique()))  # No limit on names
})

# Clean up quotes around names
condensed_df['primaryName'] = condensed_df['primaryName'].str.replace('"', '').str.strip()

# Save the condensed DataFrame to a new CSV file
condensed_df.to_csv('processed_data/condensed_movies_with_cast.csv', index=False)

print("Condensed movie data saved as 'condensed_movies_with_cast.csv'")
