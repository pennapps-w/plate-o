from requests import get, post, put, delete, HTTPError
from algo import RestaurantScorer

user_root = "https://blobotic-service1--8000.prod1.defang.dev/users/"
# restaurant_root = "https://blobotic-service1--8000.prod1.defang.dev/restaurants/"
restaurant_root = "http://127.0.0.1:8000/restaurants"
api_key = 'sk-tune-31SubFSL3vCE9hMxp9AJWzqh9MzWfUNcCNs'
scorer = None 
rejectedRecommendations = 3
sortedList = None

def getRestaurantData(n):
    return n["data"]

def get_restaurants(price_range):
    all_restaurants = get(restaurant_root)
    tmp2 = all_restaurants.json()["restaurants"]
    tmp3 = list(map(getRestaurantData, tmp2))

    tmp = len(price_range)

    return filter(lambda x: len(x) <= tmp, tmp3)


get_restaurants("$")

def restaurantsToScore(n):
    n["final_score"] = scorer.calculate_final_score(n)
    return n

# function to be called when we need to get a recommendation
def get_recommendation(user_id):
    response = get(user_root + user_id)
    # if we want to test for if the api returns correctly, need try/except
    # response.raise_for_status() 
    user_preferences = response.json()
    price_range_restaurants = get_restaurants(user_preferences["price"])

    if rejectedRecommendations >= 3:
        scorer = RestaurantScorer(user_preferences, api_key)
        rejectedRecommendations = 0
    
        restaurants_scored = list(map(restaurantsToScore, price_range_restaurants))
    
        sortedList = sorted(restaurants_scored, key=lambda d: d["final_score"], reverse=True)
    
    return sortedList[rejectedRecommendations]

def rejected_recommendation(user_id):
    rejectedRecommendations += 1
    # update user info
    
