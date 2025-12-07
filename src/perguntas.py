import csv
import os

def carregar_perguntas(caminho="data/perguntas.csv"):
    # Carrega as perguntas do CSV.
    # Retorna um dicionário: {id_pergunta: texto_pergunta}
    
    perguntas = {}

    # Verifica se o arquivo existe no caminho padrão
    if not os.path.exists(caminho):
        # Se não, tenta achar relativo a onde este script está salvo (ex: ../data/)
        base_dir = os.path.dirname(__file__)
        caminho_relativo = os.path.join(base_dir, "..", caminho)
        
        if os.path.exists(caminho_relativo):
            caminho = caminho_relativo
        else:
            # Se não achar em lugar nenhum, retorna vazio para não travar
            print(f"AVISO: Arquivo de perguntas não encontrado: {caminho}")
            return perguntas

    with open(caminho, newline='', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            pid = linha["id"].strip()
            texto = linha["texto"].strip()
            perguntas[pid] = texto

    return perguntas