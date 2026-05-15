from django.core.mail import send_mail

send_mail(
    'Teste',
    'Funcionando',
    None,
    ['gabrielalmeidaalexandreitu@email.com'],
    fail_silently=False
)