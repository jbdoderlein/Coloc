from bs4 import BeautifulSoup
import requests
import sys
import matplotlib.pyplot as plt
import json
import numpy as np
import urllib
from itertools import dropwhile
import re
from recipe_scrapers import scrape_me

class Recipe:
    def __init__(self, title, image_link, ingredients, identifier):
        self.title = title
        self.image_link = image_link
        self.ingredients = list(
            map(lambda x :
                " ".join(
                    list(
                        dropwhile(lambda x : len(x) < 3 or x[0].isdigit() or x.startswith("c.à"),
                                  re.split('\s|\'', x))
                    )
                ),
                ingredients)
        )
        self.identifier = identifier

    def overview(self):
        return Overview(self.title, self.image_link, self.identifier)

    def data(self):
        return RecipeData(self.title, self.image_link, self.ingredients)

known_recipes = [[], [], [], []]
index = 0

class Overview:
    def __init__(self, title, image_link, identifier):
        self.title = title
        self.image_link = image_link
        self.identifier = identifier

    def toJSON(self):
        return json.dumps({"title": self.title, "image_link": self.image_link, "identifier": self.identifier})

class RecipeData:
    def __init__(self, title, image_link, ingredients):
        self.title = title
        self.image_link = image_link
        self.ingredients = ingredients

    def toJSON(self):
        return json.dumps({"title": self.title, "image_link": self.image_link, "ingredients": self.ingredients})

def get_recipes(search, max_recipes = 10):
    global known_recipes, index
    url = "https://www.marmiton.org/recettes/recherche.aspx?"

    keywords = "-".join(search)
    r = requests.get(url, params = {"aqt" : keywords})

    if r.status_code != 200:
        return None

    known_recipes[index] = []

    soup = BeautifulSoup(r.text, "lxml")

    i = 0
    for link in soup.find_all('a'):
        if link.get("href").startswith("/recettes/recette_"):
            if i == max_recipes:
                break
            scraper = scrape_me("https://www.marmiton.org" + link.get("href"))
            recipe = Recipe(scraper.title(), scraper.image(), scraper.ingredients(), (index, i))
            known_recipes[index].append(recipe)
            i += 1

    res = [recipe.overview() for recipe in known_recipes[index]]
    index = (index + 1) % 4
    return res

def get_recipe(identifier):
    return known_recipes[identifier[0]][identifier[1]].data()

if __name__ == "__main__":
    ids = get_recipes("poulet")
    print(*[overview.title for overview in ids], sep="\n")
    print("----------")
    print(*[get_recipe(overview.identifier).title for overview in ids], sep="\n")
    print("----------")

    idss = get_recipes("coq")
    print(*[overview.title for overview in idss], sep="\n")
    print("----------")
    print(*[get_recipe(overview.identifier).title for overview in idss], sep="\n")
    print("----------")
    print(*[get_recipe(overview.identifier).title for overview in ids], sep="\n")
    print("----------")
    print(ids[0].toJSON())
    print("----------")
    print(get_recipe(idss[0].identifier).toJSON())
    print("----------")
