"""Genera el resourcepack medieval de Shopkeepers Medieval (MC 1.21.1, pack_format 34).

Incluye:
 - Ventana de comercio de aldeano/mercader reskineada (madera + pergamino).
 - Botones HD (CustomModelData 1001-1013 sobre PAPER).
 - Fondos para los menus de mercado / grafica / banco (glifos E000-E002).
Uso:  python3 build_rp.py   (necesita Pillow)
Salida: ../resourcepack/ShopkeepersMedieval.zip y la carpeta ../resourcepack/pack
"""
import os, json, zipfile, shutil, random, math
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'resourcepack')
PACK = os.path.join(OUT, 'pack')
VAN = os.path.join(HERE, 'vanilla')
shutil.rmtree(OUT, ignore_errors=True)
for d in ('assets/minecraft/models/item', 'assets/minecraft/font',
          'assets/minecraft/textures/gui/container',
          'assets/minecraft/textures/gui/sprites/container/villager',
          'assets/shopkeepers/models/item', 'assets/shopkeepers/textures/item',
          'assets/shopkeepers/textures/font'):
    os.makedirs(os.path.join(PACK, d))
RND = random.Random(1337)

# ----------------------------------------------------------------- paleta
INK = (34, 21, 11); WOOD_DD = (52, 32, 17); WOOD_D = (84, 54, 28); WOOD = (122, 82, 44)
WOOD_L = (165, 117, 66); GOLD = (244, 200, 72); GOLD_L = (255, 236, 150); GOLD_D = (158, 108, 24)
PARCH = (226, 205, 156); PARCH_L = (246, 233, 196); PARCH_D = (186, 160, 108)
RED = (176, 44, 44); RED_D = (110, 22, 26); GREEN = (70, 150, 66); GREEN_D = (34, 92, 38)
IRON = (150, 154, 168); IRON_D = (82, 86, 98); BLUE = (52, 98, 168)

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def jitter(c, amt):
    n = RND.randint(-amt, amt)
    return tuple(max(0, min(255, v + n)) for v in c)

def wood_texture(w, h, base=WOOD, light=WOOD_L, dark=WOOD_D, plank=0):
    img = Image.new('RGBA', (w, h))
    px = img.load()
    rows = [RND.uniform(-1, 1) for _ in range(h)]
    for y in range(h):
        row_t = 0.5 + 0.5 * math.sin(y * 0.35 + rows[y]) * 0.5
        for x in range(w):
            t = row_t + 0.18 * math.sin((x + y * 3) * 0.05) + RND.uniform(-0.06, 0.06)
            t = max(0.0, min(1.0, t))
            c = mix(dark, base, t * 2) if t < 0.5 else mix(base, light, (t - 0.5) * 2)
            px[x, y] = c + (255,)
    if plank:
        d = ImageDraw.Draw(img)
        for y in range(plank, h, plank):
            d.line([0, y, w, y], fill=WOOD_DD + (255,), width=max(1, w // 80))
    return img

def parch_texture(w, h):
    img = Image.new('RGBA', (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            dx = (x - w / 2) / (w / 2); dy = (y - h / 2) / (h / 2)
            v = min(1.0, (dx * dx + dy * dy) * 0.55)
            c = mix(PARCH_L, PARCH_D, v)
            n = RND.randint(-5, 5)
            px[x, y] = (max(0, c[0] + n), max(0, c[1] + n), max(0, c[2] + n), 255)
    return img

def shadowed(layer_fn, size, offset, shadow=(20, 10, 4, 150), blur=0):
    """Dibuja layer_fn(draw, color_override) con sombra."""
    sh = Image.new('RGBA', size, (0, 0, 0, 0))
    layer_fn(ImageDraw.Draw(sh), shadow)
    if blur:
        sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    out.alpha_composite(sh, offset)
    top = Image.new('RGBA', size, (0, 0, 0, 0))
    layer_fn(ImageDraw.Draw(top), None)
    out.alpha_composite(top)
    return out

# ----------------------------------------------------------------- botones (256 -> 64)
S = 256

def button_base():
    img = wood_texture(S, S, plank=0)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=26, outline=INK + (255,), width=8)
    d.rounded_rectangle([10, 10, S - 11, S - 11], radius=20, outline=GOLD_D + (255,), width=6)
    d.rounded_rectangle([16, 16, S - 17, S - 17], radius=16, outline=GOLD + (255,), width=4)
    d.line([30, 20, S - 30, 20], fill=GOLD_L + (255,), width=3)  # brillo superior
    d.line([20, 30, 20, S - 30], fill=GOLD_L + (200,), width=2)
    for (x, y) in [(34, 34), (S - 35, 34), (34, S - 35), (S - 35, S - 35)]:
        d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=IRON_D + (255,), outline=INK + (255,), width=3)
        d.ellipse([x - 7, y - 8, x + 3, y + 2], fill=IRON + (255,))
    # sombra interior para dar profundidad
    inner = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(inner).rounded_rectangle([26, 26, S - 27, S - 27], radius=14, fill=(0, 0, 0, 55))
    img.alpha_composite(inner)
    return img

def P(pts, dx=0, dy=0):
    return [(x + dx, y + dy) for x, y in pts]

def col(c, ov):
    return ov if ov is not None else c + (255,)

def coin_shape(d, cx, cy, r, ov):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col(GOLD_D, ov))
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5], fill=col(GOLD, ov))
    if ov is None:
        d.ellipse([cx - r + 13, cy - r + 13, cx + r - 13, cy + r - 13], outline=GOLD_D + (255,), width=5)
        d.arc([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], 200, 270, fill=GOLD_L + (255,), width=6)
        d.polygon([(cx, cy - r * 0.38), (cx + r * 0.3, cy), (cx, cy + r * 0.38), (cx - r * 0.3, cy)],
                  fill=GOLD_D + (255,))

