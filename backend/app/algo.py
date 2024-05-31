from functools import partial

# from IPython.display import display
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import glob
import os
from backend.app import crud
from backend.app.crud import get_recommended_tracks_by_user_listening_history, \
    get_recommended_tracks_by_top_similar_users, get_liked_tracks
from backend.app.pinecone_crud import query_pinecone_by_vector, query_pinecone_by_ids, upsert_pinecone

COLS_FOR_SIMILARITY = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo', 'valence', 'year_2000_2004', 'year_2005_2009', 'year_2010_2014', 'year_2015_2019', 'year_2020_2024', 'update_timestamp']


def weighted_mean(df, col="update_timestamp"):
    # print(df.dtypes)
    date_col = df[col]
    quantiles_values = date_col.quantile([0.25, 0.5, 0.75], interpolation="nearest")
    print(quantiles_values)

    min_date = df.min()
    max_date = df.max()

    # check if short period of tim
    if (max_date[col] - min_date[col]).days < 7:
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


def update_user_mean_vector(user_id: int):
    user_liked_tracks = get_liked_tracks(user_id)
    print(user_liked_tracks)
    print(type(user_liked_tracks))

    all_columns_df = pd.DataFrame.from_records(user_liked_tracks)
    mean_columns_df = all_columns_df[COLS_FOR_SIMILARITY]

    # Calc mean vector
    user_mean_vector_df = weighted_mean(mean_columns_df)
    print(user_mean_vector_df)

    user_vector_to_update = [
        {
            "id": str(user_id),
            "metadata": {
                "num_tracks": len(user_liked_tracks) * 2000
            },
            "values": [
                round(float(user_mean_vector_df["acousticness"]), 3),
                round(float(user_mean_vector_df["danceability"]), 3),
                round(float(user_mean_vector_df["energy"]), 3),
                round(float(user_mean_vector_df["instrumentalness"]), 3),
                round(float(user_mean_vector_df["liveness"]), 3),
                round(float(user_mean_vector_df["loudness"]), 3),
                round(float(user_mean_vector_df["mode"]), 3),
                round(float(user_mean_vector_df["popularity"]), 3),
                round(float(user_mean_vector_df["speechiness"]), 3),
                round(float(user_mean_vector_df["tempo"]), 3),
                round(float(user_mean_vector_df["valence"]), 3),
                round(float(user_mean_vector_df["year_2000_2004"]), 3),
                round(float(user_mean_vector_df["year_2005_2009"]), 3),
                round(float(user_mean_vector_df["year_2010_2014"]), 3),
                round(float(user_mean_vector_df["year_2015_2019"]), 3),
                round(float(user_mean_vector_df["year_2020_2024"]), 3)
            ]
        }
    ]
    print(user_vector_to_update)

    num_user_vectors_affected = upsert_pinecone('users', user_vector_to_update)
    if len(user_vector_to_update) == num_user_vectors_affected:
        print(f"Updated user_id={user_id} vector={user_vector_to_update}")
        return True
    return
    # TODO: retry?


def get_recommendations_by_user_listening_history(user_id: int):
    retrieve_user_results = query_pinecone_by_ids('users', [str(user_id)])
    user_record = retrieve_user_results.get('vectors').get(str(user_id))

    if not user_record:
        return []  # user has no likes or dislikes, can't recommend
    user_vector = user_record.get('values')
    print(f"user_vector: {user_vector}")

    # TODO: add len(user_likes_playlist) + len(user_dislikes_playlist) as METADATA to DB
    top_k_recommendations = 50# max(2 * (len(user_likes_playlist) + len(user_dislikes_playlist)), 50)
    print(f"Getting top {top_k_recommendations} vectors from pinecone")

    # Query Pinecone 'tracks' index, using 'cosine' metric, to find the top most similar vectors
    query_result = query_pinecone_by_vector('tracks', user_vector, top_k_recommendations)
    top_ids_scores = [(match['id'], match['score']) for match in query_result['matches']]

    # Get tracks information by 'track_id', and add the similarity 'score' pinecone calculated
    if len(top_ids_scores) > 0:
        result = get_recommended_tracks_by_user_listening_history(top_ids_scores, user_id)
        return result
    return []


def get_recommendations_by_similar_users(user_id: int):
    retrieve_user_results = query_pinecone_by_ids('users', [str(user_id)])
    user_record = retrieve_user_results.get('vectors').get(str(user_id))

    if not user_record:
        return []  # user has no likes or dislikes, can't recommend
    user_vector = user_record.get('values')
    print(f"user_vector: {user_vector}")

    # get similar user from pinecone, take top k user_id
    # Query Pinecone 'users' index, using 'cosine' metric, to find the top most similar vectors
    query_user_results = query_pinecone_by_vector('users', user_vector, top_k=20)
    top_ids_scores = [(match.get('id'), match.get('score')) for match in query_user_results.get('matches')]
    print(f"top_ids_scores: {top_ids_scores}")

    if not len(top_ids_scores):
        return []

    result = get_recommended_tracks_by_top_similar_users(top_ids_scores, user_id)
    print(len(result))
    return result
    # TODO: randomize the results
