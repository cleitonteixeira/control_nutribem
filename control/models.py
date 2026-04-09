from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Base(models.Model):
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Unidade(Base):
    codigo = models.IntegerField("Código", unique=True, null=True, blank=True)
    nome = models.CharField("Nome da Unidade", max_length=100)
    gu = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='unidades_gerenciadas',
        verbose_name="Gerente da Unidade (GU)"
    )
    
    supervisor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='unidades_supervisionadas',
        verbose_name="Supervisor"
    )

    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Unidade"
        verbose_name_plural = "Unidades"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class ClasseEquipamento(Base):
    nome = models.CharField("Classe de Equipamento", max_length=20, unique=True)
    sigla = models.CharField("Sigla", max_length=3, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Classe de Equipamento"
        verbose_name_plural = "Classes de Equipamento"
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
class TipoEquipamento(Base):
    nome = models.CharField("Tipo de Equipamento", max_length=100)
    classe = models.ForeignKey(ClasseEquipamento, on_delete=models.SET_DEFAULT, related_name='tipos', default=1)
    class Meta:
        verbose_name = "Tipo de Equipamento"
        verbose_name_plural = "Tipos de Equipamento"
        ordering = ['classe', 'nome']

    def __str__(self):
        return self.nome  

class Equipamento(Base):
    STATUS_CHOICES = [
        ('uso', 'Em Uso'),
        ('ocioso', 'Ocioso'),
        ('manutencao', 'Em Manutenção'),
    ]
    nome = models.CharField("Nome do Equipamento", max_length=100)
    unidade = models.ForeignKey(Unidade, on_delete=models.DO_NOTHING, related_name='equipamentos')
    tipo = models.ForeignKey(TipoEquipamento, on_delete=models.DO_NOTHING, related_name='equipamentos')
    status = models.CharField("Status do Equipamento", max_length=50, choices=STATUS_CHOICES, default="uso")
    valor = models.DecimalField("Valor do Equipamento", max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    responsavel = models.TextField("Responsável", max_length=255, null=True, blank=True, default="Dpto/Unidade")
    ativo = models.BooleanField(default=True)
    tag = models.CharField("Tag Patrimonial", max_length=20, unique=True, editable=False, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.tag:
            # 1. Obtém o prefixo da Classe (ex: TIC, MOB, MAQ)
            # Idealmente, adicione um campo 'sigla' no model ClasseEquipamento
            prefixo = self.tipo.classe.sigla or self.tipo.classe.nome[:3].upper()

            # 2. Busca o último número sequencial para este prefixo
            ultimo_equipamento = Equipamento.objects.filter(tag__startswith=prefixo).order_by('tag').last()
            
            if ultimo_equipamento and ultimo_equipamento.tag:
                # Extrai o número da tag atual (ex: 'TIC-0005' -> 5)
                try:
                    ultimo_numero = int(ultimo_equipamento.tag.split('-')[-1])
                    novo_numero = ultimo_numero + 1
                except (ValueError, IndexError):
                    novo_numero = 1
            else:
                novo_numero = 1

            # 3. Formata a nova TAG (ex: TIC-0001)
            self.tag = f"{prefixo}-{novo_numero:04d}"
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.unidade.nome})"

class HistoricoTransferencia(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='historico_transferencias')
    unidade_origem = models.ForeignKey('Unidade', on_delete=models.SET_NULL, null=True, related_name='transferencias_saida')
    unidade_destino = models.ForeignKey('Unidade', on_delete=models.SET_NULL, null=True, related_name='transferencias_entrada')
    responsavel_origem = models.CharField("Responsável Anterior", max_length=255, null=True, blank=True)
    responsavel_destino = models.CharField("Novo Responsável", max_length=255, null=True, blank=True)
    motivo = models.TextField("Motivo / Observação")
    data_transferencia = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # Quem logou no sistema

    class Meta:
        verbose_name = "Histórico de Transferência"
        verbose_name_plural = "Históricos de Transferências"
        ordering = ['-data_transferencia'] # Mostra os mais recentes primeiro

    def __str__(self):
        return f"{self.equipamento.nome} - {self.data_transferencia.strftime('%d/%m/%Y')}"
    
    @property
    def nome_usuario(self):
        if self.usuario:
            return self.usuario.get_full_name() or self.usuario.username
        return "Sistema/Removido"
    
class Manutencao(Base):
    TIPO_CHOICES = [
        ('Preventiva', 'Preventiva'),
        ('Corretiva', 'Corretiva'),
    ]
    STATUS_CHOICES = [
        ('Agendada', 'Agendada'),
        ('Em Execução', 'Em Execução'),
        ('Concluída', 'Concluída'),
    ]

    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='manutencoes')
    unidade_origem = models.ForeignKey('Unidade', on_delete=models.SET_NULL, null=True, blank=True)
    data_manutencao = models.DateField("Data")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField("O que foi feito")
    prestador = models.CharField("Técnico/Empresa", max_length=255)
    valor = models.DecimalField("Custo (R$)", max_digits=10, decimal_places=2, default=0)
    proxima_manutencao = models.DateField("Próxima Revisão", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Concluída')

    class Meta:
        verbose_name = "Manutenção"
        verbose_name_plural = "Manutenções"
        ordering = ['-data_manutencao']

    def __str__(self):
        return f"{self.equipamento.nome} - {self.data_manutencao}"
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.unidade_origem:
            self.unidade_origem = self.equipamento.unidade
        super().save(*args, **kwargs)