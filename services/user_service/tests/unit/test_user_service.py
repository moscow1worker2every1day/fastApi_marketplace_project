import uuid

import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from app.schemas.user import UpdateUserName
from app.services.user_service import UserService
from tests.unit.fake_users import UserFactory

REPO = "app.services.user_service.UserRepository"


def _patch_repo_method(mocker, name, *, return_value=None, side_effect=None):
    """Патчит метод UserReposetory в user_service."""
    if side_effect is not None:
        return mocker.patch(f"{REPO}.{name}", new=AsyncMock(side_effect=side_effect))
    return mocker.patch(f"{REPO}.{name}", new=AsyncMock(return_value=return_value))


@pytest.mark.asyncio
@pytest.mark.parametrize("user_id", [uuid.uuid4(), uuid.uuid4()])
async def test_get_user_by_id_sucsess(mocker, user_id):
    return_user = UserFactory(id=user_id)
    mock_get = _patch_repo_method(mocker, "get_user_by_id", return_value=return_user)
    session = mocker.AsyncMock()

    user = await UserService.get_user_by_id(session=session, user_id=user_id)

    assert user.id == user_id
    mock_get.assert_called_once_with(session, user_id)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(mocker):
    missing_id = uuid.uuid4()
    _patch_repo_method(mocker, "get_user_by_id", side_effect=NoResultFound)
    session = mocker.AsyncMock()

    with pytest.raises(HTTPException) as excinfo:
        await UserService.get_user_by_id(session=session, user_id=missing_id)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert f"User id={missing_id} not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_user_by_email_sucsess(mocker, fake_user):
    mock_get = _patch_repo_method(
        mocker, "get_user_by_email", return_value=fake_user
    )
    session = mocker.AsyncMock()

    user = await UserService.get_user_by_email("test.com", session=session)

    assert user.id == fake_user.id
    mock_get.assert_called_once_with(user_email="test.com", session=session)


@pytest.mark.asyncio
async def test_get_user_by_email_multiply(mocker):
    _patch_repo_method(
        mocker, "get_user_by_email", side_effect=MultipleResultsFound
    )
    session = mocker.AsyncMock()

    with pytest.raises(HTTPException) as excinfo:
        await UserService.get_user_by_email("test.com", session=session)

    assert excinfo.value.status_code == status.HTTP_409_CONFLICT
    assert "Incorrect data" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(mocker):
    _patch_repo_method(mocker, "get_user_by_email", return_value=None)
    session = mocker.AsyncMock()

    with pytest.raises(HTTPException) as excinfo:
        await UserService.get_user_by_email("test.com", session=session)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Could not find user with email 'test.com'" in excinfo.value.detail


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "first_name, last_name",
    [
        ("Anast", None),
        (None, "Ivanova"),
        ("Anast", "Ivanova"),
    ],
)
async def test_update_user_first_name_sucsess(
    mocker, fake_user, first_name, last_name
):
    updated_user = UserFactory(
        first_name=first_name or fake_user.first_name,
        last_name=last_name or fake_user.last_name,
    )
    mock_update = _patch_repo_method(
        mocker, "update_user_name", return_value=updated_user
    )
    session = mocker.AsyncMock()
    update_data = UpdateUserName(
        first_name=first_name,
        last_name=last_name,
    )

    user = await UserService.update_user_name(user_id=fake_user.id, data=update_data, session=session)

    assert user.id == updated_user.id
    assert user.first_name == updated_user.first_name
    mock_update.assert_called_once_with(
        user_id=fake_user.id,
        session=session,
        first_name=first_name,
        last_name=last_name,
    )
