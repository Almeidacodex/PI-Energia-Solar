from django.db import models

UF_CHOICES = [
    ('AC','Acre'),('AL','Alagoas'),('AM','Amazonas'),('AP','Amapá'),
    ('BA','Bahia'),('CE','Ceará'),('DF','Distrito Federal'),
    ('ES','Espírito Santo'),('GO','Goiás'),('MA','Maranhão'),
    ('MG','Minas Gerais'),('MS','Mato Grosso do Sul'),
    ('MT','Mato Grosso'),('PA','Pará'),('PB','Paraíba'),
    ('PE','Pernambuco'),('PI','Piauí'),('PR','Paraná'),
    ('RJ','Rio de Janeiro'),('RN','Rio Grande do Norte'),
    ('RO','Rondônia'),('RR','Roraima'),('RS','Rio Grande do Sul'),
    ('SC','Santa Catarina'),('SE','Sergipe'),
    ('SP','São Paulo'),('TO','Tocantins'),
]


class Cliente(models.Model):
    nome      = models.CharField(max_length=100, verbose_name="Nome completo")
    email     = models.EmailField(unique=True, verbose_name="E-mail")
    telefone  = models.CharField(max_length=20, verbose_name="Telefone")
    cidade    = models.CharField(max_length=100, verbose_name="Cidade")
    estado    = models.CharField(max_length=2, choices=UF_CHOICES,
                    verbose_name="Estado")  # ← novo campo
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Cliente"
        verbose_name_plural = "Clientes"
        ordering            = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} — {self.email}"


class Orcamento(models.Model):

    STATUS_CHOICES = [
        ("novo",       "Novo"),
        ("contatado",  "Contatado"),
        ("negociando", "Em negociação"),
        ("fechado",    "Fechado"),
        ("perdido",    "Perdido"),
    ]



    # Dados de entrada do usuário
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    consumo_kwh     = models.DecimalField(max_digits=10, decimal_places=2,
                                          verbose_name="Consumo (kWh)")
    conta_valor     = models.DecimalField(max_digits=10, decimal_places=2,
                                          verbose_name="Conta (R$)")

    # Parâmetros usados no cálculo (antes eram perdidos!)
    tarifa_kwh      = models.DecimalField(max_digits=6,  decimal_places=4, verbose_name="Tarifa (R$/kWh)", default=0.85)
    irradiacao      = models.DecimalField(max_digits=5,  decimal_places=2, verbose_name="Irradiação (hsp/dia)", default=5.0)
    percentual_geracao = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="% de geração desejada", default=100)
    reajuste_anual  = models.DecimalField(max_digits=5,  decimal_places=2, verbose_name="Reajuste anual (%)", default=8)

    # Resultados calculados
    potencia_kwp    = models.DecimalField(max_digits=10, decimal_places=2,
                                          verbose_name="Potência  (kWp)")
    custo_estimado  = models.DecimalField(max_digits=12, decimal_places=2,
                                          verbose_name="Custo  (R$)")
    economia_mensal = models.DecimalField(max_digits=10, decimal_places=2,
                                          verbose_name="Economia mensal (R$)")
    payback_anos    = models.DecimalField(max_digits = 5, decimal_places = 1,
                                                       verbose_name="Payback (anos)")


    # Gestão do lead
    status          = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="novo", verbose_name="Status"
    )
    observacoes     = models.TextField(blank=True, verbose_name="Observações")
    criado_em       = models.DateTimeField(auto_now_add=True)
    atualizado_em   = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name        = "Orçamento"
        verbose_name_plural = "Orçamentos"
        ordering            = ["-criado_em"]

    def __str__(self):
        return f"Orçamento #{self.pk} — {self.cliente.nome}"

    @property
    def economia_anual(self):
        return self.economia_mensal * 12

    @property
    def roi_percentual(self):
        if self.custo_estimado:
            return round((self.economia_anual / self.custo_estimado) * 100, 1)
        return 0
