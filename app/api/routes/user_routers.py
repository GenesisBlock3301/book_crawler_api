from fastapi import APIRouter, HTTPException, status, Body
from fastapi.params import Depends

from app.db import users_collection
from app.utils import verify_admin_api_key, generate_api_key
from app.schemas import User, UserUpdate

users_router = APIRouter(dependencies=[Depends(verify_admin_api_key)])


@users_router.post("/", status_code=status.HTTP_200_OK)
async def create_api_key_for_user(username: str = Body(..., embed=True)):
    existing_user = await users_collection.find_one({"username": username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    api_key = generate_api_key()
    user = User(username=username, api_key=api_key)
    await users_collection.insert_one(user.model_dump(mode='json'))
    return {
        "message": "User & API key created successfully",
        "user": user.model_dump(mode='json')
    }


@users_router.get("/{username}", status_code=status.HTTP_200_OK)
async def get_user_by_username(username: str):
    user = await users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@users_router.put("/{username}", status_code=status.HTTP_200_OK)
async def update_user(username: str, user_update: UserUpdate):
    user = await users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for update")

    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    await users_collection.update_one(
        {"username": username},
        {"$set": update_data}
    )
    updated_user = await users_collection.find_one({"username": username})
    return {
        "message": "User updated successfully",
        "user": updated_user
    }


@users_router.delete("/{username}", status_code=status.HTTP_200_OK)
async def delete_user(username: str):
    result = await users_collection.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for deletion")
    return {"message": f"User '{username}' deleted successfully"}
