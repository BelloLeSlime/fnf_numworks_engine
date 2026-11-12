"""
Image editor using rectangles - PC version
Portage of the Numworks version

Mouse
  left click ......... (OK)       draws a rectangle (hold)
  middle click ....... (POWER)    moves a rectangle
  right clic ......... (SQUARE)   resizes (closest corner)
  mouse button 4 ..... (BACKSPACE) deletes
  mouse button 5 ..... (COMMA)    fills with selected color
  Shift + button 5 ... (SQRT)     pipette
  molette up/down .... (PLUS/MINUS) goes up / down in the order
  Shift + molette .... (MULT/DIV) puts in the very front / the very back

Keyboard
  arrows ............. moves the cursor
  Shift + arrows ..... one pixel per press     Ctrl = 5 steps at a time
  Alt + arrows ....... (LN/COS/SIN/TAN) offsets every rectangle
  Ctrl + S ........... (EXE)      export menu
  Escap .............. (TOOLBOX)  options
  = .................. (XNT)      import a RectImage from files.py
  C .................. (ANS)      select a color
The menus display in the console

Entirely made by Claude, inspired by rect_edit.py
"""
import pygame

try:
    import files as files_module
    RectImage = files_module.RectImage
except Exception:
    files_module = None

    class RectImage:
        def __init__(self, image):
            self.image = image

# ---------------------------------------------------------------- réglages
W, H = 320, 222          # résolution logique (celle de la NumWorks)
SCALE = 3                # taille de la fenêtre = W*SCALE x H*SCALE
FPS = 60
ARROW_DELAY = 15         # ms entre deux déplacements flèches maintenues
BTN_BACK = 6             # bouton latéral "4" (X1) dans pygame 2
BTN_COMMA = 7            # bouton latéral "5" (X2) dans pygame 2
DEBUG_BUTTONS = False    # True : affiche le numéro de chaque bouton cliqué


# ---------------------------------------------------------------- données
class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

    def copy(self):
        return Rect(self.x, self.y, self.w, self.h, self.color)


def norm(rect):
    """(x, y, w, h) avec w et h positifs."""
    x, y, w, h = rect.x, rect.y, rect.w, rect.h
    if w < 0:
        x += w
        w = -w
    if h < 0:
        y += h
        h = -h
    return x, y, w, h


class RectImageEdit:
    def __init__(self):
        self.data = []  # du fond (début) vers le dessus (fin)

    def add_rect(self, rect):
        rect.x, rect.y, rect.w, rect.h = norm(rect)
        if rect.w == 0 or rect.h == 0:
            return
        self.data.append(rect)

    def rm_rect(self, rect):
        self.data.remove(rect)

    def get_rect(self, x, y):
        """Rectangle le plus haut dans la pile à cette position."""
        for rect in reversed(self.data):
            if rect.x <= x < rect.x + rect.w and rect.y <= y < rect.y + rect.h:
                return rect
        return None

    def get_pixel(self, x, y):
        rect = self.get_rect(x, y)
        return rect.color if rect else None

    def get_idx(self, rect):
        return self.data.index(rect)

    def rearange(self, sign, idx):
        """Échange avec le voisin (+1 = vers le dessus, -1 = vers le fond)."""
        j = idx + sign
        if 0 <= j < len(self.data):
            self.data[idx], self.data[j] = self.data[j], self.data[idx]

    def to_front(self, idx):
        self.data.append(self.data.pop(idx))

    def to_back(self, idx):
        self.data.insert(0, self.data.pop(idx))


# ---------------------------------------------------------------- init
pygame.init()
screen = pygame.display.set_mode((W * SCALE, H * SCALE))
canvas = pygame.Surface((W, H))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

image = RectImageEdit()
cursor = Vec(160, 111)
cursor_color = (0, 0, 0)
background_color = (225, 225, 225)
selected_color = (0, 0, 0)

drawing_rect = None
moving_rect = None
resizing_rect = None
cursor_offset = None
selected_corner = 0
og_rect = None
og_cursor = None

ignore_motion = None
last_arrow = 0
last_caption = ""
running = True

ARROWS = {
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
}


