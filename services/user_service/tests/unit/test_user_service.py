import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status
from tests.unit.fake_users import UserFactory
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from app.services.user_service import UserService
from app.schemas.user import UpdateUserName


@pytest.mark.asyncio
@pytest.mark.parametrize("id", [1, 2])
async def test_get_user_by_id_sucsess(mocker, fake_user, id):

    return_user = UserFactory(id = id)

    mocker.patch("app.storage.postgresql.repositories.user_repository.UserReposetory.get_user_by_id", return_value=return_user)

    user = await UserService.get_user_by_id(id, session=mocker.AsyncMock())
    assert user.id == id


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(mocker):
    mocker.patch("app.storage.postgresql.repositories.user_repository.UserReposetory.get_user_by_id", side_effect=NoResultFound)

    with pytest.raises(HTTPException) as excinfo:
        await UserService.get_user_by_id(999, session=mocker.AsyncMock())
    
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert "User id=999 not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_user_by_email_sucsess(mocker, fake_user):
    
    mocker.patch("app.storage.postgresql.repositories.user_repository.UserReposetory.get_user_by_email", return_value=fake_user)

    user = await UserService.get_user_by_email("test.com", session=mocker.AsyncMock())
    assert user.id == 1

@pytest.mark.asyncio
async def test_get_user_by_email_multiply(mocker):
   
    mocker.patch("app.storage.postgresql.repositories.user_repository.UserReposetory.get_user_by_email", side_effect=MultipleResultsFound)

    with pytest.raises(HTTPException) as excinfo:
        await UserService.get_user_by_email("test.com", session=mocker.AsyncMock())

    assert excinfo.value.status_code == status.HTTP_409_CONFLICT
    assert "Incorrect data" in excinfo.value.detail

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(mocker):
   
    mocker.patch("app.storage.postgresql.repositories.user_repository.UserReposetory.get_user_by_email", return_value=[])

    with pytest.raises(HTTPException) as excinfo:
        await UserService.get_user_by_email("test.com", session=mocker.AsyncMock())

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Could not find user with email 'test.com'" in excinfo.value.detail


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "first_name, last_name",
    [
        ("Anast", None),          # меняется только имя
        (None, "Ivanova"),        # меняется только фамилия
        ("Anast", "Ivanova"),     # меняются оба поля
    ]
)
async def test_update_user_first_name_sucsess(mocker, fake_user, first_name, last_name):

    updated_user = UserFactory(
        id=fake_user.id,
        first_name=first_name or fake_user.first_name,
        last_name=last_name or fake_user.last_name
    )

    mocker.patch("app.storage.postgresql.repositories.user_repository.UserReposetory.update_user_name", return_value=updated_user)

    update_data = UpdateUserName(
        id=1,
        first_name=first_name,
        last_name=last_name,
    )

    user = await UserService.update_user_name(data=update_data, session=mocker.AsyncMock())
    assert user.id == updated_user.id
    assert user.first_name == updated_user.first_name



