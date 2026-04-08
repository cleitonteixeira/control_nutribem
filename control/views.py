from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, logout, authenticate, login
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum

import openpyxl

from .forms import EquipamentoForm, ManutencaoForm, TransferenciaEquipamentoForm, UnidadeForm, LoginForm

from .models import Equipamento, HistoricoTransferencia, TipoEquipamento, Unidade

def LoginView(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('control:index')
        else:
            for field_label, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro! {error}')
    else:
        form = LoginForm()
    return render(request, 'global/login.html', {'form': form})

@login_required
def home(request):
    status_counts = Equipamento.objects.aggregate(
        total=Count('id'),
        ociosos=Count('id', filter=Q(status='ocioso')),
        em_uso=Count('id', filter=Q(status='uso')),
        manutencao=Count('id', filter=Q(status='manutencao'))
    )

    context = {
        'counts': status_counts,
    }
    return render(request, 'pages/index_control.html', context)

@login_required
def UnidadesView(request):
    unidades_list = Unidade.objects.all().order_by('codigo')
    busca = request.GET.get('search')
    if busca:
        unidades_list = unidades_list.filter(nome__icontains=busca)
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
        columns = ['Equipamento','Classe', 'Tipo', 'Unidade','Valor', 'Status', 'Ativo']
        worksheet.append(columns)
        for equipamento in equipamentos:
            worksheet.append([
                equipamento.nome,
                equipamento.tipo.classe.nome if equipamento.tipo and equipamento.tipo.classe else '',
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
            equipamento =form.save()
            HistoricoTransferencia.objects.create(
                equipamento=equipamento,
                unidade_origem=None,
                unidade_destino=equipamento.unidade,
                responsavel_destino=equipamento.responsavel,
                motivo="Cadastro Inicial do Equipamento no sistema.",
                usuario=request.user
            )
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
            return redirect('control:detalhes_equipamento', pk=equipamento.pk)
    else:
        form = EquipamentoForm(instance=equipamento)
    return render(request, 'pages/equipamento_edit.html', {'form': form, 'equipamento': equipamento})

@login_required
def transferir_equipamento(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    unidade_antiga = equipamento.unidade
    responsavel_antigo = equipamento.responsavel

    if request.method == 'POST':
        form = TransferenciaEquipamentoForm(request.POST, instance=equipamento)
        
        if form.is_valid():
            equipamento_atualizado = form.save()
            motivo_texto = form.cleaned_data['motivo']
            HistoricoTransferencia.objects.create(
                equipamento=equipamento_atualizado,
                unidade_origem=unidade_antiga,
                unidade_destino=equipamento_atualizado.unidade,
                responsavel_origem=responsavel_antigo,
                responsavel_destino=equipamento_atualizado.responsavel,
                motivo=motivo_texto,
                usuario=request.user
            )
            messages.success(request, f'{equipamento.nome} transferido para {equipamento_atualizado.unidade} com sucesso!')
            return redirect('control:detalhes_equipamento', pk=equipamento.pk)
    else:
        form = TransferenciaEquipamentoForm(instance=equipamento)
    return render(request, 'pages/equipamento_transfer.html', {'form': form, 'equipamento': equipamento})

def detalhes_equipamento(request, pk):
    equipamento = get_object_or_404(
        Equipamento.objects.prefetch_related('manutencoes'), 
        pk=pk
    )
    form_manutencao = ManutencaoForm()
    historico_transferencias = HistoricoTransferencia.objects.filter(equipamento=equipamento).select_related('unidade_origem', 'unidade_destino', 'usuario')[:3]
    total_gasto = equipamento.manutencoes.aggregate(Sum('valor'))['valor__sum'] or 0
    custo_total_manutencao = equipamento.manutencoes.aggregate(Sum('valor'))['valor__sum'] or 0
    custo_total_ativo = equipamento.valor + custo_total_manutencao
    return render(request, 'pages/equipamento_detail.html', {
        'equipamento': equipamento,
        'historico_transferencias': historico_transferencias,
        'custo_total_manutencao': custo_total_manutencao,
        'custo_total_ativo': custo_total_ativo,
        'total_gasto': total_gasto,
        'form_manutencao': form_manutencao,
    })

def load_tipos(request):
    classe_id = request.GET.get('classe_id')
    tipos = TipoEquipamento.objects.filter(classe_id=classe_id).order_by('nome')
    return JsonResponse(list(tipos.values('id', 'nome')), safe=False)

def registrar_manutencao(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        form = ManutencaoForm(request.POST)
        if form.is_valid():
            manutencao = form.save(commit=False)
            manutencao.equipamento = equipamento
            manutencao.save()
            messages.success(request, "Manutenção registrada com sucesso!")
        else:
            messages.error(request, "Erro ao registrar manutenção. Verifique os dados.")
    
    return redirect('control:detalhes_equipamento', pk=pk)