def ico_arrow(direction):
    def fn(d, ov):
        if direction == 'left':
            pts = [(54, 128), (120, 66), (120, 104), (200, 104), (200, 152), (120, 152), (120, 190)]
        else:
            pts = [(202, 128), (136, 66), (136, 104), (56, 104), (56, 152), (136, 152), (136, 190)]
        d.polygon(pts, fill=col(PARCH_L, ov))
        if ov is None:
            d.line(pts + [pts[0]], fill=INK + (255,), width=5)
    return fn

def ico_close(d, ov):
    for w, c in ((34, RED_D), (22, RED)):
        d.line([76, 76, 180, 180], fill=col(c, ov), width=w)
        d.line([180, 76, 76, 180], fill=col(c, ov), width=w)
    if ov is None:
        d.line([88, 84, 160, 156], fill=(240, 120, 110, 255), width=5)

def ico_clock(d, ov):
    d.ellipse([54, 54, 202, 202], fill=col(GOLD_D, ov))
    d.ellipse([66, 66, 190, 190], fill=col(PARCH_L, ov))
    if ov is None:
        for a in range(12):
            r1, r2 = (68, 82) if a % 3 else (62, 82)
            x1 = 128 + r1 * math.sin(a * math.pi / 6); y1 = 128 - r1 * math.cos(a * math.pi / 6)
            x2 = 128 + r2 * math.sin(a * math.pi / 6); y2 = 128 - r2 * math.cos(a * math.pi / 6)
            d.line([x1, y1, x2, y2], fill=INK + (255,), width=4)
        d.line([128, 128, 128, 84], fill=INK + (255,), width=8)
        d.line([128, 128, 164, 146], fill=RED_D + (255,), width=7)
        d.ellipse([120, 120, 136, 136], fill=GOLD_D + (255,))

def ico_refresh(d, ov):
    d.arc([60, 60, 196, 196], 40, 330, fill=col(PARCH_L, ov), width=26)
    d.polygon([(184, 48), (214, 118), (146, 108)], fill=col(PARCH_L, ov))

