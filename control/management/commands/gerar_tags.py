from django.core.management.base import BaseCommand
from django.db import transaction
from control.models import Equipamento, ClasseEquipamento

class Command(BaseCommand):
    help = 'Gera tags para equipamentos que ainda não possuem'

    def handle(self, *args, **options):
        with transaction.atomic():
            # 1. Pegamos todas as classes para resetar o contador por classe
            classes = ClasseEquipamento.objects.all()
            
            total_processado = 0
            
            for classe in classes:
                # Pegamos a sigla definida na classe (ex: TIC)
                prefixo = str(classe.sigla).upper() if classe.sigla else "TAG"
                
                # 2. Buscamos equipamentos desta classe que ainda não possuem TAG
                # Ordenamos por ID ou data de criação para manter a lógica histórica
                equipamentos_sem_tag = Equipamento.objects.filter(
                    tipo__classe=classe, 
                    tag__isnull=True
                ).order_by('id') # ou 'created_at' se o seu Base tiver esse campo
                
                if not equipamentos_sem_tag.exists():
                    continue
                    
                # 3. Verificamos qual o último número já existente para essa sigla (se houver algum com tag)
                ultimo = Equipamento.objects.filter(tag__startswith=prefixo).order_by('tag').last()
                
                if ultimo and ultimo.tag:
                    try:
                        # Tenta extrair o número da tag existente (ex: TIC-0005 -> 5)
                        ultimo_numero = int(ultimo.tag.split('-')[-1])
                        contador = ultimo_numero + 1
                    except (ValueError, IndexError):
                        contador = 1
                else:
                    contador = 1
                    
                # 4. Atribuímos as novas tags
                for eq in equipamentos_sem_tag:
                    nova_tag = f"{prefixo}-{contador:04d}"
                    eq.tag = nova_tag
                    eq.save()
                    
                    print(f"Equipamento: {eq.nome} -> Nova TAG: {nova_tag}")
                    contador += 1
                    total_processado += 1
            self.stdout.write(self.style.SUCCESS('Processo concluído!'))

        print(f"Sucesso! {total_processado} equipamentos foram atualizados.")

# Para rodar no shell:
# exec(open('gerar_tags.py').read())
# executar_migracao_tags()