from django.urls import reverse
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Driver


class DriverRegistrationTests(APITestCase):
    """Тестирование регистрации водителя."""

    def test_incorrect_email(self):
        data = {
            'email': 'thecoolestdriver@thehood@gmail.com',
            'password': '12345678',
            'full_name': 'Check',
        }

        response = self.client.post(
            path=reverse('register'),
            data=data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_correct_data(self):
        data = {
            'email': 'proba@mail.ru',
            'password': '12345678',
            'full_name': 'Lion Alex',
        }

        response = self.client.post(
            path=reverse('register'),
            data=data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DriverVerificationOfRegistrationTests(APITestCase):
    """Тестирование верификации регистрации водителя."""

    def setUp(self):
        self.email = 'proba@mail.com'
        self.verification_code = '76543'
        self.user_data = {
            'email': self.email,
            'password': '12345678',
            'full_name': 'Lion Alex',
        }

        cache.set(
            f'verification_code_{self.email}',
            self.verification_code,
            timeout=1000,
        )
        cache.set(
            f'user_data_{self.email}',
            self.user_data,
            timeout=1000,
        )

    def test_correct_data(self):
        response = self.client.post(
            path=reverse('verify_register'),
            data={
                'email': self.email,
                'verification_code': self.verification_code,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_incorrect_data(self):
        response = self.client.post(
            path=reverse('verify_register'),
            data={
                'email': self.email,
                'verification_code': '78123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DriverLoginTests(APITestCase):
    """Тестирование авторизации водителя."""

    def setUp(self):
        self.user = Driver.objects.create_user(
            email='check@check.ru',
            password='12345678',
            full_name='Lion Alex',
        )

    def test_just_login(self):
        response = self.client.post(
            path=reverse('login_driver'),
            data={
                'email': 'check@check.ru',
                'password': '12345678',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_incorrect_password_login(self):
        response = self.client.post(
            path=reverse('login_driver'),
            data={
                'email': 'check@check.ru',
                'password': '87654321',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'], 'Incorrect password!')

    def test_incorrect_email_login(self):
        response = self.client.post(
            path=reverse('login_driver'),
            data={
                'email': '',
                'password': '12345678',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_field_login(self):
        response = self.client.post(
            path=reverse('login_driver'),
            data={
                'password': '12345678',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DriverRefreshTests(APITestCase):
    """Тестирование получения refresh-токена."""

    def setUp(self):
        self.user = Driver.objects.create_user(
            email='check@check.ru',
            password='12345678',
            full_name='Lion Alex',
        )
        self.refresh_token = RefreshToken.for_user(self.user)

    def test_success_refresh(self):
        response = self.client.post(
            path=reverse('refresh_driver'),
            data={
                'refresh_token': str(self.refresh_token),
            },
            format='json',
        )
        self.assertIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_missing_params(self):
        response = self.client.post(
            path=reverse('refresh_driver'),
            data={},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DriverPasswordRecoveryTests(APITestCase):
    """Тестирование восстановления пароля."""

    def setUp(self):
        self.user = Driver.objects.create_user(
            email="check@check.ru",
            password="12345678",
            full_name="Lion Alex",
        )

    def test_password_recovery(self):
        response = self.client.post(
            path=reverse("recovery_driver"),
            data={
                "email": "check@check.ru",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("message"),
            'Check your email for the verification_code.',
        )

    def test_missing_params(self):
        response = self.client.post(
            path=reverse("recovery_driver"),
            data={},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_entered_email_does_not_exist(self):
        response = self.client.post(
            path=reverse("recovery_driver"),
            data={
                "email": "check_check@check.ru",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(
            response.data.get("email"),
            [
                ErrorDetail(
                    string='An account with this email does not exist!',
                    code='invalid',
                ),
            ],
        )


class DriverPasswordRecoveryVerifyTests(APITestCase):
    """Тестирование верификации восстановления пароля."""

    def setUp(self):
        self.user = Driver.objects.create_user(
            email="check@check.ru",
            password="12345678",
            full_name="Lion Alex",
        )

        self.email = "check@check.ru"
        self.verification_code = "12345"
        cache.set(
            key=f"verification_code_{self.email}",
            value=self.verification_code,
            timeout=1000,
        )

    def test_password_recovery_verify(self):
        response = self.client.post(
            path=reverse("recovery_verify_driver"),
            data={
                "email": self.email,
                "verification_code": self.verification_code,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data.get("message"),
            ['Verification was successful.'],
        )

    def test_missing_params(self):
        response = self.client.post(
            path=reverse("recovery_verify_driver"),
            data={
                "email": self.email,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("verification_code", response.data)

    def test_incorrect_email(self):
        response = self.client.post(
            path=reverse("recovery_verify_driver"),
            data={
                "email": "check_check@check.ru",
                "verification_code": self.verification_code,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_incorrect_verification_code(self):
        response = self.client.post(
            path=reverse("recovery_verify_driver"),
            data={
                "email": self.email,
                "verification_code": "12344",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("verification_code", response.data)
        self.assertEqual(
            response.data.get("verification_code"),
            ['The verification code is not active.'],
        )


class DriverPasswordRecoveryChangeTests(APITestCase):
    """Тестирование смены пароля для водителя."""

    def setUp(self):
        self.user = Driver.objects.create_user(
            email="check@check.ru",
            password="12345678",
            full_name="Lion Alex",
        )
        self.email = "check@check.ru"
        cache.set(
            key=f"password_recovery_{self.email}",
            value=True,
            timeout=1000,
        )

    def test_change_password(self):
        response = self.client.post(
            path=reverse("recovery_change_driver"),
            data={
                "email": self.email,
                "password": "123456789",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data.get("message"),
            ['Password successfully changed.'],
        )

    def test_missing_params(self):
        response = self.client.post(
            path=reverse("recovery_change_driver"),
            data={
                "email": self.email,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_incorrect_email(self):
        response = self.client.post(
            path=reverse("recovery_change_driver"),
            data={
                "email": "check_check@check.ru",
                "password": "123456789",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(
            response.data.get("email"),
            [
                ErrorDetail(
                    string='An account with this email does not exist!',
                    code='invalid',
                ),
            ],
        )
