import pygame
import time as std_time


def main():
    screen = pygame.display.set_mode((480, 700), 0, 32)
    background = pygame.image.load("background.png")
    player = pygame.image.load("me1.png")


    x = 480/2-100/2
    y = 530
    speed = 5

    while True:
        screen.blit(background, (0, 0))
        screen.blit(player, (x, y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_w] or key_pressed[pygame.K_UP]:
            print("上")
            y -= speed
        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            print("左")
            x -= speed
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            print("右")
            x += speed
        if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
            print("下")
            y += speed
        if key_pressed[pygame.K_SPACE]:
            print("空格")


        pygame.display.update()
        std_time.sleep(0.01)


if __name__ == "__main__":
    main()
