from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

from decimal import Decimal, ROUND_HALF_UP
import json
from .models import Cliente, Orcamento
from .forms import ClienteForm
from django.core.mail import send_mail


def calculadora(request):
    return render(request, 'solar/index.html')



def calcular(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)

    consumo = float(dados.get('consumo', 0))
    conta = float(dados.get('conta', 0))
    tarifa = float(dados.get('tarifa', 0.85))
    irradiacao = float(dados.get('irradiacao', 5.0))
    geracao = float(dados.get('geracao', 100)) / 100
    reajuste = float(dados.get('reajuste', 8)) / 100

    if consumo <= 0:
        return JsonResponse(
            {'erro': 'Consumo deve ser maior que zero'},
            status=400)
    if tarifa < 0 or irradiacao < 0:
        return JsonResponse(
            {'erro': 'Tarifa e irradiação devem ser maiores que zero.'},
            status=400
        )

    consumo_alvo    = consumo * geracao
    potencia        = consumo_alvo / (irradiacao * 30 * 0.82)
    custo           = potencia * 1000 * 4.5
    economia_mensal = consumo_alvo * tarifa
    economia_anual  = economia_mensal * 12

    acumulado = 0
    payback = None  # ← None em vez de 0
    eco_ano = economia_anual

    for ano in range(1, 26):  # ← 25 anos é o padrão do setor
        acumulado += eco_ano
        if acumulado >= custo and payback is None:
            payback = ano
        eco_ano *= (1 + reajuste)

    # Se não pagou em 25 anos, não compensa
    payback_final = payback if payback is not None else 99

    # Regras de viabilidade mais realistas:
    # - Paga em até 7 anos  → ótimo
    # - Paga em até 12 anos → razoável
    # - Mais de 12 anos     → não compensa (vida útil média do sistema é 25 anos)
    compensa = payback_final <= 8



    request.session['ultimo_calculo'] = {
        'consumo_kwh': consumo,
        'conta_valor': conta,
        'potencia_kwp': round(potencia, 2),
        'custo_estimado': round(custo, 2),
        'economia_mensal': round(economia_mensal, 2),
        'payback_anos': payback_final,
    }

    return JsonResponse({
        'potencia': round(potencia, 2),
        'custo': round(custo, 2),
        'economia_mensal': round(economia_mensal, 2),
        'payback': payback_final,
        'compensa': compensa,
        'classificacao': (
            'otimo' if payback_final <= 5 else
            'razoavel' if payback_final <= 8 else
            'nao_compensa'
        ),
    })

def cadastro(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            calculo = request.session.get('ultimo_calculo', {})
            if calculo:
                orc =  Orcamento.objects.create(cliente=cliente, **calculo)
                request.session['orcamento_id'] = orc.id

            send_mail(
                subject='☀ Seu orçamento solar foi recebido!',
                message=(
                    f'Olá {cliente.nome},\n\n'
                    f'Recebemos seu orçamento com sucesso.\n\n'
                    f'Potência estimada : {calculo.get("potencia_kwp")} kWp\n'
                    f'Custo estimado    : R$ {calculo.get("custo_estimado")}\n'
                    f'Economia mensal   : R$ {calculo.get("economia_mensal")}\n'
                    f'Payback estimado  : {calculo.get("payback_anos")} anos\n\n'
                    f'Nossa equipe entrará em contato em breve!'
                ),
                from_email=None,
                recipient_list=[cliente.email],
                fail_silently=False,  # nunca derrubar o fluxo por email
            )
            return redirect('sucesso')
    else:
        form = ClienteForm()
    return render(request, 'solar/cadastro.html', {'form': form})


def sucesso(request):
    calculo = request.session.get('ultimo_calculo')
    if not  calculo:
       return redirect('calculadora')
    return render(request, 'solar/sucesso.html', {'calculo': calculo})

def  download_pdf(request, orcamento_id):
    orcamento    = Orcamento.objects.select_related('cliente').get(id = orcamento_id)
    html_str     = render_to_string('solar/orcamento_pdf.html', {'orcamento': orcamento})
    pdf          =HTML(string=html_str).write_pdf()
    response     =HttpResponse(pdf,content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={orcamento_id}.pdf'
    return response
# deploy fix