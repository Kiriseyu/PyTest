import random
import time

import pygame
from pygame import event
from pygame.constants import *

import os,sys

def resource_path(rel):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 会把资源解压到 _MEIPASS 目录
        return os.path.join(sys._MEIPASS, rel)
    return os.path.join(os.path.abspath("."), rel)

# Sprite 精灵
class HeroPlane(pygame.sprite.Sprite):
    # 存放所有飞机的子弹的组
    bullets = pygame.sprite.Group()

    def __init__(self, screen):
        # 这个精灵的初始化方法 必须调用
        pygame.sprite.Sprite.__init__(self)
        # 图片
        self.image = pygame.image.load(resource_path('res/me1.png'))
        # 根据图片image获取矩形的对象
        self.rect = self.image.get_rect()  # rect属性：矩形
        self.rect.topleft = [Manager.bg_size[0] / 2 - 100 / 2, 600]  # 矩形左上角坐
        # 窗口
        self.screen = screen
        # 速度
        self.speed = 15
        # pygame.sprite.Group()生成一个放精灵的对象 类似一个列表
        self.bullets = pygame.sprite.Group()

    def key_control(self):
        """
        按键的监听 用来改变飞机坐标
        """
        # 监听键盘事件  键盘一直按下
        key_pressed = pygame.key.get_pressed()  # 注意这种方式是能够检测到连续按下的，比之前的版本要新

        # 改变飞机坐标
        if key_pressed[K_w] or key_pressed[K_UP]:
            self.rect.top -= self.speed
        if key_pressed[K_s] or key_pressed[K_DOWN]:
            self.rect.bottom += self.speed
        if key_pressed[K_a] or key_pressed[K_LEFT]:
            self.rect.left -= self.speed
        if key_pressed[K_d] or key_pressed[K_RIGHT]:
            self.rect.right += self.speed
        if key_pressed[K_SPACE]:
            # 按下空格键 发射一枚子弹 把飞机的坐标传入子弹
            bullet = Bullet(self.screen, self.rect.left, self.rect.top)
            # 把子弹放到列表里
            self.bullets.add(bullet)
            # 存放所有飞机的子弹的组
            HeroPlane.bullets.add(bullet)

    # 调用飞机的更新方法
    def update(self):
        self.key_control()
        self.display()

    def display(self):
        """显示飞机到窗口"""
        self.screen.blit(self.image, self.rect)
        # 更新子弹坐标
        self.bullets.update()

        # 把所有的子弹全部添加到屏幕
        self.bullets.draw(self.screen)

    @classmethod
    def clear_bullets(cls):
        # 清空子弹
        cls.bullets.empty()


# 子弹类
# 属性  坐标 速度 图片
class Bullet(pygame.sprite.Sprite):

    def __init__(self, screen, x, y):
        pygame.sprite.Sprite.__init__(self)
        # 图片
        self.image = pygame.image.load(resource_path('res/bullet1.png'))
        self.rect = self.image.get_rect()  # rect属性：矩形
        self.rect.topleft = [x + 100 / 2 - 22 / 2, y - 25]  # 矩形左上角坐
        # 窗口
        self.screen = screen
        # 速度
        self.speed = 20

    def update(self):
        # 修改子弹坐标
        self.rect.top -= self.speed
        # 如果子弹移出屏幕上方，则销毁子弹对象
        if self.rect.top < -22:
            # 超出界面 干掉自己
            self.kill()


