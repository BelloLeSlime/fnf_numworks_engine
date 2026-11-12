"""
Chart editor - version PC (pygame)
Port de la version NumWorks.

Notes (sur le personnage sélectionné, Opponent ou Player)
  flèches ................ pose / retire une note à la position courante
  Shift + flèches ........ pose / retire une note longue (hold)
                           Haut = TOOLBOX, Gauche = IMAGINARY,
                           Bas = COMMA, Droite = POWER
Navigation
  A ...................... (SHIFT) recule d'un 16e de temps
  E ...................... (EXP)   avance d'un 16e de temps
  Espace ................. (ALPHA) change de personnage
Autres
  Échap .................. (SQUARE) changer le BPM (console)
  Ctrl + S ............... (EXE)    export (console + export.txt)
  = ...................... (XNT)    importer un Chart de files.py (console)

Fait entièrement par Claude, inspiré de chart_editor.py
"""
import math
import pygame

try:
    import files as files_module
except Exception:
    files_module = None


def _from_files(name, default):
    return getattr(files_module, name, default)


class _RectImage:
    def __init__(self, image):
        self.image = image


class _Chart:
    def __init__(self, chart, bpm):
        self.chart = chart
        self.bpm = bpm


RectImage = _from_files("RectImage", _RectImage)
Chart = _from_files("Chart", _Chart)


def _placeholder(r, g, b):
    # Image de secours si files.py n'a pas la flèche (2e rect = couleur de la note)
    return RectImage([0, 0, 80, 80, 40, 40, 40, 8, 8, 64, 64, r, g, b])


left_arrow = _from_files("left_arrow", _placeholder(194, 75, 153))
down_arrow = _from_files("down_arrow", _placeholder(0, 255, 255))
up_arrow = _from_files("up_arrow", _placeholder(18, 250, 5))
right_arrow = _from_files("right_arrow", _placeholder(249, 57, 63))

# ---------------------------------------------------------------- réglages
W, H = 320, 222          # résolution logique (celle de la NumWorks)
SCALE = 3                # fenêtre = W*SCALE x H*SCALE
FPS = 60
REPEAT_DELAY = 300       # ms avant répétition de A / E maintenues
REPEAT_RATE = 60         # ms entre deux répétitions
CHAR_LIMIT = 144 * 7     # au-delà, un "!" s'affiche (limite de la calculatrice)


# ---------------------------------------------------------------- données
def to_ms(ms):
    """Les notes sont des ms entières ; la tolérance évite 2999.9999 -> 2999."""
    return int(math.floor(ms + 1e-6))


class ChartEdit:
    def __init__(self, bpm):
        # 0-3 Opponent, 4-7 Player, 8-9 réservés, 10-13 holds Opponent, 14-17 holds Player
        self.chart = [[], [], [], [], [], [], [], [], 0, 0, [], [], [], [], [], [], [], []]
        self.bpm = bpm

    @property
    def char_count(self):
        return len(str(self.chart).replace(" ", ""))

    def change_bpm(self, wanted_bpm):
        coef = wanted_bpm / self.bpm
        self.bpm = wanted_bpm
        for note in self.chart:
            if not isinstance(note, list):
                continue
            for i, ms in enumerate(note):
                note[i] = int(round(ms / coef))

    def get_mspb(self):
        return (1 / self.bpm) * 60000

    def add_note(self, ms, note):
        self.chart[note].append(to_ms(ms))

    def rm_note(self, ms, note):
        self.chart[note].remove(to_ms(ms))

    def get_line(self, ms):
        ms = to_ms(ms)
        return [i for i in range(18) if i not in (8, 9) and ms in self.chart[i]]

    def toggle_note(self, ms, note):
        if to_ms(ms) in self.chart[note]:
            self.rm_note(ms, note)
        else:
            self.add_note(ms, note)


# ---------------------------------------------------------------- init
pygame.init()
screen = pygame.display.set_mode((W * SCALE, H * SCALE))
canvas = pygame.Surface((W, H))
clock = pygame.time.Clock()

# police : on cherche la taille qui donne ~10 px logiques par caractère (comme la NumWorks)
_size = 8
while pygame.font.Font(None, _size).size("0")[0] < 8 * SCALE:
    _size += 1
font = pygame.font.Font(None, _size)

chart_edit = ChartEdit(120)
selected_ms = 0
selected_char = 0
running = True

held_key = None
held_next = 0

ARROW_NOTE = {pygame.K_LEFT: 0, pygame.K_DOWN: 1, pygame.K_UP: 2, pygame.K_RIGHT: 3}
BLACK = (0, 0, 0)


# ---------------------------------------------------------------- affichage
def draw_image(img, x, y, size):
    """Dessine une RectImage (7 nombres par rect) dans un carré de `size` pixels."""
    d = img.image
    rects = [d[i:i + 7] for i in range(0, len(d), 7)]
    base = max(r[0] + r[2] for r in rects)
    base = max(base, max(r[1] + r[3] for r in rects))
    for i, (rx, ry, rw, rh, r, g, b) in enumerate(rects):
        if i == 0:
            continue
        left = x + rx * size // base
        top = y + ry * size // base
        right = x + (rx + rw) * size // base
        bottom = y + (ry + rh) * size // base
        canvas.fill((r, g, b), (left, top, max(1, right - left), max(1, bottom - top)))