def ico_deposit(d, ov):
    coin_shape(d, 128, 92, 58, ov)
    d.polygon([(128, 232), (76, 170), (110, 170), (110, 146), (146, 146), (146, 170), (180, 170)], fill=col(GREEN, ov))
    if ov is None:
        d.line([(128, 232), (76, 170), (110, 170), (110, 146), (146, 146), (146, 170), (180, 170), (128, 232)],
               fill=GREEN_D + (255,), width=5)

def ico_withdraw(d, ov):
    coin_shape(d, 128, 164, 58, ov)
    pts = [(128, 24), (76, 86), (110, 86), (110, 110), (146, 110), (146, 86), (180, 86)]
    d.polygon(pts, fill=col(RED, ov))
    if ov is None:
        d.line(pts + [pts[0]], fill=RED_D + (255,), width=5)

def ico_coins(d, ov):
    coin_shape(d, 92, 168, 46, ov)
    coin_shape(d, 164, 168, 46, ov)
    coin_shape(d, 128, 96, 52, ov)

def ico_scroll(d, ov):
    d.rounded_rectangle([76, 56, 180, 204], radius=8, fill=col(PARCH, ov))
    d.rounded_rectangle([60, 44, 196, 72], radius=14, fill=col(PARCH_D, ov))
    d.rounded_rectangle([60, 186, 196, 214], radius=14, fill=col(PARCH_D, ov))
    if ov is None:
        for y in (92, 116, 140, 164):
            d.line([94, y, 162, y], fill=INK + (255,), width=5)
        d.ellipse([112, 168, 144, 200], fill=RED + (255,), outline=RED_D + (255,), width=4)

def ico_banner(d, ov):
    d.line([84, 44, 84, 216], fill=col(PARCH_D, ov), width=12)
    d.ellipse([74, 32, 96, 54], fill=col(GOLD, ov))
    pts = [(92, 56), (200, 66), (200, 168), (146, 148), (92, 168)]
    d.polygon(pts, fill=col(RED, ov))
    if ov is None:
        d.line(pts + [pts[0]], fill=RED_D + (255,), width=6)
        d.polygon([(146, 84), (166, 112), (146, 140), (126, 112)], fill=GOLD + (255,))

def ico_market(d, ov):
    d.polygon([(48, 112), (74, 56), (182, 56), (208, 112)], fill=col(RED, ov))
    if ov is None:
        for i, x in enumerate(range(58, 208, 38)):
            if i % 2 == 0:
                d.polygon([(x, 112), (x + 12, 56), (x + 38, 56), (x + 38, 112)], fill=PARCH_L + (255,))
        d.line([(48, 112), (74, 56), (182, 56), (208, 112), (48, 112)], fill=RED_D + (255,), width=5)
    d.rectangle([62, 112, 194, 206], fill=col(PARCH, ov))
    if ov is None:
        d.rectangle([110, 146, 146, 206], fill=WOOD_D + (255,), outline=INK + (255,), width=4)
        d.rectangle([74, 124, 100, 146], fill=GOLD + (255,), outline=GOLD_D + (255,), width=3)
        d.rectangle([156, 124, 182, 146], fill=GREEN + (255,), outline=GREEN_D + (255,), width=3)

def ico_bank(d, ov):
    d.polygon([(40, 98), (128, 40), (216, 98)], fill=col(GOLD, ov))
    for x in (66, 106, 146, 186):
        d.rectangle([x - 12, 106, x + 12, 186], fill=col(PARCH_L, ov))
        if ov is None:
            d.rectangle([x - 12, 106, x + 12, 186], outline=INK + (255,), width=3)
    d.rectangle([44, 190, 212, 214], fill=col(GOLD, ov))
    d.rectangle([34, 214, 222, 230], fill=col(GOLD_D, ov))
    if ov is None:
        d.line([(40, 98), (128, 40), (216, 98), (40, 98)], fill=GOLD_D + (255,), width=5)
        d.ellipse([116, 70, 140, 94], fill=RED + (255,), outline=RED_D + (255,), width=3)

