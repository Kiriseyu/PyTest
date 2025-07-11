import random
import pygame
import time as std_time

class HeroPlane():
    def __init__(self,screen):
        self.player = pygame.image.load("me1.png")

        self.x = 480 / 2 - 100 / 2
        self.y = 530
        self.speed = 5

        self.screen = screen
        self.bullets = []


    def key_control(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_w] or key_pressed[pygame.K_UP]:
            # print("上")
            self.y -= self.speed
        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            # print("左")
            self.x -= self.speed
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            # print("右")
            self.x += self.speed
        if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
            # print("下")
            self.y += self.speed
        if key_pressed[pygame.K_SPACE] or key_pressed[pygame.K_j]:
            bullet = Bullet(self.screen, self.x, self.y)
            self.bullets.append(bullet)


    def display(self):
        self.screen.blit(self.player, (self.x, self.y))
        for bullet in self.bullets:
            bullet.auto_move()
            bullet.display()


class Bullet(object ):
    def __init__(self, screen, x, y):
        self.x = x+122/2 -22/2
        self.y = y-22
        self.image = pygame.image.load("bullet1.png")
        self.screen = screen
        self.speed = 3


    def display(self):
        self.screen.blit(self.image, (self.x, self.y))

    def auto_move(self):
        self.y -= self.speed


class EnemyPlane():
    def __init__(self,screen):
        self.player = pygame.image.load("enemy1.png")#69*99

        self.x = 0
        self.y = 0
        self.speed = 5

        self.screen = screen
        self.bullets = []
        self.direction = 'right'

    def display(self):
        self.screen.blit(self.player, (self.x, self.y))
        for bullet in self.bullets:
            bullet.auto_move()
            bullet.display()

    def auto_move(self):
        if self.direction == 'right':
            self.x += self.speed
        elif self.direction == 'left':
            self.x -= self.speed

        if self.x > 480-51:
            self.direction = 'left'
        elif self.x < 0:
            self.direction = 'right'

    def auto_fire(self):
        random_num = random.randint(1, 10)
        if random_num == 6:
            bullet = EnemyBullet(self.screen, self.x, self.y)
            self.bullets.append(bullet)



class EnemyBullet(object ):
    def __init__(self, screen, x, y):
        self.x = x+50/2 -8/2
        self.y = y + 39
        self.image = pygame.image.load("bullet2.png")
        self.screen = screen
        self.speed = 3

    def display(self):
        self.screen.blit(self.image, (self.x, self.y))

    def auto_move(self):
        self.y += self.speed

class GameSound(object):
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.music.load("HOYO-MiX - 独角戏 Monodrama.mp3")
        pygame.mixer.music.set_volume(0.5)

    def playBackgroundMusic(self):
        pygame.mixer.music.play(-1)

def main():
    sound = GameSound()
    sound.playBackgroundMusic()
    screen = pygame.display.set_mode((480, 700), 0, 32)
    background = pygame.image.load("background.png")

    player = HeroPlane(screen)
    enemyplane = EnemyPlane(screen)
    while True:
        screen.blit(background, (0, 0))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        player.key_control()
        player.display()
        enemyplane.display()
        enemyplane.auto_move()
        enemyplane.auto_fire()

        pygame.display.update()
        std_time.sleep(0.01)


if __name__ == "__main__":
    main()
