import pygame
import sys
import os
import random 
import json

# Inicialize o Pygame e o mixer
pygame.init()
pygame.mixer.init()

# Fonte padrão
fonte = pygame.font.Font(None, 74)
cor_texto = (0, 0, 0)

# Pausa o jogo até apertarem Enter
pause_game = False

# Definições de câmeras
camera_x = 0
camera_y = 0
camera_shake_x = 0
camera_shake_y = 0
camera_shake = 0

# Lista de entidades
entidades = []
personagem = None
gambiarraNextLevel = None

def shake_me_up(strength):
    global camera_shake_x, camera_shake_y, camera_shake

    camera_shake_x = camera_x
    camera_shake_y = camera_y
    camera_shake = strength

def carrega_imagem_escalada(imagem_path, width = None, height = None):
    try:
        imagem = pygame.image.load(imagem_path)
        if width == None or height == None:
            return imagem 
        return pygame.transform.scale(imagem, (width, height))
    except pygame.error as e:
        print(f"Erro ao carregar imagens: {e}")
        pygame.quit()
        sys.exit()
        
def carrega_frames_dir(frames_dir, width = None, height = None):
    try:
        frames = [pygame.image.load(os.path.join(frames_dir, f)) for f in sorted(os.listdir(frames_dir)) if f.endswith('.png')]
        
        if width == None or height == None:
            return frames
        # Redimensionar os quadros do personagem
        return [pygame.transform.scale(frame, (width, height)) for frame in frames]
    except pygame.error as e:
        print(f"Erro ao carregar imagens: {e}")
        pygame.quit()
        sys.exit()


def random_se_list(valor):
    if isinstance(valor, list):
        return random.uniform(valor[0], valor[1])
    return valor

def render_multi_line(text):
    imagens = []
    lines = text.splitlines()
    
    for i, linha in enumerate(lines):
        imagens.append(fonte.render(linha, True, cor_texto))

    max_width = max([img.get_width() for img in imagens])
    total_height = sum([img.get_height() for img in imagens])
    gap = 10
    text_img = pygame.Surface((max_width, total_height + gap * (len(imagens) - 1)), pygame.SRCALPHA)
    y_offset = 0
    for img in imagens:
        center_x = max_width // 2 - img.get_width() // 2
        text_img.blit(img, (center_x, y_offset))
        y_offset += img.get_height() + gap
    return text_img

class Entidade:
    hitbox_offset = pygame.Rect(0, 0, 0, 0)
    collides = True
    hidden = False
    animated = False
    frames = []
    animation_timer = 0
    current_frame = 0
    frame_rate = 0.1

    def __init__(self, x, y, width, height, image=None):
        
        if isinstance(image, str):
            #foi passada uma string para uma imagem
            if os.path.isdir(image):
                self.frames = carrega_frames_dir(image,  width, height)
            else:
                self.frames = [carrega_imagem_escalada(image, width, height)]

            image = self.frames[0]
            if len(self.frames) > 1:
                self.animated = True

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image

    def draw_postprocess(self, screen):
        pass

    def draw(self, screen):
        if not self.hidden:
            screen.blit(self.image, (self.x - camera_x, self.y - camera_y))
            # Desenha as linhas da hitbox 
            #hitbox = self.get_final_hitbox()
            #pygame.draw.rect(screen, (255, 0, 0), hitbox, 2)
    
    def read_hitbox_offset_from_json(self, entity):        
        hitbox_x = entity["hitbox_x"] if "hitbox_x" in entity else  0
        hitbox_y = entity["hitbox_y"] if "hitbox_y" in entity else  0
        hitbox_width = entity["hitbox_width"] if "hitbox_width" in entity else  0
        hitbox_height = entity["hitbox_height"] if "hitbox_height" in entity else  0

        self.set_hitbox_offset( hitbox_x, hitbox_y, hitbox_width, hitbox_height )
            
    def set_hitbox_offset(self, x, y, width, height):
        self.hitbox_offset = pygame.Rect(x, y, width, height)

    def get_final_hitbox(self):
        hitbox = pygame.Rect(self.x + self.hitbox_offset.x, self.y + self.hitbox_offset.y, self.width + self.hitbox_offset.width, self.height + self.hitbox_offset.height)
        hitbox.x -= camera_x
        hitbox.y -= camera_y
        return hitbox
    
    def find_collision_direction(self, other):
        if not self.collides or not other.collides:
            return None
        
        self_hitbox = self.get_final_hitbox()
        other_hitbox = other.get_final_hitbox()
        dx = (self_hitbox.x + self_hitbox.width / 2) - (other_hitbox.x + other_hitbox.width / 2)
        dy = (self_hitbox.y + self_hitbox.height / 2) - (other_hitbox.y + other_hitbox.height / 2)
        if abs(dx) > abs(dy):
            if dx > 0:
                return "right"
            else:
                return "left"
        else:
            if dy > 0:
                return "top"
            else:
                return "bottom" 
        
    # Testa colisão
    def collides_with(self, other):
        if not self.collides or not other.collides:
            return False
        self_hitbox = self.get_final_hitbox()
        other_hitbox = other.get_final_hitbox()
        return self_hitbox.colliderect(other_hitbox)
    
    # Testa colisão com todas as entidades, exceto a própria
    def has_collision(self, x, y):
        temp_x = self.x
        temp_y = self.y
        self.x = x
        self.y = y
        for entidade in entidades:
            if entidade != self and entidade.collides_with(self):
                self.x = temp_x
                self.y = temp_y
                return entidade
            
        self.x = temp_x
        self.y = temp_y
        return None

    def update(self):
        # Processa animação, se tiver
        if self.animated:
            self.animation_timer += self.frame_rate
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
        pass

    def kill(self):
        global entidades
        entidades.remove(self)

