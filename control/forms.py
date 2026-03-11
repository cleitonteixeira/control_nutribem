from django import forms
from .models import Equipamento, Unidade
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
    class Meta:
        model = Equipamento
        fields = ['nome', 'unidade', 'tipo','valor','responsavel', 'status', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Liquidificador Industrial'}),
            'unidade': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'responsavel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João da Silva'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }