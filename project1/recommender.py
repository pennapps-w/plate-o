from requests import get, post, put, delete, HTTPError
from algo import RestaurantScorer
from updateuserinfo import Updater

user_root = "https://blobotic-service1--8000.prod1.defang.dev/users/"
restaurant_root = "https://blobotic-service1--8000.prod1.defang.dev/restaurants/"
# restaurant_root = "http://127.0.0.1:8000/restaurants"
api_key = "sk-tune-31SubFSL3vCE9hMxp9AJWzqh9MzWfUNcCNs"
updater = Updater(api_key)

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Recommender:
    def __init__(self, user_id):
        self.user_id = user_id
        self.restaurant = None
        self.rejectedRecommendations = 3
        self.scorer = None
        self.sortedList = None

    def getRestaurantData(self, n):
        return n["data"]

    def get_restaurants(self, price_range):
        all_restaurants = get(restaurant_root)
        tmp2 = all_restaurants.json()["restaurants"]
        tmp3 = list(map(self.getRestaurantData, tmp2))
        # print(f"tmp3 {tmp3}")
        tmp = price_range

        ans = list(filter(lambda x: len(x["price_point"]) <= tmp, tmp3))
        # ans_str = str(ans)
        # print(ans_str[:50])

        return ans

    def restaurantsToScore(self, n):
        n["final_score"] = self.scorer.calculate_final_score(n)
        return n

    # function to be called when we need to get a recommendation
    def get_recommendation(self):
        try:
            response = get(user_root + self.user_id)
            response.raise_for_status()
            user_data = response.json()
            print(f"user_data {user_data}")

            user_preferences = {
                "preferences": {
                    "likes": user_data.get("likes", []),
                    "dislikes": user_data.get("dislikes", []),
                    "never": user_data.get("never", []),
                },
                "budget": {
                    "max_price_point": user_data.get("price", 3),
                    "meal_budget": user_data.get("meal_budget", 0),
                },
            }

            print(f"user_preferences {user_preferences}")

            price_range_restaurants = self.get_restaurants(user_data["price"])
            # price_range_restaurants = self.get_restaurants(user_preferences["price"])
            # print(f"price_range_restaurants: {price_range_restaurants}")

            print("were before our if statement")
            if self.rejectedRecommendations >= 3:
                self.scorer = RestaurantScorer(user_preferences, api_key)
                self.rejectedRecommendations = 0

                restaurants_scored = list(
                    map(self.restaurantsToScore, price_range_restaurants)
                )

                sortedList = sorted(
                    restaurants_scored, key=lambda d: d["final_score"], reverse=True
                )

            # print(f"Sorted Restaurant List: {sortedList}")
            self.restaurant = sortedList[self.rejectedRecommendations]

            return self.restaurant
        except HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            logging.error(f"An error occurred: {err}")
        return None

    def rejected_recommendation(self, reason):
        self.rejectedRecommendations += 1
        # update user info
        response = get(user_root + self.user_id)
        user_preferences = response.json()
        newDislikes = updater.update_bad(
            {
                "preferences": {
                    "likes": user_preferences["likes"],
                    "dislikes": user_preferences["dislikes"],
                    "never": user_preferences["never"],
                },
                "budget": {
                    "max_price_point": user_preferences["price"],
                    "meal_budget": user_preferences["meal_budget"],
                },
            },
            self.restaurant,
            reason,
        )

        response = put(user_root + self.user_id, json={"dislikes": newDislikes})
        return newDislikes

    def accepted_recommendation(self):
        # update restaurant precedence to be lower
        return True
