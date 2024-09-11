import pygame
import sys
import subprocess
import os

# Inicializar o Pygame
pygame.init()

# Inicializar o mixer do Pygame
pygame.mixer.init()

# Definir dimens�es da tela
largura_tela = 1920
altura_tela = 1080
tela = pygame.display.set_mode((largura_tela, altura_tela))

# Definir t�tulo da janela
pygame.display.set_caption("Menu do Jogo")

# Carregar m�sica de fundo
pygame.mixer.music.load('sons/musica.mp3')  # Substitua pelo caminho do seu arquivo de �udio
pygame.mixer.music.set_volume(0.5)  # Ajuste o volume (0.0 a 1.0)
pygame.mixer.music.play(-1)  # -1 faz a m�sica tocar em loop

# Carregar efeitos sonoros
efeito_iniciar = pygame.mixer.Sound('sons/play.mp3')  # Substitua pelo caminho do seu arquivo de efeito sonoro
efeito_sair = pygame.mixer.Sound('sons/sair.mp3')  # Substitua pelo caminho do seu arquivo de efeito sonoro
efeito_navegacao = pygame.mixer.Sound('sons/play.mp3')

# Carregar imagem de fundo
fundo = pygame.image.load('image/fundo_menu.png')
fundo = pygame.transform.scale(fundo, (largura_tela, altura_tela))

# Carregar imagem do t�tulo
imagem_titulo = pygame.image.load('image/corede.png')  # Substitua pelo caminho da sua imagem
imagem_titulo = pygame.transform.scale(imagem_titulo, (1000, 250))  # Ajuste o tamanho conforme necess�rio

# Carregar imagem dos bot�es
imagem_iniciar = pygame.image.load('image/start.png')  # Substitua pelo caminho da sua imagem
imagem_sair = pygame.image.load('image/sair.png')

# Definir tamanhos dos bot�es
tamanho_normal_iniciar = (300, 60)
tamanho_normal_sair = (100, 60)
tamanho_maior_iniciar = (400, 70)
tamanho_maior_sair = (150, 70)

# Definir cores
branco = (255, 255, 255)

# Fun��o para desenhar a imagem clic�vel
def desenhar_imagem(tela, imagem, rect):
    tela.blit(imagem, rect)

# Fun��o principal do menu
def menu_jogo():
    # Definir �reas dos bot�es e centralizar
    botao_iniciar = pygame.Rect(largura_tela // 2 - 150, altura_tela // 2 - 30, *tamanho_normal_iniciar)
    botao_sair = pygame.Rect(largura_tela // 2 - 100, altura_tela // 2 + 150, *tamanho_normal_sair)

    selecionado = None  # Nenhum bot�o est� selecionado inicialmente

    while True:
        # Carregar o fundo
        tela.blit(fundo, (0, 0))

        # Desenhar imagem do t�tulo
        tela.blit(imagem_titulo, (largura_tela // 2 - imagem_titulo.get_width() // 2, altura_tela // 4 - imagem_titulo.get_height() // 2))

        # Desenhar imagem clic�vel
        if selecionado == 'iniciar':
            imagem_iniciar = pygame.transform.scale(pygame.image.load('image/start.png'), tamanho_maior_iniciar)
        else:
            imagem_iniciar = pygame.transform.scale(pygame.image.load('image/start.png'), tamanho_normal_iniciar)
        
        if selecionado == 'sair':
            imagem_sair = pygame.transform.scale(pygame.image.load('image/sair.png'), tamanho_maior_sair)
        else:
            imagem_sair = pygame.transform.scale(pygame.image.load('image/sair.png'), tamanho_normal_sair)

        desenhar_imagem(tela, imagem_iniciar, botao_iniciar)
        desenhar_imagem(tela, imagem_sair, botao_sair)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:  # Se a tecla para cima for pressionada
                    efeito_navegacao.play()
                    if selecionado == 'iniciar':
                        efeito_iniciar.play()  # Tocar efeito sonoro
                        jogo_script = os.path.join(os.path.dirname(__file__), 'jogo.py')
                        subprocess.Popen(['python', jogo_script])
                    selecionado = 'iniciar'
                elif evento.key == pygame.K_DOWN:  # Se a tecla para baixo for pressionada
                    efeito_navegacao.play()
                    if selecionado == 'sair':
                        efeito_sair.play()  # Tocar efeito sonoro
                        pygame.quit()
                        sys.exit()
                    selecionado = 'sair'
                elif evento.key == pygame.K_RETURN:  # Se a tecla Enter for pressionada
                    if selecionado == 'iniciar':
                        efeito_iniciar.play()  # Tocar efeito sonoro
                        jogo_script = os.path.join(os.path.dirname(__file__), 'jogo.py')
                        subprocess.Popen(['python', jogo_script])
                        pygame.quit()
                        sys.exit()
                    elif selecionado == 'sair':
                        efeito_sair.play()  # Tocar efeito sonoro
                        pygame.quit()
                        sys.exit()

        # Atualizar a tela
        pygame.display.update()

# Iniciar o menu
menu_jogo()
