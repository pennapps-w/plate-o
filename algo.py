import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json
import re

class RestaurantScorer:
    def __init__(self, user_data, restaurant_data, api_key):
        self.user_data = user_data
        self.restaurant_data = restaurant_data
        self.api_key = api_key
        self.vectorizer = TfidfVectorizer()

    def calculate_user_preference_score(self, restaurant):
        previous_ratings = np.array([r['rating'] for r in self.user_data['previous_restaurants']])
        restaurant_descriptions = [r['description'] for r in self.user_data['previous_restaurants']]
        restaurant_descriptions.append(restaurant['description'])
        
        tfidf_matrix = self.vectorizer.fit_transform(restaurant_descriptions)
        cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        
        weighted_ratings = previous_ratings * cosine_similarities[0]
        user_preference_score = np.average(weighted_ratings)
        
        return user_preference_score

    # def calculate_esg_score(self, restaurant):
    #     environmental_score = restaurant.get('environmental_score', 0)
    #     social_score = restaurant.get('social_score', 0)
    #     governance_score = restaurant.get('governance_score', 0)
        
    #     esg_score = (environmental_score + social_score + governance_score) / 3
    #     return esg_score

    def calculate_llm_score(self, restaurant):
        # Prepare the input for the LLM
        prompt = f"""
        Based on the information given, rate how well the given restaurant matches the user's preferences on a scale of 0 to 10, where 0 is a complete mismatch and 10 is a perfect match. If the restaurant description has something the user forbids, give a 0. 

        Example 1:
        User likes: Chinese, Thai, Spicy, Lamb
        User dislikes: Yogurt, Vegetables
        User forbids: Scallops, Cilantro
        Restaurant description: Chinese, Asian, Asian Fusion, Family Meals
        Sampled Reviews: TODO

        The user likes Chinese, and this restaurant has Chinese. Good.
        8

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
        9

        Example 4:
        User likes: Salmon, Tuna
        User dislikes: Sweets
        User forbids: 
        Restaurant description: Mexican
        Sampled Reviews: TODO

        This user likes salmon. The restaurant is Mexican. Ok. 
        5

        Example 5:
        User likes: Greek, Turkish
        User dislikes: Sweets
        User forbids: 
        Restaurant description: Desserts, Ice Cream + Frozen Yogurt
        Sampled Reviews: TODO

        The user dislikes sweets, but the restaurant is Desserts. Bad.
        2
        
        Now here is the information. 

        User likes: {self.user_data['preferences']['likes']}
        User dislikes: {self.user_data['preferences']['dislikes']}
        User forbids: {self.user_data['preferences']['bans']}
        Restaurant description: {restaurant['description']}
        Sampled Reviews: {restaurant['reviews'][:3]}
        """

        # Call the Tune Studio API
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        data = {
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": "You are an AI assistant that rates restaurants based on user preferences. You take into account the users likes and dislikes compared to the restaurant's description and reviews. You pay attention to whether the restaurant has something the user forbids. Your answer should end with with just one integer from the set (0,1,2,3,4,5,6,7,8,9,10). "},
                {"role": "user", "content": prompt}
            ],
            "model": "meta/llama-3.1-405b-instruct",
            "stream": False,
            "max_tokens": 10
        }

        try:
            response = requests.post("https://proxy.tune.app/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            llm_output = response.json()['choices'][0]['message']['content']
            int_output = re.search(r'(?:^|.*[^0-9])([0-9]|10)(?![0-9])', llm_output.strip())
            llm_score = float(int_output) / 10  # Convert to a 0-1 scale
            return llm_score
        except Exception as e:
            print(f"Error in LLM scoring: {e}")
            return 0.5  # Default to neutral score in case of error

    def calculate_final_score(self, restaurant):
        user_preference_score = self.calculate_user_preference_score(restaurant)
        esg_score = self.calculate_esg_score(restaurant)
        llm_score = self.calculate_llm_score(restaurant)
        
        # Combine scores (you may want to adjust these weights)
        final_score = 0.5 * user_preference_score + 0.3 * esg_score + 0.2 * llm_score
        
        return final_score

    def score_restaurant(self, restaurant):
        # Check for hard nos (allergies)
        for allergy in self.user_data['preferences']['hard_nos']:
            if allergy.lower() in restaurant['description'].lower() or allergy.lower() in restaurant['menu'].lower():
                return 0  # Automatic disqualification
        
        return self.calculate_final_score(restaurant)

# Usage
user_data = {
    'previous_restaurants': [
        {'name': 'Restaurant A', 'rating': 4.5, 'description': 'Italian cuisine with a modern twist'},
        {'name': 'Restaurant B', 'rating': 3.0, 'description': 'Casual American diner'}
    ],
    'preferences': {
        'likes': 'spicy food, vegetarian options',
        'dislikes': 'overly greasy food',
        'hard_nos': ['peanuts', 'shellfish']
    }
}

restaurant_data = {
    'name': 'New Restaurant',
    'description': 'Fusion Asian cuisine with a focus on spicy dishes and vegetarian options',
    'menu': 'Spicy tofu stir-fry, Vegetable tempura, Mango sticky rice',
    'environmental_score': 0.8,
    'social_score': 0.7,
    'governance_score': 0.9
}

api_key = 'YOUR_TUNE_STUDIO_API_KEY'
scorer = RestaurantScorer(user_data, restaurant_data, api_key)
final_score = scorer.score_restaurant(restaurant_data)
print(f"Final score for {restaurant_data['name']}: {final_score}")