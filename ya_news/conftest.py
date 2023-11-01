import pytest

from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(title='Заголовок', text='Текст')
    return news


@pytest.fixture
def news_list():
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    news_list = News.objects.bulk_create(all_news)
    return news_list


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comments_list(author, news):
    now = timezone.now()
    # all_comments = [
    #     Comment(news=news, author=author, text=f'Tекст {index}',)
    #     for index in range(2)
    # ]
    # comments_list = Comment.objects.bulk_create(all_comments)
    # for i in range(2):
    #     comments_list[i].created = now + timedelta(days=i)
    #     comments_list[i].save()
    #     comments_list[i].refresh_from_db()
    # breakpoint()
    # return comments_list
    #
    # В теории было написано, что способ создания коменнтариев с 'bulk_create'
    # не сработает, т.к. время создания комментария устанавливается
    # автоматически и оно будет совпадать у всех комментариев. Поэтому
    # сравнение по атрибуту created не получится сделать.
    #
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария'
    }


@pytest.fixture
def url_to_comments(news):
    url = reverse('news:detail', args=(news.id,))
    return f'{url}#comments'


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))
