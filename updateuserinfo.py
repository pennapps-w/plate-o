

class Updater:
    def __init__(self, user_data : str = None):
        if user_data:
            self.user_data = user_data
        else:
            self.user_data = {
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