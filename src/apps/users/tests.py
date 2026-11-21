from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


class LoginRedirectTests(TestCase):
    def test_login_redirects_to_sales_filtered_for_today(self):
        User.objects.create_user(username="seller", password="password")
        today = timezone.localdate().isoformat()

        response = self.client.post(
            reverse("users:login"),
            {"username": "seller", "password": "password"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlsplit(response.url).path, reverse("sales:list_sales"))
        self.assertEqual(
            parse_qs(urlsplit(response.url).query),
            {
                "created_at_after": [today],
                "created_at_before": [today],
            },
        )
