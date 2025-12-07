import math

def calcular_score(personagem, respostas_usuario, dados_bayes):
    # Calcula o score (soma de logaritmos) para evitar "underflow numérico", numeros próximos de zero
    # Quanto maior o valor (menos negativo), maior a probabilidade
    
    score = 0.0
    dados_p = dados_bayes.get(personagem, {})

    for pid, resp_usuario in respostas_usuario.items():
        stats = dados_p.get(pid, {"sim": 0, "nao": 0})
        total = stats["sim"] + stats["nao"]

        # Suavização de Laplace
        if resp_usuario == 's':
            prob = (stats["sim"] + 1) / (total + 2)
        else:
            prob = (stats["nao"] + 1) / (total + 2)

        score += math.log(prob)

    return score

def adivinhar(respostas_usuario, personagens, dados_bayes):
    # Encontra o personagem com o maior score logarítmico
    melhor_nome = None
    melhor_score = -float('inf') # Infinito negativo

    for p in personagens:
        nome = p["nome"]
        score = calcular_score(nome, respostas_usuario, dados_bayes)

        if score > melhor_score:
            melhor_score = score
            melhor_nome = nome

    return melhor_nome, melhor_score