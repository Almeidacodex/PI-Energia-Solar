from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class CadastroForm(UserCreationForm):
    email = forms.EmailField(
        label = "Email",
        widget=forms.EmailInput(attrs = {
            'placeholder': 'seu@email.com',
            'class' : 'form-input',
        })
    )

    class Meta:
        model = Usuario
        fields = ['email','password1','password2']
        #sem username - o login será pelo email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # usa o email como username também
        if commit:
            user.save()
        return user