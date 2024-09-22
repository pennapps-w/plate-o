import asyncio
from aiohttp import ClientSession
from requests import get, post, put, delete, HTTPError
from algo import RestaurantScorer
from updateuserinfo import Updater

user_root = "https://blobotic-service1--8000.prod1.defang.dev/users/"
restaurant_root = "https://blobotic-service1--8000.prod1.defang.dev/restaurants/"
# restaurant_root = "http://127.0.0.1:8000/restaurants"
api_key = "sk-tune-zEd2gVmvPCI6uzltkAdgtVhw6UZthlXn0gY"
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

    async def getRestaurantData(self, n):
        tmp = n["data"]
        # logging.info("ID:")
        tmp["id"] = n["id"]
        # logging.info("ID:")
        # logging.info(n["id"])
        return tmp

    async def get_restaurants(self, price_range):
        async with ClientSession() as session:
            async with session.get(restaurant_root) as response:
                all_restaurants = await response.json()
        tmp2 = all_restaurants["restaurants"]
        tmp3 = await asyncio.gather(*[self.getRestaurantData(n) for n in tmp2])
        tmp = price_range

        ans = list(filter(lambda x: len(x["price_point"]) <= tmp, tmp3))
        return ans

    # def restaurantsToScore(self, n):
    #     n["final_score"] = self.scorer.calculate_final_score(n)
    #     return n
    async def restaurantsToScore(self, n):
        n["final_score"] = await self.scorer.calculate_final_score(n)
        return n

    # function to be called when we need to get a recommendation
    async def get_recommendation(self):
        try:
            async with ClientSession() as session:
                async with session.get(user_root + self.user_id) as response:
                    user_data = await response.json()

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

            price_range_restaurants = await self.get_restaurants(user_data["price"])

            if self.rejectedRecommendations >= 3:
                self.scorer = RestaurantScorer(user_preferences, api_key)
                self.rejectedRecommendations = 0

                restaurants_scored = await asyncio.gather(
                    *[self.restaurantsToScore(n) for n in price_range_restaurants]
                )

                self.sortedList = sorted(
                    restaurants_scored, key=lambda d: d["final_score"], reverse=True
                )

            self.restaurant = self.sortedList[self.rejectedRecommendations]
            return self.restaurant
        except Exception as err:
            logging.error(f"An error occurred: {err}")
        return None

    async def rejected_recommendation(self, reason):
        self.rejectedRecommendations += 1
        # async with ClientSession() as session:
        #     async with session.get(user_root + self.user_id) as response:
        #         user_preferences = await response.json()

        # newDislikes = await updater.update_bad(
        #     {
        #         "preferences": {
        #             "likes": user_preferences["likes"],
        #             "dislikes": user_preferences["dislikes"],
        #             "never": user_preferences["never"],
        #         },
        #         "budget": {
        #             "max_price_point": user_preferences["price"],
        #             "meal_budget": user_preferences["meal_budget"],
        #         },
        #     },
        #     self.restaurant,
        #     reason,
        # )

        # async with ClientSession() as session:
        #     async with session.put(
        #         user_root + self.user_id, json={"dislikes": newDislikes}
        #     ) as response:
        #         await response.json()

        # return newDislikes

    async def accepted_recommendation(self):
        # update restaurant precedence to be lower
        return True
