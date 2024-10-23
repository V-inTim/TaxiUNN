from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models


class ClientManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. Унаследовавшись от BaseUserManager, мы получаем много того
    же самого кода, который Django использовал для создания User
    (для демонстрации).
    """

    def create_user(self, email, password):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """

        if email is None:
            raise TypeError('Clients must have an email address.')

        if password is None:
            raise TypeError('Clients must have a password.')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        """ Создает и возввращет пользователя с привилегиями суперадмина. """
        if email is None:
            raise TypeError('Clients must have an email address.')

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class Client(AbstractBaseUser):

    email = models.EmailField(db_index=True, unique=True)
    full_name = models.CharField(null=True, default=None)

    is_active = models.BooleanField(default=True)
    # определяет, кто может войти в административную часть нашего сайта.
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Временная метка создания объекта.
    created_at = models.DateTimeField(auto_now_add=True)
    # Временная метка показывающая время последнего обновления объекта.
    updated_at = models.DateTimeField(auto_now=True)

    bank_balance = models.IntegerField(default=1000)

    # USERNAME_FIELD - поле, которое используется для входа в систему.
    USERNAME_FIELD = 'email'

    # класс UserManager должен управлять объектами этого типа.
    objects = ClientManager()

    def __str__(self):
        """ Строковое представление модели """
        return self.email
