import pygame
import sys
import csv
import os


import perguntas
import personagens
import aprendizado
import adivinhar

# --- CONFIGURAÇÕES DO PYGAME ---
pygame.init()
LARGURA, ALTURA = 800, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Akinator Python")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 102, 204)
VERDE = (0, 204, 102)
VERMELHO = (204, 0, 0)
CINZA_CLARO = (220, 220, 220)
CINZA_ESCURO = (50, 50, 50)

# --- CONFIGURAÇÃO DE CAMINHOS ---
DIRETORIO_ATUAL = os.path.dirname(__file__)
PASTA_FONTES = os.path.join(DIRETORIO_ATUAL, "..", "fontes") 
PASTA_DATA = os.path.join(DIRETORIO_ATUAL, "..", "data")
PASTA_IMAGENS_PERS = os.path.join(PASTA_FONTES, "personagens")

# Caminhos de fontes
caminho_fonte_saxmono = os.path.join(PASTA_FONTES, "saxmono.ttf")
caminho_fonte_oups = os.path.join(PASTA_FONTES, "Oups.otf")

# Fontes
FONTE_GRANDE = pygame.font.SysFont("Arial", 40, bold=True)
FONTE_MEDIA = pygame.font.SysFont("Arial", 28)
FONTE_PEQUENA = pygame.font.SysFont("Arial", 20)

# Tentativa de carregar fontes personalizadas com segurança
try:
    FONTE_SAXMONO = pygame.font.Font(caminho_fonte_saxmono, 30)
except FileNotFoundError:
    FONTE_SAXMONO = FONTE_MEDIA

try:
    FONTE_OUPS = pygame.font.Font(caminho_fonte_oups, 40)
except FileNotFoundError:
    FONTE_OUPS = FONTE_GRANDE

# --- ESTADOS DO JOGO ---
ESTADO_MENU = 0
ESTADO_PERGUNTA = 1
ESTADO_CHUTE = 2
ESTADO_WIN = 3
ESTADO_LOSE_INPUT = 4
ESTADO_NOVA_PERGUNTA = 5
ESTADO_RESPOSTA_NOVA = 6

