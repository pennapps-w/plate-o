import numpy as np
import requests
import json
import re
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MenuChooser:
    def __init__(self, user_data, api_key):
        self.user_data = user_data
        self.api_key = api_key

    def select_item(self, restaurant, additional_notes=""):
        print("ADDITIONAL NOTES: ")
        print(additional_notes)
        # Prepare the input for the LLM
        prompt = (
            "Based on the information given, please select at least one and at most five items from the given restaurant's menu that match the user's preference most closely. Do not pick any menu item that has something the user forbids. Try not to pick a menu item that has anything the user dislikes. "
            + additional_notes
            + "\n\n"
            "Example 1:\n"
            "User likes: Chinese, Thai, Spicy, Lamb\n"
            "User dislikes: Yogurt, Vegetables\n"
            "User forbids: Scallops, Cilantro\n"
            'Menu item names and descriptions: ["Large General Tsos Chicken - Boneless chicken, marinated, lightly breaded and fried until crispy, blended with our chefs sweet, tangy, and spicy sauce, with a choice of rice on the side : 12.99", "Large Shrimp Imperial : 18.50", "Cup of Steamed Vegetables : 4.99"]\n'
            "Sampled Reviews: N/A\n\n"
            "The user likes Chinese, and this restaurant has Chinese food. The user dislikes vegetables, so they will not order the cup of steamed vegetables. The user likes spicy, so they want large general tso's chicken. The user does not like scallops, so maybe they don't want shrimp.\n"
            "Large General Tso's Chicken\n\n"
            "Example 2:\n"
            "User likes: Chinese, Thai, Spicy, Lamb\n"
            "User dislikes: Yogurt, Vegetables\n"
            "User forbids: Scallops\n"
            'Menu item names and descriptions: ["Pancakes (Two Pieces) : 8.00", "Chicken and Sweet Corn Soup : 3.79", "Tofu with Vegetables Soup : 4.29", "Bottle Drink : 0.99", "Fried Rice : 9.99", "Combo Fried Rice : 11.99", "Glazed Lamb Chops : 15.00"]\n'
            "Sampled Reviews: N/A\n\n"
            "The user likes lamb, so glazed lamb chops is a good order. The user dislikes vegetables, so the user should not order tofu with vegetables soup. To make a balanced meal, the user should order a bottled drink or the chicken and sweet corn soup.\n"
            "Glazed Lamb Chops, Chicken and Sweet Corn Soup\n\n"
            "Example 3:\n"
            "User likes: Paneer, Mango, Coffee\n"
            "User dislikes: Feta Cheese\n"
            "User forbids: Meat\n"
            'Menu item names and descriptions: ["Mango cheesecake : 5.00", "Mango sushi : 6.50", "Hot chocolate with a shot of espresso : 2.50", "Paneer tikka masala : 9.25", "Feta pasta : 12.00"]\n'
            "Sampled Reviews: N/A\n\n"
            "The user dislikes Feta Cheese so they should not order feta pasta. They like paneer and coffee and forbid meat, so they should order paneer tikka masala, which is vegetarian, and a hot chocolate with a shot of espresso.\n"
            "Paneer Tikka Masala, Hot chocolate with a shot of espresso\n\n"
            "Example 4:\n"
            "User likes: Salmon, Tuna\n"
            "User dislikes: Sweets\n"
            "User forbids: \n"
            'Menu item names and descriptions: ["Beijing Roasted Duck - crispy duck with a thin pancake, cucumbers, green onions, and a savory sauce that packs a punch! : 39.99", "Pineapple bun : 2.85", "Roasted cauliflower : 9.60"]\n'
            "Sampled Reviews: N/A\n\n"
            "This user likes salmon and tuna, but the restaurant doesn't serve either. Salmon and tuna are both types of meat, so the user should order beijing roasted duck, which is also savory and not sweet.\n"
            "Beijing Roasted Duck\n\n"
            "Example 5:\n"
            "User likes: Greek, Turkish\n"
            "User dislikes: Sweets\n"
            "User forbids: \n"
            'Menu item names and descriptions: ["Gyro : 10.00", "Chicken feet : 5.00", "Dumplings : 7.99"]\n'
            "Sampled Reviews: N/A\n\n"
            "The user likes Greek, so they should order a gyro.\n"
            "Gyro\n\n"
            "Now here is the information.\n\n"
            "User likes: " + self.user_data["preferences"]["likes"] + "\n"
            "User dislikes: " + self.user_data["preferences"]["dislikes"] + "\n"
            "User forbids: " + self.user_data["preferences"]["bans"] + "\n"
            "Menu item names and descriptions: "
            + str(
                [
                    a["name"]
                    + " - "
                    + a["description"]
                    + " : "
                    + str(round(float(a["price"].split(" ")[0]), 2))
                    for a in restaurant["menu"]
                ]
            )
            + "\n"
        )

        reviews = restaurant.get("reviews", [])
        if reviews:
            sampled_reviews = random.sample(reviews, min(3, len(reviews)))
            review_texts = [
                review.get("text", "No review text") for review in sampled_reviews
            ]
            prompt += "Sampled Reviews: " + str(review_texts) + "\n"
        else:
            prompt += "Sampled Reviews: No reviews available\n"

        print("Debug - Restaurant keys:", restaurant.keys())
        print("Debug - Prompt:", prompt)

        # Call the Tune Studio API
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        data = {
            "temperature": 0.5,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant that orders from a restaurant given the menu based on user preferences. You take into account the users likes and dislikes compared to the restaurant's description and reviews. You pay attention to whether the restaurant has something the user forbids. Be concise. Your answer should contain at most three sentences, and end with with a comma-separated list of menu items from the given restaurant. ",
                },
                {"role": "user", "content": prompt},
            ],
            "model": "meta/llama-3.1-405b-instruct",
            "stream": False,
            "max_tokens": 100,
        }
        try:
            response = requests.post(
                "https://proxy.tune.app/chat/completions", headers=headers, json=data
            )
            response.raise_for_status()
            llm_output = response.json()["choices"][0]["message"]["content"]
            print(llm_output.strip())
            tmp = llm_output.split("\n")[-1]
            items = [item.strip() for item in tmp.split(",")]

            # Use sklearn to find the most similar menu items
            menu_items = [
                item["name"] + " - " + item["description"]
                for item in restaurant["menu"]
            ]

            vectorizer = TfidfVectorizer()
            menu_vectors = vectorizer.fit_transform(menu_items)
            item_vectors = vectorizer.transform(items)

            similarities = cosine_similarity(item_vectors, menu_vectors)

            selected_items = []
            for i, item in enumerate(items):
                best_match_index = similarities[i].argmax()
                selected_items.append(restaurant["menu"][best_match_index])

            return selected_items
        except Exception as e:
            print("Error in LLM selection: " + str(e))
            return []

    def robust_selection(self, restaurant, additional_notes=""):
        ### RETURNS A PAIR (ORDER PRINTSTRING, PRICE) WITHIN BUDGET
        # print("restaurant: {}".format(restaurant["name"]))
        items = self.select_item(restaurant, additional_notes)
        # print(items)
        printstring = ""
        totalprice = 0
        for item in items:
            price = float(item["price"].split()[0])  # Extract numeric price
            totalprice += price
            printstring += "- {}: ${}".format(item["name"], str(round(price, 2)))
        if totalprice <= float(self.user_data["budget"]["meal_budget"]):
            return (printstring, totalprice)
        else:
            return self.robust_selection(
                restaurant,
                "The user only has a budget of {}, so you must select cheaper items. DO NOT GO OVER THE BUDGET. ".format(
                    self.user_data["budget"]["meal_budget"]
                ),
            )

        # print(f"restaurant: {restaurant}")
        # items = self.select_item(restaurant, additional_notes)
        # # print(items)
        # printstring = restaurant["name"]
        # totalprice = 0
        # for item in items:
        #     totalprice += float(item["price"])
        #     printstring += f"- {item['name']}: ${item['price']:.2f}"
        # if totalprice <= float(self.user_data["budget"]["meal_budget"]):
        #     return (printstring, totalprice)
        # else:
        #     return self.robust_selection(
        #         restaurant,
        #         f"The user only has a budget of {self.user_data['budget']['meal_budget']}, so you must select cheaper items. DO NOT GO OVER THE BUDGET. ",
        #     )


