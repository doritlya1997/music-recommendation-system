create table public.tracks
(
    track_id         varchar not null constraint tracks_pkey1 primary key,
    id               integer,
    artist_name      varchar,
    track_name       varchar,
    popularity       double precision,
    year             integer,
    genre            varchar,
    danceability     double precision,
    energy           double precision,
    key              integer,
    loudness         double precision,
    mode             integer,
    speechiness      double precision,
    acousticness     double precision,
    instrumentalness double precision,
    liveness         double precision,
    valence          double precision,
    tempo            double precision,
    duration_ms      varchar,
    time_signature   varchar,
    year_2000_2004   integer,
    year_2005_2009   integer,
    year_2010_2014   integer,
    year_2015_2019   integer,
    year_2020_2024   integer
);

create table public.users
(
    id              serial primary key,
    username        varchar(255) not null unique constraint unique_username_user unique,
    hashed_password varchar(255) not null
);

create table public.likes
(
    id               serial primary key,
    user_id          integer                 not null,
    track_id         varchar(255)            not null,
    update_timestamp timestamp default now() not null,
    constraint unique_user_likes unique (user_id, track_id)
);

create table public.dislikes
(
    id               serial primary key,
    user_id          integer                 not null,
    track_id         varchar(255)            not null,
    update_timestamp timestamp default now() not null,
    constraint unique_user_dislikes unique (user_id, track_id)
);


