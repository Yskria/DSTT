from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os

def scrapeIngredients(url, search_query):
    data = []

    with webdriver.Chrome() as driver:
        wait = WebDriverWait(driver, 20)
        driver.get(url)

        # Handle cookie popup
        try:
            cookie_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-cookies-accept"))
            )
            cookie_button.click()
            print("Cookie popup accepted.")
        except Exception as e:
            print(f"No cookie popup or error handling it: {e}")

        # Perform search
        try:
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.form-control.gtm-search-input"))
            )
            search_input.clear()
            search_input.send_keys(search_query)
            search_input.send_keys(Keys.RETURN)
            print(f"Searching for: {search_query}")

            # Wait for search results to load
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-block*='PLPListItem']"))
            )
            print("Search results loaded.")

            # Add wait time for full DOM rendering
            time.sleep(5)
            print("Waited for DOM to load fully.")
        except Exception as e:
            print(f"Error performing search: {e}")

        while len(data) < 2:
            try:
                products = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-block*='PLPListItem']"))
                )

                for i in range(len(products)):
                    try:
                        products = driver.find_elements(By.CSS_SELECTOR, "div[data-block*='PLPListItem']")
                        product = products[i]

                        product_name = product.find_element(By.CSS_SELECTOR, "div.ph.plp-item-name span").text
                        if search_query.lower() not in product_name.lower():
                            continue

                        try:
                            price_integer = product.find_element(By.CSS_SELECTOR, "div.font-bold.product-header-price-integer span").text
                        except Exception:
                            price_integer = "0"
                        try:
                            price_decimal = product.find_element(By.CSS_SELECTOR, "div.font-black.product-header-price-decimals span").text
                        except Exception:
                            price_decimal = "00"

                        price = f"{price_integer}{price_decimal}"
                        data.append({"Ingredient": product_name, "Price": price})
                        print(f"Product scraped: {product_name}, Price: {price}")

                        if len(data) == 2:
                            break
                    except Exception as e:
                        print(f"Error processing product: {e}")
                        continue

                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, "button.next-page-selector")
                    if next_button.is_enabled():
                        next_button.click()
                        wait.until(EC.staleness_of(products[-1]))
                        print("Moved to the next page.")
                    else:
                        print("No more pages available.")
                        break
                except Exception as e:
                    #print(f"No pagination or error clicking next: {e}")
                    break

            except Exception as e:
                print(f"Error scraping products: {e}")
                break

    try:
        if data:
            first_product = pd.DataFrame([data[0]])  # Only the first product
            file_exists = os.path.isfile("plus_articles.csv")

            first_product.to_csv(
                "plus_articles.csv",
                mode="a",
                index=False,
                header=not file_exists
            )
            print("First product saved to CSV:")
            print(first_product)
        else:
            print("No data collected; nothing to save.")
    except Exception as e:
        print(f"Error saving to CSV: {e}")