from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Role(models.Model):
    ROLE_CHOICES= (
        ('master', 'SuperAdmin'),
        ('seller', 'Vendedor'),
        ('cashier', 'Cajero'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f'{self.user.username} - {self.role}'


class Avatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/avatars/', null=True, blank=True)
    
    def __str__(self):
        return self.image.url