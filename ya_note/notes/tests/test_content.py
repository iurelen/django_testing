from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note_author = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Slug_author',
            author=cls.author
        )
        cls.note_reader = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Slug_reader',
            author=cls.reader
        )
        cls.urls = (
            ('notes:add', None),
            ('notes:edit', (cls.note_author.slug,)),
        )

    def test_notes_list_for_different_users(self):
        """Пользователь видит только свои заметки."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note_author, object_list)
        self.assertNotIn(self.note_reader, object_list)

    def test_authorized_client_has_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        self.client.force_login(self.author)
        for name, args in self.urls:
            with self.subTest(user=self.author, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
