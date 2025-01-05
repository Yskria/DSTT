from SummariseData import display_recipe_information, save_recipe_totals_to_csv
import pandas as pd

file_path = 'recipes_with_ingredients_and_prices_combined.csv'
df = pd.read_csv(file_path)
output_file = 'recipes_with_total_price.csv'

save_recipe_totals_to_csv(df, output_file)

def filter_recipes_by_price():
    file_path = 'recipes_with_total_price.csv'
    original_file_path = 'recipes_with_ingredients_and_prices_combined.csv'

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return

    try:
        max_price = float(input("What is your current budget?: "))
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
        return

    filtered_df = df[df['Total Price'] <= max_price]

    if filtered_df.empty:
        print(f"No recipes found with a total price less than or equal to {max_price}.")
    else:
        print(f"Recipes with a total price less than or equal to {max_price}:")
        for index, row in filtered_df.iterrows():
            print(f"{index}: {row['Recipe Name']} (Total Price: {row['Total Price']})")

        try:
            selected_index = int(input("Enter the number of the recipe you'd like to view: "))
            if selected_index in filtered_df.index:
                selected_recipe_name = filtered_df.loc[selected_index, 'Recipe Name']
                print(f"\nDetails for '{selected_recipe_name}':")

                original_df = pd.read_csv(original_file_path)
                recipe_details = original_df[original_df['RecipeName'] == selected_recipe_name]
                display_recipe_information(recipe_details)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

filter_recipes_by_price()