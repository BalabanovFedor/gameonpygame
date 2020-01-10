import copy
import os
from random import choice
import sys

import pygame


def sign(x):
    if x == 0:
        return 0
    if x > 0:
        return 1
    return -1


def load_image(name, colorkey=None):
    fullname = os.path.join('data', 'images', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/maps/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(WIDTH // tile_width, max(map(len, level_map))) + 8
    if len(level_map) < HEIGHT / tile_height:
        d = HEIGHT // tile_height - len(level_map) + 8
        if d % 2 == 0:
            level_map = d // 2 * [''] + level_map + d // 2 * ['']
        else:
            level_map = (d - 1) // 2 * [''] + level_map + ((d - 1) // 2 + 1) * ['']

    # дополняем каждую строку пустыми клетками ('0')
    return list(map(lambda x: x.ljust(max_width, '0'), level_map))


def generate_level(level):
    """генерация уровня"""
    global level_data

    level_data = {}
    tiles = {'empty': '0', 'wall': '1', 'floor': '2', 'item': '5', 'sceleton': '7', 'ghost': '8', 'player': '9'}
    new_player, x, y = None, None, None
    anim_coords = {}
    enem = []

    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == tiles['empty']:
                Tile('empty', x, y)
            elif level[y][x] == tiles['wall']:
                Tile('wall', x, y)
            elif level[y][x] == tiles['floor']:
                Tile("floor", x, y)
            elif level[y][x] == tiles['item']:
                Tile('floor', x, y)
                Item(x, y)

            elif level[y][x] == tiles['player']:
                Tile('floor', x, y)
                anim_coords['player'] = (x, y)
            elif level[y][x] == tiles['ghost']:
                Tile('floor', x, y)
                enem.append((x, y, 'ghost'))
            elif level[y][x] == tiles['sceleton']:
                Tile('floor', x, y)
                enem.append((x, y, 'sceleton'))

    new_player = Player(*anim_coords['player'])
    for e in enem:
        Enemy(*e)

    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def win(map):
    font = pygame.font.Font(None, 50)
    string_rendered = font.render("!!!WIIIINEER!!!", 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect = intro_rect.move((WIDTH-intro_rect[2])//2, (HEIGHT-intro_rect[3])//2)

    restart = False
    screen.blit(string_rendered, intro_rect)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    running = False
                    restart = True
                if event.key == pygame.K_ESCAPE:
                    running = False
        pygame.display.flip()
        clock.tick(FPS)
    if restart:
        game(map)


def gameover(map):
    font = pygame.font.Font(None, 50)
    string_rendered = font.render("LOSE(((", 1, pygame.Color('white'))
    img = load_image('wasted.png', -1)
    intro_rect = img.get_rect()
    intro_rect = intro_rect.move((WIDTH - intro_rect[2]) // 2, (HEIGHT - intro_rect[3]) // 2)

    restart = False
    screen.blit(img, intro_rect)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    running = False
                    restart = True
                if event.key == pygame.K_ESCAPE:
                    running = False
        pygame.display.flip()
        clock.tick(FPS)
    if restart:
        game(map)

def check_win():
    if len(enemy_group.sprites()) == 0:
        return True
    return False


def check_gameover():
    if player.inform['health'] == 0:
        return True
    return False

class Statusbar(pygame.sprite.Sprite):
    def __init__(self):
        super(Statusbar, self).__init__(statusbar_group)
        self.update_image()
        self.rect = self.image.get_rect()


    def update_image(self):
        col = pygame.Color('#14121c')
        img = pygame.Surface((135, 110))
        img.fill(col)
        heart = load_image('heart.png', -1)
        inf = player.inform
        sss = [f"speed: {inf['speed']}",
               f"power: {inf['power']}"]
        hp = inf['health']

        for i in range(hp):
            img.blit(heart, (10 + i * 42, 10))

        font = pygame.font.Font(None, 25)
        text_coord = 52
        for line in sss:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 5
            text_coord += intro_rect.height
            img.blit(string_rendered, intro_rect)

        img= img.convert()
        colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey)

        self.image = img

    def update(self, *args):
        self.update_image()


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.counter = [0, FPS // 5]  # счетчик и через сколько итераций менять

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.counter[0] += 1
        if self.counter[0] % self.counter[1] == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.type = tile_type
        if self.type == 'wall' or self.type == 'empty':
            wall_group.add(self)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites, animated_group)
        self.inform = {'health': 3,
                       'speed': 2,
                       'go': False,
                       'power': 1,
                       'buffs': []}
        self.vup = self.vleft = -1 * self.inform['speed']
        self.vdown = self.vright = self.inform['speed']
        self.frames, self.cur_frame, self.counter = {}, 0, 0
        self.side = 'down'
        self.cut_sheet(animated_images['player'], 4, 4)
        self.image = self.frames[self.side][self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.bullet_counter, self.death_counter = 0, 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        sides = ['down', 'left', 'right', 'up']
        for j in range(rows):
            self.frames[sides[j]] = []
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames[sides[j]].append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        def add_speed():
            self.vup = self.vleft = -1 * self.inform['speed']
            self.vdown = self.vright = self.inform['speed']
            if pygame.sprite.spritecollideany(self, wall_group):
                for wall in pygame.sprite.groupcollide(player_group, wall_group, False, False)[self]:
                    wall_rect = wall.rect
                    if wall_rect[1] + wall_rect[3] - self.inform['speed'] == self.rect[1]:
                        self.vup = 0
                    elif wall_rect[1] == self.rect[1] + self.rect[3] - self.inform['speed']:
                        self.vdown = 0
                    elif wall_rect[0] + wall_rect[2] - self.inform['speed'] == self.rect[0]:
                        self.vleft = 0
                    elif wall_rect[0] == self.rect[0] + self.rect[2] - self.inform['speed']:
                        self.vright = 0

        def add_img():
            if self.inform['go']:
                self.cur_frame = round(self.cur_frame + 0.1, 2)
                if self.cur_frame % 1 == 0:
                    self.cur_frame %= len(self.frames[self.side])
                    self.image = self.frames[self.side][int(self.cur_frame)]
            else:
                self.image = self.frames[self.side][0]

        def check_events():
            self.inform['go'] = False
            for key in BUTTONS.keys():
                if not BUTTONS[key]:
                    continue
                if key == pygame.K_w:
                    self.side = 'up'
                    self.inform['go'] = True
                    self.rect = self.rect.move(0, self.vup)
                elif key == pygame.K_s:
                    self.side = 'down'
                    self.inform['go'] = True
                    self.rect = self.rect.move(0, self.vdown)
                elif key == pygame.K_a:
                    self.rect = self.rect.move(self.vleft, 0)
                    self.side = 'left'
                    self.inform['go'] = True
                elif key == pygame.K_d:
                    self.rect = self.rect.move(self.vright, 0)
                    self.side = 'right'
                    self.inform['go'] = True

                crds = (self.rect[0] + 3, self.rect[1] + 5)
                if key == pygame.K_UP and self.bullet_counter > 40:
                    Bullet('up', self.inform['power'], *crds)
                    self.bullet_counter = 0
                elif key == pygame.K_DOWN and self.bullet_counter > 40:
                    Bullet('down', self.inform['power'], *crds)
                    self.bullet_counter = 0
                elif key == pygame.K_LEFT and self.bullet_counter > 40:
                    Bullet('left', self.inform['power'], *crds)
                    self.bullet_counter = 0
                elif key == pygame.K_RIGHT and self.bullet_counter > 40:
                    Bullet('right', self.inform['power'], *crds)
                    self.bullet_counter = 0

        def check_buffs():
            ddd = []
            for i in range(len(self.inform['buffs'])):
                buff = self.inform['buffs'][i]
                if self.counter == buff[-1]:
                    self.inform[buff[0]] = eval('self.inform[buff[0]]-' + buff[1])
                    ddd.append(i)

            for i in ddd[::-1]:
                del self.inform['buffs'][i]

        def check_enem():
            if pygame.sprite.spritecollideany(self, enemy_group) and self.death_counter > 60:
                self.inform['health'] -= 1
                self.death_counter = 0

        def check_life():
            self.inform['health'] = min(self.inform['health'], 3)
            if self.inform['health'] == 0:
                self.death()

        self.death_counter += 1
        self.bullet_counter += 1
        self.counter += 1
        add_img()
        add_speed()
        check_events()
        check_buffs()
        check_enem()
        check_life()

    def buff(self, buff):
        if buff is not None:
            buff = buff.split()
            self.inform[buff[0]] = eval('self.inform[buff[0]]' + buff[1])
            if len(buff) == 3:
                b = buff[:2] + [self.counter + int(buff[-1])]
                self.inform['buffs'].append(b)

    def death(self):
        pass


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, type):
        super().__init__(enemy_group, all_sprites, animated_group)
        self.inform = copy.deepcopy(enemies[type])
        self.inform['go'] = False
        self.vup = self.vleft = -1 * self.inform['speed']
        self.vdown = self.vright = self.inform['speed']
        self.frames, self.cur_frame, self.counter = {}, 0, 0
        self.side = 'down'
        self.cut_sheet(animated_images[type],
                       animated_images[type].get_rect()[2] // 24,
                       animated_images[type].get_rect()[3] // 24)
        self.image = self.frames[self.side][self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.bullet_counter = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        sides = ['down', 'left', 'right', 'up']
        for j in range(rows):
            self.frames[sides[j]] = []
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames[sides[j]].append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        def add_speed():
            self.vup = self.vleft = -1 * self.inform['speed']
            self.vdown = self.vright = self.inform['speed']
            if pygame.sprite.spritecollideany(self, wall_group):
                for wall in pygame.sprite.groupcollide(enemy_group, wall_group, False, False)[self]:
                    wall_rect = wall.rect
                    if wall_rect[1] + wall_rect[3] - self.inform['speed'] == self.rect[1]:
                        self.vup = 0
                    elif wall_rect[1] == self.rect[1] + self.rect[3] - self.inform['speed']:
                        self.vdown = 0
                    elif wall_rect[0] + wall_rect[2] - self.inform['speed'] == self.rect[0]:
                        self.vleft = 0
                    elif wall_rect[0] == self.rect[0] + self.rect[2] - self.inform['speed']:
                        self.vright = 0

        def add_side_go(dx, dy):
            self.inform['go'] = False
            if dy < 0 and abs(dx) < abs(dy):
                self.inform['go'] = True
                self.side = 'up'
            elif dy > 0 and abs(dx) < abs(dy):
                self.inform['go'] = True
                self.side = 'down'
            elif dx < 0 and abs(dx) > abs(dy):
                self.inform['go'] = True
                self.side = 'left'
            elif dx > 0 and abs(dx) > abs(dy):
                self.inform['go'] = True
                self.side = 'right'

        def add_img():

            if self.inform['go']:
                self.cur_frame = round(self.cur_frame + 0.1, 2)
                if self.cur_frame % 1 == 0:
                    self.cur_frame %= len(self.frames.get(self.side, self.frames['down']))
                    self.image = self.frames.get(self.side, self.frames['down'])[int(self.cur_frame)]
            else:
                self.image = self.frames.get(self.side, self.frames['down'])[0]

        def check_buffs():
            ddd = []
            for i in range(len(self.inform['buffs'])):
                buff = self.inform['buffs'][i]
                if self.counter == buff[-1]:
                    self.inform[buff[0]] = eval('self.inform[buff[0]]-' + buff[1])
                    ddd.append(i)

            for i in ddd[::-1]:
                del self.inform['buffs'][i]

        def motion():
            pl_rect = player.rect
            dx, dy = pl_rect[0] - self.rect[0], pl_rect[1] - self.rect[1]
            if dx <= 0:
                self.rect = self.rect.move(self.vleft * abs(sign(dx)), 0)
            elif dx >= 0:
                self.rect = self.rect.move(self.vright * abs(sign(dx)), 0)
            if dy <= 0:
                self.rect = self.rect.move(0, self.vup * abs(sign(dy)))
            elif dy >= 0:
                self.rect = self.rect.move(0, self.vdown * abs(sign(dy)))

            add_side_go(dx, dy)

            # self.rect = self.rect.move(sign(dx) * self.inform['speed'], sign(dy) * self.inform['speed'])

        def check_life():
            if self.inform['health'] <= 0:
                self.kill()

        self.bullet_counter += 1
        self.counter += 1

        add_img()
        add_speed()
        motion()
        check_buffs()
        check_life()

    def buff(self, buff):
        if buff is not None:
            buff = buff.split()
            self.inform[buff[0]] = eval('self.inform[buff[0]]' + buff[1])
            if len(buff) == 3:
                b = buff[:2] + [self.counter + int(buff[-1])]
                self.inform['buffs'].append(b)


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Item, self).__init__(all_sprites, animated_group)
        self.frames = []
        self.cut_sheet(animated_images['item'], 4, 1)
        self.image = self.frames[0]
        self.rect = self.rect.move(x * tile_width, y * tile_height)
        self.inform = {'broken': False,
                       'buff': choice(BUFFS)
                       }
        self.counter = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, player_group):
            self.inform['broken'] = True
            player.buff(self.inform['buff'])
            self.inform['buff'] = None
        if self.inform['broken']:
            self.image = self.frames[round(self.counter % 4)]
            if self.counter >= 3:
                self.inform['broken'] = False
            else:
                self.counter += 0.125


class Bullet(pygame.sprite.Sprite):
    def __init__(self, direction, power, x, y):
        def add_im():
            if direction == 'down':
                self.image = pygame.transform.rotate(self.image, 90)
            elif direction == 'up':
                self.image = pygame.transform.rotate(self.image, -90)
            elif direction == 'right':
                self.image = pygame.transform.flip(self.image, True, False)

        def speed_init():
            if direction == 'left':
                self.vy, self.vx = 0, -1 * self.inform['speed']
            elif direction == 'right':
                self.vy, self.vx = 0, self.inform['speed']
            elif direction == 'up':
                self.vx, self.vy = 0, -1 * self.inform['speed']
            elif direction == 'down':
                self.vx, self.vy = 0, self.inform['speed']

        super().__init__(all_sprites, animated_group)
        self.image = animated_images['bullet']
        self.rect = self.image.get_rect().move(x, y)
        self.inform = {'speed': 3,
                       'power': power,
                       'direction': direction,
                       'life': 320}
        self.inform['buff'] = f'health -{self.inform["power"]}'
        self.counter = 0
        add_im()
        speed_init()

    def update(self, *args):
        self.counter += 1
        if self.counter == self.inform['life']:
            self.kill()
        elif pygame.sprite.spritecollideany(self, wall_group):
            self.kill()
        elif pygame.sprite.spritecollideany(self, enemy_group):
            en = pygame.sprite.spritecollideany(self, enemy_group)
            en.buff(self.inform['buff'])
            self.kill()
        else:
            self.rect = self.rect.move(self.vx, self.vy)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x = (obj.rect.x + self.dx) % (level_x * tile_width) - tile_width
        obj.rect.y = (obj.rect.y + self.dy) % (level_y * tile_height) - tile_height

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2) + tile_width
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2) + tile_height


def clear():
    global player, level_x, level_y, clock, all_sprites, tiles_group, wall_group, animated_group, player_group, enemy_group, statusbar_group, BUTTONS

    player, level_x, level_y = None, 0, 0

    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    wall_group = pygame.sprite.Group()
    animated_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    statusbar_group = pygame.sprite.Group()

    BUTTONS = {}
    screen = pygame.display.set_mode((WIDTH, HEIGHT))


def game(map):
    global player, level_x, level_y

    def check_game():
        if check_win():
            return (True, win)
        if check_gameover():
            return (True, gameover)
        return (False,)

    clear()
    player, level_x, level_y = generate_level(load_level(map))
    camera = Camera()
    Statusbar()

    # start_screen()
    restart = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                BUTTONS[event.key] = True
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    restart = True
                    running = False
            elif event.type == pygame.KEYUP:
                BUTTONS[event.key] = False

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.update()
        all_sprites.draw(screen)
        statusbar_group.update()
        statusbar_group.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

        do_lst = check_game()
        if do_lst[0]:
            running = False
    if do_lst[0]:
        do_lst[1](map)
    elif restart:
        game(map)
    clear()


pygame.init()

BUFFS = ['health +1', 'power +1 900']

tile_width = tile_height = 32
WIDTH = HEIGHT = 512
FPS, clock = 60, pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
animated_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
statusbar_group = pygame.sprite.Group()

tile_images = {'wall': load_image('wall.png'),
               'empty': load_image('empty.png'),
               'floor': load_image('floor.png')}
animated_images = {'player': load_image('player.png', -1),
                   'item': load_image('item.png', -1),
                   'ghost': load_image('ghost.png', -1),
                   'sceleton': load_image('sceleton.png', -1),
                   'bullet': load_image('bullet.png', -1),
                   }
enemies = {'ghost': {'speed': 1,
                     'health': 2,
                     'power': 1,
                     'buffs': []},
           'sceleton': {'speed': 1,
                        'health': 4,
                        'power': 1,
                        'buffs': []}}
BUTTONS = {}
player, level_x, level_y = None, 1, 1