BUTTONS = [
    ('btn_back', ico_arrow('left')), ('btn_next', ico_arrow('right')), ('btn_prev', ico_arrow('left')),
    ('btn_close', ico_close), ('btn_clock', ico_clock), ('btn_refresh', ico_refresh),
    ('btn_deposit', ico_deposit), ('btn_withdraw', ico_withdraw), ('btn_coins', ico_coins),
    ('btn_scroll', ico_scroll), ('btn_banner', ico_banner), ('btn_market', ico_market), ('btn_bank', ico_bank),
]
BASE = button_base()
overrides = []
sheet = Image.new('RGBA', (64 * 7, 64 * 2), (40, 40, 40, 255))
for i, (name, fn) in enumerate(BUTTONS):
    img = BASE.copy()
    img.alpha_composite(shadowed(fn, (S, S), (6, 8), blur=3))
    small = img.resize((64, 64), Image.LANCZOS)
    small.save(f'{PACK}/assets/shopkeepers/textures/item/{name}.png')
    sheet.alpha_composite(small, ((i % 7) * 64, (i // 7) * 64))
    json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': f'shopkeepers:item/{name}'}},
              open(f'{PACK}/assets/shopkeepers/models/item/{name}.json', 'w'))
    overrides.append({'predicate': {'custom_model_data': 1001 + i}, 'model': f'shopkeepers:item/{name}'})
json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'minecraft:item/paper'}, 'overrides': overrides},
          open(f'{PACK}/assets/minecraft/models/item/paper.json', 'w'), indent=1)
sheet.resize((64 * 7 * 2, 64 * 2 * 2), Image.NEAREST).save('/tmp/prev_buttons.png')

# ----------------------------------------------------------------- fondos de menus (512 px = 2x)
K = 2  # factor de escala; el glifo se dibuja a 256 de alto (height) -> nitido en GUI grande

