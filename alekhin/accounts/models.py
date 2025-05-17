from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    username = None  # Убираем поле username
    email = models.EmailField(_('email address'), unique=True)  # Делаем email уникальным

    USERNAME_FIELD = 'email'  # Указываем, что email будет использоваться для авторизации
    REQUIRED_FIELDS = []  # Убираем email из REQUIRED_FIELDS, так как он теперь USERNAME_FIELD

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='customuser_set',
        related_query_name='customuser'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='customuser_set',
        related_query_name='customuser'
    )

    objects = CustomUserManager()  # Используем кастомный менеджер пользователей

    def __str__(self):
        return self.email