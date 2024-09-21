from requests import get, post, put, delete, HTTPError
from algo import RestaurantScorer
from updateuserinfo import Updater

user_root = "https://blobotic-service1--8000.prod1.defang.dev/users/"
restaurant_root = "https://blobotic-service1--8000.prod1.defang.dev/restaurants/"
# restaurant_root = "http://127.0.0.1:8000/restaurants"
api_key = 'sk-tune-31SubFSL3vCE9hMxp9AJWzqh9MzWfUNcCNs'
updater = Updater(api_key)


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

        tmp = len(price_range)

        return filter(lambda x: len(x) <= tmp, tmp3)


    def restaurantsToScore(self, n):
        n["final_score"] = self.scorer.calculate_final_score(n)
        return n

    # function to be called when we need to get a recommendation
    def get_recommendation(self):
        response = get(user_root + self.user_id)
        # if we want to test for if the api returns correctly, need try/except
        # response.raise_for_status() 
        user_preferences = response.json()
        price_range_restaurants = self.get_restaurants(user_preferences["price"])

        if rejectedRecommendations >= 3:
            self.scorer = RestaurantScorer(user_preferences, api_key)
            rejectedRecommendations = 0
        
            restaurants_scored = list(map(self.restaurantsToScore, price_range_restaurants))
        
            sortedList = sorted(restaurants_scored, key=lambda d: d["final_score"], reverse=True)
        
        self.restaurant = sortedList[rejectedRecommendations]
        return self.restaurant

    def rejected_recommendation(self, reason):
        rejectedRecommendations += 1
        # update user info
        response = get(user_root + self.user_id)
        user_preferences = response.json() 
        newDislikes = updater.update_bad({
            "preferences": {
                "likes": user_preferences["likes"],
                "dislikes": user_preferences["dislikes"],
                "never": user_preferences["never"],
            }, 
            "budget": {
                "max_price_point": user_preferences["price"],
                "meal_budget": user_preferences["meal_budget"]
            }
        }, self.restaurant, reason)

        response = put(user_root + self.user_id, json={"dislikes": newDislikes})
        return newDislikes
        
    def accepted_recommendation(self):
        # update restaurant precedence to be lower
        return True