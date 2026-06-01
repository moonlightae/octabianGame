import pygame, random, time

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
        self.game_frame = 120
        self.octopus_group_quantity = 10
        self.octopus_margin = 100
        self.octopus_size = 64

class GamePro:
    def __init__(self):
        self.clock = pygame.time.Clock()  # time의 sleep 함수 기능을 프레임마다 실행해서 게임 속도를 조절하도록 한다.
        self.settings = Settings()  # Settings에 저장된 값을 불러온다.
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))  # 전체 게임에 사용될 Screen이다.
        self.ship = Spaceship(self)  # 게임의 player인 spaceship을 쉽게 접근할 수 있도록 GamePro에 저장해둔다.
        self.aliens = [pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()]  # 색에 따라 다른 그룹에 저장한 후, 별개로 관리한다.
        self.bullets = [pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()]  # 외계인과 마찬가지.
        self.life = 3  # player의 목숨을 GamePro 변수로 저장한다.
        self.point = 0  # player의 점수도 마찬가지.
        self.bullet_color = 0  # LSHIFT에서 변경할 수 있는 값으로, 0, 1, 2 값을 가진다. bullet 내부 palette의 index이다.
        pygame.display.set_caption("문어외계인 침공(김태환)")

    def run_game(self):
        global d, dt, left_shift_pressed, play
        pygame.init()  # 기초 파일 생성.
        running = True  # 게임이 돌아가고 있는지에 대한 여부를 저장한다.(out이거나 목숨이 0이 되는 등에서 False)
        out = False  # 게임을 끄는 버튼을 눌렀을때 True가 된다.
        while running:
            dt += self.clock.tick(self.settings.game_frame)  # 게임 시작 이후로 지난 시간을 기록한다.
            t = self.check_events()  # 그 frame에 눌러지거나 떼어진 버튼을 list에 int로 담아 return한다. 아래가 해당하는 키이다.
            # 1: 중지, 2: A키, 3: D키, 4: LSHIFT키, 5: RSHIFT키, 6: 우주선 정지(A, D 떨어짐.) 7: LSHIFT UP, 8: Q, 9: W, 10: E
            # check_event로 받은 command에 따라 이동
            if 1 in t:
                out = True
                running = False
            if 2 in t or (d_pressed[0] == True and d_pressed[1] == False):
                d = -1
            elif 3 in t or (d_pressed[1] == True and d_pressed[0] == False):
                d = 1
            elif 6 in t:
                d = 0

            # LSHIFT로 색 전환
            if 4 in t:
                left_shift_pressed = True
            if 7 in t:
                left_shift_pressed = False
            if left_shift_pressed:
                if 8 in t:  # Q를 눌렀을때 RED로 설정
                    self.bullet_color = 0
                elif 9 in t:  # W를 눌렀을 때 GREEN으로 설정
                    self.bullet_color = 1
                elif 10 in t:  # E를 눌렀을 때 BLUE로 설정
                    self.bullet_color = 2

            # RSHIFT로 bullet 발사
            if 5 in t:
                b = Bullet(self, self.bullet_color)
                self.bullets[self.bullet_color].add(b)

            # screen을 업데이트하고, life가 0보다 작거나 같으면 게임이 정지되도록 했다.
            self.update_screen()
            if self.life <= 0:
                running = False

        if out:  # 종료버튼을 눌러서 running = False가 된 것인지
            play = False
            pygame.quit()
        else:  # life가 0이하가 되어서 running = false가 된 것인지 확인한다.
            self.game_over()

    def check_events(self):
        global d_pressed
        r = []
        # 1: 중지, 2: A키, 3: D키, 4: LSHIFT키, 5: RSHIFT키, 6: 우주선 정지(A, D 떨어짐.) 7: LSHIFT UP, 8: Q, 9: W, 10: E

        for event in pygame.event.get():  # 행동을 다 체크해서 해당되는게 있으면 r에 넣어준다.
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
                if event.key == pygame.K_q:
                    r.append(8)
                if event.key == pygame.K_w:
                    r.append(9)
                if event.key == pygame.K_e:
                    r.append(10)
                if event.key == pygame.K_SPACE:
                    r.append(11)

            if event.type == pygame.KEYUP:  # A, D키가 올라가면 그쪽이 안눌러진 것으로 적용하거나 둘 다 안눌러질 경우 멈추도록 한다.
                if event.key == pygame.K_a:  # A키가 떨어졌을 때
                    d_pressed[0] = False  # A키가 떨어진 것으로 저장.
                    if not d_pressed[1]:
                        r.append(6)
                if event.key == pygame.K_d:
                    d_pressed[1] = False
                    if not d_pressed[0]:
                        r.append(6)
                if event.key == pygame.K_LSHIFT:
                    r.append(7)
        pygame.display.flip()
        return r

    def update_screen(self):
        global left_shift_pressed
        self.screen.fill(self.settings.bg_color)  # screen을 초기화한다.
        self.create_fleet()  # 조건이 맞는다면 문어를 더 생성한다.
        for i in range(3):  # 모든 색의 alien, bullet을 화면에 나타낸다.
            self.aliens[i].update()
            self.bullets[i].update()
        self.ship.update()  # ship, board도 화면에 나타낸다.
        self.board()
        if left_shift_pressed:  # LSHIFT가 눌려 있다면 색 변경 창을 나타낸다.
            self.bullet_change_ui()
        self.change_direct()  # 문어가 벽에 닿으면 방향을 바꾸고 아래로 내린다.

        k = 0  # 프레임마다 총알과 문어가 충돌한 개수를 세서 점수에 곱해 점수를 더한다. k는 임시 변수이다.
        for i in range(3):
            for j in range(3):
                if i == j:  # 같은 색이면 k에 충돌 개수를 더한다.
                    # groupcollide의 반환값은 충돌 객체 사이의 dictionary이다.
                    k += len(pygame.sprite.groupcollide(self.aliens[i], self.bullets[j], True, True))
                else:  # 다른 색일 경우에는 총알만 없앤다.
                    pygame.sprite.groupcollide(self.aliens[i], self.bullets[j], False, True)
        if 0 < k:
            self.point += 10 * k

        k = False
        for i in range(3):  # 프레임마다 ship과 alien이 충돌했는지 확인하여
            k = k or bool(pygame.sprite.spritecollide(self.ship, self.aliens[i], True))
        if k:  # 한 번 이상 충돌했다면 life를 1 차감한다.
            self.life -= 1

        for i in range(3):  # 문어는 change_direct()가 외부 함수로 나왔기 때문에, draw를 update 내부에 넣지 않고, 따로 실행한다.
            self.aliens[i].draw(self.screen)

    def change_direct(self):  # 조건을 확인하여 문어가 벽에 닿으면 아래로 내려가도록 한다.
        global octo_d, octo_down_time
        octo_down = False
        for i in range(3):
            for j in self.aliens[i]:  # 모든 AI에 대해서 check_edges()를 하고, 그 중 하나라도 True가 나오면
                octo_down = octo_down or j.check_edges()  # octo_down을 True로 바꾼다.
        if octo_down:
            octo_d *= -1  # 방향을 바꾼다.
            for i in range(3):  # 모든 alien에 대해 아래로 20씩 내린다.
                for j in self.aliens[i]:
                    j.rect.midtop = (j.rect.midtop[0], j.rect.midtop[1] + 20)

    def create_fleet(self):  # 문어 생성 조건이 만족되면 문어를 생성한다.
        global dt
        rx, rx2, ry, ry2 = self.fleet_crit()  # 전체 문어에서 x, y의 max, min 값을 모두 반환하는 함수이다. x최소, x최대, y최소, y최대 순.
        if (rx is not None and ry > self.settings.octopus_size + 10) or (dt > 10000 and len(self.aliens[0]) + len(self.aliens[1]) + len(self.aliens[2]) == 0):
            # 문어가 존재할 때, 가장 작은 y가 octopus_size + 10보다 크거나, 문어가 존재하지 않을 때, 이전 문어 생성 이후로 10초가 지났다면 생성한다.
            dt = 0
            if rx is None or rx < 5:  # 문어가 존재하지 않거나 가장 작은 x가 5보다 작으면 왼쪽에 충돌한 것으로 간주한다.
                now_x = 0
            else:
                now_x = self.settings.octopus_margin + self.settings.octopus_size // 2
            for i in range(10):
                c = random.randint(0, 2)  # c == 0이면 Red, 1이면 Green, 2이면 Blue로.
                octo = Octopus(c, self)
                octo.x = now_x  # octopus가 충돌한 반대쪽에 margin을 100 남기고, ogq(settings에서 변수로 할당)개가 등분배되어 들어갈 수 있도록 했다.
                now_x += (self.settings.screen_width-self.settings.octopus_margin)//self.settings.octopus_group_quantity
                self.aliens[c].add(octo)

    def fleet_crit(self):  # 전체 문어에서 최대, 최소에 해당하는 x, y값을 구해 반환한다.
        if len(self.aliens[0]) + len(self.aliens[1]) + len(self.aliens[2]) != 0:
            ry = self.settings.screen_height  # 이론상 최댓값을 최소에 저장하고, 최솟값을 최대에 저장해서 계산했다.
            ry2 = 0
            rx = self.settings.screen_width
            rx2 = 0
            for i in range(3):
                for j in self.aliens[i]:  # 모든 문어에 대해서
                    if j.rect.y > self.settings.screen_height:  # 화면 밖으로 나간 문어는 없애고,
                        j.kill()
                    ry = min(ry, j.rect.y)  # 그렇지 않으면 min과 max를 계산한다.
                    ry2 = max(ry2, j.rect.y)
                    rx = min(rx, j.rect.x)
                    rx2 = max(rx2, j.rect.x)
            print(rx, rx2, ry, ry2)
            return rx, rx2+self.settings.octopus_size, ry, ry2+self.settings.octopus_size  # 최댓값에는 문어 크기를 더해서 오른쪽 끝, 아래끝을 기준으로 바꾸었다.
        else:
            return None, None, None, None  # 문어가 존재하지 않을때에는 None이 return되도록 했다.

    def board(self):  # 점수판의 ui이다.
        fontC = pygame.font.Font("global/Galmuri11-Condensed.ttf", 50)
        text = fontC.render(f"Points: {self.point}", True, (0, 0, 0))
        self.screen.blit(text, (20, 20))
        text = fontC.render(f"Life: {self.life}", True, (0, 0, 0))
        self.screen.blit(text, (20, 100))
        pallete = {0: 'Red', 1: 'Green', 2: 'Blue'}
        text = fontC.render(f"현재 총알: {pallete[self.bullet_color]}", True, (0, 0, 0))
        self.screen.blit(text, (20, 180))

    def bullet_change_ui(self):  # LSHIFT를 눌렀을 때 출력할 ui이다.
        fontb = pygame.font.Font("global/Galmuri11-Bold.ttf", 20)
        bullet_palette_rect = pygame.Rect(int(self.ship.x) + self.ship.rect.width // 2 - 50, self.settings.screen_height - 120, 100, 40)
        bullet_palette_surf = pygame.Surface(bullet_palette_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bullet_palette_surf, (0, 0, 0, 100), bullet_palette_surf.get_rect())
        pygame.draw.circle(bullet_palette_surf, (200, 0, 0), (17.5, 20), 15)
        pygame.draw.circle(bullet_palette_surf, (0, 200, 0), (50, 20), 15)
        pygame.draw.circle(bullet_palette_surf, (0, 0, 200), (82.5, 20), 15)
        textq = fontb.render("Q", True, (200, 200, 200))
        bullet_palette_surf.blit(textq, (17.5-textq.get_width()//2, 20-textq.get_height()//2))
        textw = fontb.render("W", True, (200, 200, 200))
        bullet_palette_surf.blit(textw, (50-textw.get_width()//2, 20-textw.get_height()//2))
        texte = fontb.render("E", True, (200, 200, 200))
        bullet_palette_surf.blit(texte, (82.5-texte.get_width()//2, 20-texte.get_height()//2))
        self.screen.blit(bullet_palette_surf, bullet_palette_rect.topleft)

    def game_over(self):  # 게임 오버 화면을 함수로 지정했다.
        global play
        # font 설정, 화면 어둡게 하기.
        fontC = pygame.font.Font("global/Galmuri11-Condensed.ttf", 50)
        fontB = pygame.font.Font("global/Galmuri11-Bold.ttf", 50)
        dark = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)  # 화면을 어둡게 함.
        dark.fill((0, 0, 0, 200))
        self.screen.blit(dark, (0, 0))

        # text 정의 및 출력
        text1 = fontB.render("Game Over", True, (255, 255, 255))
        text2 = fontC.render(f"최종 점수: {self.point}", True, (255, 255, 255))
        text3 = fontC.render("SPACE 키로 재시작", True, (255, 255, 255))
        self.screen.blit(text1, ((self.settings.screen_width-text1.get_width())//2, self.settings.screen_height//2 - 50))
        self.screen.blit(text2, ((self.settings.screen_width-text2.get_width())//2, self.settings.screen_height//2 + 50))
        self.screen.blit(text3, ((self.settings.screen_width-text3.get_width())//2, self.settings.screen_height//2 + 100))
        while True:  # 게임 오버 화면에서 스페이스바를 누르거나 창 종료 버튼을 눌렀을 때 기능을 실행하도록 함.
            self.clock.tick(self.settings.game_frame)
            t = self.check_events()
            if 11 in t:  # Space 키를 누르면 게임 재실행
                break
            if 1 in t:  # 창 닫기 버튼을 누르면 게임 종료.
                play = False
                break

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
        if self.x < 0:  # 우주선이 화면 밖으로 나갈 수 없게 했다.
            self.x = 0
        elif self.x > self.settings.screen_width - (self.rect.right - self.rect.left):
            self.x = self.settings.screen_width - (self.rect.right - self.rect.left)
        self.rect.x = int(self.x)  # float으로 저장된 x좌표를 int로 변환해 적용한다.
        self.draw_spaceship()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, color):
        super().__init__()  # sprite의 init을 실행한다.
        self.screen = game.screen
        self.settings = game.settings
        self.color = self.settings.bullet_color[color]  # color를 0, 1, 2로 받아서 R, G, B색 총알이 되도록 함.
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = game.ship.rect.midtop
        self.y = self.rect.y

    def update(self):
        self.y -= self.settings.bullet_speed
        self.rect.y = int(self.y)  # 마찬가지로 float로 저장했다가 int로 변환해 적용하는 방식을 사용했다.
        self.draw_bullet()

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)

class Octopus(pygame.sprite.Sprite):
    def __init__(self, color, game):
        super().__init__()
        self.screen = game.screen
        self.settings = game.settings
        self.image = pygame.image.load("global/octopus.bmp")
        self.palette = [(255, 0, 0, 80), (0, 255, 0, 80), (0, 0, 255, 80)]  # 여러 색의 문어가 존재하도록 palette를 설정했다.
        self.image.fill(self.palette[color], special_flags=pygame.BLEND_RGBA_ADD)  # 색을 넣어주기 위해 filter를 이용한다.
        self.rect = self.image.get_rect()
        self.x = self.rect.x
        self.rect.x = 0
        self.rect.y = 0

    def update(self):
        self.x += octo_d * self.settings.octopus_speed
        self.rect.x = int(self.x)  # 다른 sprite와 마찬가지로 float에 저장해서 int로 불러오는 방식을 택했다.

    def draw_octopus(self):
        self.screen.blit(self.image, self.rect)

    def check_edges(self):
        global octo_down_time
        # 양 끝에 닿았고, 이전 octo_down보다 1초 이상 더 흘렀다면
        if (self.rect.x + self.settings.octopus_size > self.settings.screen_width or self.rect.x < 0) and (time.time() - octo_down_time > 1):
            octo_down_time = time.time()
            return True  # True를 반환한다.
        else:
            return False



play = True  # 재시작과 창 닫기를 구분하기 위해 변수를 설정했다.
while play:
    # 전역변수를 정의한다. 여러 클래스에서 모두 사용되는 변수는 전역변수로 설정했다.
    d_pressed = [False, False]
    left_shift_pressed =  False
    d = 0  # 정지 0, 좌측 -1, 우측 1
    octo_d = 1  # d와 같은 규칙.
    octo_down_time = 0
    dt = 10000

    game = GamePro()
    game.run_game()