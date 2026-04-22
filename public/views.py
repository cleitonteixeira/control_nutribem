from django.shortcuts import render

from control.models import Equipamento, HistoricoTransferencia, Manutencao

def home(request):
    query = request.GET.get('tag', '').strip()
    equipamento = None
    movimentacoes = []
    manutencoes = []
    erro = None

    if query:
        equipamento = Equipamento.objects.filter(tag__iexact=query).first()
        if equipamento:
            # Busca os históricos ordenados do mais recente para o antigo
            movimentacoes = HistoricoTransferencia.objects.filter(equipamento=equipamento).order_by('-data_transferencia')
            manutencoes = Manutencao.objects.filter(equipamento=equipamento).order_by('-data_manutencao')
        else:
            erro = f"Equipamento com a TAG '{query}' não encontrado."

    return render(request, 'pages/home.html', {
        'equipamento': equipamento,
        'movimentacoes': movimentacoes,
        'manutencoes': manutencoes,
        'erro': erro,
        'query': query
    })