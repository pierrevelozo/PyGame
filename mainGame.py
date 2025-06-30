##########################################################
####        N A V I O    C A T A    M O E D A S       ####
##########################################################
#### Prof. Filipo Novo Mor - filipomor.com            ####
#### github.com/ProfessorFilipo                       ####
####                                                  ####
##########################################################
#### Editado por Pierre Velozo - pierrevelozo.com     ####
#### github.com/pierrevelozo                          ####
####                                                  ####
#### Editado em 27/06/25.                             ####
####                                                  ####
##########################################################

import pygame
from pygame import gfxdraw
import random
import sys

pygame.init()

#
# Configurações iniciais
#
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bang!!")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)

# ========== TIROS ==========
BULLET_SIZE      = (10, 4)
BULLET_SPEED     = 12            # pixels por frame
FIRE_COOLDOWN_MS = 350           # intervalo mínimo entre disparos
bullet_group = pygame.sprite.Group()   # armazena todos os projéteis

MOEDA_TAMANHO = (20, 20)

# Carregar a imagem do fundo (altere o caminho para sua imagem real)
background_img = pygame.image.load(r'./Assets/space.png').convert()
background_img = pygame.transform.scale(background_img, (HEIGHT, background_img.get_height()))
background_img = pygame.transform.scale(background_img, (WIDTH, background_img.get_width()))

# Player1
player1_sprite_img = pygame.image.load(r'./Assets/shrek.png').convert_alpha()
# Opcionalmente, ajuste o tamanho do sprite
player1_sprite_img = pygame.transform.rotate(player1_sprite_img, 0)
player1_sprite_img = pygame.transform.smoothscale(player1_sprite_img, (100, 100))

# Player2
player2_sprite_img = pygame.image.load(r'./Assets/will.png').convert_alpha()
# Opcionalmente, ajuste o tamanho do sprite
player2_sprite_img = pygame.transform.rotate(player2_sprite_img, 0)
player2_sprite_img = pygame.transform.smoothscale(player2_sprite_img, (100, 100))

#
# Função para configurar a dificuldade
#
def configurar_dificuldade(nivel):
    if nivel == 1:
        qtd_moedas = 0
        v_min = 2
        v_max = 3
    elif nivel == 2:
        qtd_moedas = 25
        v_min = 3
        v_max = 4
    elif nivel == 3:
        qtd_moedas = 35
        v_min = 4
        v_max = 6
    else:
        qtd_moedas = 15
        v_min = 2
        v_max = 3
    return qtd_moedas, v_min, v_max

def load_animation_frames(prefix, total_frames=10, tamanho=MOEDA_TAMANHO):
    frames = []
    for i in range(1, total_frames + 1):
        filename = f'{prefix}_{i}.png'
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.smoothscale(image, tamanho)
        frames.append(image)
    return frames

class Bullet(pygame.sprite.Sprite):
    """Projétil disparado por um jogador."""
    def __init__(self, x, y, direction, owner):
        """
        direction  : +1 (direita) ou -1 (esquerda)
        owner      : 'p1' ou 'p2'  – quem disparou (para não causar dano a si mesmo)
        """
        super().__init__()
        self.image  = pygame.Surface(BULLET_SIZE)
        self.image.fill((255, 0, 0))
        self.rect   = self.image.get_rect(center=(x, y))
        self.vel_x  = direction * BULLET_SPEED
        self.owner  = owner

    def update(self):
        self.rect.x += self.vel_x
        if not screen.get_rect().colliderect(self.rect):
            self.kill()                      # destrói quando sai da tela

