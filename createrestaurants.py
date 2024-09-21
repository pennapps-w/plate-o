import json
import pandas as pd
import random
from fuzzywuzzy import fuzz
from tqdm import tqdm
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def load_jsonl(file_path):
    with open(file_path, 'r') as f:
        return [json.loads(line) for line in f]

print("Loading data...")
businesses = load_jsonl('penn_businesses.json')
print(f"Loaded {len(businesses)} businesses")

reviews = load_jsonl('penn_reviews.json')
print(f"Loaded {len(reviews)} reviews")

restaurants_df = pd.read_csv('restaurants.csv')
print(f"Loaded {len(restaurants_df)} restaurants from Uber Eats data")

menus_df = pd.read_csv('restaurant-menus.csv')
print(f"Loaded {len(menus_df)} menu items")

def preprocess_name(name):
    # Remove non-alphanumeric characters and convert to lowercase
    return re.sub(r'[^a-zA-Z0-9\s]', '', str(name).lower())

print("Preprocessing data...")
businesses_df = pd.DataFrame(businesses)
businesses_df['processed_name'] = businesses_df['name'].apply(preprocess_name)
restaurants_df['processed_name'] = restaurants_df['name'].apply(preprocess_name)

print("Creating TF-IDF vectors...")
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
business_vectors = vectorizer.fit_transform(businesses_df['processed_name'])
restaurant_vectors = vectorizer.transform(restaurants_df['processed_name'])

def find_potential_matches(business_vector, restaurant_vectors, top_n=100):
    similarities = cosine_similarity(business_vector, restaurant_vectors)
    top_indices = np.argsort(similarities[0])[-top_n:][::-1]
    return top_indices

def find_best_match(business, candidates):
    best_match = None
    best_score = 0
    business_name = preprocess_name(business['name'])
    
    for _, candidate in candidates.iterrows():
        name_score = fuzz.ratio(business_name, candidate['processed_name'])
        address_score = fuzz.ratio(business.get('address', '').lower(), str(candidate['full_address']).lower())
        total_score = (name_score + address_score) / 2
        if total_score > best_score:
            best_score = total_score
            best_match = candidate
    
    return best_match if best_score > 70 else None

print("Matching businesses to Uber Eats restaurants...")
matched_data = []

for i, business in enumerate(tqdm(businesses)):
    potential_matches_indices = find_potential_matches(business_vectors[i], restaurant_vectors)
    potential_matches = restaurants_df.iloc[potential_matches_indices]
    match = find_best_match(business, potential_matches)
    
    if match is not None:
        business_reviews = [r for r in reviews if r['business_id'] == business['business_id']]
        random_reviews = random.sample(business_reviews, min(3, len(business_reviews)))
        menu_items = menus_df[menus_df['restaurant_id'] == match['id']]
        
        matched_data.append({
            'uber_eats_id': match['id'],
            'name': business['name'],
            'address': business.get('address', ''),
            'description': business.get('categories', ''),
            'price_point': match['price_range'],
            'reviews': [{'text': r['text'], 'rating': r['stars']} for r in random_reviews],
            'menu': menu_items.to_dict('records')
        })

print("Saving merged data...")
with open('merged_restaurant_data.json', 'w') as f:
    json.dump(matched_data, f, indent=2)

print(f"Merged data saved. Total matched restaurants: {len(matched_data)}")

if matched_data:
    print("\nSample of merged data:")
    print(json.dumps(matched_data[0], indent=2))
else:
    print("No matches found. Please check your data and matching criteria.")