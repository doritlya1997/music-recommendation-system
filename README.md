# music-recommendation-system

### Installation for Devs:
````
brew install poetry
poetry config virtualenvs.in-project true 
poetry install
brew tap heroku/brew && brew install heroku

heroku login
heroku create music-recommendation-system
````

### Data Preparation and loading into PostgreSQL DB
To preprocess the 1 Million tracks dataset and load into PostgreSQL DB, we need to:

- Download the dataset from the link (https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks?source=post_page-----5780cabfe194--------------------------------)
- Place the dataset here: `scripts/data/spotify_data.csv`
- Add a `scripts/secrets.py` file with your database credentials:
  ```
  DB_USER = "..."
  DB_PASSWORD = "..."
  DB_HOST = "..."
  DB_PORT = "..."
  DB_NAME = "..."
  ```
- Run `preprocess(spark)` in `scripts/main.py`


It will take the `scripts/data/spotify_data.csv` and produce these folders by order:

- `scripts/dup_track_id.csv/`
- `scripts/data_no_duplicates.csv/`
- `scripts/data_ready_for_db.csv/`
- Then spark will load the `scripts/data_ready_for_db.csv/` dataset into PostreSQL