class EnemyPlane(pygame.sprite.Sprite):
    """敌方飞机"""
    # 敌方所有子弹  类属性
    enemy_bullets = pygame.sprite.Group()

    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        # 5.创建一个飞机的图片
        self.image = pygame.image.load(resource_path('res/hanabi_1.gif'))  # 51*39 57*57
        self.rect = self.image.get_rect()
        x = random.randrange(1, Manager.bg_size[0], 50)
        self.rect.topleft = [x, 0]

        # 飞机的速度
        self.speed = 10

        # 记录当前的窗口对象
        self.screen = screen
        # 装子弹的列表
        self.bullets = pygame.sprite.Group()
        # 飞机左右飞的方向 一开始向右
        self.direction = 'right'

    def display(self):
        """显示飞机到窗口"""
        self.screen.blit(self.image, self.rect)
        # 所有子弹更新坐标
        self.bullets.update()
        # 所有子弹贴到屏幕
        self.bullets.draw(self.screen)

    def update(self):
        self.auto_move()
        self.auto_fire()
        self.display()

    def auto_move(self):
        # 一开始 飞机在左上角 向右移动
        if self.direction == 'right':
            self.rect.right += self.speed
        elif self.direction == 'left':
            self.rect.right -= self.speed

        if self.rect.right > Manager.bg_size[0] - 51:
            # 如果移动到最右侧 把方向改成左
            self.direction = 'left'
        elif self.rect.right < 0:
            # 如果移动到最右左侧 把方向改成右
            self.direction = 'right'

        self.rect.bottom += self.speed

    def auto_fire(self):
        # 获取一个随机数
        random_num = random.randint(1, 15)
        # 降低概率发射子弹  当前是1/20的概率
        if random_num == 8:
            """自动开火 创建子弹对象 添加到列表里"""
            bullet = EnemyBullet(self.screen, self.rect.left, self.rect.top)
            self.bullets.add(bullet)
            # 把子弹添加到类属性的子弹组里
            EnemyPlane.enemy_bullets.add(bullet)

    @classmethod
    def clear_bullets(cls):
        # 清空子弹  empty是精灵组提供的方法 用来清空精灵组
        cls.enemy_bullets.empty()


# 敌方子弹类
# 属性  坐标 速度 图片
class EnemyBullet(pygame.sprite.Sprite):

    def __init__(self, screen, x, y):
        pygame.sprite.Sprite.__init__(self)
        # 坐标
        # 图片
        self.image = pygame.image.load(resource_path('res/kamen.png'))  # 9*21
        self.rect = self.image.get_rect()  # rect属性：矩形
        self.rect.topleft = [x + 50 / 2 - 8 / 2, y + 39]  # 矩形左上角坐
        # 窗口
        self.screen = screen
        # 速度
        self.speed = 15

    def update(self):
        # 修改子弹坐标
        self.rect.bottom += self.speed
        # 如果子弹移出屏幕上方，则销毁子弹对象
        if self.rect.top > Manager.bg_size[1]:
            self.kill()


class GameSound(object):
    def __init__(self):
        pygame.mixer.init()  # 音乐模块初始化
        pygame.mixer.music.load(resource_path("res/HOYO-MiX - 独角戏 Monodrama.mp3"))
        pygame.mixer.music.set_volume(0.5)  # 声音大小 一半

        self.__bomb = pygame.mixer.Sound(resource_path("res/Boom.wav"))

    def playBackgroundMusic(self):
        pygame.mixer.music.play(-1)  # 开始播放背景音乐

    def playBombSound(self):
        pygame.mixer.Sound.play(self.__bomb)  # 爆炸音乐


class Bomb(object):
    # 初始化爆炸
    def __init__(self, screen, type):
        self.screen = screen
        if type == 'enemy':
            # 加载爆炸资源
            self.mImages = [
                pygame.image.load(resource_path("res/hanabi_down" + str(v) + ".png")) for v in range(2, 7)]
        else:
            # 加载爆炸资源
            self.mImages = [pygame.image.load(resource_path(
                "res/me_destroy_" + str(v) + ".png")) for v in range(1, 5)]

        self.mImages += self.mImages

        # 设置当前爆炸播放索引
        self.mIndex = 0
        # 爆炸位置
        self.mPos = [0, 0]
        # 是否可见
        self.mVisible = False

    # 设置位置
    def action(self, rect):
        # 触发爆炸方法draw
        # 爆炸的坐标
        self.mPos[0] = rect.left
        self.mPos[1] = rect.top
        # 打开爆炸的开关
        self.mVisible = True

    # 绘制爆炸
    def draw(self):
        if not self.mVisible:
            return
        self.screen.blit(self.mImages[self.mIndex], (self.mPos[0], self.mPos[1]))
        self.mIndex += 1
        if self.mIndex >= len(self.mImages):
            # 如果下标已经到最后 代表爆炸结束
            # 下标重置 mVisible重置
            self.mIndex = 0
            self.mVisible = False


