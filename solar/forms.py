from django import forms
from .models import Cliente

ESTADOS_BR = [
    ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'), ('BA', 'BA'),
    ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'), ('GO', 'GO'), ('MA', 'MA'),
    ('MT', 'MT'), ('MS', 'MS'), ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'),
    ('PR', 'PR'), ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'),
    ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'), ('SP', 'SP'),
    ('SE', 'SE'), ('TO', 'TO'),
]

class ClienteForm(forms.ModelForm):
    class Meta:
        model  = Cliente
        fields = ['nome', 'email', 'telefone', 'cidade', 'estado']
        widgets = {
            'nome':     forms.TextInput(attrs={
                'placeholder': 'Seu nome completo',
                'class': 'form-input'
            }),
            'email':    forms.EmailInput(attrs={
                'placeholder':'gabrielalmeidaalexandreitu@email.com',

                'class': 'form-input'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(11) 99999-9999',
                'class': 'form-input'
            }),
            'cidade':   forms.TextInput(attrs={
                'placeholder': 'Sua cidade',
                'class': 'form-input'
            }),
        }