class Personagem(Entidade):
    animation_timer = 0
    current_frame = 0
    frame_rate = 0.1  # Velocidade de troca dos quadros
    personagem_frames = []
    still_frame = None  # Frame específico para quando estiver parado
    moving = False
    facing_right = True  # Armazenar a direção que o personagem está virado
    novo_x = 0
    novo_y = 0
    isDead = False

    def __init__(self, x, y, width, height, frames_dir, speed, jump_strength):
        self.personagem_frames = carrega_frames_dir(frames_dir, width, height)
        self.deadImage = carrega_imagem_escalada("image/mariodead.png", width, height)
        super().__init__(x, y, width, height, self.personagem_frames[0])
        self.novo_x = x
        self.novo_y = y
        self.still_frame = self.personagem_frames[0]  # Definindo o primeiro frame como o de "parado"
        self.speed = speed
        self.jump_strength = jump_strength
        self.velocity_y = 0
        self.gravity = 0.5
        self.is_jumping = False
        self.on_ground = True
        self.moving = False  # Inicialmente, o personagem está parado
        self.facing_right = True  # Inicialmente, o personagem está virado para a direita

        # Carregar o som do pulo
        self.jump_sound = pygame.mixer.Sound('sons/pulo.mp3')  # Substitua pelo caminho do seu arquivo de áudio
        
    def update(self):
        
        if self.isDead == True:
            self.image = self.deadImage
            return
        
        
        self.moving = False
        self.novo_y = self.y
        if self.is_jumping:
            self.novo_y = self.y + self.velocity_y
            self.velocity_y += self.gravity

        if self.novo_y >= SCREEN_HEIGHT - self.height - FLOOR_HEIGHT:
            self.novo_y = SCREEN_HEIGHT - self.height - FLOOR_HEIGHT
            self.y  = SCREEN_HEIGHT - self.height - FLOOR_HEIGHT
            self.velocity_y = 0
            self.is_jumping = False
            self.on_ground = True

        # Verifica se há movimento nas teclas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.move_left()
        if keys[pygame.K_RIGHT]:
            self.move_right()

        # Animação do personagem
        if self.moving:
            self.animation_timer += self.frame_rate
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.personagem_frames)

        # Verificar a direção do personagem
            if self.facing_right:
                self.image = self.personagem_frames[self.current_frame]  # Imagem normal
            else:
                self.image = pygame.transform.flip(self.personagem_frames[self.current_frame], True, False)  # Imagem invertida

        else:
            # Definir o frame específico quando estiver parado
            if self.facing_right:
                self.image = self.still_frame  # Imagem normal parada
            else:
                self.image = pygame.transform.flip(self.still_frame, True, False)  # Imagem invertida parada


        # Verifica colisão com outras entidades
        collision = self.has_collision(self.novo_x, self.novo_y)
        if collision:
            collision.show_text = True
            direction = self.find_collision_direction(collision)
            if direction == "right" or direction == "left":
                self.y = self.novo_y
            elif direction == "bottom":
                self.x = self.novo_x
                self.on_ground = True
                self.velocity_y = 1
                
            elif direction == "top":
                self.x = self.novo_x
                self.velocity_y = 0
            else:
                self.x = self.novo_x
                self.y = self.novo_y
        else:            
            self.x = self.novo_x
            self.y = self.novo_y

    def move_left(self):
        if self.isDead == True:
            return         
        self.novo_x = self.x - self.speed
        self.moving = True
        self.facing_right = False 
    
    def move_right(self):
        if self.isDead == True:
            return         
        self.novo_x = self.x + self.speed
        self.moving = True
        self.facing_right = True

    def jump(self):  
        #self.die()
        #return
        if self.isDead == True:
            return         
        if self.on_ground:
            self.velocity_y = self.jump_strength
            self.is_jumping = True
            self.on_ground = False
            self.jump_sound.play()  # Tocar efeito sonoro

    def die(self):
        if self.isDead == False:
            self.isDead = True
            entidades.append(Particles(personagem.x, personagem.y, personagem.width, personagem.height))
            

