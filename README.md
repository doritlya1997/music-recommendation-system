# music-recommendation-system

### Link to the web-app
https://music-application-e6959040ee86.herokuapp.com/

### Heroku commands for Deployment
```
heroku login
heroku git:remote -a music-application
git push heroku main
heroku open -a music-application
```
### Run project locally
```
uvicorn backend.app:app --host 0.0.0.0 --port 8080 
```
### Run Heroku local as debug:
````
heroku config:set DEBUG=True
heroku local web
````

### Installation for Devs:
````
brew install poetry
poetry config virtualenvs.in-project true 
poetry install
brew tap heroku/brew && brew install heroku

heroku login
heroku create music-recommendation-system
````

### When problem encountered with poetry
````
python3.12 -m venv myenv
source myenv/bin/activate
poetry env use python3.12
source myenv/bin/activate
pip install setuptools wheel
python -c "import distutils"
rm poetry.lock
poetry lock
poetry install
````

### Data Preparation and loading into PostgreSQL Database
To preprocess the 1 Million tracks dataset and load into PostgreSQL DB, we need to:

- Download the dataset from the link (https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks?source=post_page-----5780cabfe194--------------------------------)
- Place the dataset here: `scripts/data/spotify_data.csv`
- Add a `scripts/secrets1.py` file with your database credentials:
  ```
  DATABASE_URL=postgres://... 
  PINECONE_API_KEY=...
  ```
- Run `preprocess(spark)` in `scripts/main.py`
  - It will take the `scripts/data/spotify_data.csv` and produce these folders by order:
  - `scripts/dup_track_id.csv/`
  - `scripts/data_no_duplicates.csv/`
  - `scripts/data_ready_for_db.csv/`
- Then spark will load the `scripts/data_ready_for_db.csv/` dataset into PostreSQL `tracks` table

### Loading Tracks data into pinecone Vector Database
- Run `scripts/pine/create_index.py`
- Then `scripts/pine/insert.py`

### Heroku commands for Deployment
#### Just once before the first deployment
```
heroku login
heroku git:remote -a music-application
heroku config:set DATABASE_URL=postgres://... --app music-application
heroku config:set PINECONE_API_KEY=... --app music-application
```
You'll see the newly set Environment Variables in the Heroku UI > Settings > Config Vars.
#### When you want to Deploy
```
heroku login
git push heroku main
heroku open -a music-application
```
### Monitoring
#### Connect to the remote heroku bash:
````
heroku run bash --app music-application
````

#### Production logs monitoring
````
heroku logs --tail --app  music-application
````