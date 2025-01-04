from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Import Keys for simulating keyboard actions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import random

data = []

# URL for the Plus website
plus_url = "https://www.plus.nl"

# Product to search for
search_query = "groente"

with webdriver.Chrome() as driver:
    wait = WebDriverWait(driver, 20)
    driver.get(plus_url)

    # Accept cookie popup if present
    try:
        cookie_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-cookies-accept"))
        )
        cookie_button.click()
        print("Cookie popup accepted.")
    except Exception as e:
        print(f"No cookie popup or error handling it: {e}")

    # Locate the search bar, input the search query, and trigger the search
    try:
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.form-control.gtm-search-input"))
        )
        search_input.clear()  # Clear any pre-existing text in the input field
        search_input.send_keys(search_query)  # Enter the search query

        # Simulate pressing Enter
        search_input.send_keys(Keys.RETURN)  # Press Enter key
        print(f"Searching for: {search_query}")

        # Wait for the search results page to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ph.plp-item-name")))
    except Exception as e:
        print(f"Error performing search: {e}")

    # Scrape the search results
    seen_products = set()
    scroll_attempts = 0

    while True:
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

        products = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-block*='PLPListItem']"))
        )
        print(f"Total products found: {len(products)}")

        new_products_loaded = False

        for product in products:
            try:
                product_name = product.find_element(By.CSS_SELECTOR, "div.ph.plp-item-name span").text
                if product_name in seen_products:
                    continue

                driver.execute_script("arguments[0].scrollIntoView();", product)
                time.sleep(random.uniform(0.5, 1.5))

                try:
                    price_integer = product.find_element(By.CSS_SELECTOR, "div.font-bold.product-header-price-integer span").text
                except Exception:
                    price_integer = "0"

                try:
                    price_decimal = product.find_element(By.CSS_SELECTOR, "div.font-black.product-header-price-decimals span").text
                except Exception:
                    price_decimal = "00"

                price = f"{price_integer}{price_decimal}"

                data.append({"Name": product_name, "Price": price})
                seen_products.add(product_name)
                new_products_loaded = True

            except Exception as e:
                print(f"Error processing product: {e}")

        if not new_products_loaded:
            scroll_attempts += 1
            if scroll_attempts >= 4:
                print("No more new products. Exiting.")
                break
        else:
            scroll_attempts = 0

# Save results to CSV
df = pd.DataFrame(data)
df.to_csv("plus_groentes.csv", index=False)
print(df)