class Particle():
    x: float
    y: float
    speed_x: float
    speed_y: float
    end_y: float
    delay: float
    
    def __init__(self, x, y, delay):
        self.delay = delay
        self.x = x 
        self.y = y 
        self.speed_x = random.uniform(-5,5)
        self.speed_y = -random.uniform(5, 20)
        self.end_y = SCREEN_HEIGHT - random.uniform(0, FLOOR_HEIGHT)

    def update(self):
        if self.delay > 0:
            self.delay -= 1
            return
        
        if(self.y < self.end_y) or self.speed_y < 0:
            self.speed_y += 0.2
            self.x += self.speed_x
            self.y += self.speed_y

    def draw(self):
        if self.delay > 0:
            return
        
        color = (255,0,0)
        pos = (self.x - camera_x, self.y - camera_y )
        screen.fill(color, (pos, (2,2)))


class ParticleSprite(Particle):
    def __init__(self, x, y, delay, imagem):
        super().__init__(x,y,delay)
        self.imagem = carrega_imagem_escalada(imagem)
        self.end_y = SCREEN_HEIGHT - FLOOR_HEIGHT - self.imagem.get_height() + 3
        self.speed_x = 5
        self.speed_y = -15

    def draw(self):
        if self.delay > 0:
            return
        pos = (self.x - camera_x, self.y - camera_y )
        screen.blit(self.imagem, pos)


class Particles(Entidade):
    particles: Particle = []

    def __init__(self, x, y, width, height):
        super().__init__(x, y, 0, 0, None)
        for i in range(10000):
            
            self.particles.append(Particle(x + random.uniform(120, 130 ),random.uniform(y+90, y+ 120), random.uniform(0, 100)))
        
        self.particles.append(ParticleSprite(personagem.x+50,personagem.y+50, 0, "image/cabecamario.png"))
    
    def update(self):
        for particle in self.particles:
            particle.update()


    def draw(self, screen):
        pass
            
    
    def draw_postprocess(self, screen):
        for particle in self.particles:
            particle.draw()
        pass




class Bloco(Entidade):
    tempo_espera = 0
    texto = "Você bateu no bloco!"
    show_text = False

    def __init__(self, x, y, width, height, image_path, texto):
        super().__init__(x, y, width, height, image_path)
        self.texto = texto
        self.fundo_texto = carrega_imagem_escalada('image/fundo_texto.png')
        self.make_text()

    def update(self):
        if self.tempo_espera > 0:
            self.tempo_espera -= 1
            if self.tempo_espera == 0:
                self.show_text = False
        pass


    def make_text(self):
        # Monta caixa de texto
        rendered_text = render_multi_line(self.texto)
        self.text_img  = pygame.transform.scale(self.fundo_texto, (rendered_text.get_width() + 100, rendered_text.get_height() + 100))
        self.text_img.blit(rendered_text, (50, 50))
        self.text_rect = self.text_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def draw_postprocess(self, screen):
        global pause_game
        if self.show_text and self.tempo_espera == 0:
            screen.blit(self.text_img, self.text_rect)
            self.tempo_espera = 100
            pause_game = True

