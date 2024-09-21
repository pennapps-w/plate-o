from fastapi import FastAPI, HTTPException, status, Body
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional, List
from typing_extensions import Annotated
from bson import ObjectId
from pymongo import ReturnDocument


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
    price: str = None

    price: int = None
    meal_budget: float = None


class UpdateUser(BaseModel):
    name: Optional[str] = None
    restaurants: Optional[list[object]] = None
    likes: Optional[str] = None
    dislikes: Optional[str] = None
    never: Optional[str] = None
    price: int = None
    meal_budget: float = None
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


# @app.put(
#     "/update_user_preferences/{id}",
#     response_description="Update user preferences",
#     response_model=User,
#     response_model_by_alias=False,
# )
# async def update_user_preferences(
#     id: str,
#     likes: Optional[str] = None,
#     dislikes: Optional[str] = None,
#     never: Optional[str] = None,
# ):
#     update_data = {}
#     if likes is not None:
#         update_data["likes"] = likes
#     if dislikes is not None:
#         update_data["dislikes"] = dislikes
#     if never is not None:
#         update_data["never"] = never

#     if update_data:
#         update_result = await collection.find_one_and_update(
#             {"_id": ObjectId(id)},
#             {"$set": update_data},
#             return_document=ReturnDocument.AFTER,
#         )
#         if update_result is not None:
#             return update_result
#         else:
#             raise HTTPException(status_code=404, detail=f"User {id} not found")

#     raise HTTPException(status_code=400, detail="No update data provided")
