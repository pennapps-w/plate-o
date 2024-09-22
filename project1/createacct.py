import requests
import json
import logging

logger = logging.getLogger(__name__)


# Replace with your API key
API_KEY = "e6b7c879373f760ae3560779d5e8e7b3"
BASE_URL = "http://api.nessieisreal.com"
USER_URL = "https://blobotic-service1--8000.prod1.defang.dev/users"


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

        url2 = f"{BASE_URL}/customers/{customer_id}/accounts?key={API_KEY}"
        payload2 = {
            "type": "Checking",
            "nickname": "Primary Checking",
            "balance": 100
        }
        response = requests.post(url2, headers=headers, data=json.dumps(payload2))
        if response.status_code == 201:
            print("YAY ACCOUNT")
        else:
            print("NO ACCT")
    else:
        print(f"Failed to create customer. Status Code: {response.status_code}")
        print("Response JSON:", response.json())


def add_expenses(purchaseList):
    # response = requests.get(BASE_URL + f"/customers?key={API_KEY}")
    # logger.info(response.json())
    # customer = response.json()[0]
    # cid = customer["_id"]
    logger.info("HI")
    # response = requests.get(BASE_URL + f"/accounts?key={API_KEY}")
    # logger.info(response.text)
    # logger.info(type(response))
    # account = response.json()[0]
    aid = "66efaa9f9683f20dd518a80d" # account["_id"]
    logger.info(purchaseList)

    response = requests.get("https://blobotic-service1--8000.prod1.defang.dev/users/66ee6b3a7aa3130e68418c7d")
    users = response.json()
    # logger.info(response.text)
    # logger.info(type(response))
    # users = response.json()["users"][0]
    uid = users["id"]
    ubal = users["balance"]

    logger.info("Starting to get to purchase list")


    for i in purchaseList:
        response = requests.post(BASE_URL + "/accounts/" + aid + f"/purchases?key={API_KEY}", json={
            "merchant_id": "n/a",
            "medium": "balance",
            "purchase_date": "2024-09-22",
            "amount": i,
            "status": "pending",
            "description": "n/a"
        })

        ubal -= i["amount"]
    
    numMeals = min(ubal//20, 30)
    response = requests.put(USER_URL + uid, json={"balance": ubal, "meal_budget": (ubal//numMeals)})
        
def add_income(billList, incomeList):
    # response = requests.get(BASE_URL + f"/accounts?key={API_KEY}")
    # print("add_income", response.json())
    # customer = response.json()[0]
    aid = "66efaa9f9683f20dd518a80d" # customer["_id"]

    logger.info(billList, incomeList)

    response = requests.get("https://blobotic-service1--8000.prod1.defang.dev/users/66ee6b3a7aa3130e68418c7d")
    users = response.json()
    uid = users["id"]
    ubal = users["balance"]

    income = 0 

    logger.info("starting billilist")

    for i in billList:
        response = requests.post(BASE_URL + "/accounts/" + aid + "/bills", json={
            "status": "pending",
            "payee": "n/a",
            "nickname": "n/a",
            "payment_date": "2024-09-21",
            "recurring_date": 30
        })
        income -= i

    for i in incomeList:
        response = requests.post(BASE_URL + "/accounts/" + aid + "/deposits", json={
            "medium": "balance",
            "transaction_date": "2024-09-21",
            "status": "pending",
            "description": "n/a"
        })
        income += i
    
    if income <= 0:
        ubal += income 
    else:
        ubal += income * 0.2


    logger.info("retrning a response haha")
    numMeals = min(ubal//20, 30)    
    response = requests.put(USER_URL + uid, json={"balance": ubal, "meal_budget": (ubal//numMeals)})

    # sumDeposits = sum(i[""])

# def get_budget():
#     expenses = add_expenses() 
#     income = add_income()

#     response = requests.get(BASE_URL + "/accounts")
#     customer = response.json()[0]
#     # cid = customer["_id"]
#     # response = requests.get(BASE_URL + "/accounts/" + cid + "/bills")
#     # bills = response.json()
#     balance = customer["balance"]

#     bal = (balance + income - expenses) * 0.2

#     numMeals = min(bal//20, 7)

#     return (numMeals, round(bal/numMeals, 2))




# use financial info, use the 50-30-20 rule or the 60-20-20 rule to allow 20% of income to be used on food ordering

