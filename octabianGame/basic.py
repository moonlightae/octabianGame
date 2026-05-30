import pygame, random, time


class GamePro:
    def __init__(self, llife, lpoint):
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.ship = Spaceship(self)
        self.aliens = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.life = llife
        self.point = lpoint
        pygame.display.set_caption("문어외계인 침공(김태환)")

    def run_game(self):
        global d, dt, left_shift_pressed, play, damaged, llife, lpoint
        pygame.init()
        running = True
        out = False
        while running:
            dt += self.clock.tick(120)
            t = self.check_events()
            # 1: 중지, 2: A키, 좌 화살표, 3: D키, 우 화살표, 4: LSHIFT키, 5: SPACE키, 6: 우주선 정지 7: LSHIFT UP, 8: Q, 9: W, 10: E
            if 1 in t:
                out = True
                running = False
            if 2 in t or (d_pressed[0] == True and d_pressed[1] == False):
                d = -1
            elif 3 in t or (d_pressed[1] == True and d_pressed[0] == False):
                d = 1
            elif 6 in t:
                d = 0
            if 5 in t:
                if len(self.bullets) < 5:
                    b = Bullet(self)
                    self.bullets.add(b)
            self.update_screen()
            if self.life <= 0:
                running = False
            if damaged:
                llife = self.life
                lpoint = self.point
                running = False
        if out:
            pygame.quit()
            play = False
        elif not damaged:
            llife = 3
            lpoint = 0
            self.game_over()

    def game_over(self):
        global play
        fontC = pygame.font.Font("global/Galmuri11-Condensed.ttf", 50)
        fontB = pygame.font.Font("global/Galmuri11-Bold.ttf", 50)
        dark = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)  # 화면을 어둡게 함.
        dark.fill((0, 0, 0, 200))
        self.screen.blit(dark, (0, 0))

        text1 = fontB.render("Game Over", True, (255, 255, 255))
        text2 = fontC.render(f"최종 점수: {self.point}", True, (255, 255, 255))
        text3 = fontC.render("SPACE 키로 재시작", True, (255, 255, 255))
        self.screen.blit(text1, ((self.settings.screen_width-text1.get_width())//2, self.settings.screen_height//2 - 50))
        self.screen.blit(text2, ((self.settings.screen_width-text2.get_width())//2, self.settings.screen_height//2 + 50))
        self.screen.blit(text3, ((self.settings.screen_width-text3.get_width())//2, self.settings.screen_height//2 + 100))
        while True:
            self.clock.tick(120)
            t = self.check_events()
            if 5 in t:
                break
            if 1 in t:
                play = False
                break



    def check_events(self):
        global d_pressed
        r = []

        for event in pygame.event.get():  # 행동을 다 체크해서 해당되는게 있으면 실행. 계속.
            if event.type == pygame.QUIT:
                r.append(1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:  # 이동에 대한 입력인 A, D는 중첩될 수 없게 elif를 이용한다.
                    d_pressed[0] = True
                    r.append(2)
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    d_pressed[1] = True
                    r.append(3)
                if event.key == pygame.K_SPACE:
                    r.append(5)

            if event.type == pygame.KEYUP:  # A, D키가 올라가면 그쪽이 안눌러진 것으로 적용하거나 둘 다 안눌러질 경우 멈추도록 한다.
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:  # A키가 떨어졌을 때
                    d_pressed[0] = False  # A키가 떨어진 것으로 저장.
                    if not d_pressed[1]:
                        r.append(6)
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    d_pressed[1] = False
                    if not d_pressed[0]:
                        r.append(6)
        pygame.display.flip()
        return r

    def update_screen(self):
        global left_shift_pressed, damaged
        self.screen.fill(self.settings.bg_color)
        self.create_fleet()
        self.aliens.update()
        self.bullets.update()
        self.ship.update()
        self.board()
        self.change_direct()

        k = bool(pygame.sprite.groupcollide(self.aliens, self.bullets, True, True))
        if k:
            self.point += 10

        k = bool(pygame.sprite.spritecollide(self.ship, self.aliens, True))
        if k:
            self.life -= 1
            damaged = True

        self.aliens.draw(self.screen)

    def create_fleet(self):
        global dt
        rx, rx2, ry, ry2 = self.fleet_crit()
        if (rx is not None and (rx < 5 or rx2 > self.settings.screen_width - 5) and ry > 74) or (dt > 10000 and len(self.aliens) == 0):
            dt = 0
            if rx == None or rx < 5:
                now_x = 0
            else:
                now_x = 138
            for i in range(10):
                octo = Octopus(self)
                octo.x = now_x # 오른쪽에 margin을 100 남기고, 10개가 등분배되어 들어갈 수 있도록 했다.
                now_x += (self.settings.screen_width-100)//10
                self.aliens.add(octo)

    def fleet_crit(self):
        if len(self.aliens) != 0:
            ry = self.settings.screen_height
            ry2 = 0
            rx = self.settings.screen_width
            rx2 = 0
            for j in self.aliens:
                if j.rect.y > self.settings.screen_height:
                    j.kill()
                ry = min(ry, j.rect.y)
                ry2 = max(ry2, j.rect.y)
                rx = min(rx, j.rect.x)
                rx2 = max(rx2, j.rect.x)

            return rx, rx2+64, ry, ry2+64
        else:
            return None, None, None, None

    def change_direct(self):
        global octo_d, octo_down_time
        octo_down = False
        for i in self.aliens:
            octo_down = octo_down or i.check_edges()
        if octo_down:
            octo_d *= -1
            for j in self.aliens:
                j.rect.midtop = (j.rect.midtop[0], j.rect.midtop[1] + 20)

    def board(self):
        fontC = pygame.font.Font("global/Galmuri11-Condensed.ttf", 50)
        text = fontC.render(f"Points: {self.point}", True, (0, 0, 0))
        self.screen.blit(text, (20, 20))
        text = fontC.render(f"Life: {self.life}", True, (0, 0, 0))
        self.screen.blit(text, (20, 100))

class Settings:
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 600
        self.bg_color = (230, 230, 230)
        self.spaceship_speed = 1.5
        self.bullet_color = (60, 60, 60)
        self.bullet_height = 15
        self.bullet_width = 3
        self.bullet_speed = 2
        self.octopus_speed = 1

class Spaceship:
    def __init__(self, game):
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()  # 아무 기능을 갖지 않으나, spec에서 요구된 정보여서 삭제하지 않았다.
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
        if self.x < 0:
            self.x = 0
        elif self.x > self.settings.screen_width - (self.rect.right - self.rect.left):
            self.x = self.settings.screen_width - (self.rect.right - self.rect.left)
        self.rect.x = int(self.x)  # float으로 저장된 x좌표를 int로 변환한다.
        self.draw_spaceship()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.screen = game.screen
        self.settings = game.settings
        self.color = self.settings.bullet_color  # color를 0, 1, 2로 받아서 R, G, B색 총알이 되도록 함.
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = game.ship.rect.midtop
        self.y = self.rect.y

    def update(self):
        self.y -= self.settings.bullet_speed
        self.rect.y = int(self.y)
        if self.y < 0:
            self.kill()
        self.draw_bullet()

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)





class Octopus(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.screen = game.screen
        self.settings = game.settings
        self.image = pygame.image.load("global/octopus.bmp")
        self.rect = self.image.get_rect()
        self.x = self.rect.x

    def update(self):
        self.x += octo_d * self.settings.octopus_speed
        self.rect.x = int(self.x)

    def draw_octopus(self):
        self.screen.blit(self.image, self.rect)

    def check_edges(self):
        global octo_down_time
        if (self.rect.x + 64 > self.settings.screen_width or self.rect.x < 0) and (time.time() - octo_down_time > 1):
            octo_down_time = time.time()
            return True
        else:
            return False

play = True
llife = 3
lpoint = 0
while play:
    d_pressed = [False, False]
    left_shift_pressed =  False
    d = 0  # 정지 0, 좌측 -1, 우측 1
    octo_d = 1  # d와 같은 규칙.
    octo_down_time = 0
    dt = 10000
    damaged = False

    game = GamePro(llife, lpoint)
    game.run_game()