def bg(name, accent, accent_d):
    W = 256 * K
    img = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    def r(x0, y0, x1, y1):
        return [x0 * K, y0 * K, x1 * K - 1, y1 * K - 1]
    # marco de madera
    img.alpha_composite(wood_texture(176 * K, 222 * K, plank=0), (0, 0))
    d.rectangle(r(0, 0, 176, 222), outline=INK + (255,), width=2 * K)
    d.rectangle(r(2, 2, 174, 220), outline=GOLD_D + (255,), width=K)
    d.rectangle(r(3, 3, 173, 219), outline=GOLD + (255,), width=K)
    # cinta del titulo
    d.rectangle(r(5, 5, 171, 16), fill=PARCH_L + (255,), outline=accent_d + (255,), width=K)
    d.rectangle(r(5, 14, 171, 16), fill=accent + (255,))
    # zona del cofre en pergamino
    img.alpha_composite(parch_texture(166 * K, 118 * K), (5 * K, 17 * K))
    d.rectangle(r(5, 17, 171, 135), outline=accent_d + (255,), width=K)
    # rejilla de rombos muy tenue
    lat = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lat)
    for o in range(-200, 400, 14):
        ld.line([o * K, 17 * K, (o + 118) * K, 135 * K], fill=(120, 90, 50, 28), width=1)
        ld.line([o * K, 135 * K, (o + 118) * K, 17 * K], fill=(120, 90, 50, 28), width=1)
    mask = Image.new('L', (W, W), 0)
    ImageDraw.Draw(mask).rectangle(r(6, 18, 170, 134), fill=255)
    img.alpha_composite(Image.composite(lat, Image.new('RGBA', (W, W), (0, 0, 0, 0)), mask))
    # slots del cofre (grabados)
    for rr in range(6):
        for c in range(9):
            x, y = 7 + 18 * c, 17 + 18 * rr
            d.rectangle(r(x, y, x + 18, y + 18), fill=(150, 122, 78, 255))
            d.rectangle(r(x + 1, y + 1, x + 17, y + 17), fill=(192, 166, 116, 255))
            d.line([x * K, y * K, (x + 18) * K, y * K], fill=(96, 72, 40, 255), width=K)
            d.line([x * K, y * K, x * K, (y + 18) * K], fill=(96, 72, 40, 255), width=K)
            d.line([x * K, (y + 18) * K - 1, (x + 18) * K, (y + 18) * K - 1], fill=(244, 228, 186, 255), width=K)
            d.line([(x + 18) * K - 1, y * K, (x + 18) * K - 1, (y + 18) * K], fill=(244, 228, 186, 255), width=K)
    # separador con rombo dorado
    d.rectangle(r(5, 135, 171, 139), fill=WOOD_DD + (255,))
    d.line([8 * K, 137 * K, 168 * K, 137 * K], fill=GOLD + (255,), width=K)
    cx, cy = 88 * K, 137 * K
    d.polygon([(cx, cy - 4 * K), (cx + 6 * K, cy), (cx, cy + 4 * K), (cx - 6 * K, cy)], fill=GOLD + (255,), outline=INK + (255,))
    # inventario del jugador
    img.alpha_composite(wood_texture(166 * K, 78 * K, base=WOOD_D, light=WOOD, dark=WOOD_DD), (5 * K, 139 * K))
    for rr in range(3):
        for c in range(9):
            x, y = 7 + 18 * c, 139 + 18 * rr
            d.rectangle(r(x, y, x + 18, y + 18), fill=(52, 34, 18, 255), outline=(28, 17, 9, 255), width=K)
            d.line([x * K + K, (y + 18) * K - 1, (x + 18) * K - K, (y + 18) * K - 1], fill=(120, 86, 48, 255), width=K)
    for c in range(9):
        x, y = 7 + 18 * c, 197
        d.rectangle(r(x, y, x + 18, y + 18), fill=(52, 34, 18, 255), outline=(28, 17, 9, 255), width=K)
        d.line([x * K + K, (y + 18) * K - 1, (x + 18) * K - K, (y + 18) * K - 1], fill=(120, 86, 48, 255), width=K)
    # esquinas ornamentales
    for (x, y) in [(4, 4), (172, 4), (4, 218), (172, 218)]:
        d.ellipse([(x - 3) * K, (y - 3) * K, (x + 3) * K, (y + 3) * K], fill=GOLD + (255,), outline=INK + (255,), width=1)
    img.save(f'{PACK}/assets/shopkeepers/textures/font/{name}.png')
    return img

bgs = [bg('bg_market', (176, 44, 44), RED_D), bg('bg_graph', (52, 98, 168), (28, 52, 96)),
       bg('bg_bank', GOLD, GOLD_D)]
pv = Image.new('RGBA', (3 * 360, 450), (60, 60, 60, 255))
for i, b in enumerate(bgs):
    pv.alpha_composite(b.crop((0, 0, 352, 444)).resize((352 * 1, 444 * 1)), (i * 360 + 4, 3))
pv.save('/tmp/prev_bgs.png')

