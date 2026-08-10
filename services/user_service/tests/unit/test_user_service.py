import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from app.schemas.user import UpdateUserName
from app.services.user_service import UserService
from tests.unit.fake_users import UserFactory


def _make_service(mocker, **mock_returns):
    """Создаёт UserService с мок-репозиторием. mock_returns: имя_метода=return_value."""
    repo = mocker.MagicMock()
    for name, value in mock_returns.items():
        repo.attach_mock(mocker.AsyncMock(return_value=value), name)
    return UserService(repository=repo)


@pytest.mark.asyncio
@pytest.mark.parametrize("id", [1, 2])
async def test_get_user_by_id_sucsess(mocker, fake_user, id):
    return_user = UserFactory(id=id)
    service = _make_service(mocker, get_user_by_id=return_user)
    session = mocker.AsyncMock()

    user = await service.get_user_by_id(id, session=session)

    assert user.id == id
    service._repository.get_user_by_id.assert_called_once_with(id, session)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(mocker):
    service = _make_service(mocker)
    session = mocker.AsyncMock()
    service._repository.get_user_by_id = mocker.AsyncMock(side_effect=NoResultFound)

    with pytest.raises(HTTPException) as excinfo:
        await service.get_user_by_id(999, session=session)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert "User id=999 not found" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_user_by_email_sucsess(mocker, fake_user):
    service = _make_service(mocker, get_user_by_email=fake_user)
    session = mocker.AsyncMock()

    user = await service.get_user_by_email("test.com", session=session)

    assert user.id == 1
    service._repository.get_user_by_email.assert_called_once_with(
        user_email="test.com", session=session
    )


@pytest.mark.asyncio
async def test_get_user_by_email_multiply(mocker):
    service = _make_service(mocker)
    service._repository.get_user_by_email = mocker.AsyncMock(
        side_effect=MultipleResultsFound
    )
    session = mocker.AsyncMock()

    with pytest.raises(HTTPException) as excinfo:
        await service.get_user_by_email("test.com", session=session)

    assert excinfo.value.status_code == status.HTTP_409_CONFLICT
    assert "Incorrect data" in excinfo.value.detail


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(mocker):
    service = _make_service(mocker, get_user_by_email=None)
    session = mocker.AsyncMock()

    with pytest.raises(HTTPException) as excinfo:
        await service.get_user_by_email("test.com", session=session)

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
        id=fake_user.id,
        first_name=first_name or fake_user.first_name,
        last_name=last_name or fake_user.last_name,
    )
    service = _make_service(mocker, update_user_name=updated_user)
    session = mocker.AsyncMock()
    update_data = UpdateUserName(
        id=1,
        first_name=first_name,
        last_name=last_name,
    )

    user = await service.update_user_name(data=update_data, session=session)

    assert user.id == updated_user.id
    assert user.first_name == updated_user.first_name
    service._repository.update_user_name.assert_called_once_with(
        user_id=1,
        session=session,
        first_name=first_name,
        last_name=last_name,
    )
