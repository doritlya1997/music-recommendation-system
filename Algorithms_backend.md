# Music Recommendation System Algorithm

## Link to the Web App
[https://music-application-e6959040ee86.herokuapp.com/](https://music-application-e6959040ee86.herokuapp.com/)

If you want to learn how this magical system works, keep reading (and listening)!

![Recommendation Types](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/bf7a7b32-bf65-4f7e-999f-8850000cdb1f)

## Pre-Processing Steps

### Clean, Normalize, and Validate the Data

1. **Dataset**: We downloaded the **Spotify_1Million_Tracks** dataset from [Kaggle](https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks?source=post_page-----5780cabfe194--------------------------------).

2. **Data Preprocessing**: Run the `scripts/main.py -> preprocess()` function:
    ```python
    def preprocess(spark: SparkSession):
        get_track_id_counts(spark)
        drop_duplicate_track_id_songs(spark)
        process_data_write_parquet(spark)
        validate_result(spark)
        write_data_to_postgres(spark)
    ```

3. **Audio Feature Information**: For each track, we have its Audio Feature Information. Learn more about it [here](https://developer.spotify.com/documentation/web-api/reference/get-audio-features).

4. **Apache Spark**: We use [Apache Spark](https://spark.apache.org/) to process the big data file effectively.
    - `get_track_id_counts(spark)`: Finds duplicate `track_id`s and writes the result to files.
    - `drop_duplicate_track_id_songs(spark)`: Removes duplicate tracks to ensure `track_id` uniqueness.
    - `process_data_write_parquet(spark)`: Preprocesses data for ease of use in later algorithms:
        - The `year` column is encoded using One Hot Encoding into: `year_2000_2004`, `year_2005_2009`, `year_2010_2014`, `year_2015_2019`, `year_2020_2024`.
        - The `popularity`, `loudness`, and `tempo` columns are scaled using `MinMaxScaler` to fit the range of `[0, 1]`.
    - `validate_result(spark)`: Prints the schema and track count.
    - `write_data_to_postgres(spark)`: Writes the cleaned data to PostgreSQL.

## Recommendation Logic

### Base Steps
Each time the user **likes** or **removes likes** from certain tracks, the system performs the following steps:

1. **Calculate the Mean Values**:
    - Compute the mean values of the user's liked tracks.
    - If the user has been using the app for a substantial period (e.g., more than a week, a month, a year), the algorithm calculates a weighted mean vector, giving more weight to recently liked tracks to reflect the user's current taste better.
    ![Weighted Mean Calculation](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/9b580fac-857a-41f1-8d5c-1d99a0fe4be9)

2. **Upsert the Vector**:
    - Upsert the vector into [Pinecone VectorDB](https://docs.pinecone.io/home). If the user exists in the VectorDB `users` Index, we `UPDATE` the record; otherwise, we `INSERT` it.
    - If the user removes all liked tracks, we **delete** their mean vector from Pinecone VectorDB as we no longer know the user's "average taste."

### Track Similarity

This method, known as Content-Based Filtering, recommends songs similar to those the user has liked.

![Track Similarity](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/7d5192cc-ca1c-4d8c-9fa8-db216afe6686)

#### Steps

1. Retrieve the user's mean vector from the VectorDB `users` index by user ID.
2. Query the VectorDB `tracks` by similarity to the `current_user_mean_vector` using the Cosine distance algorithm.
3. Get the top `k` most similar tracks.
4. Retrieve the track metadata (e.g., track name, artist name) from PostgreSQL, excluding already liked and disliked tracks of the current user.
5. Send the recommendation list back to the client.

### User Similarity

This method, known as collaborative filtering, finds similar users and recommends their favorite songs to the current user.

![User Similarity](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/7d9a18d1-365f-4238-ba5e-354b552ee0d8)

#### Steps

1. Retrieve the user's mean vector from the VectorDB `users` index by user ID.
2. Query the VectorDB `users` by similarity to the `current_user_mean_vector`.
3. Get the top `k` of the most similar users.
4. Select the liked tracks of those similar users from PostgreSQL, excluding already liked and disliked tracks of the current user.
5. Show the recommendations.

### When the User Has No Liked Tracks

To avoid showing an empty recommendation list, we select the most recent songs liked by other users in the system, effectively recommending "What's trending now."

## Our Learning Curve

Initially, the Track Similarity recommendation logic calculated the cosine distance of the user's vector (mean of favorite songs) against the entire tracks table. We used `Pandas` to load the tracks table from Postgres DB for each request, which was memory-intensive and suboptimal for Heroku's limited resources.

The solution was Pinecone VectorDB, which allowed us to apply vector operations directly against the database without loading all data into memory. This was the right choice for handling large-scale vector operations efficiently.
