from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from .. import admin
from ..factories import MembershipFactory

User = get_user_model()


class UsersViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='username',
            password='password',
        )

    def test_membership_create(self):
        url = reverse('users:user_membership_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Requires login now

        self.client.login(username='username', password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            'legal_name': 'Some Name',
            'preferred_name': 'Sommy',
            'email_address': 'sommy@example.com',
            'city': 'Lawrence',
            'region': 'Kansas',
            'country': 'USA',
            'postal_code': '66044',
            'psf_code_of_conduct': True,
            'psf_announcements': True,
            settings.HONEYPOT_FIELD_NAME: settings.HONEYPOT_VALUE,
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:user_membership_thanks'))

    def test_membership_update(self):
        url = reverse('users:user_membership_edit')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Requires login now

        membership = MembershipFactory(creator=self.user)
        self.client.login(username='username', password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            'legal_name': 'Some Name',
            'preferred_name': 'Sommy',
            'email_address': 'sommy@example.com',
            'city': 'Lawrence',
            'region': 'Kansas',
            'country': 'USA',
            'postal_code': '66044',
            'psf_announcements': True,
            settings.HONEYPOT_FIELD_NAME: settings.HONEYPOT_VALUE,
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

    def test_user_update(self):
        self.client.login(username='username', password='password')
        url = reverse('users:user_profile_edit')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            settings.HONEYPOT_FIELD_NAME: settings.HONEYPOT_VALUE,
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)

    def test_user_detail(self):
        # Ensure detail page is viewable without login, but that edit URLs
        # do not appear
        detail_url = reverse('users:user_detail', kwargs={'slug': self.user.username})
        edit_url = reverse('users:user_profile_edit')
        response = self.client.get(detail_url)
        self.assertNotContains(response, edit_url)

        # Ensure edit url is available to logged in users
        self.client.login(username='username', password='password')
        response = self.client.get(detail_url)
        self.assertContains(response, edit_url)

    def test_special_usernames(self):
        # Ensure usernames in the forms of:
        # first.last
        # user@host.com
        # are allowed to view their profile pages since we allow them in
        # the username field
        u1 = User.objects.create_user(
            username='user.name',
            password='password',
        )
        detail_url = reverse('users:user_detail', kwargs={'slug': u1.username})
        edit_url = reverse('users:user_profile_edit')

        self.client.login(username=u1.username, password='password')
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)

        u2 = User.objects.create_user(
            username='user@example.com',
            password='password',
        )

        detail_url = reverse('users:user_detail', kwargs={'slug': u2.username})
        edit_url = reverse('users:user_profile_edit')

        self.client.login(username=u2.username, password='password')
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)

