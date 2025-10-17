from fastapi import APIRouter, HTTPException, status, Body
from fastapi.params import Depends
from bson import ObjectId

from app.utils import verify_admin_api_key, generate_api_key
from app.schemas import User, UserUpdate
from app.api.deps import get_user_service
from app.services import UserService

users_router = APIRouter(dependencies=[Depends(verify_admin_api_key)])


def serialize_user(user: User) -> User:
    user = user.model_copy()  # avoid mutating the original
    if "_id" in user and isinstance(user["_id"], ObjectId):
        user["_id"] = str(user["_id"])
    return user


@users_router.post("/", status_code=status.HTTP_200_OK)
async def create_api_key_for_user(
        service: UserService = Depends(get_user_service),
        username: str = Body(..., embed=True)
):
    existing_user = await service.get_user_by_username(username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    api_key = generate_api_key()
    user = User(username=username, api_key=api_key)
    await service.create_user(user)
    return {
        "message": "User & API key created successfully",
        "user": user.model_dump(mode='json')
    }


@users_router.get("/{username}", status_code=status.HTTP_200_OK)
async def get_user_by_username(
        username: str,
        service: UserService = Depends(get_user_service),
):
    user = await service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = User(**user)
    return user.model_dump(mode='json')


@users_router.put("/{username}", status_code=status.HTTP_200_OK)
async def update_user(
        username: str,
        user_update: UserUpdate,
        service: UserService = Depends(get_user_service),
):
    user = await service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for update")
    api_key = generate_api_key()
    update_data = user_update.model_dump(exclude_unset=True)
    update_data.pop('username', None)
    update_data["api_key"] = api_key
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    await service.update_user(username, update_data)
    updated_user = await service.get_user_by_username(username)
    return {
        "message": "User updated successfully",
        "user": serialize_user(updated_user)
    }


@users_router.delete("/{username}", status_code=status.HTTP_200_OK)
async def delete_user(
        username: str,
        service: UserService = Depends(get_user_service),
):
    result = await service.delete_user(username)
    if result == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for deletion")
    return {"message": f"User '{username}' deleted successfully"}
