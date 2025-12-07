import os
import perguntas
import personagens
import aprendizado
import adivinhar

# --- CONFIGURAÇÃO DE CAMINHOS ---
# Tenta achar a pasta data voltando um nível (padrão do projeto)
DIRETORIO_ATUAL = os.path.dirname(__file__)
PASTA_DATA = os.path.join(DIRETORIO_ATUAL, "..", "data")

# Fallback: Se não achar, tenta na pasta atual
if not os.path.exists(PASTA_DATA):
    PASTA_DATA = os.path.join(DIRETORIO_ATUAL, "data")

ARQ_PERGUNTAS = os.path.join(PASTA_DATA, "perguntas.csv")
ARQ_PERSONAGENS = os.path.join(PASTA_DATA, "personagens.csv")
ARQ_BAYES = os.path.join(PASTA_DATA, "dados_bayes.csv")

def jogar():
    print("\n" + "="*40)
    print(" 🧞‍♂️  AKINATOR PYTHON (Versão Terminal)")
    print("="*40 + "\n")

    # 1. Carregar Dados
    dict_perguntas = perguntas.carregar_perguntas(ARQ_PERGUNTAS)
    lista_personagens = personagens.carregar_personagens(ARQ_PERSONAGENS)
    dados_bayes = aprendizado.carregar_dados_bayes(ARQ_BAYES)

    if not dict_perguntas:
        print("❌ ERRO: Nenhuma pergunta encontrada.")
        return

    print(f"Conheço {len(lista_personagens)} personagens. Pense em um...")
    input("Pressione ENTER para começar...")

    respostas_usuario = {}
    lista_ids = list(dict_perguntas.keys())
    
    chute_nome = None
    chute_score = 0

    # 2. Loop de Perguntas
    for i, pid in enumerate(lista_ids):
        texto = dict_perguntas[pid]
        
        # Validação de input (s/n)
        while True:
            r = input(f"[{i+1}] {texto} (s/n): ").strip().lower()
            if r in ('s', 'n'): break
        
        respostas_usuario[pid] = r

        # Parada Antecipada (após 5 perguntas)
        if i >= 4:
            # Calcula o melhor e o vice para ver a diferença
            melhor, score_melhor = adivinhar.adivinhar(respostas_usuario, lista_personagens, dados_bayes)
            
            # Ranking manual para pegar o vice
            ranking = []
            for p in lista_personagens:
                s = adivinhar.calcular_score(p["nome"], respostas_usuario, dados_bayes)
                ranking.append(s)
            ranking.sort(reverse=True)
            score_vice = ranking[1] if len(ranking) > 1 else -9999

            # Se a diferença for grande (> 3.5), para de perguntar
            if (score_melhor - score_vice) > 3.5:
                print("\n💡 Tive uma ideia! Parando perguntas...")
                break

    # 3. Adivinhação
    chute_nome, chute_score = adivinhar.adivinhar(respostas_usuario, lista_personagens, dados_bayes)

    acerto = "n"
    if chute_nome:
        print(f"\n🔮 Meu palpite é: **{chute_nome}** (Certeza: {chute_score:.2f})")
        while True:
            acerto = input("Acertei? (s/n): ").strip().lower()
            if acerto in ('s', 'n'): break
    else:
        print("\n😵 Não faço a menor ideia de quem seja.")

    # 4. Resultado e Aprendizado
    if acerto == 's':
        print("\n😎 AHA! Eu sabia! Mais uma vitória para a IA.")
        # Reforça a memória
        if chute_nome:
            aprendizado.atualizar_memoria(chute_nome, respostas_usuario, dados_bayes)
            aprendizado.salvar_dados_bayes(ARQ_BAYES, dados_bayes)

    else:
        # ERROU - Hora de aprender
        print("\n😔 Poxa, errei!")
        nome_real = input("Quem era o personagem? ").strip()

        # Verifica se o personagem já existe na lista (case insensitive)
        nomes_existentes = [p["nome"].lower() for p in lista_personagens]
        
        if nome_real.lower() in nomes_existentes:
            # CASO 1: Personagem já existia, só reforça
            nome_corrigido = next(p["nome"] for p in lista_personagens if p["nome"].lower() == nome_real.lower())
            print(f"Ah, o {nome_corrigido}! Eu devia ter imaginado.")
            
            aprendizado.atualizar_memoria(nome_corrigido, respostas_usuario, dados_bayes)
            aprendizado.salvar_dados_bayes(ARQ_BAYES, dados_bayes)
        
        else:
            # CASO 2: Personagem Novo
            print(f"\n🆕 Aprendendo novo personagem: {nome_real}")
            
            # Se houve um chute errado, pede a diferença
            if chute_nome:
                print(f"Preciso diferenciar {nome_real} de {chute_nome}.")
                nova_pergunta = input("Digite uma pergunta que diferencie os dois: ").strip()
                
                while True:
                    resp_nova = input(f"Para {nome_real}, a resposta é (s/n)? ").strip().lower()
                    if resp_nova in ('s', 'n'): break
                
                # Salva o novo personagem na lista
                lista_personagens.append({"nome": nome_real})
                personagens.salvar_personagens(ARQ_PERSONAGENS, lista_personagens)
                
                # Atualiza memória das perguntas antigas
                aprendizado.atualizar_memoria(nome_real, respostas_usuario, dados_bayes)
                
                # Cria a nova pergunta e aplica pesos opostos
                aprendizado.aprender_nova_pergunta(nova_pergunta, resp_nova, nome_real, chute_nome)
                
            else:
                # Se não tinha chute (banco vazio), só salva
                lista_personagens.append({"nome": nome_real})
                personagens.salvar_personagens(ARQ_PERSONAGENS, lista_personagens)
                
                aprendizado.atualizar_memoria(nome_real, respostas_usuario, dados_bayes)
                aprendizado.salvar_dados_bayes(ARQ_BAYES, dados_bayes)

    print("\n✨ Jogo finalizado! Até a próxima.")

if __name__ == "__main__":
    jogar()