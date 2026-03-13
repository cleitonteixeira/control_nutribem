from django.contrib import admin
from .models import ClasseEquipamento, HistoricoTransferencia, Unidade, TipoEquipamento, Equipamento

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    ...

@admin.register(TipoEquipamento)
class TipoEquipamentoAdmin(admin.ModelAdmin):
    ...

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    ...

@admin.register(ClasseEquipamento)
class ClasseEquipamentoAdmin(admin.ModelAdmin):
    ...

@admin.register(HistoricoTransferencia)
class HistoricoTransferenciaAdmin(admin.ModelAdmin):
    ...