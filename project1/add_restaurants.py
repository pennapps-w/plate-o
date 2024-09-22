from requests import get, post, put, delete, HTTPError
import json 


jd = None 

with open("merged_restaurant_data.json") as f:
    jd = json.load(f)



def test_api():
    """
    An automated version of the manual testing I've been doing,
    testing the lifecycle of an inserted document.
    """
    user_root = "https://blobotic-service1--8000.prod1.defang.dev/restaurants/"

    try:
        # Insert a user
        print(len(jd))
        for i in jd:
            print(i)
            response = post(user_root, json={"data": i})
            response.raise_for_status()
            doc = response.json()
            print(doc)
            inserted_id = doc["id"]
            print(inserted_id)
            print(f"Inserted document with id: {inserted_id}")
            print(
                "If the test fails in the middle you may want to manually remove the document."
            )

            # List users and ensure it's present
            # response = get(user_root)
            # response.raise_for_status()
            # user_ids = {s["id"] for s in response.json()["users"]}


        
    except HTTPError as he:
        print(he.response.json())
        raise

test_api()