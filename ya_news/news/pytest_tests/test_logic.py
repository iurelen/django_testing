import pytest

from http import HTTPStatus

from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    comments_count_before = Comment.objects.count()
    client.post(url, data=form_data)
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_user_can_create_comment(
    author_client, news, form_data, url_to_comments, author
):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    comments_count_before = Comment.objects.count()
    response = author_client.post(url, data=form_data)
    comments_count_after = Comment.objects.count()
    assertRedirects(response, url_to_comments)
    assert comments_count_after == comments_count_before + 1
    comment = Comment.objects.last()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_author_can_delete_comment(author_client, comment, url_to_comments):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    comments_count_before = Comment.objects.count()
    response = author_client.delete(delete_url)
    comments_count_after = Comment.objects.count()
    assertRedirects(response, url_to_comments)
    assert comments_count_after == comments_count_before - 1
    try:
        comment = Comment.objects.get(pk=comment.id)
    except ObjectDoesNotExist:
        comment = None
    assert comment is None


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    comments_count_before = Comment.objects.count()
    response = admin_client.delete(delete_url)
    comments_count_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count_after == comments_count_before


def test_author_can_edit_comment(
    author_client, comment, url_to_comments
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    new_form_data = {'text': 'Обновлённый комментарий'}
    response = author_client.post(edit_url, data=new_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_form_data['text']


def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, form_data
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    new_form_data = {'text': 'Обновлённый комментарий'}
    response = admin_client.post(
        edit_url,
        data=new_form_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_use_bad_words(author_client, news):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    comments_count_before = Comment.objects.count()
    response = author_client.post(url, data=bad_words_data)
    comments_count_after = Comment.objects.count()
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert comments_count_after == comments_count_before
