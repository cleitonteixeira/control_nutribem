from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, logout, authenticate, login
from django.core.paginator import Paginator

import openpyxl

from .forms import EquipamentoForm, UnidadeForm

from .models import Equipamento, TipoEquipamento, Unidade

def home(request):
    return render(request, 'pages/index_control.html')

@login_required
def UnidadesView(request):
    unidades_list = Unidade.objects.all().order_by('codigo')
    
    # Filtro de busca (opcional, mas recomendado)
    busca = request.GET.get('search')
    if busca:
        unidades_list = unidades_list.filter(nome__icontains=busca)

    # Define 12 unidades por página (ideal para o grid de 4 colunas no PC)
    paginator = Paginator(unidades_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pages/unidade_index.html', context={
        'page_obj': page_obj
    })

@login_required
def cadastrar_unidade(request):
    if request.method == 'POST':
        form = UnidadeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unidade cadastrada com sucesso!')
            return redirect('control:unidades')
    else:
        form = UnidadeForm()
    
    return render(request, 'pages/unidade_create.html', {'form': form})
@login_required
def editar_unidade(request, pk):
    unidade = get_object_or_404(Unidade, pk=pk)
    
    if request.method == 'POST':
        form = UnidadeForm(request.POST, instance=unidade)
        if form.is_valid():
            form.save()
            messages.success(request, f'Unidade "{unidade.nome}" atualizada com sucesso!')
            return redirect('control:unidades')
    else:
        form = UnidadeForm(instance=unidade)
    
    return render(request, 'pages/unidade_edit.html', {'form': form, 'unidade': unidade})

@login_required
def EquipamentosView(request):
    equipamentos = Equipamento.objects.select_related('unidade', 'tipo').all()

    unidade_id = request.GET.get('unidade')
    tipo_id = request.GET.get('tipo')

    if unidade_id:
        equipamentos = equipamentos.filter(unidade_id=unidade_id)
    if tipo_id:
        equipamentos = equipamentos.filter(tipo_id=tipo_id)

    if request.GET.get('exportar') == 'xlsx':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="relatorio_equipamentos.xlsx"'

        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Equipamentos'

        # Cabeçalho da planilha
        columns = ['Equipamento', 'Tipo', 'Unidade','Valor', 'Status', 'Ativo']
        worksheet.append(columns)

        # Inserindo os dados filtrados
        for equipamento in equipamentos:
            worksheet.append([
                equipamento.nome,
                equipamento.tipo.nome if equipamento.tipo else '',
                equipamento.unidade.nome if equipamento.unidade else '',
                equipamento.valor if equipamento.valor else 0.00,
                equipamento.get_status_display(),
                'Sim' if equipamento.ativo else 'Não'
            ])

        workbook.save(response)
        return response
    paginator = Paginator(equipamentos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Contexto para popular os selects do filtro
    unidades = Unidade.objects.all()
    tipos = TipoEquipamento.objects.all()

    contexto = {
        'page_obj': page_obj,
        'unidades': unidades,
        'tipos': tipos,
    }
    return render(request, 'pages/equipamento_index.html', contexto)

@login_required
def cadastrar_equipamento(request):
    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipamento cadastrado com sucesso!')
            return redirect('control:equipamentos')
    else:
        form = EquipamentoForm()
    return render(request, 'pages/equipamento_create.html', context={
        'form': form
        })

@login_required
def editar_equipamento(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        form = EquipamentoForm(request.POST, instance=equipamento)
        if form.is_valid():
            form.save()
            messages.success(request, f'{equipamento.nome} atualizado com sucesso!')
            return redirect('control:equipamentos')
    else:
        form = EquipamentoForm(instance=equipamento)
    return render(request, 'pages/equipamento_edit.html', {'form': form, 'equipamento': equipamento})

def load_tipos(request):
    classe_id = request.GET.get('classe_id')
    tipos = TipoEquipamento.objects.filter(classe_id=classe_id).order_by('nome')
    return JsonResponse(list(tipos.values('id', 'nome')), safe=False)