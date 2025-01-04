from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Initialize variables
data = []
recipe_url = "https://www.plus.nl/recepten/avondeten"

# Start the driver
driver = webdriver.Chrome()

try:
    wait = WebDriverWait(driver, 20)
    print("Opening the website...")
    driver.get(recipe_url)

    # Handle cookie popup
    try:
        print("Checking for cookie popup...")
        cookie_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-cookies-accept"))
        )
        cookie_button.click()
        print("Cookie popup accepted.")
    except Exception as e:
        print(f"No cookie popup or error handling it: {e}")

    # Step 1: Collect all recipe URLs
    recipe_urls = []

    # Main page recipe links
    main_page_links = driver.find_elements(By.CSS_SELECTOR, "a.cf-recipe-item--link-wrapper")
    recipe_urls.extend([link.get_attribute("href") for link in main_page_links])

    print(f"Collected {len(main_page_links)} recipes from the main page.")

    # Category links with 'Bekijk'
    try:
        category_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Bekijk')]")
        print(f"Found {len(category_links)} additional category links.")

        for link in category_links:
            category_url = link.get_attribute("href")
            if category_url:
                print(f"Navigating to category: {category_url}")
                driver.get(category_url)
                time.sleep(3)

                # Collect recipe links on the category page
                category_page_links = driver.find_elements(By.CSS_SELECTOR, "a.cf-recipe-item--link-wrapper")
                recipe_urls.extend([link.get_attribute("href") for link in category_page_links])
                print(f"Collected {len(category_page_links)} recipes from category: {category_url}")

    except Exception as e:
        print(f"Error finding or navigating category links: {e}")

    # Step 2: Remove duplicates
    recipe_urls = list(set(recipe_urls))
    print(f"Total unique recipes collected: {len(recipe_urls)}")

    # Step 3: Scrape each recipe
    for idx, recipe_url in enumerate(recipe_urls, start=1):
        print(f"Scraping recipe {idx}/{len(recipe_urls)}: {recipe_url}")
        driver.get(recipe_url)
        time.sleep(2)

        try:
            # Get recipe name
            recipe_name = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.cf-recipe-page__title.margin-bottom-m span")
                )
            ).text

            # Get ingredients
            ingredient_elements = driver.find_elements(
                By.CSS_SELECTOR, "div.cf-recipe-page__ingredient span"
            )
            ingredients = [ingredient.text for ingredient in ingredient_elements]

            # Save data
            row = {"RecipeName": recipe_name}
            for i, ingredient in enumerate(ingredients, start=1):
                row[f"Ingredient{i}"] = ingredient
            data.append(row)

            print(f"Recipe '{recipe_name}' scraped successfully with {len(ingredients)} ingredients")

        except Exception as e:
            print(f"Error extracting data for recipe {recipe_url}: {e}")

finally:
    print("Closing the browser...")
    driver.quit()

# Step 4: Save data to CSV
if data:
    print("Converting scraped data to a DataFrame...")
    df = pd.DataFrame(data)

    df.to_csv("recipes_with_ingredients_and_prices.csv", index=False)
    print("Data saved to 'recipes_with_ingredients_and_prices.csv'")
else:
    print("No data was scraped.")

# Step 5: Display results
from tabulate import tabulate

csv_file_path = "recipes_with_ingredients_and_prices.csv"
data = pd.read_csv(csv_file_path)

max_ingredients = max([len([col for col in row[2:] if pd.notna(col)]) for _, row in data.iterrows()])

# Print data
for _, row in data.iterrows():
    print(f"Recipe Name: {row['RecipeName']}")
    ingredients = [row[f"Ingredient{i}"] for i in range(1, max_ingredients + 1) if pd.notna(row.get(f"Ingredient{i}", None))]
    for idx, ingredient in enumerate(ingredients, start=1):
        print(f"  Ingredient {idx}: {ingredient}")
    print("-" * 40)  # Separator for readability
