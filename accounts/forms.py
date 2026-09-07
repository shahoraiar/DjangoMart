from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'User name',
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email address',
            'password1': 'Create password',
            'password2': 'Repeat password',
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control auth-input',
                'placeholder': placeholders.get(name, ''),
            })
