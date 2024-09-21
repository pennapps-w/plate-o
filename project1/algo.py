import numpy as np
import requests
import json
import re
import random
import aiohttp
import math


class RestaurantScorer:
    def __init__(
        self,
        user_data,
        api_key,
        delivery_address="3401 Walnut St, Philadelphia, PA 19104",
    ):
        self.user_data = user_data
        self.api_key = api_key
        self.delivery_address = delivery_address
        self.max_distance = 50.0

    async def calculate_llm_score(self, restaurant):
        # Prepare the input for the LLM
        prompt = f"""
        Based on the information given, rate how well the given restaurant matches the user's preferences on a scale of 0 to 100, where 0 is a complete mismatch and 100 is a perfect match. If the restaurant description has something the user forbids, give a 0. 

        Example 1:
        User likes: Chinese, Thai, Spicy, Lamb
        User dislikes: Yogurt, Vegetables
        User forbids: Scallops, Cilantro
        Restaurant description: Chinese, Asian, Asian Fusion, Family Meals, Noodles
        Restaurant rating: 4.3
        Sampled Reviews: [What I expect from a chain. It’s pretty good food, and if you can do happy hour I’d say it’s worth it., Nice firm noodles, A tad spicy but delicious]

        The user likes Chinese, and this restaurant has Chinese. Good.
        81

        Example 2:
        User likes: Chinese, Thai, Spicy, Lamb
        User dislikes: Yogurt, Vegetables
        User forbids: Scallops
        Restaurant description: Sushi, Asian, Japanese
        Restaurant rating: 3.9
        Sampled Reviews: [Pretty fresh sushi!, Definitely will come back., Watch out. I brought my three year old son to this restaurant before learning they only serve raw food!]

        The user forbids scallops, but this restaurant has sushi. Banned. 
        0

        Example 3:
        User likes: Paneer, Mango, Coffee
        User dislikes: Feta Cheese
        User forbids: Meat
        Restaurant description: Indian, Vegan, Vegetarian, Asian, Pakistani, Gluten Free, Indian Curry
        Restaurant rating: 4.9
        Sampled Reviews: [Their lunch specialty is undoubtedly the best deal and you can't beat it., The food is fantastic and the place always looks clean., Good local spot and reasonably priced]

        This user likes paneer and forbids meat, and this restaurant is Indian and Vegan. Good.
        96

        Example 4:
        User likes: Salmon, Tuna
        User dislikes: Sweets
        User forbids: 
        Restaurant description: Mexican
        Restaurant rating: 4.1
        Sampled Reviews: [The menu offered a wide range of flavors and ingredients, and the presentation of the dishes was impressive., Quick service!, Really delicious food for good prices and the owners are so friendly!]

        This user likes salmon and the restaurant is Mexican, but the reviews are pretty good. Ok. 
        65

        Example 5:
        User likes: Greek, Turkish
        User dislikes: Sweets
        User forbids: 
        Restaurant description: Desserts, Ice Cream + Frozen Yogurt
        Restaurant rating: 4.3
        Sampled Reviews: [Great hangout spot!, My go-to spot in the summer, I have a sweet tooth and this place has been the best one I've ever tried.]

        The user dislikes sweets, but the restaurant is Desserts. Bad.
        15

        Example 6:
        User likes: Asian
        User dislikes: Vinegar, lemons
        User forbids: Gluten
        Restaurant description: Chinese, Cantonese
        Restaurant rating: 2.3
        Sampled Reviews: [Terrible service. Ignored me for thirty minutes, then accused me of ordering right before closing., Because the entrance, all I seen was 50lbs bag of white onions, sodas and ect. all over the floor..., This place is disgusting, the service is bad and the food is worse.]

        The user likes Asian, and this restaurant has Chinese. However the restaurant rating is too low. Bad.
        25
        
        Now here is the information. 

        User likes: {self.user_data['preferences']['likes']}
        User dislikes: {self.user_data['preferences']['dislikes']}
        User forbids: {self.user_data['preferences']['never']}
        Restaurant description: {restaurant['description']}
        Restaurant rating: {str(restaurant['avg_score'])}
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
                {
                    "role": "system",
                    "content": "You are an AI assistant that rates restaurants based on user preferences. You take into account the users likes and dislikes compared to the restaurant's description and reviews. You pay attention to whether the restaurant has something the user forbids. Be concise. Your answer should contain at most three sentences, and end with with just one integer from 0 to 100. ",
                },
                {"role": "user", "content": prompt},
            ],
            "model": "meta/llama-3.1-405b-instruct",
            "stream": False,
            "max_tokens": 100,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://proxy.tune.app/chat/completions",
                    headers=headers,
                    json=data,
                ) as response:
                    response_data = await response.json()
                    llm_output = response_data["choices"][0]["message"]["content"]
                    print(llm_output.strip())
                    int_output = re.findall(r"\d+", llm_output.strip())[-1]
                    llm_score = float(int_output) / 10  # Convert to a 0-10 scale
                    return llm_score
        except Exception as e:
            print(f"Error in LLM scoring: {e}")
            return 5.0  # Default to neutral score in case of error

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 3959  # Earth's radius in miles

        # Convert latitude and longitude to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c

        return distance

    def calculate_carbon_impact(self, restaurant_location):
        # Calculate distance between restaurant and delivery location
        distance = self.haversine_distance(
            39.952305, -75.193703, restaurant_location[0], restaurant_location[1]
        )

        # Normalize distance to a 0-1 scale
        normalized_distance = min(distance / self.max_distance, 1)

        # Calculate environmental factor:
        # At distance 0, factor is 1.1 (10% boost)
        # At max distance, factor is 0.5 (50% penalty)
        environmental_factor = 1.1 - 0.7 * (normalized_distance**2)

        return environmental_factor

    def calculate_final_score(self, restaurant):
        llm_score = self.calculate_llm_score(restaurant)

        # Calculate environmental factor based on carbon impact
        environmental_factor = self.calculate_carbon_impact(
            (restaurant["latitude"], restaurant["longitude"])
        )

        # Apply the environmental factor to the LLM score
        final_score = llm_score * environmental_factor

        return final_score


# Example usage
user_data = {
    "preferences": {
        "likes": "spicy food, vegetarian options",
        "dislikes": "overly greasy food",
        "never": "peanuts, shellfish",
    },
    "budget": {"max_price_point": 2, "meal_budget": 15.00},
}

restaurant_data = {
    "name": "New Restaurant",
    "description": "Fusion Asian cuisine with a focus on spicy dishes and vegetarian options",
    "menu": ["Spicy tofu stir-fry, Vegetable tempura, Mango sticky rice"],
    "reviews": [
        "Best food ever!",
        "Only go if you are ok with sticky chairs.",
        "Creative fusion cuisine",
    ],
    "price point": "$",
    "avg_score": 5.0,
}


# FOR TESTING
async def test_scorer():
    api_key = "sk-tune-31SubFSL3vCE9hMxp9AJWzqh9MzWfUNcCNs"
    scorer = RestaurantScorer(user_data, api_key)
    final_score = await scorer.calculate_final_score(restaurant_data)
    print(f"Final score for {restaurant_data['name']}: {final_score}")