# Classe do player1
class Player1(pygame.sprite.Sprite):
    def __init__(self):

        super().__init__()
        self.image = player1_sprite_img  # sprite carregado
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT - 100))
        self.speed = 8
        self.carga = 0
        self.max_carga = 100
        self.hp        = 100     # vida
        self.last_shot = 0       # controla cadência de tiro

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys_pressed[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys_pressed[pygame.K_DOWN]:
            self.rect.y += self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def voltar_ao_porto(self):
        self.rect.midbottom = (WIDTH // 2, HEIGHT - 100)
        self.carga = 0

class Player2(pygame.sprite.Sprite):
    def __init__(self):
        
        super().__init__()
        self.image = player2_sprite_img  # sprite carregado
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT - 100))
        self.speed = 8
        self.carga = 0
        self.max_carga = 100
        self.hp        = 100     # vida
        self.last_shot = 0       # controla cadência de tiro

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_a]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_d]:
            self.rect.x += self.speed
        if keys_pressed[pygame.K_w]:
            self.rect.y -= self.speed
        if keys_pressed[pygame.K_s]:
            self.rect.y += self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def voltar_ao_porto(self):
        self.rect.midbottom = (WIDTH // 2, HEIGHT - 100)
        self.carga = 0

# Instanciar o player1
player1 = Player1()
player2 = Player2()


#
# Loop principal do jogo
#
running = True
while running:
    clock.tick(60)  # 60 frames por segundo
    

    # Processar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # ---------- DISPARO DE PROJÉTEIS ----------
    now_ms = pygame.time.get_ticks()

    coordenada_x_do_player1 = player1.rect.x
    coordenada_y_do_player1 = player1.rect.y

    coordenada_x_do_player2 = player2.rect.x
    coordenada_y_do_player2 = player2.rect.y

    if coordenada_x_do_player1 < coordenada_x_do_player2:
        direcao = 1
    else: 
        direcao = -1

    if keys[pygame.K_BACKSPACE]:
        # Player1 atira para a direita
        if now_ms - player1.last_shot >= FIRE_COOLDOWN_MS:
            bullet_group.add(

                Bullet(*player1.rect.midright, direction= (1 * direcao), owner='p1')
            )
            player1.last_shot = now_ms

    if keys[pygame.K_SPACE]:

        # Player2 atira para a esquerda
        if now_ms - player2.last_shot >= FIRE_COOLDOWN_MS:
            bullet_group.add(

                Bullet(*player2.rect.midleft,  direction= (-1 * direcao), owner='p2')
            )
            player2.last_shot = now_ms

    # Atualiza movimento do player1
    player1.update(keys)
    player2.update(keys)

    bullet_group.update()

    # ---------- COLISÃO: projéteis atingem jogadores ----------
    hits_p1 = [b for b in bullet_group if b.owner == 'p2' and b.rect.colliderect(player1.rect)]
    hits_p2 = [b for b in bullet_group if b.owner == 'p1' and b.rect.colliderect(player2.rect)]

    for b in hits_p1:
        player1.hp -= 10
        b.kill()
        print(f'Player1 HP: {player1.hp}')
    for b in hits_p2:
        player2.hp -= 10
        b.kill()
        print(f'Player2 HP: {player2.hp}')

    if player1.hp <= 0 or player2.hp <= 0:
        vencedor = 'Player2' if player1.hp <= 0 else 'Player1'
        print(f'{vencedor} venceu!')
        running = False

    #
    # Desenhar a tela
    #
    screen.blit(background_img, (0, 0))
    # Pode adicionar desenho do porto se desejar
    # screen.blit(port_sprite, port_rect) # nao esquecer de carregar a imagem e criar o rect
    score_text = f" "
    score_surface = FONT.render(score_text, True, (255, 255, 255))

    bullet_group.draw(screen)

    #screen.blit(sea_sprite, sea_rect)
    screen.blit(player1.image, player1.rect)
    screen.blit(player2.image, player2.rect)


    screen.blit(FONT.render(f'HP P1: {player1.hp}', True, (0,255,100)), (10,140))
    screen.blit(FONT.render(f'HP P2: {player2.hp}', True, (0,200,255)), (10,110))

    # Se desejar, pode aqui aumentar o nível
    if player1.carga >= player1.max_carga:
        nivel += 1
        if nivel > 3:
            nivel = 3  # máximo nível
        qtd_moedas, v_min, v_max = configurar_dificuldade(nivel)

    # Atualiza a tela
    pygame.display.flip()

# Encerra o pygame ao sair do loop
pygame.quit()
sys.exit()