# ----------------------------------------------------------------- ventana de comercio (recolor)
def gradient_map(img, stops, texture=True, lattice=False):
    img = img.convert('RGBA')
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0 or max(r, g, b) - min(r, g, b) > 14:
                continue
            l = (r + g + b) / 3.0
            for i in range(len(stops) - 1):
                l0, c0 = stops[i]; l1, c1 = stops[i + 1]
                if l <= l1:
                    t = (l - l0) / max(1.0, (l1 - l0))
                    c = mix(c0, c1, max(0.0, min(1.0, t)))
                    break
            else:
                c = stops[-1][1]
            if texture and 132 <= l <= 146:  # lista de trades: veta de madera
                n = int(7 * math.sin(y * 0.9 + (x // 24) * 1.7)) + RND.randint(-4, 4)
                c = (c[0] + n, c[1] + n, c[2] + n)
            if texture and 190 <= l <= 205:  # color base del panel
                n = RND.randint(-6, 6)
                c = (c[0] + n, c[1] + n, c[2] + n)
                if lattice and ((x + y) % 14 == 0 or (x - y) % 14 == 0):
                    c = (c[0] - 14, c[1] - 14, c[2] - 12)
            px[x, y] = (max(0, min(255, c[0])), max(0, min(255, c[1])), max(0, min(255, c[2])), a)
    return img

STOPS = [(0, (30, 18, 9)), (55, (74, 46, 24)), (90, (96, 64, 34)), (139, (132, 98, 60)),
         (198, (218, 196, 146)), (255, (252, 240, 204))]
vil = gradient_map(Image.open(f'{VAN}/villager.png'), STOPS, texture=True, lattice=True)
vd = ImageDraw.Draw(vil)
for (x, y) in [(272, 4), (3, 162), (272, 162)]:   # tachuelas doradas en el marco
    vd.ellipse([x - 2, y - 2, x + 1, y + 1], fill=GOLD + (255,), outline=INK + (255,))
vil.save(f'{PACK}/assets/minecraft/textures/gui/container/villager.png')

SPR = f'{PACK}/assets/minecraft/textures/gui/sprites/container/villager'
for n in ('scroller', 'scroller_disabled', 'experience_bar_background', 'trade_arrow', 'trade_arrow_out_of_stock'):
    im = gradient_map(Image.open(f'{VAN}/s_{n}.png'), STOPS, texture=False)
    if n == 'trade_arrow':
        px = im.load()
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                if px[x, y][3]:
                    px[x, y] = GOLD_D + (255,) if x % 2 else GOLD + (255,)
    if n == 'scroller':
        px = im.load()
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                if px[x, y][3]:
                    px[x, y] = mix(GOLD_D, GOLD_L, 0.2 + 0.8 * (1 - x / 6.0)) + (255,)
    im.save(f'{SPR}/{n}.png')
shutil.copy(f'{VAN}/s_experience_bar_current.png', f'{SPR}/experience_bar_current.png')
shutil.copy(f'{VAN}/s_experience_bar_result.png', f'{SPR}/experience_bar_result.png')
shutil.copy(f'{VAN}/s_out_of_stock.png', f'{SPR}/out_of_stock.png')
shutil.copy(f'{VAN}/s_discount_strikethrough.png', f'{SPR}/discount_strikethrough.png')
vp = Image.new('RGBA', (300, 180), (60, 60, 60, 255)); vp.alpha_composite(vil.crop((0, 0, 276, 166)), (2, 2))
vp.resize((900, 540), Image.NEAREST).save('/tmp/prev_villager.png')

# ----------------------------------------------------------------- font, pack.mcmeta, pack.png
spaces = {chr(0xF800 + n): -n for n in (1, 2, 4, 8, 16, 32, 64, 128)}
font = {'providers': [
    {'type': 'bitmap', 'file': 'shopkeepers:font/bg_market.png', 'ascent': 13, 'height': 256, 'chars': ['\uE000']},
    {'type': 'bitmap', 'file': 'shopkeepers:font/bg_graph.png', 'ascent': 13, 'height': 256, 'chars': ['\uE001']},
    {'type': 'bitmap', 'file': 'shopkeepers:font/bg_bank.png', 'ascent': 13, 'height': 256, 'chars': ['\uE002']},
    {'type': 'space', 'advances': spaces},
]}
json.dump(font, open(f'{PACK}/assets/minecraft/font/default.json', 'w'), indent=1)
json.dump({'pack': {'pack_format': 34, 'description': '\u00a76Shopkeepers Medieval \u00a77- madera, pergamino y oro (1.21.1)'}},
          open(f'{PACK}/pack.mcmeta', 'w'), indent=1)
icon = BASE.copy(); icon.alpha_composite(shadowed(ico_coins, (S, S), (6, 8), blur=3))
icon.resize((128, 128), Image.LANCZOS).save(f'{PACK}/pack.png')

zpath = os.path.join(OUT, 'ShopkeepersMedieval.zip')
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(PACK):
        for f in files:
            full = os.path.join(root, f)
            z.write(full, os.path.relpath(full, PACK))
print('ok', zpath, os.path.getsize(zpath) // 1024, 'KB')
