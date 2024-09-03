from django import forms 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Role, Avatar
from django.utils.safestring import mark_safe
from django.forms.widgets import RadioSelect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'autocapitalize': 'off',
        'autocomplete': 'new-username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'autocomplete': 'new-password'
    }))

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
    email = forms.EmailField(
        label='Email', 
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={'invalid': 'Correo inválido.'}
    )
    password1 = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Campo obligatorio.'}
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Campo obligatorio.',
            'password_mismatch': 'Las contraseñas no coinciden.'
        }
    )   

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'usable_password' in self.fields:
            del self.fields['usable_password']

        for field_name, field in self.fields.items():
            if field_name in self.errors:
                field.widget.attrs.update({'class': 'form-control is-invalid'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

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
                f'<label style="display: inline-block; text-align: center;" class="pe-1">'
                f'<img src="{image_url}" alt="{option_value}" style="width: 70px; border-radius: 20%;">'
                f'<br>'
                f'<input type="radio" name="{name}" value="{option_value}" class="mt-2"'
                f'{" checked" if value == option_value else ""} style="margin-bottom: 5px;">'
                f'</label>'
            )
        return mark_safe('\n'.join(output))


class ImageChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = ImageRadioSelect
        super().__init__(*args, **kwargs)


class UserUpdateForm(UserChangeForm):
    password = None
    email = forms.EmailField(label='Email')
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
            try:
                avatar_choice = self.cleaned_data['avatar']
                avatar_image = dict(self.fields['avatar'].choices)[avatar_choice]
                Avatar.objects.update_or_create(user=user, defaults={'image':avatar_image})
            except:
                pass
        return user


class RoleAssignForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña Actual', 
        error_messages={
            'required': 'Campo obligatorio.',
            'invalid': 'Contraseña inválida.'
        }
    )

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Nueva Contraseña', 
        error_messages={'required': 'Campo obligatorio.',
            'invalid': 'Contraseña inválida.',
            'password_too_common': 'La contraseña es muy común.',
            'password_entirely_numeric': 'La contraseña no puede ser completamente numérica.',
            'password_too_short': 'La contraseña es muy corta.'
        }
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar Contraseña',
        error_messages={
            'required': 'Campo obligatorio.', 
            'invalid': 'Las contraseñas no coinciden.',
            'password_mismatch': 'Las contraseñas no coinciden.'  
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'error_messages' in field.widget.attrs:
                field.widget.attrs.update({'class':'form-control'})
            if field_name in self.errors:
                field.widget.attrs.update({'class':'form-control is-invalid'})
            else:
                field.widget.attrs.update({'class':'form-control'})