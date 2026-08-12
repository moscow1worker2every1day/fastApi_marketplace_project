import uuid

from app.constants import DEFAULT_USERS_LIMIT, DEFAULT_USERS_OFFSET, MAX_USERS_LIMIT
from app.dependencies.auth_user_dependency import AdminUserDep, SelfOrAdminUserDep, TargetUserDep
from app.schemas.user import GetUser, ResponseMessage, UpdateUserEmail, UpdateUserName
from app.storage.postgresql.connection import SessionDep
from fastapi import APIRouter, Query
from app.services.user_service import UserService
from app.enums import SortOrder, UserRoles, UserSortField


router = APIRouter(prefix="/users")


@router.get("/{user_id}", response_model=GetUser, tags=["CRUD"])
async def get_user(
    session: SessionDep,
    current_user: SelfOrAdminUserDep,
    target_user: TargetUserDep,
):
    """Get user by id"""
    return await UserService.get_user_by_id(session=session, user_id=target_user.id)


@router.get("/", response_model=list[GetUser], tags=["CRUD"])
async def get_all_users(
    session: SessionDep,
    current_user: AdminUserDep,
    limit: int = Query(
        default=DEFAULT_USERS_LIMIT,
        ge=1,
        le=MAX_USERS_LIMIT,
        description="Page size",
    ),
    offset: int = Query(
        default=DEFAULT_USERS_OFFSET,
        ge=0,
        description="Number of users to skip",
    ),
    user_role: UserRoles = Query(
        default=UserRoles.user,
        description="Role of users to get",
    ),
    sort_by: UserSortField = Query(
        default=UserSortField.created_at,
        description="Field to sort by",
    ),
    sort_order: SortOrder = Query(
        default=SortOrder.asc,
        description="Sort direction",
    ),
):
    """Get all users with role 'user'"""
    return await UserService.get_all_users(
        session=session,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
        user_role=user_role,
    )


@router.delete("/{user_id}", response_model=ResponseMessage, tags=["CRUD"])
async def delete_user(
    target_user: TargetUserDep,
    session: SessionDep,
    current_user: SelfOrAdminUserDep,
):
    return await UserService.delete_user(user_id=target_user.id, session=session)


@router.put("/{user_id}/name", response_model=GetUser, tags=["CRUD"])
async def update_user_name(
    target_user: TargetUserDep,
    data: UpdateUserName,
    session: SessionDep,
    current_user: SelfOrAdminUserDep,
):
    return await UserService.update_user_name(user_id=target_user.id, data=data, session=session)


@router.put("/{user_id}/email", response_model=GetUser, tags=["CRUD"])
async def update_user_email(
    target_user: TargetUserDep,
    data: UpdateUserEmail,
    session: SessionDep,
    current_user: SelfOrAdminUserDep,
):
    return await UserService.update_user_email(user_id=target_user.id, data=data, session=session)
