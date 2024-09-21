import json

def load_business_ids(business_file):
    business_ids = set()
    with open(business_file, 'r') as f:
        for line in f:
            business = json.loads(line.strip())
            business_ids.add(business['business_id'])
    return business_ids

def filter_reviews(review_file, output_file, business_ids):
    filtered_reviews = 0
    with open(review_file, 'r') as input_f, open(output_file, 'w') as output_f:
        for line in input_f:
            review = json.loads(line.strip())
            if review['business_id'] in business_ids:
                json.dump(review, output_f)
                output_f.write('\n')
                filtered_reviews += 1
                
                # Optional: Print out the first few filtered reviews
                if filtered_reviews <= 3:
                    print(f"Sample filtered review {filtered_reviews}:")
                    print(json.dumps(review, indent=2))
                    print()

    print(f"Total filtered reviews: {filtered_reviews}")

# File paths
business_file = 'penn_businesses.json'  # The filtered business file from the previous script
review_file = 'yelp_academic_dataset_review.json'  # Your input review file
output_file = 'penn_reviews.json'  # The output file for filtered reviews

# Load business IDs
business_ids = load_business_ids(business_file)
print(f"Loaded {len(business_ids)} unique business IDs")

# Filter reviews
filter_reviews(review_file, output_file, business_ids)

# Optional: Validate the output
print("\nValidating output file:")
with open(output_file, 'r') as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line)
        except json.JSONDecodeError:
            print(f"Error in line {i}")
        if i == 1:
            print("First line is valid JSON")
        if i == 100:
            print("First 100 lines are valid JSON")
            break
    else:
        print(f"All {i} lines are valid JSON")