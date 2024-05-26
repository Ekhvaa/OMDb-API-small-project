import requests
import json
import sqlite3


class Film:
    api_key = "b39ede14"

    def __init__(self, film):
        self.film = film

    def request(self):
        # მეთოდი request-ის გასაკეთებლად.
        url = f"http://www.omdbapi.com/?apikey={Film.api_key}&t={self.film}&plot=full"
        r = requests.get(url)
        return r

    @property
    def response(self):
        # აბრუნებს JSON მონაცემებს რექუესთის შემდგომ.
        data = self.request().json()
        return data

    @property
    def rating(self):
        # აბრუნებს ფილმის IMDB რეიტინგს. თუ ფილმს არ აქვს რეიტინგი, მაშინ დააბრუნებს "N/A"-ს.
        rating = self.response["imdbRating"]
        return rating

    @property
    def title(self):
        # JSON მონაცემებიდან გამოაქვს მხოლოდ ფილმის დასახელება იმ შემთხვევაში, თუ ეს ფილმი არსებობს.
        title = self.response["Title"]
        return title

    def plot(self):
        try:
            plot = self.response["Plot"]
            return plot
        except KeyError:
            print("The summary of the plot is not in the provided data.")

    def write_in_json(self):
        # ფილმის მონაცემებს JSON მონაცემის სახით ჩაწერს ფიალში FilmData.txt.
        with open("FilmData.txt", 'w') as file:
            json.dump(self.response, file, indent=4)


def connect(database):
    return sqlite3.connect(database)


def create_database(filename):
    # ქმნის ბაზას. პარამეტრად გადაეცემა ბაზის ფაილის დასახელება
    conn = connect(filename)
    c = conn.cursor()
    create = "CREATE TABLE Films (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, release_year INTEGER, genre TEXT, imdb_rating VARCHAR 10)"
    c.execute(create)
    conn.close()


def insert_data(film):
    # ამატებს მონაცემებს, კერძოდ: დასახელებას, გამოშვების წელს, ჯანრებს და IMDB რეიტინგს.
    conn = connect("Films.sqlite")
    c = conn.cursor()
    title = film.title
    release_year = film.response["Year"]
    genre = film.response["Genre"]
    rating = film.rating
    values = (title, release_year, genre, rating)
    c.execute("INSERT INTO Films (title, release_year, genre, imdb_rating) VALUES (?,?,?,?)", values)
    conn.commit()
    conn.close()


user_input = input("Enter a film: ")
movie = Film(user_input)
req = movie.request()

if movie.response["Response"] == "True":
    structured_data = json.dumps(movie.response, indent=4)
    print(structured_data)
    print(movie.title)
    print(movie.plot())
    print(movie.rating)
    print(req.status_code)
    print(req.headers)
    movie.write_in_json()
    # create_database("Films.sqlite")
    insert_data(movie)
elif movie.response["Response"] == "False":
    print("The film was not found.")