class Decoracao(Entidade):
    speed = 0
    basespeed = 0
    respawn = False

    def __init__(self, x, y, width, height, image, basespeed, respawn):
        super().__init__(x, y, width, height, image)
        self.collides = False
        self.basespeed = basespeed
        self.respawn = respawn
        self.speed = random_se_list(basespeed)

    def update(self):
        super().update()

        #Movimento
        if self.speed != 0:
            #Tem velocidade
            x = self.x - self.speed 
            #confere o respawn
            if self.respawn:
                if x < -self.width + camera_x:
                    x = SCREEN_WIDTH + camera_x
                    #self.y = random.randint(0, SCREEN_HEIGHT // 2)
                    self.speed = random_se_list(self.basespeed)            
                elif x > self.width + camera_x+SCREEN_WIDTH+1:
                    x =  camera_x - self.width + 1
                    #self.y = random.randint(0, SCREEN_HEIGHT // 2)
                    self.speed = random_se_list(self.basespeed)            
            
            self.x = x

        pass

    def draw(self, screen):
        screen.blit(self.image, (self.x - camera_x, self.y - camera_y))

    def draw_postprocess(self, screen):
        pass


class Parallax(Entidade):
    layer = 0
    start_x = 0
    start_y = 0

    def __init__(self, x, y, width, height, image, layer):
        super().__init__(x, y, width, height, image)
        self.collides = False
        self.layer = layer
        self.start_x = x
        self.start_y = y

    def update(self):
        super().update()

        #Calcula posição com base no layer
        self.x = self.start_x + (self.start_x - camera_x) * self.layer
        self.y = self.start_y - camera_y
        
        pass

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def draw_postprocess(self, screen):
        pass


class OverlayTransparente(Entidade):
    tempo = 0    
    fadestart = 0

    def __init__(self, x, y, width, height, image, tempo):
        super().__init__(x, y, width, height, image)
        self.collides = False
        self.tempo = tempo
        self.fadestart = tempo * 0.2

    def update(self):
        super().update()

        if self.tempo == 0:
            self.kill()

        if self.tempo > 0:
            self.tempo -= 1
        pass

    def draw(self, screen):
        pass

    def draw_postprocess(self, screen):
        if self.tempo > 0:
            if self.tempo < self.fadestart:
                #calcula a transparencia
                alpha = 255 * (self.tempo / self.fadestart)
                self.image.set_alpha(alpha)
                
            screen.blit(self.image, (self.x, self.y))
        pass



class Plane(Entidade):

    def __init__(self, x, y, width, height, image, speed_x, drop_x, ativacao_x):
        super().__init__(x, y, width, height, image)
        self.ativacao_x = ativacao_x
        self.speed_x = speed_x
        self.drop_x = drop_x
        self.dropped_bomb = False
        self.collides = False
        self.hidden = True

    def update(self):
        global entidades
        if personagem.x > self.ativacao_x and self.hidden == True:
            self.hidden = False
            pygame.mixer.music.load('sons/bomba.mp3')  # Substitua pelo caminho do seu arquivo de áudio
            pygame.mixer.music.set_volume(0.5)  # Ajuste o volume (0.0 a 1.0)
            pygame.mixer.music.play(-1)  # -1 faz a música tocar em loop

            if gambiarraNextLevel != None:
                gambiarraNextLevel.setTrap()

        if self.hidden == False:
            self.x += self.speed_x
            if self.x < self.drop_x and not self.dropped_bomb:
                self.dropped_bomb = True
                entidades.insert(0, Bomb(self.x, self.y))
        


