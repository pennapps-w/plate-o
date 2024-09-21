from requests import get, post, put, delete, HTTPError

def test_api():
    """
    An automated version of the manual testing I've been doing,
    testing the lifecycle of an inserted document.
    """
    user_root = "http://127.0.0.1:8000/users/"

    initial_doc = {
        "name": "Bob Joe",
        "restaurants": [
            {
            "Rating": 10,
            "Name": "Kujira",
            "id": 1,
            "Review": "I LOVE all you can eat sushi!! Would come again 10/10."
            }
        ],
        "likes": "asian food",
        "dislikes": "tasteless food",
        "never": "nuts",
        "price point": 1,
        "max_budget": 15.0
    }

    try:
        # Insert a user
        print("HIIII")
        response = post(user_root, json=initial_doc)
        response.raise_for_status()
        doc = response.json()
        print(doc)
        inserted_id = doc["id"]
        print(inserted_id)
        print(f"Inserted document with id: {inserted_id}")
        print(
            "If the test fails in the middle you may want to manually remove the document."
        )
        assert doc["name"] == "Bob Joe"
        assert doc["likes"] == "asian food"
        assert doc["dislikes"] == "tasteless food"
        assert doc["never"] == "nuts"

        # List users and ensure it's present
        response = get(user_root)
        response.raise_for_status()
        user_ids = {s["id"] for s in response.json()["users"]}
        assert inserted_id in user_ids

        # Get individual user doc
        response = get(user_root + inserted_id)
        print(response.json())
        response.raise_for_status()
        doc = response.json()
        assert doc["id"] == inserted_id
        assert doc["name"] == "Bob Joe"
        assert doc["likes"] == "asian food"
        assert doc["dislikes"] == "tasteless food"
        assert doc["never"] == "nuts"

        # Update the user doc
        response = put(
            user_root + inserted_id,
            json={
                "likes": "ALL FOOD",
            },
        )
        response.raise_for_status()
        doc = response.json()
        assert doc["id"] == inserted_id
        assert doc["name"] == "Bob Joe"
        assert doc["likes"] == "ALL FOOD"
        assert doc["dislikes"] == "tasteless food"
        assert doc["never"] == "nuts"

        # Get the user doc and check for change
        response = get(user_root + inserted_id)
        response.raise_for_status()
        doc = response.json()
        assert doc["id"] == inserted_id
        assert doc["name"] == "Bob Joe"
        assert doc["likes"] == "ALL FOOD"
        assert doc["dislikes"] == "tasteless food"
        assert doc["never"] == "nuts"

        # Delete the doc
        # response = delete(user_root + inserted_id)
        # response.raise_for_status()

        # Get the doc and ensure it's been deleted
        # response = get(user_root + inserted_id)
        # assert response.status_code == 404
    except HTTPError as he:
        print(he.response.json())
        raise

test_api()