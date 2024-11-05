import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

### This script is used to visualize the distribution of movie data (used for the data checkpoint) ###

# Load the condensed CSV file
condensed_df = pd.read_csv('processed_data/condensed_movies_with_cast.csv', 
                            na_values=["\\N"], 
                            dtype={
                                'startYear': 'Int64',  
                                'averageRating': 'float',
                                'numVotes': 'Int64' 
                            })

# Check for any NaN values and drop rows with missing values in essential columns
condensed_df.dropna(subset=['startYear', 'averageRating', 'numVotes'], inplace=True)

sns.set(style="whitegrid")

## The figures are saved as PNG files rather than displayed
# 1. Distribution of movie release years (startYear)
plt.figure(figsize=(12, 6))
sns.histplot(data=condensed_df, x='startYear', bins=30, kde=True)
plt.title('Distribution of Start Year')
plt.xlabel('Start Year')
plt.ylabel('Frequency')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('data_graphs/start_year_distribution.png')
plt.close()  # Close the figure

# 2. Distribution of average ratings (averageRating)
plt.figure(figsize=(12, 6))
sns.histplot(data=condensed_df, x='averageRating', bins=20, kde=True)
plt.title('Distribution of Average Ratings')
plt.xlabel('Average Rating')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('data_graphs/average_rating_distribution.png')
plt.close()  # Close the figure

# 3. Scatter plot of average rating (averageRating) vs. number of votes (numVotes)
plt.figure(figsize=(12, 8))
sns.scatterplot(data=condensed_df, x='averageRating', y='numVotes', alpha=0.6)
plt.title('Average Rating vs. Number of Votes')
plt.xlabel('Average Rating')
plt.ylabel('Number of Votes')
plt.xscale('linear')
plt.yscale('log')
plt.tight_layout()
plt.savefig('data_graphs/rating_vs_votes.png')
plt.close()