# VVVVVV FOR TESTING VVVVVV


# # Example usage
# user_data = {
#     "preferences": {
#         "likes": "spicy food, vegetarian options",
#         "dislikes": "overly greasy food",
#         "bans": "peanuts, shellfish",
#     },
#     "budget": {"max_price_point": 2, "meal_budget": 15.00},
# }

# restaurant_data = {
#     "name": "New Restaurant",
#     "description": "Fusion Asian cuisine with a focus on spicy dishes and vegetarian options",
#     "menu": ["Spicy tofu stir-fry, Vegetable tempura, Mango sticky rice"],
#     "reviews": [
#         "Best food ever!",
#         "Only go if you are ok with sticky chairs.",
#         "Creative fusion cuisine",
#     ],
#     "price point": "$",
#     "score": 5,
# }

# api_key = "sk-tune-31SubFSL3vCE9hMxp9AJWzqh9MzWfUNcCNs"
# # Example usage
# user_data = {
#     "preferences": {
#         "likes": "spicy food, vegetarian options",
#         "dislikes": "overly greasy food",
#         "bans": "peanuts, shellfish",
#     },
#     "budget": {"max_price_point": 2, "meal_budget": 10.00},
# }

# restaurant_data = {
#     "name": "New Restaurant",
#     "description": "Fusion Asian cuisine with a focus on spicy dishes and vegetarian options",
#     "menu": [
#         {
#             "name": "Spicy tofu stir-fry",
#             "description": "Crispy tofu cubes in a spicy sauce with mixed vegetables",
#             "price": 12.99,
#         },
#         {
#             "name": "Vegetable tempura",
#             "description": "Assorted vegetables fried in a light, crispy batter",
#             "price": 9.99,
#         },
#         {
#             "name": "Mango sticky rice",
#             "description": "Sweet sticky rice topped with fresh mango and coconut cream",
#             "price": 6.99,
#         },
#     ],
#     "reviews": [
#         "Best food ever!",
#         "Only go if you are ok with sticky chairs.",
#         "Creative fusion cuisine",
#     ],
#     "price point": "$",
#     "score": 5,
# }

# # api_key = 'sk-tune-31SubFSL3vCE9hMxp9AJWzqh9MzWfUNcCNs'
# # scorer = MenuChooser(user_data, api_key)
# # orderinfo = scorer.robust_selection(restaurant_data)
# # print("ORDER:")
# # printstring = orderinfo[0]
# # totalprivce = orderinfo[1]
# # print(printstring)
