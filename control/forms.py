from django import forms
from .models import ClasseEquipamento, Equipamento, Unidade
from django.contrib.auth.models import User

class UserFullNameChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.username

class UnidadeForm(forms.ModelForm):
    gu = UserFullNameChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Gerente da Unidade (GU)"
    )
    supervisor = UserFullNameChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Supervisor"
    )

    class Meta:
        model = Unidade
        fields = ['nome', 'gu', 'supervisor']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Nutribem Centro'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gu'].queryset = User.objects.order_by('first_name', 'last_name')
        self.fields['supervisor'].queryset = User.objects.order_by('first_name', 'last_name')

class EditUnidadeForm(forms.ModelForm):
    gu = UserFullNameChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Gerente da Unidade (GU)"
    )
    supervisor = UserFullNameChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Supervisor"
    )

    class Meta:
        model = Unidade
        fields = ['nome', 'gu', 'supervisor']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Nutribem Centro'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gu'].queryset = User.objects.order_by('first_name', 'last_name')
        self.fields['supervisor'].queryset = User.objects.order_by('first_name', 'last_name')


class EquipamentoForm(forms.ModelForm):
    classe = forms.ModelChoiceField(
        queryset=ClasseEquipamento.objects.all(),
        label="Classe de Equipamento",
        empty_label="Selecione uma Classe",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_classe'})
    )
    class Meta:
        model = Equipamento
        fields = ['nome', 'unidade', 'classe', 'tipo','valor','responsavel', 'status', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Liquidificador Industrial'}),
            'unidade': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'responsavel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João da Silva'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se estiver editando um equipamento, pré-seleciona a classe dele
        if self.instance.pk and self.instance.tipo:
            self.fields['classe'].initial = self.instance.tipo.classe
        
class TransferenciaEquipamentoForm(forms.ModelForm):
    motivo = forms.CharField(
        label="Motivo / Observação",
        widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 100px', 'placeholder': 'Descreva o motivo da transferência'}),
        required=True
    )

    class Meta:
        model = Equipamento
        fields = ['unidade', 'responsavel']
        widgets = {
            'unidade': forms.Select(attrs={'class': 'form-select'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Responsável'}),
        }