from django import forms 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Role, Avatar
from django.utils.safestring import mark_safe
from django.forms.widgets import RadioSelect

AVATAR_CHOICES = [
    ('0', 'avatars/default.jpeg'),
    ('1', 'avatars/avatar01.jpeg'),
    ('2', 'avatars/avatar02.jpeg'),
    ('3', 'avatars/avatar03.jpeg'),
    ('4', 'avatars/avatar04.jpeg'),
    ('5', 'avatars/avatar05.jpeg'),
    ('6', 'avatars/avatar06.jpeg'),
    ('7', 'avatars/avatar07.jpeg')    
]

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=50, required=False)
    last_name = forms.CharField(label='Apellido', max_length=50, required=False)
    email = forms.EmailField(label='Correo electrónico', required=False)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)   

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        #avatar por defecto
        if commit:
            user.save()
            Avatar.objects.create(user=user, image='avatars/default.jpeg') 

        return user


class ImageRadioSelect(RadioSelect):
    def render(self, name, value, attrs=None, choices=(), renderer=None):
        output = []
        for option_value, option_label in self.choices:
            image_url = f'/media/{option_label}'  # Convertir la ruta de la imagen a una URL absoluta
            output.append(
                f'<label><input type="radio" name="{name}" value="{option_value}"'
                f'{" checked" if value == option_value else ""}>'
                f'<img src="{image_url}" alt="{option_value}" style="height: 50px; width: 50px;"></label>'
            )
        return mark_safe('\n'.join(output))


class ImageChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = ImageRadioSelect
        super().__init__(*args, **kwargs)


class UserUpdateForm(UserChangeForm):
    password = None
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(label='Nombre', max_length=50, required=False)
    last_name = forms.CharField(label='Apellido', max_length=50, required=False)
    avatar = ImageChoiceField(choices=AVATAR_CHOICES, label='Avatar', required=False)


    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'avatar']


    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            avatar_choice = self.cleaned_data['avatar']
            avatar_image = dict(self.fields['avatar'].choices)[avatar_choice]
            Avatar.objects.update_or_create(user=user, defaults={'image':avatar_image})
        return user


class RoleAssignForm(forms.ModelForm):
    role = forms.ChoiceField(choices=Role.ROLE_CHOICES, label='Rol')

    class Meta:
        model = Role
        fields = ['role']
