# Welcome to our Music Recommendation music
If you want to learn how this magical system works, keep reading, and listening!

When you enter the system or click the Refresh button, the Algorithm gets your request, and does the following:

![img.png](docs/resources/img.png)

## Pre-Processing Steps
- We downloaded the **Spotify_1Million_Tracks** Dataset from the [kaggle.com](https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks?source=post_page-----5780cabfe194--------------------------------)
- Run the `scripts/main.py -> preprocess()` function:
```
def preprocess(spark: SparkSession):
    get_track_id_counts(spark)
    drop_duplicate_track_id_songs(spark) 
    process_data_write_parquet(spark)
    validate_result(spark)
    write_data_to_postgres(spark)
```
In English:
- For each track, we have its Audio Feature Information (you can read more about it [here](https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks?source=post_page-----5780cabfe194--------------------------------) and
  [here](https://developer.spotify.com/documentation/web-api/reference/get-audio-features))
- To process the Big Data file effectively we use [Apache Spark](https://spark.apache.org/).
- `get_track_id_counts(spark)` -> Spark finds the duplicate `track_id`, and writes the result to files (that's how spark works). 
- `drop_duplicate_track_id_songs(spark) ` -> We do this de-duplication to clean the dataset of junk data (`track_id` is how we identify tracks! It must be unique)
- `process_data_write_parquet(spark)` -> Here we do preprocessing for ease of use for later algorithms:
  - `year` column is encoded using `One Hot Encoding` method into: `year_2000_2004`, `year_2005_2009`,`year_2010_2014`, `year_2015_2019`, `year_2020_2024` columns.
  - `popularity`, `loudness`, `tempo` columns are scaled using `MinMaxScaler` to fit the range of `[0,1]`.
- `validate_result(spark)` -> Prints the schema, and counts how many tracks are there (for later monitoring).
- `write_data_to_postgres(spark)` -> Writs the clean, scaled, encoded tracks data into Postgres DB.

## Steps During App Usage
- Each time the user **likes** or **removes likes** from certain tracks:
  - Calculate the mean values of his liked tracks.
    - If user has been using the App for a substantial period of time (more than a week, a month, a year...), the algo will calculate a weighted mean vector, which takes into account, that latter liked tracks will have a greater influence of the "average taste of the user".
    - ![img_1.png](docs/resources/img_1.png)
    - Upsert the vector into [Pinecone VectorDB](https://docs.pinecone.io/home). Meaning, if the user exists in VectorDB `users` Index, we `UPDATE` the record, else, we `INSERT` it.
  - If the user has remove all of its liked tracks we **delete** its mean vector from Pinecone VectorDB. Since we don't know the user's "average taste".

## Get Recommendation by User Listening History
This method is also known as Content-Based Filtering (see the picture above). 
In this method, we characterize the user's listening history and find similar songs to the ones the user liked in the past.

### Steps

- Get the user's mean vector from VectorDB `users` Index by user id.
- Query the VectorDB `tracks` by similarity to the current_user_mean_vector.
- Get the top `k` most similar tracks.
- Get the textual data (like track name, artist name, etc...) from Postgres DB, excluding already liked and disliked tracks of the current user.
- Show the recommendations.

## Get Recommendation by Similar Users
This method is known as Collaborative Filtering. 
In this method, we characterize the **user** and find similar users whose songs we recommend to the current user.

### Steps

- Get the user's mean vector from VectorDB `users` Index by user id.
- Query the VectorDB `users` by similarity to the current_user_mean_vector.
- Get the top `k` most similar `users`.
- Select the liked tracks of those similar users from Postgres DB, excluding already liked and disliked tracks of the current user.
- Show the recommendations.

## When the user has no liked tracks
To avoid showing an empty recommendation list, we simply select the top most recent liked songs in the system, by other users. You can call this method - "What's trending now" ;)

## Our Learning Curve
At first, we implemented the recommendation logic using the Postgres DB (as source of the user likes/dislikes) and Spotify_1Million_Tracks **CSV** file. We used `Pandas` library to select the ...
