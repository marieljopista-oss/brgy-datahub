from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'enter username',
            'class': 'form-input',
            'autocomplete': 'username',
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'enter password',
            'class': 'form-input',
            'autocomplete': 'current-password',
        })
    )
