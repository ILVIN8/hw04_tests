from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание группы",
        )
        cls.group2 = Group.objects.create(
            title="Тестовая группа 2",
            slug="test-slug-2",
            description="Тестовое описание группы 2",
        )
        cls.posts = []
        for i in range(13):
            cls.posts.append(
                Post.objects.create(
                    author=cls.user,
                    text=f"Тестовый текст поста {i}",
                    group=cls.group,
                )
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="HasNoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:profile", kwargs={"username": "auth"}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": 1}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": 1}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ): "posts/group_list.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse("posts:index") + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_first_group_list_page_contains_ten_records(self):
        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_group_list_page_contains_three_records(self):
        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_first_profile_list_page_contains_ten_records(self):
        response = self.client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_profile_list_page_contains_three_records(self):
        response = self.client.get(
            reverse("posts:profile", kwargs={"username": "auth"}) + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": 1})
        )
        first_object = response.context["post"]
        post_text = first_object.text
        post_group_title = first_object.group.title
        post_author_username = first_object.author.username
        self.assertEqual(post_text, "Тестовый текст поста 0")
        self.assertEqual(post_group_title, "Тестовая группа")
        self.assertEqual(post_author_username, "auth")

    def test_existing_post_some_pages(self):
        tests_pages = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": "auth"}
            ): "posts/profile.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug-2"}
            ): "posts/group_list.html",
        }
        for page, template in tests_pages.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                result = False
                for post in response.context["page_obj"]:
                    post_text = post.text
                    post_group_title = post.group.title
                    post_author_username = post.author.username
                    if (
                        post_text == "Тестовый текст поста 12"
                        and post_group_title == "Тестовая группа"
                        and post_author_username == "auth"
                    ):
                        result = True
                        break
                if post_group_title == "Тестовая группа 2":
                    self.assertFalse(result)
                else:
                    self.assertTrue(result)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон /edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": 1})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_show_correct_context(self):
        """Шаблон /create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)
