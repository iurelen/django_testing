import pytest

from django.urls import reverse
from django.conf import settings


HOME_URL = reverse('news:home')
# Где в этом модуле нужно использовать
# урл = pytest.lazy_fixture('фикстура_с_урлом')?


@pytest.mark.django_db
@pytest.mark.usefixtures('news_list')
def test_news_count(client):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('news_list')
def test_news_order(client):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('comments_list')
def test_comments_order(client, news, detail_url):
    """Комментарии на странице отдельной новости отсортированы
    от старых к новым.
    """
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    for i in range(len(all_comments) - 1):
        assert all_comments[i].created < all_comments[i + 1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_on_page',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_pages_contains_form(parametrized_client, form_on_page, detail_url):
    """Анонимному пользователю не видна форма для отправки комментария
    на странице отдельной новости, а авторизованному видна.
    """
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) == form_on_page
