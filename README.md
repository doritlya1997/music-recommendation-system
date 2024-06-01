# Music Recommendation System Algorithm UI walkthrough 

The client-side of the application is developed using plain HTML, CSS, and JavaScript.
The backend is written in python, using Fast-Api [Fast-API](https://fastapi.tiangolo.com/) framework. 
The application uses Postgres DB for RDS, and Pinecone DB for recommendation vector logic operations.

Link to the recommendation **algorithm README** file : https://github.com/doritlya1997/music-recommendation-system/blob/main/Algorithms_backend.md

Link for **devs technical README** : https://github.com/doritlya1997/music-recommendation-system/blob/main/README_for_dev.md

## Our web-app
Our web app is hosted on Heroku, providing a reliable and scalable platform for deployment. [Heroku](https://dashboard.heroku.com/)  server.

Link to the web-app https://music-application-e6959040ee86.herokuapp.com/
 ____
Before we dive into the walkthrough, we'd like to highlight the attention and care given to the development of our web app UI. We focused on design, simplicity, user experience (UX), and interactivity to ensure a smooth and enjoyable user experience. Although it was challenging, we are thrilled with the results and hope you will be too!
____


## Login Page
After the user successfully logs in, their session is managed using the web's local cache, storing their user_id and user_name. For security reasons, each user interaction with the UI involves a backend check to verify and authenticate the user. Since the local cache is editable, these backend validations are essential to ensure the security of the web app.

![login_page.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/a80e8788-2616-4794-bab8-0a5b3f4e8996)

## Login Page Validation
![login_page_validation.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/4d89aae5-793c-4309-bea0-68a2315eac89)

## Sign-up Page
![signup_page.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/51f4bb43-d9e6-48de-bcef-dc0d2af4fe88)

## Login Page Validation
![signup_validation.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/39e5d67b-a432-440b-9e2d-d2a423a1369f)

## recommendation Page 
![recommendation_page.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/da148dd8-9bd6-4490-953d-d7c4411917d2)

## Add single spotify track link to Favorites list 

#### Insert the spotify track link in the input text
Notes: 
- We can only add tracks from spotify
- The tracks must be from the 1M dataset from **Spotify_1Million_Tracks** dataset from [Kaggle](https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks?source=post_page-----5780cabfe194--------------------------------).
![add_spotify_link.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/5bdb97d7-3ab7-49ab-a7b3-f01e4fbc680e)

    #### Popup approval the track was added (By click the add button)
    ![spotify_link_added.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/3423dd01-11fc-4a6a-bba0-72a19983c602)
    
    ### The track added to the favorites list
    ![added_as_favorite.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/c73912d1-747c-4ed2-aab5-41d9e870eb5c)
* The recommendation list refresh automatically

## Add multi spotify tracks to Favorites list 

#### Insert spotify track links using upload csv (Click upload csv button)
Notes: 
- The csv format should be one column, with `links` title
- The values of the column should be spotify tracks links, one at a row
![click_csv_button.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/ef21e7eb-f214-4f96-9073-8c0a9db8a136)

    #### Choose csv file window  from the file system (Click open)
    ![click_open_csv.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/0646303c-fffb-4dc8-a58f-c4fc9b6782b9)
    
    ### The tracks added to the favorites list
    ![the_tracks_added.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/3e59267e-de74-45a2-b5d6-4005ecaeec23)
* The recommendation list refresh automatically 

## Click like/dislike from the recommendation list, move the tracks to the relevant list
![click_like_dislike.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/5e41ff67-8ebd-4c4a-9aa0-66fc4f175ae3)

### Click the Refresh button
* All the time suggest brand-new recommendations based on the user favorites tracks
* Each recommended track item in the recommendation list consist of:
  * Metadata regarding the track (name, band, year of publish)
  * Link to listen on Spotify
  * Match percentage for the user
  * Small icon indicate the source recommendation logic this track item originated from
  ![Recommendation_list.png](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/7b3f5ff7-f1d1-407d-bfe0-bf9d0c7ba4a4)


* Clicking the logout button (in the top right corner) will disconnect the user and take him back to the login page