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
   git clone https://github.com/ChristianJeardoe/ReelSeekEngine.git
2. Download `processed_data` folder from Google drive link: https://drive.google.com/drive/folders/14kBdoN8o2sJtLdsCf0SsTJKNUpY4B4oN?usp=drive_link
3. Unzip the download and then unzip `condensed_movies_with_cast.csv`. Ensure `condensed_movies_with_cast.csv` is inside of the `processed_data` folder. This folder needs to be in the same directory as app.py.
4. Install required Python packages:
   ```bash
   pip install pandas
5. Run the main program:
   ```bash
   app.py
Note: It may take a several seconds to start as it needs to frame the dataset

## Usage

You will be prompted to enter 3 to 5 movies of your choice. As you type the title in a drop down menu will appear with option to select from. Just click on your movie when you see it and it'll be added to your list below. If your movie is not showing up in the list you can enter in its year of release in the year section next to it, this will filter all results in the drop down by movies from that year. Once you have selected at least 3 movies press the "Get Recommendations" button and your top ten movie suggestions will appear.

## How It Works

- **Inverted Index**: An inverted index is created for efficient retrieval of documents based on user-provided search terms.
- **BM25 Scoring**: BM25 is used to calculate the relevance of each movie to the user's query. The term frequency (`k1 = 1.5`) and length normalization (`b = 0.5`) parameters are adjustable.
- **Hybrid Scoring**: The BM25 score is combined with normalized movie ratings and number of votes to generate a hybrid score that balances content relevance, movie quality, and popularity.
- **Hybrid Weights (`alpha`, `beta`, `gamma`)**: Control the contribution of BM25, rating, and votes to the final hybrid score.