from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    email    = models.EmailField(unique=True, verbose_name="E-mail")
    username = models.CharField(max_length=150, unique=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name        = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.email_mascarado

    @property
    def email_mascarado(self):
        """Mostra só as 2 primeiras letras + asteriscos. ex: jo***@gmail.com"""
        local, dominio = self.email.split('@')
        oculto = local[:2] + '*' * (len(local) - 2)
        return f"{oculto}@{dominio}"