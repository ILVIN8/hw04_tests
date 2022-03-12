from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст поста",
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="HasNoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/test_slug/ доступна любому пользователю."""
        response = self.guest_client.get("/group/test-slug/")
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/auth/ доступна любому пользователю."""
        response = self.guest_client.get("/profile/auth/")
        self.assertEqual(response.status_code, 200)

    def test_posts_url_exists_at_desired_location(self):
        """Страница /posts/1/ доступна любому пользователю."""
        response = self.guest_client.get("/posts/1/")
        self.assertEqual(response.status_code, 200)

    def test_404_url_exists_at_desired_location(self):
        """Страница /unexisting_page/
        возращает 404 ошибку любому пользователю."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, 404)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location_authorized(self):
        """Страница /posts/1/edit/ доступна авторизованному автору поста
        пользователю."""
        response = self.authorized_client.get("/posts/1/edit/")
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/": "posts/index.html",
            "/group/test-slug/": "posts/group_list.html",
            "/profile/auth/": "posts/profile.html",
            "/posts/1/": "posts/post_detail.html",
            "/create/": "posts/create_post.html",
            "/posts/1/edit/": "posts/create_post.html",
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
