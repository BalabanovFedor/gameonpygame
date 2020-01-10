import pygame
from game import game, WIDTH, HEIGHT, screen, load_image


def btn_img(s, color, fontStyle, fontHeight):
    font = pygame.font.Font(fontStyle, fontHeight)
    text_coord = 2
    string_rendered = font.render(s, 1, color)
    intro_rect = string_rendered.get_rect()
    text_coord += 5
    intro_rect.top = text_coord
    intro_rect.x = 5
    text_coord += intro_rect.height
    return string_rendered


def buttons_init():
    Button('start', (all_sprites, menubtn_group, btn_group), (30, 40, 193, 50), levelbtn_group.draw, (screen,),
           btn_img('START', purple, None, 90))  # start
    levelbtns_init()
    Button('control', (all_sprites, menubtn_group, btn_group), (30, 130, 193, 50), rulesp_group.draw, (screen,),
           btn_img('CONTROL', purple, None, 60))
    Button('easter egg', (all_sprites,), (500, 500, 12, 12), print,
           ("Мои поздравления!!! Это первая пасхалка. Осталось найти остальные"),
           btn_img('', pygame.Color('#f01010'), None, 1))


def levelbtns_init():
    rect = pygame.Rect(0, 0, 35, 40)
    levels = {1: '1.txt', 2: '2.txt', 3: '3.txt'}
    x0, y0 = 280, 50
    space = 40
    for n, map in levels.items():
        img = btn_img(str(n), pygame.Color('blue'), None, 60)
        pygame.draw.rect(img, pygame.Color('blue'), rect, 1)
        Button('level', (all_sprites, levelbtn_group, btn_group),
               rect.move(x0 + space * ((n - 1) % 3), y0 + space * ((n - 1) // 3 % 3)), game,
               (map,), img)


def check_menu():
    for btn in menubtn_group:
        if btn.status:
            btn.run()


def footsp():
    footer = pygame.sprite.Sprite(all_sprites, footsp_group)
    footer.image = load_image('footer.png', -1)
    footer.rect = footer.image.get_rect().move(20, 460)


def rulsp():
    intro_text = ["Для ходьбы используйте",
                  "клавиши WASD,",
                  "для стрельбы - стрелочки,",
                  "рестарт - R.",
                  "---------------------",
                  "Замочите всех в этих",
                  "подземельях)))"]
    font = pygame.font.Font(None, 25)
    text_coord = 0
    img = pygame.Surface((280, 300))
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        img.blit(string_rendered, intro_rect)

    rulesp = pygame.sprite.Sprite(all_sprites, rulesp_group)
    rulesp.image = img
    rulesp.rect = (265, 50, 190, 220)


class Button(pygame.sprite.Sprite):
    def __init__(self, type, groups, rect, func, func_args=None, img=None):
        super(Button, self).__init__(groups)
        self.type = type
        self.image = img
        self.rect = rect
        self.func, self.args = func, func_args
        self.status = False

    def check_touch(self, x, y):
        xxx = (self.rect[0] <= x <= (self.rect[0] + self.rect[2]))
        yyy = (self.rect[1] <= y <= (self.rect[1] + self.rect[3]))
        return xxx and yyy

    def event(self, mouse_pos):
        if self.check_touch(*mouse_pos):
            self.run()
            self.status = True
        else:
            self.status = False

    def run(self):
        if self.args is not None:
            self.func(*self.args)
        else:
            self.func()

    def add_status(self, bool):
        self.status = bool

def clear():
    global btn_group, menubtn_group, levelbtn_group, all_sprites, rulesp_group, footsp_group, FPS
    btn_group = pygame.sprite.Group()
    menubtn_group = pygame.sprite.Group()
    levelbtn_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    rulesp_group = pygame.sprite.Group()
    footsp_group = pygame.sprite.Group()
    footsp()
    rulsp()
    buttons_init()
    FPS = 60


def menu():
    pygame.init()

    clear()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for btn in btn_group:
                    btn.event(pos)

        screen.fill(pygame.Color('black'))

        check_menu()
        menubtn_group.draw(screen)
        footsp_group.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


purple = pygame.Color('#a349a4')


if __name__ == '__main__':
    menu()
