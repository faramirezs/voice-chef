#!/usr/bin/python3
#NOTE MK: This script is meant to be run once to seed the database with photos for existing recipes that don't have any.
#It uses the Pexels API to search for relevant images based on the recipe name, downloads them, and saves them locally.
#You can then manually upload these images to your server and update the photo_url field in the database accordingly.

import os
import time
import requests
from sqlalchemy import create_engine, text
import re
import unicodedata

# Public picture service API key (replace with your own key)
# An example is PEXELS API: https://api.pexels.com/v1/search
API_URL = "https://api.pexels.com/v1/search"
API_KEY = ""

DATABASE_URL = "postgresql://recipe_user:recipe_pass123@localhost:5432/recipe_db"
SAVE_DIR = "../../assets/recipe_seed_images"

HEADERS = {
    "Authorization": API_KEY
}


def slugify(name: str) -> str:
    # normalize unicode (ä → a, etc.)
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()

    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)  # replace non-alphanum with dash
    name = name.strip("-")

    return name


def get_recipes():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, LOWER(name) AS name
            FROM recipes
            WHERE photo_url IS NULL
        """))
        return result.fetchall()


def search_image(query):
    url = API_URL
    params = {"query": query, "per_page": 1}

    res = requests.get(url, headers=HEADERS, params=params)
    data = res.json()

    if data.get("photos"):
        return data["photos"][0]["src"]["large"]

    return None


def download_image(url, filepath):
    res = requests.get(url, stream=True)

    if res.status_code == 200:
        with open(filepath, "wb") as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)
        return True

    return False


def main():
    os.makedirs(SAVE_DIR, exist_ok=True)

    recipes = get_recipes()

    for recipe_id, name in recipes:
        print(f"Fetching: {name}")

        image_url = search_image(name) or search_image(f"{name} food")

        if not image_url:
            print(f"No image found for {name}")
            continue

        slug = slugify(name)
        filepath = os.path.join(SAVE_DIR, f"{slug}.jpg")
     
        if os.path.exists(filepath):
            print(f"Skipping existing: {name}")
            continue

        success = download_image(image_url, filepath)

        if success:
            print(f"Saved → {filepath}")
        else:
            print(f"Failed download: {name}")

        time.sleep(0.5)  # avoid rate limits


if __name__ == "__main__":
    main()