# 地图
class GameBackground(object):
    # 初始化地图
    def __init__(self, screen):
        self.screen = screen
        self.img = pygame.image.load(resource_path("res/background.png")).convert()#图片大小480*700
        self.y1 = 0
        self.y2 = -Manager.bg_size[1]

    def move(self):
        self.y1 += 2
        self.y2 += 2
        # 无缝循环
        if self.y1 >= Manager.bg_size[1]:
            self.y1 = -Manager.bg_size[1]
        if self.y2 >= Manager.bg_size[1]:
            self.y2 = -Manager.bg_size[1]

    def draw(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.img, (0, self.y1))
        self.screen.blit(self.img, (0, self.y2))

class PauseMenu:
    def __init__(self, screen, bg_size):
        self.screen = screen
        self.bg_size = bg_size
        # 加载两张按钮图（resume / quit）
        self.btn_resume = pygame.image.load(resource_path("res/resume.png")).convert_alpha()
        self.btn_quit   = pygame.image.load(resource_path("res/gameover.png")).convert_alpha()
        self.resume_rect = self.btn_resume.get_rect(center=(bg_size[0]//2, bg_size[1]//2 - 60))
        self.quit_rect   = self.btn_quit.get_rect(center=(bg_size[0]//2, bg_size[1]//2 + 60))
        self.selected = None   # 0=resume 1=quit

    def draw(self):
        # 半透明遮罩
        s = pygame.Surface(self.bg_size, pygame.SRCALPHA)
        s.fill((0,0,0,180))
        self.screen.blit(s, (0,0))
        # 画按钮
        self.screen.blit(self.btn_resume, self.resume_rect)
        self.screen.blit(self.btn_quit,   self.quit_rect)

    def handle_key(self, key):
        if key in (K_w, K_UP):
            self.selected = 0
        elif key in (K_s, K_DOWN):
            self.selected = 1
        elif key in (K_RETURN, K_KP_ENTER):
            return self.selected
        return None

    def handle_mouse(self, pos):
        if self.resume_rect.collidepoint(pos):
            self.selected = 0
            if pygame.mouse.get_pressed()[0]:
                return 0
        elif self.quit_rect.collidepoint(pos):
            self.selected = 1
            if pygame.mouse.get_pressed()[0]:
                return 1
        else:
            self.selected = None
        return None

class Manager(object):
    bg_size = (480, 700)
    # 创建敌机定时器的id
    create_enemy_id = 10
    # 游戏结束 倒计时的id
    game_over_id = 11
    # 游戏是否结束
    is_game_over = False
    # 倒计时时间
    over_time = 3

    def __init__(self):
        pygame.init()
        # 1创建一个窗口 Manager.bg_size 是宽高
        self.screen = pygame.display.set_mode(Manager.bg_size, 0, 32)

        # 2创建一个背景图片
        # self.background = pygame.image.load('.background.png')
        self.map = GameBackground(self.screen)

        # 初始化一个装玩家精灵的group
        self.players = pygame.sprite.Group()
        # 初始化一个装敌机精灵的group
        self.enemys = pygame.sprite.Group()

        # 初始化一个玩家爆炸的对象
        self.player_bomb = Bomb(self.screen, 'player')
        # 初始化一个敌机爆炸的对象
        self.enemy_bomb = Bomb(self.screen, 'enemy')
        # 初始化一个声音播放的对象
        self.sound = GameSound()

    def exit(self):
        print('退出')
        # 执行pygame退出
        pygame.quit()
        # python程序的退出
        exit()

    def show_over_text(self):
        # 游戏结束 倒计时后重新开始
        self.drawText('gameover %d' % Manager.over_time, 100, Manager.bg_size[1] / 2,
                      textHeight=50, fontColor=[255, 0, 0])

    def game_over_timer(self):
        self.show_over_text()
        # 倒计时-1
        Manager.over_time -= 1
        if Manager.over_time == 0:
            # 参数2改为0 定时间停止
            pygame.time.set_timer(Manager.game_over_id, 0)
            # 倒计时后重新开始
            Manager.over_time = 3
            Manager.is_game_over = False
            self.start_game()

    def start_game(self):
        # 重新开始游戏 有些类属性要清空
        EnemyPlane.clear_bullets()
        HeroPlane.clear_bullets()
        manager = Manager()
        manager.main()

    def new_player(self):
        # 创建一个飞机的对象 添加到玩家的组
        player = HeroPlane(self.screen)
        self.players.add(player)

    def new_enemy(self):
        # 创建一个飞机的对象 添加到敌机的组
        enemy = EnemyPlane(self.screen)
        self.enemys.add(enemy)

    # 绘制文字  rgb 红绿蓝 0 - 255
    # 参1要绘制的文字 参2 x轴坐标 参3y轴坐标 参4文字大小 参5 文字颜色 参6 背景颜色
    def drawText(self, text, x, y, textHeight=30, fontColor=(255, 255, 255), backgroudColor=None):

        # 通过字体文件获得字体对象  参数1 字体文件 参数2 字体大小
        font_obj = pygame.font.Font(resource_path('res/svgafix.fon'), textHeight)
        # 1文字  2是否抗锯齿 3文字颜色 4背景颜色
        text_obj = font_obj.render(text, True, fontColor, backgroudColor)  # 配置要显示的文字
        # 获得要显示的对象的rect
        text_rect = text_obj.get_rect()
        # 设置显示对象的坐标
        text_rect.topleft = (x, y)
        # 绘制字 到指定区域  参1是文字对象 参2 矩形对象
        self.screen.blit(text_obj, text_rect)

    def main(self):
        # 播放背景音乐
        self.sound.playBackgroundMusic()
        # 创建一个玩家
        self.new_player()
        # 开启创建敌机的定时器
        pygame.time.set_timer(Manager.create_enemy_id, 1000)

        paused = False                  # ← 1. 新增：是否暂停
        self.pause_menu = PauseMenu(self.screen, Manager.bg_size)  # ← 2. 新增：暂停菜单

        while True:
            # ====== 3. 事件循环（已加入 ESC 暂停逻辑） ======
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()

                # ESC 切换暂停/继续
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    paused = not paused

                # 暂停状态下只处理菜单
                if paused:
                    if event.type == KEYDOWN:
                        choice = self.pause_menu.handle_key(event.key)
                        if choice == 0:         # 继续
                            paused = False
                        elif choice == 1:       # 退出
                            self.exit()
                    elif event.type in (MOUSEMOTION, MOUSEBUTTONDOWN):
                        choice = self.pause_menu.handle_mouse(event.pos)
                        if choice is not None and event.type == MOUSEBUTTONDOWN:
                            if choice == 0:
                                paused = False
                            elif choice == 1:
                                self.exit()
                    continue   # 暂停时跳过后面的游戏逻辑

                # 非暂停状态下的原事件
                if event.type == Manager.create_enemy_id:
                    self.new_enemy()
                elif event.type == Manager.game_over_id:
                    self.game_over_timer()

            # ====== 4. 游戏主逻辑（包在 if not paused 里） ======
            if not paused:
                # 移动并绘制地图
                self.map.move()
                self.map.draw()
                self.drawText('hp:10000', 0, 0)

                if Manager.is_game_over:
                    self.show_over_text()

                # 爆炸绘制
                self.player_bomb.draw()
                self.enemy_bomb.draw()

                # 玩家、敌机、子弹碰撞检测
                if self.players.sprites():
                    isover = pygame.sprite.spritecollide(self.players.sprites()[0], EnemyPlane.enemy_bullets, True)
                    if isover:
                        Manager.is_game_over = True
                        pygame.time.set_timer(Manager.game_over_id, 1000)
                        self.player_bomb.action(self.players.sprites()[0].rect)
                        self.players.remove(self.players.sprites()[0])
                        self.sound.playBombSound()

                    iscollide = pygame.sprite.groupcollide(self.players, self.enemys, True, True)
                    if iscollide:
                        Manager.is_game_over = True
                        pygame.time.set_timer(Manager.game_over_id, 1000)
                        items = list(iscollide.items())[0]
                        x, y = items[0], items[1][0]
                        self.player_bomb.action(x.rect)
                        self.enemy_bomb.action(y.rect)
                        self.sound.playBombSound()

                    is_enemy = pygame.sprite.groupcollide(HeroPlane.bullets, self.enemys, True, True)
                    if is_enemy:
                        y = list(is_enemy.items())[0][1][0]
                        self.enemy_bomb.action(y.rect)
                        self.sound.playBombSound()

                # 更新精灵
                self.players.update()
                self.enemys.update()

            # ====== 5. 暂停时只画菜单 ======
            if paused:
                self.pause_menu.draw()

            pygame.display.update()
            time.sleep(0.03)


if __name__ == '__main__':
    manager = Manager()
    manager.main()

input('skjf')