class Bomb(Entidade):

    def __init__(self, x, y):
 
        image = "image/decoracao_fabrica/bomb.png"
        width = 337 // 5
        height = 396 // 5
        super().__init__(x, y, width, height, image)
        self.speed_y = 1
        self.explode_y = SCREEN_HEIGHT - FLOOR_HEIGHT - height - 160
        self.exploded = False
        self.collides = False

    def update(self):
        if not self.exploded:
            global camera_shake_x
            global camera_shake_y
            gonnaExplode = False
            shake_me_up(5)
            camera_shake_x = self.x - SCREEN_WIDTH / 2
            camera_shake_y = self.y  - SCREEN_HEIGHT / 2
            if camera_shake_y > 0:
                camera_shake_y = 0

            #Testar colisoes
            #if self.has_collision(self.x, self.y + self.speed_y):
            #    gonnaExplode = True
                                
            if self.y > self.explode_y:
                gonnaExplode = True
        
            if gonnaExplode == False:
                self.y += self.speed_y
            else:
                self.exploded = True
                # cria imagem branca
                pygame.mixer.music.fadeout(1500)
                white = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                white.fill((255, 255, 255))            
                entidades.append(OverlayTransparente(0,0,1920,1080,white, 1200))    
                entidades.insert(entidades.index(personagem), Explosion(self.x, self.y))
                self.kill()
        

class Explosion(Entidade):
    def __init__(self, x, y):
        self.collides = False
        # Carregar os frames da explosão
        frame_width = 1 #SCREEN_WIDTH//2  # Largura desejada do frame
        frame_height = 1 #SCREEN_HEIGHT//2  # Altura desejada do frame
        self.x = x - frame_width // 2
        y = SCREEN_HEIGHT - frame_height
        self.contador = 0
        super().__init__(self.x, y, frame_width, frame_height, "image/decoracao_fabrica/explosion/explosion_3.png")
        
    def update(self):
        
        if self.contador > 150:
            carrega_nivel("agua.json")
            white = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            white.fill((255, 255, 255))            
            entidades.append(OverlayTransparente(0,0,1920,1080,white, 50))  

        self.contador +=1
        return super().update()
    


class NextLevel(Entidade):
    level = ""
    def __init__(self, x, y, width, height, level):
        
        imagem_tubo = "image/cano.png"
        super().__init__(x, y, width, height, imagem_tubo)
        self.collides = True
        self.isTrap = False
        
        self.level = level

    def setTrap(self):
        self.image = carrega_imagem_escalada("image/canotrap.png", self.width, self.height)
        self.isTrap = True
        shake_me_up(50)

    def update(self):
        if self.isTrap == False:
            if keys[pygame.K_DOWN]:
                temp_y = self.y
                self.y-=100
                if self.collides_with(personagem):
                    carrega_nivel(self.level)

                self.y = temp_y
                
        #pass
    def draw_postprocess(self, screen):
        pass

