from fastapi import FastAPI, HTTPException, status, Body
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional, List
from typing_extensions import Annotated
from bson import ObjectId
from pymongo import ReturnDocument
from recommender import Recommender
import tracemalloc
import logging

logger = logging.getLogger(__name__)


tracemalloc.start()

from updateuserinfo import update_bad

api_key = "sk-tune-31SubFSL3vCE9hMxp9AJWzqh9MzWfUNcCNs"

import asyncio

app = FastAPI(title="Food API", summary="stores users preference data for restaurants")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# MongoDB connection
# MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_URI = "mongodb+srv://Cluster90742:YnlhQVJ3W21X@cluster90742.xshuc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster90742"
client = AsyncIOMotorClient(MONGODB_URI)
db = client.plato
collection = db.plato_users
rest_collection = db.plato_restaurants


# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


# user stuff


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = None
    restaurants: list[object] = []
    likes: str = None
    dislikes: str = None
    never: str = None
    price: int = None
    meal_budget: float = None
    balance: float = None
    rejected_recommendations: list[str] = []


class UpdateUser(BaseModel):
    name: Optional[str] = None
    restaurants: Optional[list[object]] = None
    likes: Optional[str] = None
    dislikes: Optional[str] = None
    never: Optional[str] = None
    price: Optional[int] = None
    meal_budget: Optional[float] = None
    balance: Optional[float] = None
    rejected_recommendations: Optional[list[str]] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True, json_encoders={ObjectId: str}
    )


class UserCollection(BaseModel):
    users: List[User]


@app.post(
    "/users/",
    response_description="Add new user",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_user(user: User = Body(...)):
    new_user = await collection.insert_one(
        user.model_dump(by_alias=True, exclude=["id"])
    )
    created_user = await collection.find_one({"_id": new_user.inserted_id})
    return created_user
    # result = await collection.insert_one(user.dict())
    # if result.inserted_id:
    #     return user
    # raise HTTPException(status_code=400, detail="Item could not be created")


@app.get(
    "/users/",
    response_description="List all users",
    response_model=UserCollection,
    response_model_by_alias=False,
)
async def list_users():
    return UserCollection(users=await collection.find().to_list(1000))


@app.get(
    "/users/{id}",
    response_description="Get a single user",
    response_model=User,
    response_model_by_alias=False,
)
async def read_user(id: str):
    # print(user_id)
    # user = await collection.find_one({"_id": user_id})
    # if user:
    #     return User(**user)
    # raise HTTPException(status_code=404, detail=f"user {user_id} not found")
    if (user := await collection.find_one({"_id": ObjectId(id)})) is not None:
        return user

    raise HTTPException(status_code=404, detail=f"user {id} not found")


@app.put(
    "/users/{id}",
    response_description="Update a user",
    response_model=User,
    response_model_by_alias=False,
)
async def update_user(id: str, user: UpdateUser = Body(...)):
    print("updating user.....")
    user = {k: v for k, v in user.model_dump(by_alias=True).items() if v is not None}

    if len(user) >= 1:
        update_result = await collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": user},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"User {id} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_user := await collection.find_one({"_id": id})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {id} not found")


@app.delete("/users/{id}", response_description="Delete a user")
async def delete_user(id: str):
    delete_result = await collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"user {id} not found")


# restaurant stuff


class Restaurant(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    data: object = None


class RestaurantCollection(BaseModel):
    restaurants: List[Restaurant]


@app.post(
    "/restaurants/",
    response_description="Add new restaurant",
    response_model=Restaurant,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_restaurant(restaurant: Restaurant = Body(...)):
    new_restaurant = await rest_collection.insert_one(
        restaurant.model_dump(by_alias=True, exclude=["id"])
    )
    created_restaurant = await rest_collection.find_one(
        {"_id": new_restaurant.inserted_id}
    )
    return created_restaurant


@app.get(
    "/restaurants/",
    response_description="List all users",
    response_model=RestaurantCollection,
    response_model_by_alias=False,
)
async def list_restaurants():
    return RestaurantCollection(restaurants=await rest_collection.find().to_list(1000))


@app.get(
    "/get_recommendation/{id}", response_description="Get a restaurant recommendation"
)
async def get_recommendation(id: str):
    logger.info("STARTING TO GET RECOMMENDATION")
    recommender = Recommender(id)
    logger.info("STARTING TO GET RECOMMENDATION")
    recommendation = await recommender.get_recommendation()
    if recommendation:
        return {"recommendation": recommendation, "recommender": recommender}
    raise HTTPException(status_code=404, detail="No recommendation found")
    return recommendation
    raise HTTPException(status_code=404, detagitil="No recommendation found")


class DislikeEntry(BaseModel):
    id: str = None 
    reason: str = None 
    restaurant_id: str = None

@app.post("/dislike_because/{id}", response_description="Reject a recommendation")
# async def dislike_because(id: str, reason: str, restaurant_id: str):
async def dislike_because(id: str, stuff : DislikeEntry = Body(...)):
    # Fetch the user
    logger.info("dsilike_because")
    stuff2 = stuff.model_dump()
    logger.info(stuff2)
    id = stuff2["id"]
    reason = stuff2["reason"]
    restaurant_id = stuff2["restaurant_id"]

    logger.info(id,reason,restaurant_id)
    logger.info("ILOVEDISLIKE_BECAUSE")

    # logger.info("starting dislike_because")
    user = await collection.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # logger.info(f"User: {user}")
    # Update dislikes
    current_dislikes = user.get("dislikes", [])
    # current_dislikes += reason

    restaurant_data = await rest_collection.find_one({"_id": ObjectId(restaurant_id)})
    # WAIT FOR IT TO FINISH:
    # logger.info("Waiting for restaurant data")
    while restaurant_data is None:
        # logger.info("Waiting for restaurant data....")
        await asyncio.sleep(1)  # Wait for 100ms before checking again
    logger.info("RESTUARANT: DATA:")
    logger.info(restaurant_data)

    # logger.info("Starting update_bad 2222")
    current_dislikes = update_bad(
        api_key, current_dislikes, restaurant_data["data"], reason
    )
    logger.info(f"Current dislikes: {current_dislikes}, blah blah blah")

    # Update rejected_recommendations
    logger.info("updating rejected recommendations")
    rejected_recommendations = user.get("rejected_recommendations", [])
    logger.info("user gotten")
    rejected_recommendations.append(restaurant_id)
    logger.info("appended")
    # logger.info(f"Rejected recommendations: {rejected_recommendations}")
    # logger.info(f"Restaurant ID: {restaurant_id}")
    # Update the user in the database
    logger.info("haven't started updating result")
    update_result = await collection.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "dislikes": current_dislikes,
                "rejected_recommendations": rejected_recommendations,
            }
        },
    )

    logger.info("updated result")

    return update_result

@app.options("/dislike_because/{id}")
async def preflight_dislike_because(id: str):
    # Return appropriate CORS headers for the preflight request
    return JSONResponse(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "*",
        },
    )

    # if update_result.modified_count == 0:
    #     raise HTTPException(status_code=400, detail="Failed to update user preferences")

    # recommender = Recommender(id)
    # result = await recommender.rejected_recommendation(reason)

    # if result:
    # return {
    #     "message": "Recommendation rejected successfully",
    #     "new_dislikes": current_dislikes,
    #     "rejected_recommendations": rejected_recommendations,
    # }
    # return result
    # raise HTTPException(status_code=404, detail="Failed to reject recommendation")
