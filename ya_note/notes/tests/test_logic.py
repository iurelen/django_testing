from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    TITLE_FIELD = 'Заголовок'
    TEXT_FIELD = 'Текст'
    SLUG_FIELD = 'Slugified_title'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.author = User.objects.create(username='Автор заметки')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': cls.TITLE_FIELD,
            'text': cls.TEXT_FIELD,
            'slug': cls.SLUG_FIELD,
            'author': cls.author
        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE_FIELD)
        self.assertEqual(note.slug, self.SLUG_FIELD)
        self.assertEqual(note.author, self.author)

    def test_empty_slug(self):
        """Если при создании заметки не заполнен slug,
        то он формируется автоматически.
        """
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    TITLE_FIELD = 'Заголовок'
    TEXT_FIELD = 'Текст'
    SLUG_FIELD = 'Slugified_title'
    NEW_TITLE_FIELD = 'Обновлённый заголовок'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': cls.TITLE_FIELD,
            'text': cls.TEXT_FIELD,
            'slug': cls.SLUG_FIELD,
            'author': cls.author
        }
        cls.new_form_data = {
            'title': cls.NEW_TITLE_FIELD,
            'text': cls.TEXT_FIELD,
            'slug': cls.SLUG_FIELD,
            'author': cls.author
        }
        cls.note = Note.objects.create(**cls.form_data)
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

    def test_author_can_delete_note(self):
        """Авторизованный пользователь может удалять свои заметки."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_other_user_cant_delete_note(self):
        """Авторизованный пользователь не может удалять чужие заметки."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Авторизованный пользователь может редактировать свои заметки."""
        response = self.author_client.post(
            self.edit_url,
            data=self.new_form_data
        )
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE_FIELD)

    def test_other_user_cant_edit_note(self):
        """Авторизованный пользователь не может редактировать чужие заметки."""
        response = self.reader_client.post(
            self.edit_url,
            data=self.new_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE_FIELD)

    def test_user_cant_use_slug_twice(self):
        """Невозможно создать заметки с одинаковым слаг."""
        response = self.author_client.post(
            self.add_url,
            data=self.new_form_data
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG_FIELD + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE_FIELD)