class Boss(Entidade):
    tempo_espera = 0
    textos = "Você bateu no bloco!"
    creditos = "Desenvolvedor: Igor Ascoli\nDesign: Vitor Adriano Johann\nPesquisa: Betina Bock\n          Guilherme Baum\nReferências: readme.txt\n\n\n\nFim"
    show_text = False

    def __init__(self, x, y, width, height, image_path, textos, gatilho_x):
        super().__init__(x, y, width, height, image_path)
        self.collides = False
        self.fim = False
        self.textos = textos
        self.gatilho_x = gatilho_x
        self.last_gatilho = 0
        self.tempolaser = 0
        self.delaytchau = 0
        self.tchau = False
        self.fundo_texto = carrega_imagem_escalada('image/fundo_texto.png')
        self.make_text()

    def update(self):
        if self.tchau == True:
            self.x += 1
                

        if self.delaytchau > 0:
            self.delaytchau -= 1
            if self.delaytchau == 0:
                self.faz_tchau()

        if camera_x + SCREEN_WIDTH > self.x + self.width:
            self.x = camera_x + SCREEN_WIDTH - self.width

        novo_gatilho = personagem.x // self.gatilho_x
        if novo_gatilho > self.last_gatilho:
            
            self.last_gatilho = novo_gatilho
            
            if novo_gatilho  > len(self.textos):
                if self.fim == False:
                    self.fim = True
                    self.tempolaser = 100
                    self.delaytchau = 200
                    personagem.die()
            else:
                self.make_text()                
                self.show_text = True

        if self.tempo_espera > 0:
            self.tempo_espera -= 1
            if self.tempo_espera == 0:
                self.show_text = False
        pass

    def faz_tchau(self):
        if self.tchau == False:
            self.make_creditos()            
            self.image = pygame.transform.flip(self.image, True, False)  # Imagem invertida
            self.tchau = True
            

    def make_text(self):
        # Monta caixa de texto
        rendered_text = render_multi_line(self.textos[self.last_gatilho - 1])
        self.text_img  = pygame.transform.scale(self.fundo_texto, (rendered_text.get_width() + 100, rendered_text.get_height() + 100))
        self.text_img.blit(rendered_text, (50, 50))
        self.text_rect = self.text_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def make_creditos(self):
        # Monta caixa de texto
        rendered_text = render_multi_line(self.creditos)
        self.text_img  = pygame.transform.scale(self.fundo_texto, (rendered_text.get_width() + 100, rendered_text.get_height() + 100))
        self.text_img.blit(rendered_text, (50, 50))
        self.text_rect = self.text_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def draw_postprocess(self, screen):
        global pause_game
        if self.tchau == True:
            screen.blit(self.text_img, self.text_rect)
        else:
            if self.tempolaser > 0:
                self.tempolaser -= 1
                start_pos = (self.x - camera_x + 10, self.y - camera_y + 116)
                for i in range(10):                
                    end_pos = (personagem.x + 120 - camera_x + random.uniform(-10,10), personagem.y + 120 - camera_y + random.uniform(-10,10))
                    color = (0, random.uniform(192,255), random.uniform(225,255))
                    shake_me_up(5)
                    pygame.draw.line(screen, color, start_pos, end_pos, random.randint(1,4))

            else: 
                if self.show_text and self.tempo_espera == 0:
                    screen.blit(self.text_img, self.text_rect)
                    self.tempo_espera = 10
                    pause_game = True


