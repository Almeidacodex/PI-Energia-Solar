from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, Orcamento


class OrcamentoInline(admin.TabularInline):
    """Mostra os orçamentos do cliente diretamente na tela do Cliente."""
    model          = Orcamento
    extra          = 0
    readonly_fields = (
        "potencia_kwp", "custo_estimado", "economia_mensal",
        "payback_anos", "status", "criado_em",
    )
    fields = readonly_fields
    show_change_link = True


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display   = ("nome", "email", "telefone", "cidade", "estado", "total_orcamentos", "criado_em")
    search_fields  = ("nome", "email", "cidade")
    list_filter    = ("estado", "criado_em")
    readonly_fields = ("criado_em",)
    inlines        = [OrcamentoInline]

    @admin.display(description="Orçamentos")
    def total_orcamentos(self, obj):
        return obj.orcamentos.count()


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display   = (
        "id", "cliente", "potencia_kwp", "custo_formatado",
        "economia_mensal_fmt", "payback_anos","status", "status_badge", "criado_em",
    )
    list_filter    = ("status", "criado_em")
    search_fields  = ("cliente__nome", "cliente__email")
    list_editable  = ("status",)
    readonly_fields = (
        "criado_em", "atualizado_em",
        "tarifa_kwh", "irradiacao", "percentual_geracao", "reajuste_anual",
    )
    fieldsets = (
        ("Cliente", {
            "fields": ("cliente", "status", "observacoes"),
        }),
        ("Resultado do Cálculo", {
            "fields": (
                "consumo_kwh", "conta_valor",
                "potencia_kwp", "custo_estimado",
                "economia_mensal", "payback_anos",
            ),
        }),
        ("Parâmetros utilizados", {
            "classes": ("collapse",),
            "fields": ("tarifa_kwh", "irradiacao", "percentual_geracao", "reajuste_anual"),
        }),
        ("Datas", {
            "classes": ("collapse",),
            "fields": ("criado_em", "atualizado_em"),
        }),
    )

    @admin.display(description="Custo estimado")
    def custo_formatado(self, obj):
        return f"R$ {obj.custo_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @admin.display(description="Economia/mês")
    def economia_mensal_fmt(self, obj):
        return f"R$ {obj.economia_mensal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @admin.display(description="Status")
    def status_badge(self, obj):
        cores = {
            "novo":       "#3498db",
            "contatado":  "#f39c12",
            "negociando": "#9b59b6",
            "fechado":    "#27ae60",
            "perdido":    "#e74c3c",
        }
        cor = cores.get(obj.status, "#999")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600">{}</span>',
            cor, obj.get_status_display()
        )


admin.site.site_header = "☀️ PI Energia Solar — Painel Administrativo"
admin.site.site_title  = "PI Energia Solar"
admin.site.index_title = "Gerenciamento do Sistema"
