import os

import django
import json
import requests
import time
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prs_project.settings")

django.setup()

from recommender.models import MovieDescriptions
from moviegeeks.models import Movie


def get_imdb_movie(movie_id):
    api_key = get_api_key()
    url = f'https://www.omdbapi.com?apikey={api_key}&i=tt{movie_id}'

    req = requests.get(url)
    req_json = req.json()
    if 'imdbID' not in req_json:
        print('No such id: ', movie_id)
        return None
    else:
        return req_json


def get_api_key():
    # Load credentials
    cred = json.loads(open(".prs").read())
    return cred["omdb_apikey"]


def populate_descriptions_omdb():
    # MovieDescriptions.objects.all().delete()
    all_movies = Movie.objects.all()
    for movie in tqdm(all_movies):
        _id = movie.movie_id
        md = MovieDescriptions.objects.get_or_create(movie_id=_id)[0]
        omdb_movie = get_imdb_movie(_id)
        if None != omdb_movie:
            md.imdb_id = omdb_movie["imdbID"]
            md.title = omdb_movie["Title"]
            md.description = omdb_movie["Plot"]
            md.genres = omdb_movie["Genre"]
            md.save()


def populate_descriptions_csv():
    import pandas as pd
    df = pd.read_csv('data/IMDb_movies.csv')[['imdb_title_id', 'title', 'description', 'genre', 'avg_vote']]
    df = df.sort_values(by='avg_vote', ascending=False).head(1000).reset_index(drop=True)
    print(df.columns)

    for _, row in tqdm(df[0:10000].iterrows()):
        _id = row['imdb_title_id']
        md = MovieDescriptions.objects.get_or_create(movie_id=_id[2:])[0]
        md.imdb_id = _id
        md.title = row['title']
        md.description = row['description']
        md.genres = row['genre']
        md.save()



if __name__ == "__main__":
    print("Starting MovieGeeks Population script...")
    populate_descriptions_csv()
    # populate_descriptions_omdb()
    # m = get_imdb_movie('1234')
    # print(m)