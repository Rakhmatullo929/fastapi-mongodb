from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

app = FastAPI()

# Подключение к MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["my_database"]

# Коллекции
users_collection = db["users"]
products_collection = db["products"]
orders_collection = db["orders"]

# MongoDB ObjectId -> str


def to_dict(data):
    data["_id"] = str(data["_id"])
    return data

# Модели данных


class User(BaseModel):
    name: str
    email: str
    phone: str
    address: dict
    created_at: Optional[str] = None


class Product(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int


class Order(BaseModel):
    user_id: str
    products: List[dict]
    total_price: float
    status: str
    created_at: Optional[str] = None

# ---- USERS ----


@app.post("/users/", response_model=dict)
async def create_user(user: User):
    user = user.dict()
    result = await users_collection.insert_one(user)
    return {"id": str(result.inserted_id)}


@app.get("/users/", response_model=List[dict])
async def get_users():
    users = await users_collection.find().to_list(100)
    return [to_dict(user) for user in users]


@app.get("/users/{user_id}", response_model=dict)
async def get_user(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return to_dict(user)


@app.put("/users/{user_id}", response_model=dict)
async def update_user(user_id: str, user: User):
    user = user.dict()
    result = await users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": user})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated"}


@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

# ---- PRODUCTS ----


@app.post("/products/", response_model=dict)
async def create_product(product: Product):
    product = product.dict()
    result = await products_collection.insert_one(product)
    return {"id": str(result.inserted_id)}


@app.get("/products/", response_model=List[dict])
async def get_products():
    products = await products_collection.find().to_list(100)
    return [to_dict(product) for product in products]


@app.put("/products/{product_id}", response_model=dict)
async def update_product(product_id: str, product: Product):
    product = product.dict()
    result = await products_collection.update_one({"_id": ObjectId(product_id)}, {"$set": product})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated"}

# ---- ORDERS ----


@app.post("/orders/", response_model=dict)
async def create_order(order: Order):
    order = order.dict()
    result = await orders_collection.insert_one(order)
    return {"id": str(result.inserted_id)}


@app.get("/orders/", response_model=List[dict])
async def get_orders():
    orders = await orders_collection.find().to_list(100)
    return [to_dict(order) for order in orders]


@app.delete("/orders/{order_id}", response_model=dict)
async def delete_order(order_id: str):
    result = await orders_collection.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted"}
