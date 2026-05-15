from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone


@receiver(user_logged_in)
def enviar_email_login(sender, request, user, **kwargs):
    """Dispara automaticamente quando qualquer usuário faz login."""

    horario = timezone.localtime(timezone.now()).strftime('%d/%m/%Y às %H:%M')

    assunto = '☀️ Novo acesso detectado — Solar Calc'

    mensagem = f"""
Olá!

Um acesso foi realizado na sua conta Solar Calc.

📧 Conta:   {user.email}
🕐 Horário: {horario}
🔗 Painel:  http://127.0.0.1:8000/admin/

Se não foi você, entre em contato imediatamente.

— Equipe Solar Calc
    """.strip()

    send_mail(
        subject=assunto,
        message=mensagem,
        from_email=None,          # usa o DEFAULT_FROM_EMAIL do settings
        recipient_list=[user.email],
        fail_silently=True,       # não quebra o login se o email falhar
    )