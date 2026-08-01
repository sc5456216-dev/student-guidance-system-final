
from django.db import models
from django.contrib.auth.models import AbstractUser
from base.models import BaseModel

class User(AbstractUser, BaseModel):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('counselor', 'Counselor'),
        ('staff', 'Staff'),
        ('advisor', 'Advisor'),   
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username'],
                condition=models.Q(is_deleted=False),
                name='unique_user_username_when_not_deleted'
            ),
            models.UniqueConstraint(
                fields=['phone'],
                condition=models.Q(is_deleted=False) & ~models.Q(phone=''),
                name='unique_user_phone_when_not_deleted'
            ),
        ]

    def __str__(self):
        return self.email


class CustomFormatDateField(models.DateField):
    def formfield(self, **kwargs):
        defaults = {'input_formats': ['%d/%m/%Y', '%d-%m-%Y']}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.CharField(max_length=100, blank=True)
    birth_date = CustomFormatDateField(null=True, blank=True)

    def __str__(self):
        return self.user.username