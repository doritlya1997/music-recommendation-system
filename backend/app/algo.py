from functools import partial

from IPython.display import display
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import glob

from backend.app import crud
from backend.app.database import get_db

# def query_db(query, columns) -> pandas.DataFrame:
#     DATABASE_URL="postgres://ghiabcwcxsyfvo:9de383d33fe38cec6d6bb1f41fa313df2f054cc6091bd08cb018f02e74c0cdd7@ec2-34-252-152-193.eu-west-1.compute.amazonaws.com:5432/d9mck4patkc46n"
#
#     with get_db(DATABASE_URL) as conn:
#         with conn.cursor() as cur:
#             try:
#                 cur.execute(query)
#             except (Exception, psycopg2.DatabaseError) as error:
#                 print("Error: %s" % error)
#                 cur.close()
#                 return 1
#             # The execute returns a list of tuples:
#             tuples_list = cur.fetchall()
#             cur.close()
#
#             columns = [
#                 "track_id",
#                 "id",
#                 "artist_name",
#                 "track_name",
#                 "popularity",
#                 "genre",
#                 "danceability",
#                 "energy",
#                 "key",
#                 "loudness",
#                 "mode",
#                 "speechiness",
#                 "acousticness",
#                 "instrumentalness",
#                 "liveness",
#                 "valence",
#                 "tempo",
#                 "duration_ms",
#                 "time_signature",
#                 "year_2000_2004",
#                 "year_2005_2009",
#                 "year_2010_2014",
#                 "year_2015_2019",
#                 "year_2020_2024",
#                 "update_timestamp"
#             ]
#
#             # Now we need to transform the list into a pandas DataFrame:
#             df = pd.DataFrame(tuples_list, columns=columns)
#             display(df)
#             return df


def get_tracks_df(user_id: int, type: str):
    tuples_list = []
    if type == "like":
        tuples_list = crud.get_liked_tracks(user_id)
    else:
        tuples_list = crud.get_disliked_tracks(user_id)

    columns = [
        "track_id",
        "id",
        "artist_name",
        "track_name",
        "popularity",
        "year",
        "genre",
        "danceability",
        "energy",
        "key",
        "loudness",
        "mode",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
        "duration_ms",
        "time_signature",
        "year_2000_2004",
        "year_2005_2009",
        "year_2010_2014",
        "year_2015_2019",
        "year_2020_2024",
        "update_timestamp"
    ]

    # transform the list into a pandas DataFrame
    df = pd.DataFrame(tuples_list, columns=columns)
    display(df)
    return df


def weighted_mean(df, col="update_timestamp"):
    # print(df.dtypes)
    date_col = df[col]
    quantiles_values = date_col.quantile([0.25, 0.5, 0.75], interpolation="nearest")
    print(quantiles_values)

    min_date = df.min()
    max_date = df.max()

    # check if short period of tim
    if (max_date['update_timestamp'] - min_date['update_timestamp']).days < 7:
        mean_df = df.mean().drop(col)
    else:
        # calculate each quantile mean and multiply be matching weight
        # the later the records, the bigger the weight
        first_quantile_df = df[df[col] <= quantiles_values[0.25]].mean().drop(col).mul(1)
        second_quantile_df = df[(df[col] > quantiles_values[0.25]) & (df[col] <= quantiles_values[0.5])].mean().drop(col).mul(2)
        third_quantile_df = df[(df[col] > quantiles_values[0.5]) & (df[col] <= quantiles_values[0.75])].mean().drop(col).mul(3)
        fourth_quantile_df = df[df[col] > quantiles_values[0.75]].mean().drop(col).mul(4)

        all_quantile_df = pd.DataFrame({
            'first': first_quantile_df,
            'second': second_quantile_df,
            'third': third_quantile_df,
            'fourth': fourth_quantile_df})

        mean_df = all_quantile_df.mean(axis=1)
    return mean_df


def get_recommendations_by_user_listening_history(user_id: int):
    cols_for_similarity = [
        "acousticness",
        "danceability",
        "energy",
        "instrumentalness",
        "liveness",
        "loudness",
        "mode",
        "popularity",
        "speechiness",
        "tempo",
        "valence",
        "year_2000_2004",
        "year_2005_2009",
        "year_2010_2014",
        "year_2015_2019",
        "year_2020_2024",
        "update_timestamp"
    ]
    other_cols = ['artist_name', 'duration_ms', 'genre', 'id', 'key', 'year', 'time_signature', 'track_id', 'track_name']

    tracks_df = pd.concat(map(partial(pd.read_parquet),
                              glob.glob("scripts/data_ready_for_db_parquet/*.parquet")))
    tracks_similarity_df = tracks_df[cols_for_similarity[:-1]]
    tracks_other_cols_df = tracks_df[other_cols]
    display(tracks_df)

    user_likes_playlist = get_tracks_df(user_id, type="like")
    user_dislikes_playlist = get_tracks_df(user_id, type="dislike")

    if len(user_likes_playlist) == 0:
        return []

    user_likes_similarity_df = user_likes_playlist[cols_for_similarity]
    user_likes_other_cols_df = user_likes_playlist[other_cols]
    column_averages = weighted_mean(user_likes_similarity_df)
    user_likes_similarity_df_mean = pd.DataFrame([column_averages], index=['Average'])

    # display(user_likes_similarity_df_mean)

    tracks_similarity_df = tracks_similarity_df.sort_index(axis=1)
    user_likes_similarity_df_mean = user_likes_similarity_df_mean.sort_index(axis=1)

    similarity_scores = cosine_similarity(tracks_similarity_df, user_likes_similarity_df_mean)
    tracks_similarity_df['relevance_percentage'] = similarity_scores
    tracks_similarity_df['relevance_percentage'] = tracks_similarity_df['relevance_percentage'].mul(100).round(1)

    # Reset indexes to ensure uniqueness
    tracks_similarity_df = tracks_similarity_df.reset_index(drop=True)
    tracks_other_cols_df = tracks_other_cols_df.reset_index(drop=True)
    display(tracks_similarity_df)
    display(tracks_other_cols_df)
    scored_tracks_df = pd.concat([tracks_similarity_df, tracks_other_cols_df], axis=1, join='inner')

    # remove tracks which are already liked/disliked
    top_similarities = scored_tracks_df.sort_values(by='relevance_percentage', ascending=False)
    top_similarities = top_similarities[~top_similarities['track_id'].isin(user_likes_playlist['track_id'])]

    if len(user_dislikes_playlist) > 0:
        top_similarities = top_similarities[~top_similarities['track_id'].isin(user_dislikes_playlist['track_id'])]
    top_similarities = top_similarities.head(10)

    top_similarities = top_similarities[['track_id', 'track_name', 'artist_name', 'relevance_percentage', 'year']]
    display(top_similarities)

    lod = top_similarities.to_dict('records')
    return lod