def carrega_nivel(arquivo):
    global entidades, chao_img, cor_fundo, camera_x, camera_y, fundo_img, fonte, camera_x, camera_y, camera_shake
    
    pygame.mixer.music.load('sons/musica.mp3')  # Substitua pelo caminho do seu arquivo de áudio
    pygame.mixer.music.set_volume(0.5)  # Ajuste o volume (0.0 a 1.0)
    pygame.mixer.music.play(-1)  # -1 faz a música tocar em loop
    camera_shake = 0
    camera_x = 0
    camera_y = 0    
    # Abre arquivo json do mapa
    f = open(arquivo, 'r', encoding="utf-8")
    
    level = json.load(f)
    chao_img = level["chao"] if "chao" in level else "image/grama.png"
    chao_img = carrega_imagem_escalada(chao_img, SCREEN_WIDTH, FLOOR_HEIGHT)

    fundo_img = level["imagem_fundo"] if "imagem_fundo" in level else None
    if fundo_img != None:
        fundo_img = carrega_imagem_escalada(fundo_img, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Carrega a fonte pixelada
    fonte_ttf = level["fonte"] if "fonte" in level else None
    fonte = pygame.font.Font(fonte_ttf, 50)  # 24 é o tamanho da fonte

    cor_fundo = level["cor_fundo"]
    cor_fundo = (cor_fundo[0] or 135, cor_fundo[1] or 206, cor_fundo[2] or 235)

    # carrega entidades
    entidades = []    
    for entity in level['entities']:
        x = random_se_list(entity["x"])
        y = random_se_list(entity["y"])
        width = random_se_list(entity["width"])
        height = random_se_list(entity["height"])

        
        if "prescale" in entity:
            prescale = entity["prescale"]
            width *= prescale
            height *= prescale
            y -= height


        match entity["type"]:
            case "decoracao":
                entidades.append(Decoracao(x,y,width,height, entity["image"], entity["speed"] or 0, entity["respawn"] or False))

            case "parallax":
                entidades.append(Parallax(x,y,width,height, entity["image"], entity["layer"] or 0))
            
            case "nextlevel":
                global gambiarraNextLevel
                nextlevel = NextLevel(x,y,width,height, entity["level"])
                nextlevel.read_hitbox_offset_from_json(entity)
                entidades.append(nextlevel)
                gambiarraNextLevel = nextlevel

            case "personagem":
                # exceção para o tipo personagem: declara a variavel global
                global personagem

                # Adicionar entidade personagem
                personagem = Personagem(x, y, width, height, entity["frames_dir"], entity["speed"], entity["jump_strength"])
                personagem.read_hitbox_offset_from_json(entity)
                entidades.append(personagem)
                print("Carregou personagem")


            case "bloco":                
                entidades.append(Bloco(x, y, width, height, entity["image"], entity["texto"]))

            case "boss":                
                entidades.append(Boss(x, y, width, height, entity["image"], entity["falas"], entity["gatilho_x"]))

            case "plane":                
                entidades.append(Plane(x, y, width, height, entity["image"], entity["speed_x"], entity["drop_x"], entity["ativacao_x"]))

            case "overlay":                
                entidades.append(OverlayTransparente(x, y, width, height, entity["image"], entity["tempo"]))
            #case  ....

    # Closing file
    f.close()
    #shake_me_up(100)

def desenha_fundo():
    screen.fill(cor_fundo)
    if fundo_img != None:
        screen.blit(fundo_img, (background_x, 0 - camera_y)) 
        # Desenha o fundo repetido para garantir que não haja lacunas
        screen.blit(fundo_img, (background_x + SCREEN_WIDTH, 0 - camera_y))
        screen.blit(fundo_img, (background_x - SCREEN_WIDTH, 0 - camera_y))


def desenha_chao():
    screen.blit(chao_img, (background_x, SCREEN_HEIGHT - FLOOR_HEIGHT - camera_y)) 
    # Desenha o fundo repetido para garantir que não haja lacunas
    screen.blit(chao_img, (background_x + SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_HEIGHT - camera_y))
    screen.blit(chao_img, (background_x - SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_HEIGHT - camera_y))


# Configurações da tela
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FLOOR_HEIGHT = 70
CAMERA_TARGET_X = SCREEN_WIDTH // 5
CAMERA_TARGET_Y = SCREEN_HEIGHT - 200

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Jogo 2D com Pulo")
print(pygame.display.Info())

# Carregar música de fundo
pygame.mixer.music.load('sons/musica.mp3')  # Substitua pelo caminho do seu arquivo de áudio
pygame.mixer.music.set_volume(0.5)  # Ajuste o volume (0.0 a 1.0)
pygame.mixer.music.play(-1)  # -1 faz a música tocar em loop

# Tente carregar as imagens
carrega_nivel("boss.json")
#carrega_nivel("praca.json")


# FPS
clock = pygame.time.Clock()
FPS = 60

while True:
    # Lidar com eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Captura de teclas
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        
        personagem.move_left()
    if keys[pygame.K_RIGHT]:
        personagem.move_right()
    if keys[pygame.K_SPACE]:
        personagem.jump()
    

    # Atualiza a posição da câmera
    camera_x += (personagem.x - camera_x - CAMERA_TARGET_X ) * 0.05

    if camera_shake > 0:
        camera_x = camera_shake_x + random.uniform(-camera_shake, camera_shake)
        camera_y = camera_shake_y + random.uniform(-camera_shake, camera_shake)
        if camera_y > 0: 
            camera_y = -camera_y
        camera_shake -= 1 

    # Ajusta a posição do fundo para criar um efeito de movimento
    background_x = -camera_x % SCREEN_WIDTH
    background_y = CAMERA_TARGET_Y-camera_y % SCREEN_HEIGHT

    # Atualizar tela
    desenha_fundo()

    # Atualiza entidades
    for entidade in entidades:
        entidade.update()

    # Desenha entidades
    for entidade in entidades:
        if isinstance(entidade, Personagem): 
            desenha_chao()
        entidade.draw(screen)

    # Desenha entidades pós-processamento
    for entidade in entidades:
        entidade.draw_postprocess(screen)

    # Atualizar a tela
    pygame.display.flip()

    if pause_game:
        while pause_game:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pause_game = False

    # Controla a taxa de atualização
    clock.tick(FPS)