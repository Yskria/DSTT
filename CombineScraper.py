import pandas as pd
import re
from IngredientScraper import scrapeIngredients
import os
from fuzzywuzzy import process

def extract_ingredients_from_csv(file_path):
    data = pd.read_csv(file_path)

    max_ingredients = max(
        int(col.replace("Ingredient", "")) 
        for col in data.columns 
        if col.startswith("Ingredient")
    )

    recipes = []
    for _, row in data.iterrows():
        recipe = {"RecipeName": row["RecipeName"]}
        ingredients = [
            re.sub(r'^.*?([A-Z].*)', r'\1', str(row[f"Ingredient{i}"]))
            for i in range(1, max_ingredients + 1)
            if pd.notna(row.get(f"Ingredient{i}", None))
        ]
        recipe["Ingredients"] = ingredients
        recipes.append(recipe)
    
    return recipes

def scrape_and_save_ingredients(recipe_file, plus_url):
    recipes = extract_ingredients_from_csv(recipe_file)
    scraped_data = []

    for recipe in recipes:
        for ingredient in recipe["Ingredients"]:
            results = scrapeIngredients(plus_url, ingredient)
            if results:
                scraped_data.append({"Ingredient": ingredient, "Price": results[0]["Price"]})

    file_exists = os.path.isfile("plus_articles.csv")
    df = pd.DataFrame(scraped_data)
    df.to_csv("plus_articles.csv", index=False, mode="a", header=not file_exists)
    print("Scraped ingredient prices saved to plus_articles.csv")

def find_closest_match(ingredient, ingredient_list, threshold=80):
    match, score = process.extractOne(ingredient, ingredient_list)
    return match if score >= threshold else None

def combine_data(recipe_file, plus_url, output_file):
    scrape_and_save_ingredients(recipe_file, plus_url)

    if not os.path.isfile("plus_articles.csv"):
        print("No scraped price data found.")
        return

    scraped_prices = pd.read_csv("plus_articles.csv")
    ingredient_price_map = dict(zip(scraped_prices["Ingredient"], scraped_prices["Price"]))
    ingredient_list = list(ingredient_price_map.keys())

    recipes = extract_ingredients_from_csv(recipe_file)
    all_results = []

    for recipe in recipes:
        recipe_name = recipe["RecipeName"]
        ingredients = recipe["Ingredients"]
        recipe_data = {"RecipeName": recipe_name}

        for i, ingredient in enumerate(ingredients, start=1):
            closest_match = find_closest_match(ingredient, ingredient_list)

            price = ingredient_price_map.get(closest_match, "Not Found") if closest_match else "Not Found"

            recipe_data[f"Ingredient{i}"] = ingredient
            recipe_data[f"Price{i}"] = price

        all_results.append(recipe_data)

    df = pd.DataFrame(all_results)
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

    try:
        os.remove("plus_articles.csv")
        print("plus_articles.csv cleared after combination.")
    except FileNotFoundError:
        print("plus_articles.csv not found, nothing to clear.")