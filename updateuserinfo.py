import requests
import json

class Updater:
    def __init__(self, api_key):
        self.api_key = api_key
    def update_bad(self, user_data, restaurant_data, reason):
        prompt = f"""
        Given the information about the user and the restaurant, print out a new dislikes string for the user. The user's previous dislikes should be a subset of this new string. You do not necessarily need to add anything, for example if the user's reason is "I don't feel like it today". However, if they cite some specific dislike in their reason, add that to the dislikes string.
        
        Here are some examples:
        
        Example 1

        The user does not want the following restaurant: Rowdy BBQ. This restaurant is rated 4.4 stars by Yelp and Uber Eats.
        This restaurant has the following descriptors: "BBQ, American, Grilled Meat, Casual Dining". 

        The user's current dislikes is the following string: "spicy food, greasy dishes".
        The user's reason for not picking the current restaurant is this: "I don't like how smoky the flavors are and it's too heavy for dinner." 

        Updated dislike string:
        spicy food, greasy dishes, smoky flavors, heavy meals

        Example 2

        The user does not want the following restaurant: El Taco. This restaurant is rated 4.5 stars by Yelp and Uber Eats.
        This restaurant has the following descriptors: "Mexican, Tacos, Street Food".

        The user's current dislikes is the following string: "spicy food".
        The user's reason for not picking the current restaurant is this: "I just had tacos yesterday, and I want something different today." 

        Updated dislike string:
        spicy food
        
        Example 3

        The user does not want the following restaurant: By George. This restaurant is rated 3.9 stars by Yelp and Uber Eats.
        This restaurant has the following descriptors: "Italian, Pizza".

        The user's current dislikes is the following string: "ice cream".
        The user's reason for not picking the current restaurant is this: "I'm avoiding cheese because of my lactose intolerance." 

        Updated dislike string:
        ice cream, dairy products

        Now here is the relevant information:

        The user does not want the following restaurant: \"{restaurant_data['name']}\". This restaurant is rated {str(restaurant_data['score'])} stars by Yelp and Uber Eats.
        This restaurant has the following descriptors: \"{restaurant_data['description']}\". 

        The user's current dislikes is the following string: \"{user_data['preferences']['dislikes']}\".
        The user's reason for not picking the current restaurant is this: \"{reason}\".

        Updated dislike string:

        """
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        data = {
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": "You are an AI assistant that needs to update the string that tracks the user's dislikes. You will be given their current dislikes, as well as a restaurant and the restaurant description and the user's stated reason for disliking the restaurant. You will then return just the user's dislikes. Do not print any thinking. Your response will become the user's new dislikes string. "},
                {"role": "user", "content": prompt}
            ],
            "model": "meta/llama-3.1-405b-instruct",
            "stream": False,
            "max_tokens": 150
        }

        try:
            response = requests.post("https://proxy.tune.app/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            llm_output = response.json()['choices'][0]['message']['content']
            print(llm_output.strip())
            return llm_output.strip()
        except Exception as e:
            print(f"Error in LLM call: {e}")
            return user_data['preferences']['dislikes']


    def update_good(self, user_data, restaurant_data):
        # Extract current likes and restaurant descriptors
        current_likes = user_data['preferences']['likes']
        restaurant_descriptors = restaurant_data['description'].lower().split(', ')
        
        # Convert current likes into a set for easy checking
        current_likes_set = set(current_likes.split(', ')) if current_likes else set()

        # Add any new descriptor from the restaurant that isn't already in the current likes
        new_likes = current_likes_set.union(restaurant_descriptors)
        
        # Return the updated likes as a string, sorted for consistency
        updated_likes = ', '.join(sorted(new_likes))
        
        return updated_likes
    

# myupdater = Updater('API KEY')
# user_data['preferences']['dislikes'] = myupdater.update_bad({
#     'preferences': {
#         'likes': 'spicy food',
#         'dislikes': 'overly greasy food',
#         'bans': 'peanuts, shellfish'
#     },
#     'budget': {
#         'max_price_point': 2,
#         'meal_budget': 15.00
#     }
# }, {
#     'name': 'New Restaurant',
#     'description': 'Fusion Asian cuisine with a focus on spicy dishes and vegetarian options',
#     'menu': ['Spicy tofu stir-fry, Vegetable tempura, Mango sticky rice'],
#     'reviews': ['Best food ever!', 'Only go if you are ok with sticky chairs.', 'Creative fusion cuisine'],
#     'price point': '$',
#     'score': 5
# }, 'I don\'t like tofu')