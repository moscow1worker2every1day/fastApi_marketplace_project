from fastapi import APIRouter
from app.dependencies.auth_user_dependency import SelfUserDep
from app.schemas.user import GetUser

router = APIRouter(prefix="/users/account")


@router.get("/my_account/", response_model=GetUser, tags=["User Account"])
async def get_user_account(current_user: SelfUserDep):
    return current_user