def hold_color(image):
    d = image.image
    return (min(d[11] + 50, 255), min(d[12] + 50, 255), min(d[13] + 50, 255))


def draw_arrow(y, note):
    images = [left_arrow, down_arrow, up_arrow, right_arrow]
    if note in (0, 1, 2, 3):
        draw_image(images[note], 32 * note, y, 32)
    elif note in (4, 5, 6, 7):
        draw_image(images[note - 4], 130 + 32 * (note - 4), y, 32)
    elif note in (10, 11, 12, 13):
        canvas.fill(hold_color(images[note - 10]), (8 + 32 * (note - 10), y - 20, 16, 52))
    elif note in (14, 15, 16, 17):
        canvas.fill(hold_color(images[note - 14]), (138 + 32 * (note - 14), y - 20, 16, 52))


def draw_string(text, x, y):
    screen.blit(font.render(text, True, BLACK), (x * SCALE, y * SCALE))


def render():
    canvas.fill((225, 225, 225))
    canvas.fill((255, 255, 0), (129 * selected_char, 0, 128, 40))
    canvas.fill(BLACK, (0, 38, 257, 2))
    canvas.fill(BLACK, (127, 0, 3, 222))
    canvas.fill(BLACK, (257, 0, 3, 222))
    canvas.fill((255, 0, 0), (0, 108 + 16, 257, 1))

    mspb = chart_edit.get_mspb()
    ms = selected_ms - mspb / 4 * 2
    y = 40
    for i in range(6):
        canvas.fill(BLACK, (0, 40 + i * 34, 257, 2 if ms % mspb <= 2 else 1))
        for note in chart_edit.get_line(ms):
            draw_arrow(y, note)
        ms += mspb / 4
        y += 34

    pygame.transform.scale(canvas, screen.get_size(), screen)

    draw_string("Opponent", 25, 10)
    draw_string("Player", 160, 10)
    draw_string(str(int(selected_ms)) + "ms", 260, 0)
    draw_string(str(chart_edit.bpm) + "BPM", 260, 20)
    count = chart_edit.char_count
    draw_string(str(count) + "c" + ("!" if count > CHAR_LIMIT else ""), 260, 40)
    pygame.display.flip()


# ---------------------------------------------------------------- navigation
def step_time(direction):
    global selected_ms
    selected_ms = max(0, selected_ms + direction * chart_edit.get_mspb() / 4)


# ---------------------------------------------------------------- console
def reset_after_console():
    global held_key
    held_key = None
    pygame.event.clear()


def ask_bpm():
    try:
        bpm = int(input("BPM: > "))
    except ValueError:
        print("Valeur invalide")
        return
    if bpm <= 0:
        print("Le BPM doit être > 0")
        return
    chart_edit.change_bpm(bpm)


def export_chart():
    chart_str = str(chart_edit.chart).replace(" ", "")
    print(chart_str)
    print("BPM: " + str(chart_edit.bpm))
    with open("export.txt", "w") as f:
        f.write(chart_str + "\n")
        f.write("BPM: " + str(chart_edit.bpm) + "\n")
    print("(aussi écrit dans export.txt)")


def import_chart():
    found = []
    if files_module:
        for name, value in vars(files_module).items():
            if isinstance(value, Chart):
                found.append((name, value))
    if not found:
        print("Aucun Chart trouvé dans files.py")
        return
    print("\n0. Cancel")
    for i, (name, _) in enumerate(found, 1):
        print(str(i) + ". " + name)
    try:
        idx = int(input("> "))
    except ValueError:
        return
    if not (1 <= idx <= len(found)):
        return
    chrt = found[idx - 1][1]
    # copie, pour ne pas modifier le Chart de files.py en éditant
    chart_edit.chart = [list(n) if isinstance(n, list) else n for n in chrt.chart]
    chart_edit.bpm = chrt.bpm


# ---------------------------------------------------------------- boucle
while running:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYUP:
            if event.key == held_key:
                held_key = None

        elif event.type == pygame.KEYDOWN:
            k = event.key
            mods = pygame.key.get_mods()
            shift = bool(mods & pygame.KMOD_SHIFT)
            ctrl = bool(mods & pygame.KMOD_CTRL)

            if k in ARROW_NOTE:
                note = ARROW_NOTE[k] + (10 if shift else 0) + 4 * selected_char
                chart_edit.toggle_note(selected_ms, note)

            elif k == pygame.K_SPACE:                    # ALPHA
                selected_char = 1 - selected_char

            elif k in (pygame.K_a, pygame.K_e):          # SHIFT / EXP
                step_time(-1 if k == pygame.K_a else 1)
                held_key = k
                held_next = now + REPEAT_DELAY

            elif k == pygame.K_ESCAPE:                   # SQUARE
                ask_bpm()
                reset_after_console()

            elif k == pygame.K_s and ctrl:               # EXE
                export_chart()
                reset_after_console()

            elif k == pygame.K_EQUALS:                   # XNT
                import_chart()
                reset_after_console()

    # répétition de A / E maintenues
    if held_key is not None and now >= held_next:
        if pygame.key.get_pressed()[held_key]:
            step_time(-1 if held_key == pygame.K_a else 1)
            held_next = now + REPEAT_RATE
        else:
            held_key = None

    render()

    caption = "Chart editor - " + ("Player" if selected_char else "Opponent")
    pygame.display.set_caption(caption)

    clock.tick(FPS)

pygame.quit()