import csv
import os

def carregar_personagens(caminho="data/personagens.csv"):
    #Lê o CSV e retorna uma lista de dicionários com os personagens
    personagens = []


    if not os.path.exists(caminho):
        print("Arquivo não encontrado. Criando base padrão...")
        
        # Lista de personagens iniciais
        lista_padrao = [
            {"nome": "Mario"},
            {"nome": "Bowser"},
            {"nome": "Bob Esponja"},
            {"nome": "Homem-Aranha"},
            {"nome": "Harry Potter"},
            {"nome": "Shrek"},
            {"nome": "Princesa Fiona"},
            {"nome": "Yoda"},
            {"nome": "Darth Vader"},
            {"nome": "Gato de botas"}
        ]
        
        # Salva essa lista imediatamente no arquivo
        salvar_personagens(caminho, lista_padrao)
        
        # Retorna a lista padrão para o jogo já começar com ela
        return lista_padrao
 
    # Se o arquivo já existe, lê normalmente
    with open(caminho, newline='', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            personagens.append(linha)

    return personagens

def salvar_personagens(caminho, personagens):
    # Sobrescreve o arquivo CSV com a lista atualizada
    if not personagens:
        return

    with open(caminho, "w", newline='', encoding="utf-8") as f:
        # Pega as chaves do primeiro personagem para criar o cabeçalho (ex: ["nome"])
        fieldnames = personagens[0].keys()
        
       
        escritor = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        
        escritor.writeheader()
        escritor.writerows(personagens)