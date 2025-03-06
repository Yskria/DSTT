from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random

def scrape_recipes(recipe_url):
    data = []

    with webdriver.Chrome() as driver:
        wait = WebDriverWait(driver, 20)
        driver.get(recipe_url)

        try:
            cookie_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-cookies-accept"))
            )
            cookie_button.click()
            print("Cookie popup accepted.")
        except Exception as e:
            print(f"No cookie popup or error handling it: {e}")

        recipe_urls = []

        main_page_links = driver.find_elements(By.CSS_SELECTOR, "a.cf-recipe-item--link-wrapper")
        recipe_urls.extend([link.get_attribute("href") for link in main_page_links])

        print(f"Collected {len(main_page_links)} recipes from the main page.")

        recipe_urls = list(set(recipe_urls))
        print(f"Total unique recipes collected: {len(recipe_urls)}")

        for idx, recipe_url in enumerate(recipe_urls, start=1):
            print(f"Scraping recipe {idx}/{len(recipe_urls)}: {recipe_url}")
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

                print(f"Recipe '{recipe_name}' scraped successfully with {len(ingredients)} ingredients")

            except Exception as e:
                print(f"Error extracting data for recipe {recipe_url}: {e}")

    if data:
        print("Converting scraped data to a DataFrame...")
        df = pd.DataFrame(data)
        df.to_csv("recipes_with_ingredients_and_prices.csv", index=False)
        print("Data saved to 'recipes_with_ingredients_and_prices.csv'")
    else:
        print("No data was scraped.")