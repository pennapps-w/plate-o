import numpy as np
import requests
import json
import re
import random

class RestaurantScorer:
    def __init__(self, user_data, api_key):
        self.user_data = user_data
        self.api_key = api_key

    def calculate_llm_score(self, restaurant):
        # Prepare the input for the LLM
        prompt = f"""
        Based on the information given, rate how well the given restaurant matches the user's preferences on a scale of 0 to 100, where 0 is a complete mismatch and 100 is a perfect match. If the restaurant description has something the user forbids, give a 0. 

        Example 1:
        User likes: Chinese, Thai, Spicy, Lamb
        User dislikes: Yogurt, Vegetables
        User forbids: Scallops, Cilantro
        Restaurant description: Chinese, Asian, Asian Fusion, Family Meals
        Sampled Reviews: TODO

        The user likes Chinese, and this restaurant has Chinese. Good.
        81

        Example 2:
        User likes: Chinese, Thai, Spicy, Lamb
        User dislikes: Yogurt, Vegetables
        User forbids: Scallops
        Restaurant description: Sushi, Asian, Japanese
        Sampled Reviews: TODO

        The user forbids scallops, but this restaurant has sushi. Banned. 
        0

        Example 3:
        User likes: Paneer, Mango, Coffee
        User dislikes: Feta Cheese
        User forbids: Meat
        Restaurant description: Indian, Vegan, Vegetarian, Asian, Pakistani, Gluten Free, Indian Curry
        Sampled Reviews: TODO

        This user likes paneer and forbids meat, and this restaurant is Indian and Vegan. Good.
        96

        Example 4:
        User likes: Salmon, Tuna
        User dislikes: Sweets
        User forbids: 
        Restaurant description: Mexican
        Sampled Reviews: TODO

        This user likes salmon. The restaurant is Mexican. Ok. 
        50

        Example 5:
        User likes: Greek, Turkish
        User dislikes: Sweets
        User forbids: 
        Restaurant description: Desserts, Ice Cream + Frozen Yogurt
        Sampled Reviews: TODO

        The user dislikes sweets, but the restaurant is Desserts. Bad.
        15
        
        Now here is the information. 

        User likes: {self.user_data['preferences']['likes']}
        User dislikes: {self.user_data['preferences']['dislikes']}
        User forbids: {self.user_data['preferences']['bans']}
        Restaurant description: {restaurant['description']}
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
                {"role": "system", "content": "You are an AI assistant that rates restaurants based on user preferences. You take into account the users likes and dislikes compared to the restaurant's description and reviews. You pay attention to whether the restaurant has something the user forbids. Be concise. Your answer should contain at most three sentences, and end with with just one integer from 0 to 100. "},
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
            int_output = re.findall(r'\d+', llm_output.strip())[-1]
            llm_score = float(int_output) / 10  # Convert to a 0-1 scale
            return llm_score
        except Exception as e:
            print(f"Error in LLM scoring: {e}")
            return 0.5  # Default to neutral score in case of error

    def calculate_final_score(self, restaurant):
        llm_score = self.calculate_llm_score(restaurant)
        
        return llm_score

# Example usage
user_data = {
    'preferences': {
        'likes': 'spicy food, vegetarian options',
        'dislikes': 'overly greasy food',
        'bans': ['peanuts', 'shellfish']
    },
    'budget': {
        'max_price_point': 2,
        'meal_budget': 15.00
    }
}

restaurant_data = {
    'name': 'New Restaurant',
    'description': 'Fusion Asian cuisine with a focus on spicy dishes and vegetarian options',
    'menu': 'Spicy tofu stir-fry, Vegetable tempura, Mango sticky rice',
    'reviews': ['Best food ever!', 'Only go if you are ok with sticky chairs.', 'Creative fusion cuisine'],
    'price point': '$'
}

api_key = 'sk-tune-31SubFSL3vCE9hMxp9AJWzqh9MzWfUNcCNs'
scorer = RestaurantScorer(user_data, api_key)
final_score = scorer.calculate_final_score(restaurant_data)
print(f"Final score for {restaurant_data['name']}: {final_score}")