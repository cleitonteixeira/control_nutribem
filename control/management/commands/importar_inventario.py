import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from control.models import Equipamento, Unidade, TipoEquipamento, ClasseEquipamento
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Importa equipamentos a partir de um arquivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('arquivo_csv', type=str, help='Caminho para o arquivo CSV')

    def handle(self, *args, **options):
        caminho = options['arquivo_csv']
        
        try:
            df = pd.read_csv(caminho, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(caminho, encoding='latin-1')

        self.stdout.write(self.style.SUCCESS(f"Iniciando importação de {len(df)} registros..."))

        status_map = {'EM USO': 'uso', 'OSCIOSO': 'ocioso', 'MANUTENCAO': 'manutencao'}

        classe_padrao, _ = ClasseEquipamento.objects.get_or_create(
            nome="IMPORTADO", 
            defaults={'sigla': 'IMP'}
        )
        usuario_padrao = User.objects.filter(username='cleiton').first()
        sucesso = 0
        erros = 0

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # 1. Tratar Unidade (CR)
                    unidade, _ = Unidade.objects.get_or_create(codigo=str(row['CR']).strip())

                    # 2. Tratar Tipo
                    tipo, _ = TipoEquipamento.objects.get_or_create(
                        nome=str(row['TIPO']).strip(),
                        defaults={'classe': classe_padrao}
                    )

                    # 3. Tratar Responsável (USUARIO/FILIAL)
                    # Verifica se é nulo (NaN) ou se está vazio após o strip
                    resp_original = row['USUARIO/FILIAL']
                    if pd.isna(resp_original) or str(resp_original).strip() == "":
                        responsavel_final = "Dpto/Unidade"
                    else:
                        responsavel_final = str(resp_original).strip()

                    # 4. Tratar Valor
                    valor_raw = str(row['VALOR']).replace('R$', '').replace('.', '').replace(',', '.').strip()
                    try:
                        valor_final = float(valor_raw)
                    except ValueError:
                        valor_final = 0.00

                    # 5. Criar o Equipamento
                    novo_equipamento = Equipamento.objects.create(
                        nome=row['PRODUTO'],
                        unidade=unidade,
                        tipo=tipo,
                        responsavel=responsavel_final, # Campo com a regra de fallback
                        valor=valor_final,
                        status=status_map.get(str(row['STATUS']).strip().upper(), 'uso'),
                        ativo=True
                    )
                    from control.models import HistoricoTransferencia # Coloque isso lá no topo do arquivo junto com os outros imports
                    
                    HistoricoTransferencia.objects.create(
                        equipamento=novo_equipamento,
                        unidade_origem=None,
                        unidade_destino=novo_equipamento.unidade,
                        responsavel_destino=novo_equipamento.responsavel,
                        motivo="Cadastro Inicial do Equipamento no sistema (Via Planilha).",
                        usuario=usuario_padrao # Como é via script, não temos request.user
                    )
                    sucesso += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erro na linha {index + 2}: {e}"))
                    erros += 1

        self.stdout.write(self.style.SUCCESS(f"Finalizado! Sucesso: {sucesso} | Erros: {erros}"))