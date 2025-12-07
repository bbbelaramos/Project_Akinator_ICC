# 🧞‍♂️ Akinator Python - Algoritmo Naive Bayes

> Um clone do Akinator desenvolvido em Python que utiliza Probabilidade Bayesiana e Aprendizado de Máquina para adivinhar personagens e aprender com o usuário.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Pygame](https://img.shields.io/badge/Library-Pygame-green?style=flat&logo=pygame)
![Status](https://img.shields.io/badge/Status-Concluído-success)

## 📋 Sobre o Projeto

Este projeto foi desenvolvido como trabalho final da disciplina de **Introdução à Ciência da Computação (ICC)**. O objetivo é simular o jogo "Akinator", onde o computador tenta adivinhar em qual personagem o usuário está pensando através de uma série de perguntas "Sim" ou "Não".

O diferencial deste projeto é que ele **não utiliza uma árvore de decisão estática**. Ele usa um modelo probabilístico (Naive Bayes) que aprende dinamicamente. Se o computador errar, ele pede ao usuário para ensinar quem era o personagem e qual pergunta diferencia o chute errado do correto.

## 🚀 Funcionalidades

* **Interface Gráfica (GUI):** Desenvolvida com `pygame` para uma experiência visual interativa.
* **Cérebro Bayesiano:** Utiliza o Teorema de Bayes com Suavização de Laplace para calcular probabilidades.
* **Aprendizado Contínuo:**
    * Adiciona novos personagens automaticamente.
    * Cria novas perguntas dinamicamente para resolver conflitos entre personagens.
    * Reforça o conhecimento sobre personagens existentes a cada partida.
* **Parada Antecipada:** O algoritmo para de perguntar assim que a certeza estatística atinge um limiar seguro, tornando o jogo mais rápido.

## 📦 Estrutura do Projeto

```text
Projeto/
├── src/
│   ├── main_gui.py       # Loop principal e Interface Gráfica
│   ├── adivinhar.py      # Lógica matemática (Cálculo de Score/Probabilidade)
│   ├── jogo.py           # Versáo terminal(Console)
│   ├── aprendizado.py    # Lógica de escrita no CSV e atualização de pesos
│   ├── perguntas.py      # Gerenciador de perguntas
│   └── personagens.py    # Gerenciador de lista de personagens
├── data/
│   ├── dados_bayes.csv   # O "Cérebro" (Matriz de Pesos)
│   ├── personagens.csv   # Lista de nomes conhecidos
│   └── perguntas.csv     # Lista de perguntas e IDs
├── assets/               # Imagens e Fontes
│   ├── personagens/      # Fotos dos personagens (ex: Mario.png)
│   ├── akinator_logo.png
│   └── ...
└── README.md
