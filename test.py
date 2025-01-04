from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

data = []

recipe_url = "https://www.plus.nl/recepten-zoeken"

driver = webdriver.Chrome()

try:
    wait = WebDriverWait(driver, 20)
    print("Opening the website...")
    driver.get(recipe_url)

    try:
        print("Checking for cookie popup...")
        cookie_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-cookies-accept"))
        )
        cookie_button.click()
        print("Cookie popup accepted.")
    except Exception as e:
        print(f"No cookie popup or error handling it: {e}")

    try:
        print("Fetching recipe links...")
        recipe_links = driver.find_elements(By.CSS_SELECTOR, "a.cf-recipe-item--link-wrapper")
        recipe_urls = [link.get_attribute("href") for link in recipe_links]
        print(f"Found {len(recipe_urls)} recipes.")
    except Exception as e:
        print(f"Error finding recipe links: {e}")
        recipe_urls = []

    for idx, recipe_url in enumerate(recipe_urls[:10], start=1):
        print(f"Scraping recipe {idx}: {recipe_url}")
        driver.get(recipe_url)
        time.sleep(2)

        try:
            recipe_name = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.cf-recipe-page__title.margin-bottom-m span")
                )
            ).text

            ingredient_elements = driver.find_elements(
                By.CSS_SELECTOR, "div.cf-recipe-page__ingredient span"
            )
            ingredients = [ingredient.text for ingredient in ingredient_elements]

            row = {"RecipeName": recipe_name}
            for i, ingredient in enumerate(ingredients, start=1):
                row[f"Ingredient{i}"] = ingredient
            data.append(row)

            print(f"Recipe '{recipe_name}' scraped successfully with {len(ingredients)} ingredients.")

        except Exception as e:
            print(f"Error extracting data for recipe {recipe_url}: {e}")

finally:
    print("Closing the browser...")
    driver.quit()

if data:
    print("Converting scraped data to a DataFrame...")
    df = pd.DataFrame(data)

    df.to_csv("recipes_with_ingredients.csv", index=False)
    print("Data saved to 'recipes_with_ingredients.csv'")
else:
    print("No data was scraped.")

from tabulate import tabulate

csv_file_path = "recipes_with_ingredients.csv"
data = pd.read_csv(csv_file_path)

max_ingredients = max([len([col for col in row[1:] if pd.notna(col)]) for _, row in data.iterrows()])

# Iterate through each recipe and print the data in a list format
for _, row in data.iterrows():
    print(f"Recipe Name: {row['RecipeName']}")
    ingredients = [row[f"Ingredient{i}"] for i in range(1, max_ingredients + 1) if pd.notna(row[f"Ingredient{i}"])]
    for idx, ingredient in enumerate(ingredients, start=1):
        print(f"  Ingredient {idx}: {ingredient}")
    print("-" * 40)  # Separator for readability
