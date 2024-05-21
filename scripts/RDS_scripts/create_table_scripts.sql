DROP TABLE tracks;

CREATE TABLE tracks (
    track_id VARCHAR PRIMARY KEY,
    id INTEGER,
    artist_name VARCHAR,
    track_name VARCHAR,
    popularity DOUBLE PRECISION,
    genre VARCHAR,
    danceability DOUBLE PRECISION,
    energy DOUBLE PRECISION,
    key INTEGER,
    loudness DOUBLE PRECISION,
    mode INTEGER,
    speechiness DOUBLE PRECISION,
    acousticness DOUBLE PRECISION,
    instrumentalness DOUBLE PRECISION,
    liveness DOUBLE PRECISION,
    valence DOUBLE PRECISION,
    tempo DOUBLE PRECISION,
    duration_ms VARCHAR,
    time_signature VARCHAR,
    year_2000_2004 INTEGER,
    year_2005_2009 INTEGER,
    year_2010_2014 INTEGER,
    year_2015_2019 INTEGER,
    year_2020_2024 INTEGER
);

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
);

-- Create likes table
CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    track_id VARCHAR(255) NOT NULL
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
--     FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
);

-- Create dislikes table
CREATE TABLE dislikes (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    track_id VARCHAR(255) NOT NULL
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
--     FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
);