from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
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

    consumo    = float(dados.get('consumo', 0))
    conta      = float(dados.get('conta', 0))
    tarifa     = float(dados.get('tarifa', 0.85))
    irradiacao = float(dados.get('irradiacao', 5.0))
    geracao    = float(dados.get('geracao', 100)) / 100
    reajuste   = float(dados.get('reajuste', 8)) / 100

    if consumo <= 0:
        return JsonResponse({'erro': 'Consumo deve ser maior que zero'}, status=400)
    if tarifa <= 0 or tarifa > 5.0:
        return JsonResponse({'erro': 'Tarifa inválida. Use um valor entre 0 e R$ 5,00/kWh.'}, status=400)
    if irradiacao <= 0:
        return JsonResponse({'erro': 'Irradiação deve ser maior que zero'}, status=400)

    consumo_alvo    = consumo * geracao
    potencia        = consumo_alvo / (irradiacao * 30 * 0.82)
    custo           = potencia * 1000 * 4.5
    economia_mensal = consumo_alvo * tarifa
    economia_anual  = economia_mensal * 12

    acumulado = 0
    payback   = None
    eco_ano   = economia_anual

    for ano in range(1, 26):
        acumulado += eco_ano
        if acumulado >= custo and payback is None:
            payback = ano
        eco_ano *= (1 + reajuste)

    payback_final = payback if payback is not None else 99

    request.session['ultimo_calculo'] = {
        'consumo_kwh':     consumo,
        'conta_valor':     conta,
        'potencia_kwp':    round(potencia, 2),
        'custo_estimado':  round(custo, 2),
        'economia_mensal': round(economia_mensal, 2),
        'payback_anos':    payback_final,
    }
    request.session.modified = True

    return JsonResponse({
        'potencia':        round(potencia, 2),
        'custo':           round(custo, 2),
        'economia_mensal': round(economia_mensal, 2),
        'payback':         payback_final,
        'compensa':        payback_final <= 8,
        'classificacao': (
            'otimo'       if payback_final <= 5 else
            'razoavel'    if payback_final <= 8 else
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
                orc = Orcamento.objects.create(cliente=cliente, **calculo)
                request.session['orcamento_id'] = orc.id
                request.session.modified = True

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
                fail_silently=False
            )
            return redirect('sucesso')
    else:
        form = ClienteForm()
    return render(request, 'solar/cadastro.html', {'form': form})


def sucesso(request):
    calculo = request.session.get('ultimo_calculo')
    if not calculo:
        return redirect('calculadora')
    orcamento_id = request.session.get('orcamento_id')
    return render(request, 'solar/sucesso.html', {
        'calculo': calculo,
        'orcamento_id': orcamento_id,
    })


def download_pdf(request, orcamento_id):
    orcamento = get_object_or_404(Orcamento.objects.select_related('cliente'), id=orcamento_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, altura - 80, "Orcamento Solar")
    p.setFont("Helvetica", 12)
    p.drawString(50, altura - 120, f"Cliente: {orcamento.cliente.nome}")
    p.drawString(50, altura - 140, f"Email:   {orcamento.cliente.email}")
    p.line(50, altura - 160, largura - 50, altura - 160)

    dados = [
        ("Potencia necessaria", f"{orcamento.potencia_kwp} kWp"),
        ("Custo estimado",      f"R$ {orcamento.custo_estimado}"),
        ("Economia mensal",     f"R$ {orcamento.economia_mensal}"),
        ("Payback estimado",    f"{orcamento.payback_anos} anos"),
    ]
    y = altura - 200
    for label, valor in dados:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y, f"{label}:")
        p.setFont("Helvetica", 11)
        p.drawString(220, y, valor)
        y -= 28

    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.drawCentredString(largura / 2, 40, "PI Energia Solar — gerado automaticamente")
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="orcamento_{orcamento_id}.pdf"'
    return response