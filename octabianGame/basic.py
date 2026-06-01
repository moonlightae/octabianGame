import pygame, random, time

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
        self.game_frame = 120
        self.octopus_group_quantity = 10
        self.octopus_margin = 100
        self.octopus_size = 64

class GamePro:
    def __init__(self, llife, lpoint):
        self.clock = pygame.time.Clock()  # time의 sleep 함수 기능을 프레임마다 실행해서 게임 속도를 조절하도록 한다.
        self.settings = Settings()  # Settings에 저장된 값을 불러온다.
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))  # 전체 게임에 사용될 Screen이다.
        self.ship = Spaceship(self)  # 게임의 player인 spaceship을 쉽게 접근할 수 있도록 GamePro에 저장해둔다.
        self.aliens = pygame.sprite.Group()  # 문어를 넣을 Group을 만든다.
        self.bullets = pygame.sprite.Group()  # 총알도 마찬가지로 Group을 통해 관리한다.
        self.life = 3  # player의 목숨을 GamePro 변수로 저장한다.
        self.point = 0  # player의 점수도 마찬가지.
        pygame.display.set_caption("문어외계인 침공(김태환)")

    def run_game(self):
        global d, dt, left_shift_pressed, play, damaged, llife, lpoint
        pygame.init()  # 기초 파일 생성.
        running = True  # 게임이 돌아가고 있는지에 대한 여부를 저장한다.(out이거나 목숨이 0이 되는 등에서 False)
        out = False  # 게임을 끄는 버튼을 눌렀을때 True가 된다.
        while running:
            dt += self.clock.tick(self.settings.game_frame)  # 게임 시작 이후로 지난 시간을 기록한다.
            t = self.check_events()  # 그 frame에 눌러지거나 떼어진 버튼을 list에 int로 담아 return한다. 아래가 해당하는 키이다.
            # 1: 중지, 2: A키, 좌 화살표, 3: D키, 우 화살표, 4: LSHIFT키, 5: SPACE키, 6: 우주선 정지 7: LSHIFT UP, 8: Q, 9: W, 10: E
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

            # SPACE로 bullet 발사
            if 5 in t:
                if len(self.bullets) < 5:
                    b = Bullet(self)
                    self.bullets.add(b)

            # screen을 업데이트하고, life가 0보다 작거나 같으면 게임이 정지되도록 했다.
            self.update_screen()
            if self.life <= 0:
                running = False
            if damaged:
                llife = self.life
                lpoint = self.point
                running = False

        if out:  # 종료버튼을 눌러서 running = False가 된 것인지
            play = False
            pygame.quit()
        elif not damaged:  # 게임이 멈췄을 때 damaged=True로 멈춘것인지 life=0으로 멈춘것인지 확인한다.
            llife = 3
            lpoint = 0
            self.game_over()  # life = 0으로 멈춘 경우이므로 게임오버 화면을 나타낸다.
        # damaged=True인 경우는 life가 -1될 뿐, 다시 게임이 시작되므로, play=True에 의해 점수, 목숨이 유지된 상태로 다시 시작된다.

    def check_events(self):
        global d_pressed
        r = []
        for event in pygame.event.get():  # 행동을 다 체크해서 해당되는게 있으면 r에 넣어준다.
            if event.type == pygame.QUIT:
                r.append(1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:  # 이동에 대한 입력인 A, D는 중첩될 수 없게 elif를 이용한다.
                    d_pressed[0] = True
                    r.append(2)
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    d_pressed[1] = True
                    r.append(3)
                if event.key == pygame.K_SPACE:  # space는 좌우키와 겹칠 수 있으므로 elif가 아닌 if를 이용했다.
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
        self.screen.fill(self.settings.bg_color)  # screen을 초기화한다.
        self.create_fleet()  # 조건이 맞는다면 문어를 더 생성한다.
        self.aliens.update()  # alien, bullet, ship, board을 화면에 나타낸다.
        self.bullets.update()
        self.ship.update()
        self.board()
        self.change_direct()  # 문어가 벽에 닿으면 방향을 바꾸고 아래로 내린다.

        # 총알과 문어가 충돌한 경우만큼, 점수를 +10한다.
        # groupcollide의 반환값은 충돌 객체 사이의 dictionary이다.
        k = len(pygame.sprite.groupcollide(self.aliens, self.bullets, True, True))
        if 0 < k:
            self.point += k * 10
        # 프레임마다 ship과 alien이 충돌했는지 확인하여
        k = bool(pygame.sprite.spritecollide(self.ship, self.aliens, True))
        if k:  # 한 번 이상 충돌했다면 life를 1 차감한다.
            self.life -= 1
            damaged = True

        self.aliens.draw(self.screen)  # 문어는 change_direct()가 외부 함수로 나왔기 때문에, draw를 update 내부에 넣지 않고, 따로 실행한다.

    def change_direct(self):  # 조건을 확인하여 문어가 벽에 닿으면 아래로 내려가도록 한다.
        global octo_d, octo_down_time
        octo_down = False
        for i in self.aliens:  # 모든 AI에 대해서 check_edges()를 하고, 그 중 하나라도 True가 나오면
            octo_down = octo_down or i.check_edges()  # octo_down을 True로 바꾼다.
        if octo_down:
            octo_d *= -1  # 방향을 바꾼다.
            for j in self.aliens:  # 모든 alien에 대해 아래로 20씩 내린다.
                j.rect.midtop = (j.rect.midtop[0], j.rect.midtop[1] + 20)

    def create_fleet(self):  # 문어 생성 조건이 만족되면 문어를 생성한다.
        global dt
        rx, rx2, ry, ry2 = self.fleet_crit()
        if (rx is not None and (rx < 5 or rx2 > self.settings.screen_width - 5) and ry > self.settings.octopus_size + 10) or (dt > 10000 and len(self.aliens) == 0):
            # 문어가 존재할 때, 가장 작은 y가 octopus_size + 10보다 크거나, 문어가 존재하지 않을 때, 이전 문어 생성 이후로 10초가 지났다면 생성한다.
            dt = 0
            if rx is None:
                now_x = 0
            elif rx < 5:  # 문어가 존재하지 않거나 가장 작은 x가 5보다 작으면 왼쪽에 충돌한 것으로 간주한다.
                now_x = rx
            else:
                now_x = rx2
            for i in range(10):
                octo = Octopus(self)
                octo.x = now_x  # octopus가 충돌한 반대쪽에 margin을 100 남기고, ogq(settings에서 변수로 할당)개가 등분배되어 들어갈 수 있도록 했다.
                if rx is None or rx < 5:
                    now_x += (self.settings.screen_width-self.settings.octopus_margin)//self.settings.octopus_group_quantity
                else:
                    now_x -= (self.settings.screen_width-self.settings.octopus_margin)//self.settings.octopus_group_quantity
                self.aliens.add(octo)

    def fleet_crit(self):  # 전체 문어에서 최대, 최소에 해당하는 x, y값을 구해 반환한다.
        if len(self.aliens) != 0:
            ry = self.settings.screen_height  # 이론상 최댓값을 최소에 저장하고, 최솟값을 최대에 저장해서 계산했다.
            ry2 = 0
            rx = self.settings.screen_width
            rx2 = 0
            for j in self.aliens:  # 모든 문어에 대해서
                if j.rect.y > self.settings.screen_height:  # 화면 밖으로 나간 문어는 없애고,
                    j.kill()
                ry = min(ry, j.rect.y)  # 그렇지 않으면 min과 max를 계산한다.
                ry2 = max(ry2, j.rect.y)
                rx = min(rx, j.rect.x)
                rx2 = max(rx2, j.rect.x)

            return rx, rx2+self.settings.octopus_size, ry, ry2+self.settings.octopus_size  # 최댓값에는 문어 크기를 더해서 오른쪽 끝, 아래끝을 기준으로 바꾸었다.
        else:
            return None, None, None, None  # 문어가 존재하지 않을때에는 None이 return되도록 했다.

    def board(self):  # 점수판의 ui이다.
        fontC = pygame.font.Font("global/Galmuri11-Condensed.ttf", 50)
        text = fontC.render(f"Points: {self.point}", True, (0, 0, 0))
        self.screen.blit(text, (self.settings.screen_width-text.get_width()-20, 20))
        text = fontC.render(f"Life: {self.life}", True, (0, 0, 0))
        self.screen.blit(text, (20, 20))

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
            self.clock.tick(120)
            t = self.check_events()
            if 5 in t:  # Space 키를 누르면 게임 재실행
                break
            if 1 in t:  # 창 닫기 버튼을 누르면 게임 종료.
                play = False
                break

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
        if self.x < 0:  # 우주선이 화면 밖으로 나갈 수 없게 했다.
            self.x = 0
        elif self.x > self.settings.screen_width - (self.rect.right - self.rect.left):
            self.x = self.settings.screen_width - (self.rect.right - self.rect.left)
        self.rect.x = int(self.x)  # float으로 저장된 x좌표를 int로 변환해 적용한다.
        self.draw_spaceship()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()  # sprite의 init을 실행한다.
        self.screen = game.screen
        self.settings = game.settings
        self.color = self.settings.bullet_color
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = game.ship.rect.midtop
        self.y = self.rect.y

    def update(self):
        self.y -= self.settings.bullet_speed
        self.rect.y = int(self.y)  # 마찬가지로 float로 저장했다가 int로 변환해 적용하는 방식을 사용했다.
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
llife = 3
lpoint = 0
while play:
    # 전역변수를 정의한다. 여러 클래스에서 모두 사용되는 변수는 전역변수로 설정했다.
    d_pressed = [False, False]
    left_shift_pressed =  False
    d = 0  # 정지 0, 좌측 -1, 우측 1
    octo_d = 1  # d와 같은 규칙.
    octo_down_time = 0
    dt = 10000
    damaged = False

    game = GamePro(llife, lpoint)
    game.run_game()