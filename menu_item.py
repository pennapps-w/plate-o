import numpy as np
import requests
import json
import re
import random

class MenuChooser:
    def __init__(self, user_data, api_key):
        self.user_data = user_data
        self.api_key = api_key

    def calculate_llm_score(self, restaurant):
        # Prepare the input for the LLM
        prompt = f"""
        Based on the information given, please select at least one and at most five items from the given restaurant's menu that match the user's preference most closely. Do not pick any menu item that has something the user forbids. Try not to pick a menu item that has anything the user dislikes.

        Example 1:
        User likes: Chinese, Thai, Spicy, Lamb
        User dislikes: Yogurt, Vegetables
        User forbids: Scallops, Cilantro
        Menu item names and descriptions: ["Large General Tsos Chicken - Boneless chicken, marinated, lightly breaded and fried until crispy, blended with our chefs sweet, tangy, and spicy sauce, with a choice of rice on the side", "Large Shrimp Imperial", "Cup of Steamed Vegetables"]
        Sampled Reviews: TODO

        The user likes Chinese, and this restaurant has Chinese food. The user dislikes vegetables, so they will not order the cup of steamed vegetables. The user likes spicy, so they want large general tso's chicken. The user does not like scallops, so maybe they don't want shrimp.
        Large General Tso's Chicken

        Example 2:
        User likes: Chinese, Thai, Spicy, Lamb
        User dislikes: Yogurt, Vegetables
        User forbids: Scallops
        Menu item names and descriptions: ["Pancakes (Two Pieces)", "Chicken and Sweet Corn Soup", "Tofu with Vegetables Soup", "Bottle Drink", "Fried Rice", "Combo Fried Rice", "Glazed Lamb Chops"]
        Sampled Reviews: TODO

        The user likes lamb, so glazed lamb chops is a good order. The user dislikes vegetables, so the user should not order tofu with vegetables soup. To make a balanced meal, the user should order a bottled drink or the chicken and sweet corn soup.
        Glazed Lamb Chops, Chicken and Sweet Corn Soup

        Example 3:
        User likes: Paneer, Mango, Coffee
        User dislikes: Feta Cheese
        User forbids: Meat
        Menu item names and descriptions: ["Mango cheesecake", "Mango sushi", "Hot chocolate with a shot of espresso", "Paneer tikka masala", "Feta pasta"]
        Sampled Reviews: TODO

        The user dislikes Feta Cheese so they should not order feta pasta. They like paneer and coffee and forbid meat, so they should order paneer tikka masala, which is vegetarian, and a hot chocolate with a shot of espresso. 
        Paneer Tikka Masala, Hot chocolate with a shot of espresso

        Example 4:
        User likes: Salmon, Tuna
        User dislikes: Sweets
        User forbids: 
        Menu item names and descriptions: ["Beijing Roasted Duck - crispy duck with a thin pancake, cucumbers, green onions, and a savory sauce that packs a punch!", "Pineapple bun", "Roasted cauliflower"]
        Sampled Reviews: TODO

        This user likes salmon and tuna, but the restaurant doesn't serve either. Salmon and tuna are both types of meat, so the user should order beijing roasted duck, which is also savory and not sweet.
        Beijing Roasted Duck

        Example 5:
        User likes: Greek, Turkish
        User dislikes: Sweets
        User forbids: 
        Menu item names and descriptions: ["Gyro", "Chicken feet", "Dumplings"]
        Sampled Reviews: TODO

        The user likes Greek, so they should order a gyro. 
        Gyro
        
        Now here is the information. 

        User likes: {self.user_data['preferences']['likes']}
        User dislikes: {self.user_data['preferences']['dislikes']}
        User forbids: {self.user_data['preferences']['bans']}
        Menu item names and descriptions: {[a["name"] + " - " + a["description"] for a in restaurant['menu']]}
        Sampled Reviews: {random.sample(restaurant['reviews'],3)}
        """

        # Call the Tune Studio API
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        data = {
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": "You are an AI assistant that orders from a restaurant given the menu based on user preferences. You take into account the users likes and dislikes compared to the restaurant's description and reviews. You pay attention to whether the restaurant has something the user forbids. Be concise. Your answer should contain at most three sentences, and end with with a comma-separated list of menu items from the given restaurant. "},
                {"role": "user", "content": prompt}
            ],
            "model": "meta/llama-3.1-405b-instruct",
            "stream": False,
            "max_tokens": 100
        }

        try:
            response = requests.post("https://proxy.tune.app/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            llm_output = response.json()['choices'][0]['message']['content']
            print(llm_output.strip())
            tmp = llm_output.split("\n")
            
            return tmp[-1]
        except Exception as e:
            print(f"Error in LLM scoring: {e}")
            return ""  # Default to neutral score in case of error

    def calculate_final_score(self, restaurant):
        llm_score = self.calculate_llm_score(restaurant)
        
        return llm_score

# Example usage
user_data = {
    'preferences': {
        'likes': 'spicy food, vegetarian options',
        'dislikes': 'overly greasy food',
        'bans': 'peanuts, shellfish'
    },
    'budget': {
        'max_price_point': 2,
        'meal_budget': 15.00
    }
}

restaurant_data = {
    'name': 'New Restaurant',
    'description': 'Fusion Asian cuisine with a focus on spicy dishes and vegetarian options',
    'menu': ['Spicy tofu stir-fry, Vegetable tempura, Mango sticky rice'],
    'reviews': ['Best food ever!', 'Only go if you are ok with sticky chairs.', 'Creative fusion cuisine'],
    'price point': '$',
    'score': 5
}

# FOR TESTING
api_key = 'sk-tune-31SubFSL3vCE9hMxp9AJWzqh9MzWfUNcCNs'
scorer = RestaurantScorer(user_data, api_key)
final_score = scorer.calculate_final_score(restaurant_data)
print(f"Final score for {restaurant_data['name']}: {final_score}")