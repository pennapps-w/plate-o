import requests
import json

# Replace with your API key
API_KEY = "e6b7c879373f760ae3560779d5e8e7b3"
BASE_URL = "http://api.nessieisreal.com"
USER_URL = "https://blobotic-service1--8000.prod1.defang.dev/users/"


def create_acct(**kwargs):
    # Endpoint for creating a customer
    url = f"{BASE_URL}/customers?key={API_KEY}"

    # Payload for creating a customer
    payload = {
        "first_name": kwargs["First"],
        "last_name": kwargs["Last"],
        "address": kwargs["Address"]
    }

    # Headers
    headers = {
        "Content-Type": "application/json"
    }

    # Make the POST request to create the customer
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check the response
    if response.status_code == 201:
        print("Customer created successfully!")
        customer_data = response.json()
        customer_id = customer_data["objectCreated"]["_id"]
        print("Customer ID:", customer_id)
    else:
        print(f"Failed to create customer. Status Code: {response.status_code}")
        print("Response JSON:", response.json())

def add_expenses(billList, purchaseList):
    response = requests.get(BASE_URL + "/customers")
    customer = response.json()[0]
    cid = customer["_id"]

    response = requests.get(BASE_URL + "/accounts")
    account = response.json()[0]
    aid = account["_id"]

    response = requests.get(USER_URL)
    users = response.json()[0]
    uid = users["id"]
    ubal = users["balance"]

    for i in billList:
        response = requests.post(BASE_URL + "/accounts/" + aid + "/bills", json={
            "status": "pending",
            "payee": i["payee"],
            "nickname": i["nickname"],
            "payment_date": "2024-09-21",
            "recurring_date": 30
        })
    
    for i in purchaseList:
        response = requests.post(BASE_URL + "/accounts/" + aid + "/purchases", json={
            "merchant_id": i["merchant_id"],
            "medium": "balance",
            "purchase_date": i["purchase_date"],
            "amount": i["amount"],
            "status": "pending",
            "description": i["description"]
        })

        ubal -= i["amount"]
    
    numMeals = min(ubal//20, 7)
    response = requests.put(USER_URL + uid, json={"balance": ubal, "meal_budget": (ubal//numMeals)})
        

    # response = requests.get(BASE_URL + "/customers/" + cid + "/bills")
    # bills = response.json()

    # sumBills = sum(i["amount"])

    # response = requests.get(BASE_URL + "/accounts/" + aid + "/purchases")
    # purchases = response.json()

    # sumPurchases = sum(i["amount"] for i in purchases)

    # return sumPurchases

def add_income():
    response = requests.get(BASE_URL + "/accounts")
    customer = response.json()[0]
    cid = customer["_id"]
    response = requests.get(BASE_URL + "/accounts/" + cid + "/deposits")
    deposits = response.json()    

    # sumDeposits = sum(i[""])
    return 0

def get_budget():
    expenses = add_expenses() 
    income = add_income()

    response = requests.get(BASE_URL + "/accounts")
    customer = response.json()[0]
    # cid = customer["_id"]
    # response = requests.get(BASE_URL + "/accounts/" + cid + "/bills")
    # bills = response.json()
    balance = customer["balance"]

    bal = (balance + income - expenses) * 0.2

    numMeals = min(bal//20, 7)

    return (numMeals, round(bal/numMeals, 2))




# use financial info, use the 50-30-20 rule or the 60-20-20 rule to allow 20% of income to be used on food ordering

