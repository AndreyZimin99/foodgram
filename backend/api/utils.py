def create_file_shopping_cart(ingredients):
    content = 'Shopping_cart\n'
    for ingredient in ingredients:
        ingredient_data = f"{ingredient['name__name']} \
({ingredient['measurement_unit']}) - {ingredient['total_amount']}"
        content += ingredient_data + '\n'
    return content
