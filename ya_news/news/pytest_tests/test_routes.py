import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

HOME_URL = reverse('news:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')


@pytest.mark.parametrize(
    'url',
    (
        HOME_URL,
        DETAIL_URL,
        LOGIN_URL,
        LOGOUT_URL,
        SIGNUP_URL,
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, url):
    """Доступность страниц для анонимного пользователя."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        EDIT_URL,
        DELETE_URL
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, expected_status, url
):
    """Страницы редактирования и удаления комментария доступны
    только автору.
    """
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        EDIT_URL,
        DELETE_URL
    ),
)
def test_redirects(client, url):
    """Анонимный пользователь перенаправляется на страницу авторизации."""
    expected_url = f'{LOGIN_URL}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