# ---------------------------------------------------------------- utilitaires
def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def move_cursor(dx, dy):
    """Déplace le curseur et téléporte la vraie souris au même endroit."""
    global ignore_motion
    cursor.x = clamp(cursor.x + dx, 0, W)
    cursor.y = clamp(cursor.y + dy, 0, H)
    px = clamp(cursor.x * SCALE + SCALE // 2, 0, W * SCALE - 1)
    py = clamp(cursor.y * SCALE + SCALE // 2, 0, H * SCALE - 1)
    ignore_motion = (px, py)
    pygame.mouse.set_pos((px, py))


def render():
    canvas.fill(background_color)
    for rect in image.data:
        canvas.fill(rect.color, norm(rect))
    if drawing_rect:
        canvas.fill(drawing_rect.color, norm(drawing_rect))
    pygame.transform.scale(canvas, screen.get_size(), screen)
    screen.fill(cursor_color, (cursor.x * SCALE, cursor.y * SCALE, SCALE, SCALE))
    pygame.display.flip()


def apply_resize():
    r, o = resizing_rect, og_rect
    if selected_corner in (0, 2):      # côté gauche
        r.x = cursor.x - cursor_offset.x
        r.w = o.w + (o.x - r.x)
    else:                              # côté droit
        r.w = o.w + (cursor.x - og_cursor.x)
    if selected_corner in (0, 1):      # côté haut
        r.y = cursor.y - cursor_offset.y
        r.h = o.h + (o.y - r.y)
    else:                              # côté bas
        r.h = o.h + (cursor.y - og_cursor.y)


# ---------------------------------------------------------------- console
def ask_int(prompt="> "):
    try:
        return int(input(prompt))
    except ValueError:
        return None


def ask_color():
    try:
        r = int(input("r: > "))
        g = int(input("g: > "))
        b = int(input("b: > "))
    except ValueError:
        print("Valeur invalide")
        return None
    return (clamp(r, 0, 255), clamp(g, 0, 255), clamp(b, 0, 255))


def reset_interaction():
    """À appeler après un menu console (les événements souris ont pu être perdus)."""
    global drawing_rect, moving_rect, resizing_rect
    drawing_rect = moving_rect = resizing_rect = None
    pygame.event.clear()


def settings():
    global background_color, cursor_color
    while True:
        print("\n0. Back")
        print("1. Change Background Color")
        print("2. Change Cursor Color")
        choice = ask_int()
        if choice == 0:
            return
        if choice in (1, 2):
            col = ask_color()
            if col:
                if choice == 1:
                    background_color = col
                else:
                    cursor_color = col


def export_image():
    data = []
    for rect in image.data:
        data += [rect.x, rect.y, rect.w, rect.h,
                 rect.color[0], rect.color[1], rect.color[2]]
    line = "image=RectImage(" + str(data).replace(" ", "") + ")"
    print(line)
    with open("../../export.txt", "w") as f:
        f.write(line + "\n")
    print("(aussi écrit dans export.txt)")


def import_image():
    found = []
    if files_module:
        for name, value in vars(files_module).items():
            if isinstance(value, RectImage):
                found.append((name, value))
    if not found:
        print("Aucune RectImage trouvée dans files.py")
        return
    print("\n0. Cancel")
    for i, (name, _) in enumerate(found, 1):
        print(str(i) + ". " + name)
    idx = ask_int()
    if not idx or not (1 <= idx <= len(found)):
        return
    img = found[idx - 1][1].image
    rects = []
    for i in range(len(img) // 7):
        x, y, w, h, r, g, b = img[i * 7:i * 7 + 7]
        rects.append(Rect(x, y, w, h, (r, g, b)))
    image.data = rects


# ---------------------------------------------------------------- boucle
while running:
    mods = pygame.key.get_mods()
    shift = bool(mods & pygame.KMOD_SHIFT)
    ctrl = bool(mods & pygame.KMOD_CTRL)
    alt = bool(mods & pygame.KMOD_ALT)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEMOTION:
            if ignore_motion == event.pos:
                ignore_motion = None
            else:
                cursor.x = clamp(event.pos[0] // SCALE, 0, W)
                cursor.y = clamp(event.pos[1] // SCALE, 0, H)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            b = event.button
            if DEBUG_BUTTONS:
                print("bouton", b)
            rect = image.get_rect(cursor.x, cursor.y)

            if b == 1:                                   # OK
                drawing_rect = Rect(cursor.x, cursor.y, 0, 0, selected_color)

            elif b == 2 and rect:                        # POWER
                moving_rect = rect
                cursor_offset = Vec(cursor.x - rect.x, cursor.y - rect.y)

            elif b == 3 and rect:                        # SQUARE
                resizing_rect = rect
                og_rect = rect.copy()
                og_cursor = Vec(cursor.x, cursor.y)
                cursor_offset = Vec(cursor.x - rect.x, cursor.y - rect.y)
                left = cursor.x < rect.x + rect.w / 2
                top = cursor.y < rect.y + rect.h / 2
                if left:
                    selected_corner = 0 if top else 2
                else:
                    selected_corner = 1 if top else 3

            elif b == BTN_BACK and rect:                 # BACKSPACE
                image.rm_rect(rect)

            elif b == BTN_COMMA and shift:               # SQRT : prélever la couleur
                if rect:
                    selected_color = rect.color

            elif b == BTN_COMMA and rect:                # COMMA : recolorer
                rect.color = selected_color

        elif event.type == pygame.MOUSEBUTTONUP:
            b = event.button
            if b == 1 and drawing_rect:
                image.add_rect(drawing_rect)
                drawing_rect = None
            elif b == 2:
                moving_rect = None
            elif b == 3 and resizing_rect:
                resizing_rect.x, resizing_rect.y, resizing_rect.w, resizing_rect.h = norm(resizing_rect)
                if resizing_rect.w == 0 or resizing_rect.h == 0:
                    image.rm_rect(resizing_rect)
                resizing_rect = None

        elif event.type == pygame.MOUSEWHEEL:
            d = event.y or event.x       # certains OS renvoient Shift+molette en x
            rect = image.get_rect(cursor.x, cursor.y)
            if d and rect:
                idx = image.get_idx(rect)
                if shift:                                # MULT / DIV
                    if d > 0:
                        image.to_front(idx)
                    else:
                        image.to_back(idx)
                else:                                    # PLUS / MINUS
                    image.rearange(1 if d > 0 else -1, idx)

        elif event.type == pygame.KEYDOWN:
            k = event.key
            if k in ARROWS:
                dx, dy = ARROWS[k]
                if alt:                                  # LN / COS / SIN / TAN
                    for rect in image.data:
                        rect.x += dx
                        rect.y += dy
                elif shift:                              # un pixel par appui
                    step = 5 if ctrl else 1
                    move_cursor(dx * step, dy * step)

            elif k == pygame.K_s and ctrl:               # EXE
                print("\n0. Cancel")
                print("1. Export rects")
                if ask_int() == 1:
                    export_image()
                reset_interaction()

            elif k == pygame.K_ESCAPE:                   # TOOLBOX
                settings()
                reset_interaction()

            elif k == pygame.K_EQUALS:                   # XNT
                import_image()
                reset_interaction()

            elif k == pygame.K_c:                        # ANS
                col = ask_color()
                if col:
                    selected_color = col
                reset_interaction()

    # --- flèches maintenues (curseur continu)
    if not shift and not alt:
        now = pygame.time.get_ticks()
        if now - last_arrow >= ARROW_DELAY:
            keys = pygame.key.get_pressed()
            dx = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
            dy = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
            if dx or dy:
                step = 5 if ctrl else 1
                move_cursor(dx * step, dy * step)
                last_arrow = now

    # --- actions maintenues
    if drawing_rect:
        drawing_rect.w = cursor.x - drawing_rect.x
        drawing_rect.h = cursor.y - drawing_rect.y
    if moving_rect:
        moving_rect.x = cursor.x - cursor_offset.x
        moving_rect.y = cursor.y - cursor_offset.y
    if resizing_rect:
        apply_resize()

    render()

    caption = "Rect editor  (%d, %d)  couleur %s  rects: %d" % (
        cursor.x, cursor.y, selected_color, len(image.data))
    if caption != last_caption:
        pygame.display.set_caption(caption)
        last_caption = caption

    clock.tick(FPS)

pygame.quit()