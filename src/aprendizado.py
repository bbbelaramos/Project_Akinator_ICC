import csv
import os
from collections import defaultdict

def carregar_dados_bayes(caminho):
    # Carrega o banco de dados em um dicionário aninhado que cria chaves automaticamente
    # Retorna: dados[personagem][pergunta] = {"sim": X, "nao": Y}
    dados = defaultdict(lambda: defaultdict(lambda: {"sim": 0, "nao": 0}))

    if not os.path.exists(caminho):
        return dados

    with open(caminho, newline='', encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            p = linha["personagem"]
            q = linha["pergunta"]
            dados[p][q]["sim"] = int(linha["sim"])
            dados[p][q]["nao"] = int(linha["nao"])

    return dados

def salvar_dados_bayes(caminho, dados):
    # Escreve a estrutura da memória para o arquivo CSV
    with open(caminho, "w", newline='', encoding="utf-8") as f:
        campos = ["personagem", "pergunta", "sim", "nao"]
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()

        for personagem, perguntas in dados.items():
            for pergunta, contadores in perguntas.items():
                escritor.writerow({
                    "personagem": personagem,
                    "pergunta": pergunta,
                    "sim": contadores["sim"],
                    "nao": contadores["nao"]
                })

def atualizar_memoria(personagem, respostas_usuario, dados):
    # Recebe o personagem correto e as respostas dadas na partida
    # Aumenta os contadores de Sim/Não no 'cérebro' (dados)
    _ = dados[personagem] 

    for pergunta_id, resposta in respostas_usuario.items():
        if resposta == 's':
            dados[personagem][pergunta_id]["sim"] += 1
        else:
            dados[personagem][pergunta_id]["nao"] += 1

def aprender_nova_pergunta(texto_pergunta, resposta_para_novo, nome_novo, nome_velho_chute):
 
    # Cria uma nova pergunta no CSV e atualiza os pesos para diferenciar
    # o personagem novo do antigo.
    
    import perguntas  # Import local para evitar erro de ciclo ou duplicidade
    
    # 1. Definir caminhos (Assume estrutura ../data em relação a este arquivo)
    base_dir = os.path.dirname(__file__)
    caminho_perguntas = os.path.join(base_dir, "..", "data", "perguntas.csv")
    caminho_bayes = os.path.join(base_dir, "..", "data", "dados_bayes.csv")
    
    # Fallback se não achar (caso a estrutura de pastas seja diferente)
    if not os.path.exists(caminho_perguntas):
         caminho_perguntas = os.path.join(base_dir, "data", "perguntas.csv")
         caminho_bayes = os.path.join(base_dir, "data", "dados_bayes.csv")

    # 2. Gerar novo ID (ex: p21)
    dict_perguntas = perguntas.carregar_perguntas(caminho_perguntas)
    if dict_perguntas:
        # Extrai o número de 'p1', 'p2', etc.
        ids_numericos = [int(k[1:]) for k in dict_perguntas.keys() if k.startswith('p') and k[1:].isdigit()]
        if ids_numericos:
            novo_num = max(ids_numericos) + 1
        else:
            novo_num = 1
    else:
        novo_num = 1
    
    novo_id = f"p{novo_num}"

    # 3. Salvar no CSV de Perguntas

    with open(caminho_perguntas, "a+", newline='', encoding="utf-8") as f:
        
        
        f.seek(0, os.SEEK_END) # Vai para o final do arquivo
        tamanho = f.tell()     # Vê qual o tamanho do arquivo
        
        if tamanho > 0:
            # Volta 1 caractere para ver qual é o último
            f.seek(tamanho - 1)
            ultimo_char = f.read(1)
            
            # Se o último caractere não for uma quebra de linha, adiciona uma
            if ultimo_char != '\n':
                f.write('\n')

        writer = csv.writer(f)
        writer.writerow([novo_id, texto_pergunta])

    # 4. Atualizar o Cérebro (Bayes) para diferenciar
    dados = carregar_dados_bayes(caminho_bayes)
    
    PESO_DIFERENCIACAO = 50  # Peso alto para garantir a diferença imediata
    
    # Para o NOVO personagem, usamos a resposta que o usuário deu
    if resposta_para_novo == 's':
        dados[nome_novo][novo_id]["sim"] += PESO_DIFERENCIACAO
    else:
        dados[nome_novo][novo_id]["nao"] += PESO_DIFERENCIACAO
        
    # Para o VELHO personagem (chute errado), assumimos o OPOSTO
    if resposta_para_novo == 's':
        dados[nome_velho_chute][novo_id]["nao"] += PESO_DIFERENCIACAO
    else:
        dados[nome_velho_chute][novo_id]["sim"] += PESO_DIFERENCIACAO
        
    salvar_dados_bayes(caminho_bayes, dados)