import pygame
import random
import time

class GamePro:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.ship = Spaceship(self)
        self.aliens = [pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()]
        self.bullets = [pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()]
        self.life = 3
        self.point = 0
        self.bullet_color = 0

    def run_game(self):
        global d, dt
        pygame.init()
        running = True
        out = False
        while running:
            dt += self.clock.tick(120)
            t = self.check_events()
            # 1: 중지, 2: A키, 3: D키, 4: LSHIFT키, 5: RSHIFT키, 6: 우주선 정지
            if 1 in t:
                out = True
                running = False
            if 2 in t or (d_pressed[0] == True and d_pressed[1] == False):
                d = -1
            elif 3 in t or (d_pressed[1] == True and d_pressed[0] == False):
                d = 1
            elif 6 in t:
                d = 0

            if 4 in t:
                self.bullet_color += 1
                self.bullet_color %= 3

            if 5 in t:
                b = Bullet(self, self.bullet_color)
                self.bullets[self.bullet_color].add(b)
            self.update_screen()
            if self.life <= 0:
                running = False
        if out:
            pygame.quit()
        else:
            dark = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)  # 화면을 어둡게 함.
            dark.fill((0, 0, 0, 200))
            self.screen.blit(dark, (0, 0))

            fontC = pygame.font.Font("global/Galmuri11-Condensed.ttf", 50)
            fontB = pygame.font.Font("global/Galmuri11-Bold.ttf", 50)
            text1 = fontB.render("Game Over", True, (255, 255, 255))
            text2 = fontC.render(f"최종 점수: {self.point}", True, (255, 255, 255))
            self.screen.blit(text1, ((self.settings.screen_width-text1.get_width())//2, self.settings.screen_height//2 - 50))
            self.screen.blit(text2, ((self.settings.screen_width-text2.get_width())//2, self.settings.screen_height//2 + 50))

            while True:
                self.clock.tick(120)
                t = self.check_events()
                if 1 in t:
                    pygame.quit()

    def check_events(self):
        global d_pressed
        r = []

        for event in pygame.event.get():  # 행동을 다 체크해서 해당되는게 있으면 실행. 계속.
            if event.type == pygame.QUIT:
                r. append(1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:  # 이동에 대한 입력인 A, D는 중첩될 수 없게 elif를 이용한다.
                    d_pressed[0] = True
                    r.append(2)
                elif event.key == pygame.K_d:
                    d_pressed[1] = True
                    r.append(3)

                if event.key == pygame.K_LSHIFT:  # bullet 발사 및 그 외 기능을 담당할 입력은 if만을 이용한다.
                    r.append(4)
                if event.key == pygame.K_RSHIFT:
                    r.append(5)

            if event.type == pygame.KEYUP:  # A, D키가 올라가면 그쪽이 안눌러진 것으로 적용하거나 둘 다 안눌러질 경우 멈추도록 한다.
                if event.key == pygame.K_a:  # A키가 떨어졌을 때
                    d_pressed[0] = False  # A키가 떨어진 것으로 저장.
                    if not d_pressed[1]:
                        r.append(6)
                if event.key == pygame.K_d:
                    d_pressed[1] = False
                    if not d_pressed[0]:
                        r.append(6)
        pygame.display.flip()
        return r

    def update_screen(self):
        global octo_down
        self.screen.fill(self.settings.bg_color)

        self.create_fleet()
        for i in range(3):
            self.aliens[i].update()
            self.bullets[i].update()
        self.ship.update()
        self.board()

        if octo_down:
            for i in range(3):
                for j in self.aliens[i]:
                    j.rect.midtop = (j.rect.midtop[0], j.rect.midtop[1] + 20)

        k = False
        for i in range(3):
            for j in range(3):
                if i == j:
                    k = k or bool(pygame.sprite.groupcollide(self.aliens[i], self.bullets[j], True, True))
                else:
                    pygame.sprite.groupcollide(self.aliens[i], self.bullets[j], False, True)
        if k:
            self.point += 10

        k = False
        for i in range(3):
            k = k or bool(pygame.sprite.spritecollide(self.ship, self.aliens[i], True))
        if k:
            self.life -= 1

        for i in range(3):
            self.aliens[i].draw(self.screen)
        octo_down = False

    def create_fleet(self):
        global dt
        ry = self.settings.screen_height
        rx = self.settings.screen_width
        for i in range(3):
            for j in self.aliens[i]:
                if j.rect.y > self.settings.screen_height:
                    j.kill()
                ry = min(ry, j.rect.y)
                rx = min(rx, j.rect.x)

        if (rx < 5 and ry > 74) or (dt > 10000 and len(self.aliens[0]) + len(self.aliens[1]) + len(self.aliens[2]) == 0):
            dt = 0
            now_x = 0
            for i in range(10):
                c = random.randint(0, 2)  # c == 0이면 Red, 1이면 Green, 2이면 Blue로.
                octo = Octopus(c, self)
                octo.x = now_x # 양쪽에 margin을 50 남기고, 10개가 등분배되어 들어갈 수 있도록 했다.
                now_x += (self.settings.screen_width-100)//10
                self.aliens[c].add(octo)

    def board(self):
        font = pygame.font.Font("global/Galmuri11-Condensed.ttf", 50)
        text = font.render(f"Points: {self.point}", True, (0, 0, 0))
        self.screen.blit(text, (20, 20))
        text = font.render(f"Life: {self.life}", True, (0, 0, 0))
        self.screen.blit(text, (20, 100))
        pallete = {0: 'Red', 1: 'Green', 2: 'Blue'}
        text = font.render(f"현재 총알: {pallete[self.bullet_color]}", True, (0, 0, 0))
        self.screen.blit(text, (20, 180))


class Settings:
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 600
        self.bg_color = (230, 230, 230)
        self.spaceship_speed = 5
        self.bullet_color = [(255, 60, 60), (60, 255, 60), (60, 60, 255)]
        self.bullet_height = 15
        self.bullet_width = 3
        self.bullet_speed = 3
        self.octopus_speed = 1


class Spaceship:
    def __init__(self, game):
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()
        self.image = pygame.image.load("global/spaceship.bmp")
        self.rect = self.image.get_rect()
        self.settings = Settings()
        self.rect.midbottom = (self.settings.screen_width // 2, self.settings.screen_height)
        self.x = self.settings.screen_width / 2  # spaceship의 x좌표를 float으로 따로 저장한다.

    def draw_spaceship(self):  # 이름이 snake표기법이 아니라서 수정.
        self.screen.blit(self.image, self.rect)

    def update(self):
        global d
        self.x += d * self.settings.spaceship_speed
        self.rect.x = int(self.x)  # float으로 저장된 x좌표를 int로 변환한다.
        self.draw_spaceship()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, color):
        super().__init__()
        self.screen = game.screen
        self.settings = game.settings
        self.color = self.settings.bullet_color[color]  # color를 0, 1, 2로 받아서 R, G, B색 총알이 되도록 함.
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = game.ship.rect.midtop
        self.y = self.rect.y

    def update(self):
        self.y -= self.settings.bullet_speed
        self.rect.y = int(self.y)
        self.draw_bullet()

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)


class Octopus(pygame.sprite.Sprite):
    def __init__(self, color, game):
        super().__init__()
        self.screen = game.screen
        self.settings = game.settings
        self.image = pygame.image.load("global/octopus.bmp")
        self.pallete = [(255, 0, 0, 80), (0, 255, 0, 80), (0, 0, 255, 80)]
        self.image.fill(self.pallete[color], special_flags=pygame.BLEND_RGBA_ADD)  # 색을 넣어주기 위해 filter를 이용한다.
        self.rect = self.image.get_rect()
        self.x = self.rect.x

    def update(self):
        global octo_d, octo_down, octo_down_time
        if (self.rect.midright[0] > self.settings.screen_width or self.rect.midleft[0] < 0) and (not octo_down) and (time.time() - octo_down_time > 1):
            octo_d *= -1
            octo_down = True
            octo_down_time = time.time()

        self.x += octo_d * self.settings.octopus_speed
        self.rect.x = int(self.x)

    def draw_octopus(self):
        self.screen.blit(self.image, self.rect)


d_pressed = [False, False]
d = 0  # 정지 0, 좌측 -1, 우측 1
octo_d = 1  # d와 같은 규칙.
octo_down = False
octo_down_time = 0






dt = 10000

game = GamePro()
game.run_game()