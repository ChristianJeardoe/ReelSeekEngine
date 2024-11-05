# Reel Seek Engine

This is my movie search engine project for CSCE 470. It is using IMDb's non-commercial datasets along with a hybrid BM25 model to rank the results. This hybrid model allows me to take advantage of both the BM25 algorithm as well as the ratings for the movies to generate better results.

## Contents

1. **Data Files**
- `raw_data`: This is where I have stored the IMDb datasets that I used for this project.
- `processed_data`: In this folder I have the processed csv files that came from the raw datasets.
- `data_graphs`: This folder contains the graphs I used to show my data for the data checkpoint.

2. **Python Files**
- `app.py`: This is the main file that you will run for this project.
- `preprocessing.py`: This script is used to preprocess the multiple raw IMDb data files and merge them into a single CSV file. It takes quite a while to run due to the large size of the IMDb datasets (It took me about 45 mins to an hour to complete).
- `csvfixing.py`: This script was used to further process the data found in the csv I originally made using the script above.
- `dataShowcase.py` This script was just used to make the graphs found in `data_graph` folder.

## Dependencies

To run this program you will need these Python packages along with Python 3.x installed:
- `pandas`: For data manipulation.
- `tqdm`: Only for `preprocessing.py` if you want to run it.

## How To Run Main

1. Clone the repository:
   ```bash
   git clone https://github.com/
2. Install required Python packages:
   ```bash
   pip install pandas
3. Ensure `condensed_movies_with_cast.csv` is inside of the `processed_data` folder.
4. Run the main program:
   ```bash
   python app.py
Note: It may take a few seconds to run as it need to frame the dataset

## Usage

You will be prompted to enter 3 to 10 movies of your choice along with the year they came out. This will be changed in the next checkpoint, this is just a temporary UI. This can be done by entering the names and years by heart, looking through the `condenced_movies_with_cast.csv` file, or by looking up what you need on Google. If title doesn't exist or the year doesn't match with the title it'll let you know and reprompt you.

Once you have entered all of the movies you want (3 - 10 movies) press Enter to finish.

You will then be asked to enter 1 or 2 for the formatting of your results. Entering 1 will give you just a basic output with the top 10 movies along with their titles and release years. Entering 2 will give you a much more detailed output including the title of the movie, Genres, Names of the people associated with the movie (actors, directors, and writers), the rating (out of 10), the number of votes, and the hybrid BM25 score it got.

## How It Works

- **Inverted Index**: An inverted index is created for efficient retrieval of documents based on user-provided search terms.
- **BM25 Scoring**: BM25 is used to calculate the relevance of each movie to the user's query. The term frequency (`k1 = 1.5`) and length normalization (`b = 0.5`) parameters are adjustable.
- **Hybrid Scoring**: The BM25 score is combined with normalized movie ratings and number of votes to generate a hybrid score that balances content relevance, movie quality, and popularity.
- **Hybrid Weights (`alpha`, `beta`, `gamma`)**: Control the contribution of BM25, rating, and votes to the final hybrid score.