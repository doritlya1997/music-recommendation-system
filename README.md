# Music Recommendation System Algorithm UI Walkthrough

The client-side of the application is developed using plain HTML, CSS, and JavaScript. The backend is built using Python with the [FastAPI](https://fastapi.tiangolo.com/) framework. The application utilizes PostgreSQL for its relational database and Pinecone DB for recommendation vector operations.

- Link to the recommendation **algorithm README**: [Algorithms_backend.md](https://github.com/doritlya1997/music-recommendation-system/blob/main/Algorithms_backend.md)
- Link for **devs technical README**: [README_for_dev.md](https://github.com/doritlya1997/music-recommendation-system/blob/main/README_for_dev.md)

## Our Web App

Our web app is hosted on [Heroku](https://dashboard.heroku.com/), providing a reliable and scalable platform for deployment.

- Link to the web app: [https://music-application-e6959040ee86.herokuapp.com/](https://music-application-e6959040ee86.herokuapp.com/)

____
Before we dive into the walkthrough, we'd like to highlight the attention and care given to the development of our web app UI. We focused on design, simplicity, user experience (UX), and interactivity to ensure a smooth and enjoyable user experience. Although it was challenging, we are thrilled with the results and hope you will be too!
____

## Login Page

After the user successfully logs in, their session is managed using the web's local cache, storing their user_id and user_name. For security reasons, each user interaction with the UI involves a backend check to verify and authenticate the user. Since the local cache is editable, these backend validations are essential to ensure the security of the web app.

![Login Page](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/a80e8788-2616-4794-bab8-0a5b3f4e8996)

## Login Page Validation
![Login Page Validation](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/4d89aae5-793c-4309-bea0-68a2315eac89)

## Sign-up Page
![Sign-up Page](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/51f4bb43-d9e6-48de-bcef-dc0d2af4fe88)

## Sign-up Validation
![Sign-up Validation](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/39e5d67b-a432-440b-9e2d-d2a423a1369f)

## Recommendation Page
![Recommendation Page](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/da148dd8-9bd6-4490-953d-d7c4411917d2)

## Add Single Spotify Track Link to Favorites List 

#### Insert the Spotify track link in the input text
Notes: 
- We can only add tracks from Spotify.
- The tracks must be from the 1M dataset from the **Spotify_1Million_Tracks** dataset from [Kaggle](https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks?source=post_page-----5780cabfe194--------------------------------).

![Add Spotify Link](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/5bdb97d7-3ab7-49ab-a7b3-f01e4fbc680e)

#### Popup approval the track was added (By clicking the add button)
![Spotify Link Added](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/3423dd01-11fc-4a6a-bba0-72a19983c602)

### The track added to the favorites list
![Added as Favorite](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/c73912d1-747c-4ed2-aab5-41d9e870eb5c)

* The recommendation list refreshes automatically

## Add Multiple Spotify Tracks to Favorites List 

#### Insert Spotify track links using upload CSV (Click upload CSV button)
Notes: 
- The CSV format should be one column, with `links` as the title.
- The values of the column should be Spotify track links, one per row.

![Click CSV Button](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/ef21e7eb-f214-4f96-9073-8c0a9db8a136)

#### Choose CSV file window from the file system (Click open)
![Click Open CSV](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/0646303c-fffb-4dc8-a58f-c4fc9b6782b9)

### The tracks added to the favorites list
![The Tracks Added](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/3e59267e-de74-45a2-b5d6-4005ecaeec23)

* The recommendation list refreshes automatically 

## Click like/dislike from the recommendation list to move the tracks to the relevant list
![Click Like/Dislike](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/5e41ff67-8ebd-4c4a-9aa0-66fc4f175ae3)

### Click the Refresh button
* Always suggests brand-new recommendations based on the user's favorite tracks.
* Each recommended track item in the recommendation list consists of:
  * Metadata regarding the track (name, band, year of publish)
  * Link to listen on Spotify
  * Match percentage for the user
  * A small icon indicating the source recommendation logic this track item originated from

![Recommendation List](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/7b3f5ff7-f1d1-407d-bfe0-bf9d0c7ba4a4)

* Clicking the logout button (in the top right corner) will disconnect the user and take them back to the login page
