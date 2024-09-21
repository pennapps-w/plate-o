import json
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3959  # Earth's radius in miles

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c
    return distance

def filter_businesses(input_file, output_file, center_lat, center_lon, max_distance):
    filtered_businesses = []
    
    with open(input_file, 'r') as f:
        for line in f:
            try:
                business = json.loads(line.strip())
                lat = business['latitude']
                lon = business['longitude']
                
                distance = haversine_distance(center_lat, center_lon, lat, lon)
                
                if distance <= max_distance:
                    filtered_businesses.append(business)
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {line.strip()}")

    with open(output_file, 'w') as f:
        for business in filtered_businesses:
            json.dump(business, f)
            f.write('\n')

    print(f"Filtered {len(filtered_businesses)} businesses within {max_distance} miles of UPenn")

# UPenn coordinates (approximate center of campus)
upenn_lat = 39.9522
upenn_lon = -75.1932

# Run the filter
filter_businesses('yelp_academic_dataset_business.json', 'penn_businesses.json', upenn_lat, upenn_lon, 50)