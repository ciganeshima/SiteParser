# import asyncio
# from aiohttp import ClientSession
import csv
import requests
from bs4 import BeautifulSoup

start_url = 'https://www.imdb.com/search/title/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=cd28805a-4e91-4f0f-b066-0db5ff4dd1a7&pf_rd_r=PJG88E5FT3NY5TTMZYN1&pf_rd_s=right-6&pf_rd_t=15506&pf_rd_i=boxoffice&ref_=chtbo_gnr_5&genres=comedy&explore=title_type,genres'


class MovieConstructor:
    def __init__(self, title, genre):
        self.title = title
        self.genre = genre


class SiteParser:
    def __init__(self, start_url):
        self.base_url = 'https://www.imdb.com'
        self.start_url = start_url
        self.session = self.init_session()
        self.movie_params = []
        self.movie_list = []
        self.next_link = ""
        self.current_page = ""

    @staticmethod
    def init_session():
        with requests.Session():
            return requests.Session()

    def set_next_link(self):
        try:  # exception : Nonetype object is not subscriptable
            self.next_link = self.base_url + (self.current_page.find("a", class_="lister-page-next next-page")['href'])
        except TypeError:
            self.next_link = None

    def start_parse(self):
        start_parse_session = self.session.get(self.start_url)
        self.current_page = BeautifulSoup(start_parse_session.content, 'html.parser')
        self.set_next_link()

        self.collect_movies()

    def get_next_link(self):
        get_next_parse_session = self.session.get(self.next_link)
        self.current_page = BeautifulSoup(get_next_parse_session.content, 'html.parser')
        self.set_next_link()

        self.collect_movies()

    def collect_movies(self):
        for item in self.current_page.findAll("div", class_="lister-item mode-advanced"):
            self.movie_params.append(item.h3.contents[3].text.strip())  # Title
            self.movie_params.append(item.find("span", attrs={"class": "genre"}).text.strip())  # Genre
            movie = MovieConstructor(*self.movie_params)
            self.movie_list.append(movie)
            self.movie_params = []

    def write_movie_to_csv(self):
        f = open('movies.csv', 'w', encoding="utf-8")

        with f:
            writer = csv.writer(f, delimiter=';')
            for movie in self.movie_list:
                writer.writerow([movie.title, movie.genre])

    def get_all_movies(self):
        self.start_parse()
        while self.next_link is not None:
            if len(self.movie_list) < 100:  # Указать количество страниц*50, которое нужно распарсить;
                # На одной странице 50 фильмов.
                self.get_next_link()
                print("Processing...")
            else:
                self.write_movie_to_csv()
                return len(self.movie_list)
        self.write_movie_to_csv()
        return len(self.movie_list)


if __name__ == "__main__":
    imp = SiteParser(start_url)
    imp.get_all_movies()
    print("Finished!")
