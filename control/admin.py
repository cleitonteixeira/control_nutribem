from django.contrib import admin
from .models import Unidade, TipoEquipamento

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    ...

@admin.register(TipoEquipamento)
class TipoEquipamentoAdmin(admin.ModelAdmin):
    ...