class AkinatorGame:
    def __init__(self):
        self.estado = ESTADO_MENU
        
        # Carregar Dados
        self.arq_perguntas = os.path.join(PASTA_DATA, "perguntas.csv")
        self.arq_personagens = os.path.join(PASTA_DATA, "personagens.csv")
        self.arq_bayes = os.path.join(PASTA_DATA, "dados_bayes.csv")

        self.perguntas = perguntas.carregar_perguntas(self.arq_perguntas)
        self.personagens = personagens.carregar_personagens(self.arq_personagens)
        self.dados_bayes = aprendizado.carregar_dados_bayes(self.arq_bayes)
        
        # Controle
        self.lista_perguntas_ids = list(self.perguntas.keys())
        self.indice_pergunta = 0
        self.respostas_usuario = {} 
        self.chute_nome = ""
        self.chute_score = 0
        self.texto_entrada = ""
        
        # Variáveis temp
        self.temp_nome_novo = ""
        self.temp_pergunta_nova = ""
        self.LIMIAR_CERTEZA = 3.5

        # 1. Imagem do Logo
        self.imagem_akinator = None
        caminho_logo = os.path.join(PASTA_FONTES, "akinator_logo.png")
        try:
            img = pygame.image.load(caminho_logo)
            self.imagem_akinator = pygame.transform.smoothscale(img, (500, int(img.get_height() * (500/img.get_width()))))
            self.rect_akinator = self.imagem_akinator.get_rect(midtop=(LARGURA//2, 90))
        except FileNotFoundError:
            pass
        
        # 2. Imagem Acertou (Vitória)
        self.imagem_vitoria = None
        caminho_vitoria = os.path.join(PASTA_FONTES, "akinator_acertou.png")
        try:
            img_vit = pygame.image.load(caminho_vitoria)
            self.imagem_vitoria = pygame.transform.smoothscale(img_vit, (300, int(img_vit.get_height() * (300/img_vit.get_width()))))
            self.rect_vitoria = self.imagem_vitoria.get_rect(midtop=(LARGURA//2, 150))
        except FileNotFoundError:
            # Fallback
            self.imagem_vitoria = self.imagem_akinator 
            self.rect_vitoria = self.rect_akinator

        # 3. Imagem Errou (Derrota)
        self.imagem_derrota = None
        caminho_derrota = os.path.join(PASTA_FONTES, "akinator_errou.png")
        try:
            img_err = pygame.image.load(caminho_derrota)
            self.imagem_derrota = pygame.transform.smoothscale(img_err, (300, int(img_err.get_height() * (300/img_err.get_width()))))
            self.rect_derrota = self.imagem_derrota.get_rect(midtop=(LARGURA//2, 100))
        except FileNotFoundError:
            # Fallback
            self.imagem_derrota = self.imagem_akinator 
            self.rect_derrota = self.imagem_akinator.get_rect(midtop=(LARGURA//2, 100))

        # Imagem do Personagem (Carregada Dinamicamente)
        self.img_personagem_atual = None

    def resetar_jogo(self):
        self.indice_pergunta = 0
        self.respostas_usuario = {}
        self.texto_entrada = ""
        self.temp_nome_novo = ""
        self.temp_pergunta_nova = ""
        self.img_personagem_atual = None 
        self.estado = ESTADO_PERGUNTA

    def carregar_imagem_personagem(self, nome):
        self.img_personagem_atual = None 
        nome_limpo = nome.strip()
        
        
        caminhos_possiveis = [
            os.path.join(PASTA_IMAGENS_PERS, f"{nome_limpo}.png"),
            os.path.join(PASTA_IMAGENS_PERS, f"{nome_limpo}.jpg"),
            os.path.join(PASTA_IMAGENS_PERS, f"{nome_limpo}.jpeg"),
        ]

        # Verifica se a pasta existe antes de tudo
        if not os.path.exists(PASTA_IMAGENS_PERS):
            print(f"ERRO CRÍTICO: A pasta de imagens não existe: {PASTA_IMAGENS_PERS}")
            return

        for caminho in caminhos_possiveis:
            print(f"Procurando em: {caminho}")
            
            if os.path.exists(caminho):
                try:
                    img = pygame.image.load(caminho).convert_alpha() # .convert_alpha ajuda na performance e transparência
                    
                    altura_max = 250
                    escala = altura_max / img.get_height()
                    largura_nova = int(img.get_width() * escala)
                    
                    self.img_personagem_atual = pygame.transform.smoothscale(img, (largura_nova, altura_max))
                    return
                except Exception as e:
                    print(f"-> ERRO AO LER O ARQUIVO: {e}")
                    print("O arquivo pode estar corrompido ou não ser uma imagem real")
            else:
                print("Arquivo não existe neste caminho")
        

    def aprender_personagem(self, nome_correto):
        # 1. Salva na lista se for novo
        nomes_existentes = [p["nome"] for p in self.personagens]
        if nome_correto not in nomes_existentes:
            self.personagens.append({"nome": nome_correto})
            personagens.salvar_personagens(self.arq_personagens, self.personagens)
            
        # 2. Atualiza Bayes
        aprendizado.atualizar_memoria(nome_correto, self.respostas_usuario, self.dados_bayes)
        
        # 3. Salva Bayes
        aprendizado.salvar_dados_bayes(self.arq_bayes, self.dados_bayes)

    def calcular_melhor_chute(self):
        melhor_nome, melhor_score = adivinhar.adivinhar(self.respostas_usuario, self.personagens, self.dados_bayes)
        ranking = []
        for p in self.personagens:
            s = adivinhar.calcular_score(p["nome"], self.respostas_usuario, self.dados_bayes)
            ranking.append(s)
        ranking.sort(reverse=True)
        vice = ranking[1] if len(ranking) > 1 else -9999
        return melhor_nome, melhor_score, vice

    def finalizar_aprendizado_complexo(self, resposta_nova_s_n):
        nomes = [p["nome"] for p in self.personagens]
        if self.temp_nome_novo not in nomes:
            self.personagens.append({"nome": self.temp_nome_novo})
            personagens.salvar_personagens(self.arq_personagens, self.personagens)

        aprendizado.atualizar_memoria(self.temp_nome_novo, self.respostas_usuario, self.dados_bayes)

        if self.chute_nome and self.temp_pergunta_nova:
            aprendizado.aprender_nova_pergunta(
                self.temp_pergunta_nova, resposta_nova_s_n, self.temp_nome_novo, self.chute_nome
            )
            self.perguntas = perguntas.carregar_perguntas(self.arq_perguntas)
            self.lista_perguntas_ids = list(self.perguntas.keys())

        aprendizado.salvar_dados_bayes(self.arq_bayes, self.dados_bayes)
        self.estado = ESTADO_MENU

    def processar_resposta(self, resposta):
        pid = self.lista_perguntas_ids[self.indice_pergunta]
        self.respostas_usuario[pid] = resposta
        self.indice_pergunta += 1
        
        fim_perguntas = self.indice_pergunta >= len(self.lista_perguntas_ids)
        parada_antecipada = False
        
        if self.indice_pergunta >= 5:
            melhor, score, vice = self.calcular_melhor_chute()
            if (score - vice) > self.LIMIAR_CERTEZA:
                parada_antecipada = True

        if parada_antecipada or fim_perguntas:
            melhor, score, _ = self.calcular_melhor_chute()
            self.chute_nome = melhor
            self.chute_score = score
            
            if melhor:
                self.carregar_imagem_personagem(melhor)
            
            self.estado = ESTADO_CHUTE

    def desenhar_texto_centralizado(self, texto, y, fonte, cor=PRETO):
        surf = fonte.render(texto, True, cor)
        rect = surf.get_rect(center=(LARGURA//2, y))
        TELA.blit(surf, rect)
    
    def desenhar_texto_multilinha(self, texto, y_inicial, fonte, cor=PRETO):
        """Quebra o texto em várias linhas se passar da largura da tela."""
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        
        # Define uma margem (Tela inteira - 100px de folga nas bordas)
        largura_maxima = LARGURA - 100 

        for palavra in palavras:
            # Testa como ficaria a linha se adicionássemos essa palavra
            teste_linha = linha_atual + palavra + " "
            w, h = fonte.size(teste_linha)

            if w < largura_maxima:
                # Se couber, adiciona a palavra na linha atual
                linha_atual = teste_linha
            else:
                # Se não couber, salva a linha anterior e começa uma nova
                linhas.append(linha_atual)
                linha_atual = palavra + " "
        
        # Adiciona a última linha que sobrou
        linhas.append(linha_atual)

        # Desenha todas as linhas calculadas
        altura_linha = fonte.get_linesize()
        for i, linha in enumerate(linhas):
            # Desenha centralizado, descendo um pouco a cada linha (y + altura)
            surf = fonte.render(linha, True, cor)
            rect = surf.get_rect(center=(LARGURA//2, y_inicial + (i * altura_linha)))
            TELA.blit(surf, rect)

    def desenhar_botao(self, texto, x, y, w, h, cor_base, cor_hover, acao=None):
        mouse = pygame.mouse.get_pos()
        clique = pygame.mouse.get_pressed()
        rect = pygame.Rect(x,y, w, h)
        cor = cor_hover if rect.collidepoint(mouse) else cor_base
        pygame.draw.rect(TELA, cor, rect, border_radius=10)
        texto_surf = FONTE_MEDIA.render(texto, True, BRANCO)
        texto_rect = texto_surf.get_rect(center=rect.center)
        TELA.blit(texto_surf, texto_rect)
        if rect.collidepoint(mouse) and clique[0] == 1 and acao:
            pygame.time.delay(200)
            acao()

    def loop(self):
        rodando = True
        while rodando:
            TELA.fill(BRANCO)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                    sys.exit()
                
                if evento.type == pygame.KEYDOWN:
                    if self.estado in [ESTADO_LOSE_INPUT, ESTADO_NOVA_PERGUNTA]:
                        if evento.key == pygame.K_RETURN:
                            if self.texto_entrada.strip():
                                if self.estado == ESTADO_LOSE_INPUT:
                                    nome_digitado = self.texto_entrada.strip()
                                    nomes_existentes_lower = [p["nome"].lower() for p in self.personagens]
                                    
                                    # Se JÁ EXISTE o personagem
                                    if nome_digitado.lower() in nomes_existentes_lower:
                                        nome_real = next(p["nome"] for p in self.personagens if p["nome"].lower() == nome_digitado.lower())
                                        
                                        # Agora a função existe!
                                        self.aprender_personagem(nome_real)
                                        self.estado = ESTADO_MENU
                                        print(f"Reforçando personagem existente: {nome_real}")
                                    else:
                                        # Se é NOVO
                                        self.temp_nome_novo = nome_digitado
                                        self.texto_entrada = ""
                                        
                                        # Se não tinha chute (Banco Vazio), salva direto
                                        if not self.chute_nome:
                                            self.aprender_personagem(self.temp_nome_novo)
                                            self.estado = ESTADO_MENU
                                            print(f"Primeiro personagem salvo: {self.temp_nome_novo}")
                                        else:
                                            # Se teve conflito, pede pergunta
                                            self.estado = ESTADO_NOVA_PERGUNTA
                                
                                elif self.estado == ESTADO_NOVA_PERGUNTA:
                                    self.temp_pergunta_nova = self.texto_entrada.strip()
                                    self.texto_entrada = ""
                                    self.estado = ESTADO_RESPOSTA_NOVA

                        elif evento.key == pygame.K_BACKSPACE:
                            self.texto_entrada = self.texto_entrada[:-1]
                        else:
                            self.texto_entrada += evento.unicode

            # --- TELAS ---
            if self.estado == ESTADO_MENU:
                if self.imagem_akinator:
                    TELA.blit(self.imagem_akinator, self.rect_akinator)
                else:
                    self.desenhar_texto_centralizado("AKINATOR PYTHON", 150, FONTE_GRANDE, AZUL)
                
                self.desenhar_texto_centralizado(f"Conheço {len(self.personagens)} personagens", 60, FONTE_SAXMONO)
                self.desenhar_botao("JOGAR", 180, 480, 200, 60, VERDE, (0, 255, 0), lambda: self.resetar_jogo())
                self.desenhar_botao("SAIR", 420, 480, 200, 60, VERMELHO, (255, 50, 50), lambda: sys.exit())

            elif self.estado == ESTADO_PERGUNTA:
                pid = self.lista_perguntas_ids[self.indice_pergunta]
                self.desenhar_texto_centralizado(f"Pergunta {self.indice_pergunta + 1}/{len(self.perguntas)}", 100, FONTE_SAXMONO, CINZA_ESCURO)
                self.desenhar_texto_centralizado(self.perguntas[pid], 200, FONTE_MEDIA)
                self.desenhar_botao("SIM", 200, 400, 150, 80, VERDE, (0, 255, 0), lambda: self.processar_resposta('s'))
                self.desenhar_botao("NÃO", 450, 400, 150, 80, VERMELHO, (255, 50, 50), lambda: self.processar_resposta('n'))
                
            elif self.estado == ESTADO_CHUTE:
                self.desenhar_texto_centralizado("Eu acho que é...", 50, FONTE_MEDIA)
                
                y_nome = 200
                if self.img_personagem_atual:
                    rect_img = self.img_personagem_atual.get_rect(center=(LARGURA//2, 200))
                    TELA.blit(self.img_personagem_atual, rect_img)
                    y_nome = 350
                
                self.desenhar_texto_centralizado(self.chute_nome, y_nome, FONTE_GRANDE, AZUL)
                self.desenhar_texto_centralizado(f"(Certeza: {self.chute_score:.2f})", y_nome + 50, FONTE_PEQUENA, CINZA_ESCURO)
                
                self.desenhar_botao("SIM!", 250, 480, 120, 60, VERDE, (0, 255, 0), lambda: setattr(self, 'estado', ESTADO_WIN))
                self.desenhar_botao("NÃO", 430, 480, 120, 60, VERMELHO, (255, 50, 50), lambda: setattr(self, 'estado', ESTADO_LOSE_INPUT))
                
            elif self.estado == ESTADO_WIN:
                self.desenhar_texto_centralizado("AHA! Eu sabia!", 80, FONTE_GRANDE, AZUL)
                
                if self.imagem_vitoria:
                    TELA.blit(self.imagem_vitoria, self.rect_vitoria)
                
                self.desenhar_botao("Menu Principal", 300, 500, 200, 60, CINZA_ESCURO, PRETO, lambda: setattr(self, 'estado', ESTADO_MENU))
                
                if self.chute_nome:
                     self.aprender_personagem(self.chute_nome)
                     self.chute_nome = None
                     
            elif self.estado == ESTADO_LOSE_INPUT:
                # 1. Título
                self.desenhar_texto_centralizado("Puts, errei!", 50, FONTE_SAXMONO)
                
                # 2. Imagem
                if self.imagem_derrota:
                    TELA.blit(self.imagem_derrota, self.rect_derrota)
                
                # 3. Pergunta
                self.desenhar_texto_centralizado("Quem era o personagem?", 500, FONTE_MEDIA)
                
                # 4. Caixa
                pygame.draw.rect(TELA, BRANCO, (200, 350, 400, 50))
                pygame.draw.rect(TELA, AZUL, (200, 350, 400, 50), 2)
                
                # Texto
                texto_surf = FONTE_MEDIA.render(self.texto_entrada, True, PRETO)
                TELA.blit(texto_surf, (210, 360))
                
                # Instrução
                self.desenhar_texto_centralizado("Digite o nome e aperte ENTER", 420, FONTE_SAXMONO, CINZA_ESCURO)

            elif self.estado == ESTADO_NOVA_PERGUNTA:
                # NOVO (Quebra linha automaticamente):
                texto_pergunta = f"Qual pergunta diferencia {self.temp_nome_novo} de {self.chute_nome}?"
                self.desenhar_texto_multilinha(texto_pergunta, 50, FONTE_SAXMONO)
                pygame.draw.rect(TELA, BRANCO, (50, 250, 700, 50))
                pygame.draw.rect(TELA, AZUL, (50, 250, 700, 50), 2)
                texto_surf = FONTE_MEDIA.render(self.texto_entrada, True, PRETO)
                TELA.blit(texto_surf, (60, 260))
                self.desenhar_texto_centralizado("Digite a pergunta e tecle ENTER", 350, FONTE_SAXMONO, CINZA_ESCURO)

            elif self.estado == ESTADO_RESPOSTA_NOVA:
                self.desenhar_texto_centralizado(f"Para {self.temp_nome_novo}, a resposta é:", 150, FONTE_SAXMONO)
                self.desenhar_texto_centralizado(f"'{self.temp_pergunta_nova}'", 220, FONTE_MEDIA, AZUL)
                self.desenhar_botao("SIM", 200, 400, 150, 80, VERDE, (0, 255, 0), lambda: self.finalizar_aprendizado_complexo('s'))
                self.desenhar_botao("NÃO", 450, 400, 150, 80, VERMELHO, (255, 50, 50), lambda: self.finalizar_aprendizado_complexo('n'))

            pygame.display.update()

if __name__ == "__main__":
    game = AkinatorGame()
    game.loop()