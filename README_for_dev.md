# Music Recommendation System

## Link to the Web App
[https://music-application-e6959040ee86.herokuapp.com/](https://music-application-e6959040ee86.herokuapp.com/)

### Installation for Developers

To set up the development environment, follow these steps:

1. **Install Poetry**:
    ```bash
    brew install poetry
    poetry config virtualenvs.in-project true 
    poetry install
    ```

2. **Install Heroku CLI**:
    ```bash
    brew tap heroku/brew && brew install heroku
    heroku login
    heroku create music-recommendation-system
    ```

### Troubleshooting Poetry Issues

If you encounter problems with Poetry, try the following steps:

1. **Set Up a Virtual Environment**:
    ```bash
    python3.12 -m venv myenv
    source myenv/bin/activate
    ```

2. **Configure Poetry to Use the Virtual Environment**:
    ```bash
    poetry env use python3.12
    source myenv/bin/activate
    pip install setuptools wheel
    python -c "import distutils"
    rm poetry.lock
    poetry lock
    poetry install
    ```

### Creating Tables in PostgreSQL Database

1. **Open your preferred database management tool** (e.g., `pgAdmin`, `DataGrip`).
2. **Run the SQL scripts** located in `scripts/RDS_scripts/create_table_scripts.sql` to create the necessary tables.

### Preparing and Loading Tracks Data into PostgreSQL Database

1. **Download the Dataset**:
    - Get the dataset from [Kaggle: Spotify_1Million_Tracks](https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks?source=post_page-----5780cabfe194--------------------------------).

2. **Place the Dataset**:
    - Save the dataset to `scripts/data/spotify_data.csv`.

3. **Add Database Credentials**:
    - Create a `scripts/secrets1.py` file with your database credentials:
      ```python
      DATABASE_URL="postgres://..."
      PINECONE_API_KEY="..."
      ```

4. **Run Preprocessing**:
    - Execute the `preprocess(spark)` function in `scripts/main.py`:
      ```bash
      python scripts/main.py
      ```
    - This will process `spotify_data.csv` and produce the following files in order:
      - `scripts/dup_track_id.csv/`
      - `scripts/data_no_duplicates.csv/`
      - `scripts/data_ready_for_db.csv/`
    - The final processed data will be loaded into the PostgreSQL `tracks` table.

### Creating and Loading Tracks Data into Pinecone Vector Database

1. **Create the Index**:
    ```bash
    python scripts/pine/create_index.py
    ```

2. **Insert Data into Pinecone**:
    ```bash
    python scripts/pine/insert.py
    ```

### Running the Project Locally

To run the project locally, use one of the following commands:

1. **Using Uvicorn**:
    ```bash
    uvicorn backend.app:app --host 0.0.0.0 --port 8080 
    ```

2. **Using Heroku**:
    ```bash
    heroku config:set DEBUG=True
    heroku local web
    ```

### Heroku Commands for Deployment

#### Initial Setup for Deployment

1. **Login to Heroku**:
    ```bash
    heroku login
    ```

2. **Set Remote Repository and Environment Variables**:
    ```bash
    heroku git:remote -a music-application
    heroku config:set DATABASE_URL=postgres://... --app music-application
    heroku config:set PINECONE_API_KEY=... --app music-application
    ```

3. **Check Environment Variables**:
    - You can view the newly set environment variables in the Heroku UI under Settings > Config Vars.

#### Deploying the Application

To deploy the application, you can either:

1. **Use the Heroku UI**:
    - Go to the Deploy tab.
    - Select "Manual deploy".
    - Choose the `main` branch.
    - Click the `Deploy Branch` button.

2. **Use the Command Line**:
    ```bash
    heroku login
    heroku git:remote -a music-application
    git push heroku main
    heroku open -a music-application
    ```

### Monitoring

#### Access the Remote Heroku Bash:
```bash
heroku run bash --app music-application
```

### Monitor Production Logs:
```bash
heroku logs --tail --app music-application
```
