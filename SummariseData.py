from RecipeScraper import scrape_recipes
from CombineScraper import combine_data
import pandas as pd

def display_recipe_information(df):
    ingredient_columns = [col for col in df.columns if col.startswith('Ingredient')]
    price_columns = [col for col in df.columns if col.startswith('Price')]

    num_pairs = min(len(ingredient_columns), len(price_columns))

    for _, row in df.iterrows():
        recipe_name = row['RecipeName']
        print(f"Recipe: {recipe_name}")

        total_price = 0
        found_ingredients = False

        for i in range(num_pairs):
            ingredient_col = ingredient_columns[i]
            price_col = price_columns[i]

            if pd.notna(row[ingredient_col]) and pd.notna(row[price_col]):
                ingredient = row[ingredient_col]
                try:
                    price = float(row[price_col])
                    print(f"  - {ingredient}: {round(price, 2)}")
                    total_price += price
                    found_ingredients = True
                except ValueError:
                    pass

        if not found_ingredients:
            print("  No ingredients or prices found.")

        print(f"  - Total Price: {round(total_price, 2)}")

def save_recipe_totals_to_csv(df, output_file):
    
    # scrape_recipes("https://www.plus.nl/recepten/avondeten")
    
    # combine_data(
    #     recipe_file="recipes_with_ingredients_and_prices.csv",
    #     plus_url="https://www.plus.nl",
    #     output_file="recipes_with_ingredients_and_prices_combined.csv"
    # )
    
    ingredient_columns = [col for col in df.columns if col.startswith('Ingredient')]
    price_columns = [col for col in df.columns if col.startswith('Price')]

    num_pairs = min(len(ingredient_columns), len(price_columns))

    recipes_total_price = []

    for _, row in df.iterrows():
        recipe_name = row['RecipeName']
        total_price = 0

        for i in range(num_pairs):
            price_col = price_columns[i]
            if pd.notna(row[price_col]):
                try:
                    total_price += float(row[price_col])
                except ValueError:
                    pass

        recipes_total_price.append({"Recipe Name": recipe_name, "Total Price": round(total_price, 2)})

    output_df = pd.DataFrame(recipes_total_price)
    output_df.to_csv(output_file, index=False)
    print(f"\nRecipes with total prices have been saved to {output_file}")