# -*- coding: utf-8 -*-
"""64x64 monster sprite generator -> monsters3.js (+ preview html)"""
import io, json, math, sys

PAL = {
    'k':'#1a1a2e','w':'#ffffff','r':'#e63946','R':'#9b1d2a','o':'#f4a261','y':'#ffd60a','g':'#52b788','G':'#2d6a4f',
    'b':'#4895ef','B':'#1d4ed8','p':'#b47aea','P':'#6d28d9','n':'#b08968','N':'#6b4423','s':'#ffd6a5','e':'#c9c9c9',
    'E':'#6b7280','c':'#7fdfff','m':'#ff8fab','t':'#e9c46a',
    'l':'#8ecbff','i':'#d6b4ff','j':'#8fe3b3','x':'#dcdcf5','q':'#3b1a6e','d':'#c26a2a','f':'#ff6b35','a':'#9a9aa8','u':'#4a4a5c',
    # 64x64 で追加
    'h':'#ffe9a8',  # pale yellow highlight
    'z':'#3d2412',  # very dark brown
    'D':'#1b4332',  # very dark green
    'U':'#2b2b3a',  # near-black steel
    'O':'#8a3a0f',  # burnt orange
    'Y':'#b8860b',  # dark gold
    'M':'#c2185b',  # dark pink
    'Q':'#250a45',  # darkest purple
    'S':'#e0a070',  # skin shade
    'T':'#fff4c2',  # bright gold highlight
    'X':'#b9b9d6',  # deeper lavender shade (ghost/white shadow)
    'L':'#2a6fd6',  # mid blue (iris shade)
    'F':'#ff3b3b',  # bright red (eyes/glow)
}
W = H = 64

class C:
    def __init__(self):
        self.g = [['.']*W for _ in range(H)]
    def px(self, x, y, ch):
        x = int(x); y = int(y)
        if 0 <= x < W and 0 <= y < H: self.g[y][x] = ch
    def get(self, x, y):
        x = int(x); y = int(y)
        return self.g[y][x] if 0 <= x < W and 0 <= y < H else '.'
    def rect(self, x, y, w, h, ch):
        for yy in range(int(y), int(y+h)):
            for xx in range(int(x), int(x+w)): self.px(xx, yy, ch)
    def ell(self, cx, cy, rx, ry, ch):
        for yy in range(max(0,int(cy-ry-1)), min(H,int(cy+ry+2))):
            for xx in range(max(0,int(cx-rx-1)), min(W,int(cx+rx+2))):
                dx = (xx+0.5-cx)/rx; dy = (yy+0.5-cy)/ry
                if dx*dx+dy*dy <= 1: self.px(xx, yy, ch)
    def sphere(self, cx, cy, rx, ry, base, sh, dk=None, hi=None, lx=-0.55, ly=-0.75, t1=0.15, t2=0.6, th=-0.78, only=None):
        """ellipse with lighting from upper-left. only: restrict to pixels currently == only"""
        for yy in range(max(0,int(cy-ry-1)), min(H,int(cy+ry+2))):
            for xx in range(max(0,int(cx-rx-1)), min(W,int(cx+rx+2))):
                nx = (xx+0.5-cx)/rx; ny = (yy+0.5-cy)/ry
                if nx*nx+ny*ny > 1: continue
                if only is not None and self.g[yy][xx] != only: continue
                t = -(nx*lx + ny*ly)   # 1 at light side
                col = base
                if hi and t > -th and nx*nx+ny*ny > 0.35: col = hi
                elif t < -t2 and dk: col = dk
                elif t < -t1: col = sh
                self.px(xx, yy, col)
    def line(self, x0, y0, x1, y1, ch, wd=1):
        n = int(max(abs(x1-x0), abs(y1-y0), 1))
        vert = abs(y1-y0) >= abs(x1-x0)
        for i in range(n+1):
            x = round(x0+(x1-x0)*i/n); y = round(y0+(y1-y0)*i/n)
            for k in range(-(wd//2), wd-(wd//2)):
                if vert: self.px(x+k, y, ch)
                else: self.px(x, y+k, ch)
    def path(self, pts, ch, wd=1):
        for i in range(len(pts)-1): self.line(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],ch,wd)
    def poly(self, pts, ch):
        ys = [p[1] for p in pts]
        for yy in range(max(0,int(min(ys))-1), min(H,int(max(ys))+2)):
            y = yy+0.5; xs = []
            n = len(pts)
            for i in range(n):
                (x0,y0),(x1,y1) = pts[i], pts[(i+1)%n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0+(y-y0)*(x1-x0)/(y1-y0))
            xs.sort()
            for i in range(0, len(xs)-1, 2):
                for xx in range(int(math.floor(xs[i])), int(math.ceil(xs[i+1]))+1):
                    if xs[i] <= xx+0.5 <= xs[i+1]: self.px(xx, yy, ch)
    def polyshade(self, pts, base, sh, frac=0.55, dk=None, dfrac=0.85):
        """fill poly, then shade the right part (x beyond frac of bbox width)"""
        xs = [p[0] for p in pts]; x0, x1 = min(xs), max(xs)
        tmp = C(); tmp.poly(pts, '1')
        for y in range(H):
            for x in range(W):
                if tmp.g[y][x] != '1': continue
                f = (x+0.5-x0)/max(1,(x1-x0))
                self.px(x, y, dk if (dk and f > dfrac) else (sh if f > frac else base))
    def recolor(self, src, dst, x0=0, y0=0, x1=W, y1=H):
        for y in range(y0, y1):
            for x in range(x0, x1):
                if self.g[y][x] == src: self.g[y][x] = dst
    def texture(self, fn, x0=0, y0=0, x1=W, y1=H, only=None):
        """fn(x,y) -> color or None, applied where pixel==only (or any non-empty)"""
        for y in range(y0, y1):
            for x in range(x0, x1):
                cur = self.g[y][x]
                if cur == '.': continue
                if only is not None and cur not in only: continue
                c = fn(x, y)
                if c: self.g[y][x] = c
    def scales(self, ch, x0=0, y0=0, x1=W, y1=H, only=None, step=5):
        def fn(x, y):
            off = (y // step % 2) * (step // 2)
            if y % step == step-1 and (x + off) % step in (0, 1, 2): return ch
            if y % step == step-2 and (x + off) % step in (0, 2): return ch
            return None
        self.texture(fn, x0, y0, x1, y1, only)
    def dots(self, ch, x0=0, y0=0, x1=W, y1=H, only=None, seed=7, every=11):
        def fn(x, y):
            h = (x*73856093 ^ y*19349663 ^ seed) % every
            return ch if h == 0 else None
        self.texture(fn, x0, y0, x1, y1, only)
    def outline(self, ch='k'):
        g = self.g; out = [r[:] for r in g]
        for y in range(H):
            for x in range(W):
                if g[y][x] != '.': continue
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    xx, yy = x+dx, y+dy
                    if 0 <= xx < W and 0 <= yy < H and g[yy][xx] not in ('.', ch):
                        out[y][x] = ch; break
        self.g = out
    def art(self): return [''.join(r) for r in self.g]

M = []
def add(id, name, lv, fn, flip=False, map=None):
    c = C(); fn(c); c.outline()
    d = {'id':id,'name':name,'lv':lv,'art':c.art()}
    if flip: d['flip'] = True
    if map: d['map'] = map
    M.append(d)

# ---------- 1 スライム ----------
def slime(c, base='b', sh='B', dk='q', hi='l'):
    c.polyshade([(29,5),(35,5),(52,32),(12,32)], base, sh, 0.62)         # tip (shaded right)
    c.sphere(32, 40, 25, 19, base, sh, dk, hi, t1=0.2, t2=0.8)           # body
    c.path([(29,8),(19,26)], hi, 2)                                       # tip edge gloss
    c.ell(20, 27, 4, 2.5, hi); c.rect(15, 30, 3, 2, hi)
    # eyes
    c.ell(22, 38, 6, 7, 'w'); c.ell(42, 38, 6, 7, 'w')
    c.ell(23, 39, 3.5, 4, 'k'); c.ell(43, 39, 3.5, 4, 'k')
    c.rect(21, 36, 2, 2, 'w'); c.rect(41, 36, 2, 2, 'w')
    # mouth
    c.path([(22,49),(25,53),(39,53),(42,49)], 'k', 2)
    c.rect(27, 54, 10, 1, dk)

add('slime','スライム',1, slime)

# ---------- 2 おおコウモリ ----------
def bat(c):
    # wings (membrane with bones)
    c.polyshade([(1,14),(23,27),(25,43),(14,45),(2,52),(4,40),(1,30)], 'P', 'q', 0.0)
    c.polyshade([(62,14),(40,27),(38,43),(49,45),(61,52),(59,40),(62,30)], 'P', 'q', 0.55)
    c.poly([(1,14),(23,27),(25,43),(14,45),(2,52),(4,40),(1,30)], 'P')
    c.poly([(62,14),(40,27),(38,43),(49,45),(61,52),(59,40),(62,30)], 'q')
    c.poly([(45,27),(62,16),(60,40),(50,44)], 'P')
    for pts in (((23,27),(1,14)),((23,27),(2,31)),((24,38),(3,51))): c.path(pts, 'q', 2)
    for pts in (((40,27),(62,14)),((40,27),(61,31)),((39,38),(60,51))): c.path(pts, 'Q', 2)
    c.path([(2,16),(22,28)], 'i', 1); c.path([(61,16),(42,28)], 'i', 1)
    # body + head
    c.sphere(32, 38, 9, 13, 'p', 'P', 'q', 'i')
    c.sphere(32, 24, 10, 9, 'p', 'P', 'q', 'i')
    c.poly([(23,20),(26,8),(30,22)], 'p'); c.poly([(41,20),(38,8),(34,22)], 'p')      # ears
    c.poly([(25,18),(26,11),(28,19)], 'm'); c.poly([(39,18),(38,11),(36,19)], 'm')
    # face
    c.ell(27, 24, 3, 3, 'w'); c.ell(37, 24, 3, 3, 'w'); c.px(28,24,'F'); c.px(27,24,'F'); c.px(37,24,'F'); c.px(36,24,'F')
    c.px(26,23,'w')
    c.rect(27, 29, 10, 2, 'k'); c.rect(28, 31, 2, 3, 'w'); c.rect(34, 31, 2, 3, 'w')   # mouth + fangs
    c.px(32, 27, 'q')
    # feet
    c.rect(26, 50, 4, 5, 'P'); c.rect(34, 50, 4, 5, 'P'); c.rect(25, 54, 2, 2, 'q'); c.rect(37, 54, 2, 2, 'q')
add('bat','おおコウモリ',1, bat)

# ---------- 3 おおガラス (右向きに描いて flip) ----------
def crow(c):
    c.sphere(28, 40, 21, 13, 'u', 'U', None, 'E')                 # body
    c.sphere(43, 20, 12, 10, 'u', 'U', None, 'E')                 # head
    c.poly([(36,26),(50,24),(46,34)], 'u')                        # neck join
    c.poly([(53,17),(63,21),(53,26)], 'y'); c.poly([(53,21),(63,21),(53,26)], 'd')   # beak
    c.px(54,20,'h'); c.px(55,20,'h')
    c.ell(45, 18, 3, 3, 'w'); c.ell(46, 18, 1.5, 1.5, 'F'); c.px(44,17,'w')         # eye
    c.polyshade([(4,30),(32,28),(30,48),(10,52),(2,46)], 'u', 'U', 0.6)              # wing
    for yy in (33, 38, 43): c.path([(5,yy),(28,yy-2)], 'E', 1)
    c.path([(8,48),(26,44)], 'E', 1)
    c.poly([(2,32),(8,20),(16,34)], 'u'); c.path([(4,30),(9,22)], 'E')                # tail
    c.path([(22,52),(20,60)], 'y', 3); c.path([(36,52),(38,60)], 'y', 3)             # legs
    c.rect(14, 59, 10, 2, 'y'); c.rect(32, 59, 10, 2, 'y'); c.px(13,60,'d'); c.px(42,60,'d')
    c.dots('E', 10, 30, 48, 50, only='u', seed=3, every=13)                           # feather speckle
add('crow','おおガラス',2, crow, flip=True)

# ---------- 4 ゴースト ----------
def ghost(c):
    c.rect(10, 26, 44, 24, 'w')
    c.sphere(32, 26, 22, 22, 'w', 'x', 'X', None, t1=0.35, t2=0.8)
    c.rect(10, 26, 20, 24, 'w'); c.polyshade([(30,26),(54,26),(54,50),(30,50)], 'w', 'x', 0.25, 'X', 0.8)
    for x in range(10, 54, 9): c.poly([(x,50),(x+9,50),(x+4.5,58)], 'w' if x < 36 else 'x')   # wavy hem
    c.poly([(46,50),(54,50),(50,58)], 'X')
    c.ell(22, 14, 6, 4, 'w'); c.ell(20, 13, 3, 2, 'w')
    # eyes
    c.ell(23, 26, 6, 7, 'b'); c.ell(41, 26, 6, 7, 'b')
    c.ell(24, 27, 4, 5, 'B'); c.ell(42, 27, 4, 5, 'B'); c.ell(24.5, 28, 2, 2.5, 'k'); c.ell(42.5, 28, 2, 2.5, 'k')
    c.rect(20, 22, 3, 3, 'w'); c.rect(38, 22, 3, 3, 'w')
    # mouth
    c.ell(32, 40, 5, 4, 'k'); c.ell(32, 42, 3, 1.5, 'M')
    # hands
    c.ell(7, 34, 5, 4, 'w'); c.ell(57, 34, 5, 4, 'x')
    c.px(26, 33, 'm'); c.px(27, 33, 'm'); c.px(37, 33, 'm'); c.px(38, 33, 'm')
add('ghost','ゴースト',2, ghost)

# ---------- 5 まどうし ----------
def mage(c):
    c.polyshade([(29,2),(35,2),(50,30),(14,30)], 'P', 'q', 0.55)                     # hat cone
    c.path([(31,4),(22,26)], 'p', 2)
    c.px(38,14,'y'); c.px(40,22,'y'); c.px(27,20,'y'); c.rect(36,13,1,1,'h')
    c.ell(32, 31, 27, 4, 'P'); c.ell(32, 32, 27, 3, 'q'); c.rect(6, 30, 52, 2, 'P')  # brim
    c.rect(18, 27, 28, 3, 't'); c.rect(18, 29, 28, 1, 'Y')                             # band
    c.sphere(32, 40, 11, 9, 's', 'S', None, None, t1=0.3)                              # face
    c.rect(21, 33, 22, 2, 'q')
    c.ell(27, 40, 2.5, 3, 'k'); c.ell(37, 40, 2.5, 3, 'k'); c.px(26,39,'w'); c.px(36,39,'w')
    c.rect(30, 45, 4, 1, 'R'); c.px(29,44,'S'); c.px(34,44,'S')
    c.polyshade([(20,48),(44,48),(54,62),(10,62)], 'P', 'q', 0.6)                     # robe
    c.rect(30, 50, 4, 12, 't'); c.rect(32, 50, 2, 12, 'Y')
    c.path([(24,52),(20,61)], 'q'); c.path([(40,52),(44,61)], 'Q')
    c.rect(19, 48, 26, 2, 'i')
    c.rect(49, 16, 4, 46, 'N'); c.rect(49, 16, 2, 46, 'n'); c.rect(48, 24, 6, 2, 't')  # staff
    c.sphere(51, 12, 7, 7, 'y', 't', 'Y', 'h'); c.rect(48, 9, 2, 2, 'w')              # orb
    c.ell(47, 47, 4, 3, 's'); c.ell(48, 47, 2, 2, 'S')                                 # hand
    c.px(46, 46, 's')
add('mage','まどうし',3, mage)

# ---------- 6 がいこつ ----------
def skeleton(c):
    c.sphere(32, 14, 13, 12, 'w', 'x', 'X', None, t1=0.4, t2=0.85)                    # skull
    c.rect(22, 22, 20, 7, 'w'); c.rect(36, 22, 6, 7, 'x')
    c.ell(26, 13, 4.5, 5, 'k'); c.ell(38, 13, 4.5, 5, 'k'); c.ell(27, 14, 2, 2, 'F'); c.ell(39, 14, 2, 2, 'F')
    c.poly([(31,18),(33,18),(32,22)], 'k')                                             # nose
    for x in range(24, 41, 3): c.rect(x, 25, 1, 4, 'k')                                # teeth
    c.rect(22, 25, 20, 1, 'X')
    c.rect(30, 30, 4, 20, 'e'); c.rect(32, 30, 2, 20, 'a')                             # spine
    for i, (yy, hw) in enumerate(((33,13),(38,12),(43,10))):                            # ribs
        c.ell(32, yy, hw, 3.5, 'w'); c.ell(32, yy+1, hw-2, 2, '.'); c.rect(31, yy-2, 2, 1, 'e')
    c.rect(30, 30, 4, 20, 'e'); c.rect(32, 30, 2, 20, 'a')
    c.ell(32, 50, 9, 4, 'w'); c.ell(32, 51, 5, 2, 'x')                                 # pelvis
    c.rect(14, 32, 10, 4, 'w'); c.rect(12, 34, 5, 14, 'w'); c.rect(42, 32, 10, 4, 'w'); c.rect(49, 34, 5, 14, 'x')   # arms
    c.ell(12, 33, 3, 3, 'w'); c.ell(53, 33, 3, 3, 'w'); c.rect(11, 47, 7, 4, 'w'); c.rect(47, 47, 7, 4, 'x')         # joints/hands
    c.rect(24, 52, 5, 10, 'w'); c.rect(35, 52, 5, 10, 'x'); c.ell(26,52,3,2,'w'); c.ell(37,52,3,2,'w')                # legs
    c.rect(20, 60, 10, 3, 'e'); c.rect(34, 60, 10, 3, 'a')
    c.rect(55, 14, 5, 34, 'E'); c.rect(55, 14, 2, 34, 'e'); c.ell(57, 12, 5, 4, 'e'); c.ell(57, 48, 4, 3, 'e')      # bone club
add('skeleton','がいこつ',3, skeleton)

# ---------- 7 おおサソリ (左向き) ----------
def scorpion(c):
    # tail (right, curling up over the back)
    tail = [(46,40),(53,34),(58,26),(58,16),(53,9),(46,8)]
    for i,(x,y) in enumerate(tail):
        r = 5.5 - i*0.4
        c.sphere(x, y, r, r, 'o', 'd', 'O', 'h')
    c.poly([(48,3),(32,8),(48,13)], 'R'); c.poly([(46,5),(36,8),(46,11)], 'r'); c.px(33,8,'k')      # stinger
    # body segments
    for i, x in enumerate((44, 36, 28, 20)):
        c.sphere(x, 40, 8, 8-i*0.5, 'o', 'd', 'O', 'h')
    c.sphere(13, 38, 9, 8, 'o', 'd', 'O', 'h')                                        # head
    for x in (24, 32, 40): c.rect(x, 33, 1, 14, 'O')                                  # segment lines
    # claws (left)
    c.sphere(10, 24, 7, 5, 'o', 'd', 'O', 'h'); c.poly([(1,20),(9,18),(9,30),(1,28),(4,24)], 'o')
    c.poly([(1,20),(9,18),(9,24),(4,24)], 'd'); c.px(2,24,'k'); c.px(3,24,'k')
    c.sphere(10, 50, 7, 5, 'o', 'd', 'O', 'h'); c.poly([(1,46),(9,44),(9,56),(1,54),(4,50)], 'o')
    c.poly([(1,50),(4,50),(9,56),(1,54)], 'd')
    c.path([(12,26),(14,36)], 'd', 3); c.path([(12,48),(14,44)], 'd', 3)
    # legs
    for x in (20, 28, 36, 44):
        c.path([(x,46),(x-3,54),(x-6,58)], 'd', 2); c.path([(x,46),(x-3,54)], 'o', 1)
    # eyes
    c.ell(8, 36, 2.5, 2.5, 'k'); c.px(7, 35, 'w'); c.ell(9, 42, 1.5, 1.5, 'k')
    c.scales('d', 16, 32, 52, 48, only='o', step=6)
add('scorpion','おおサソリ',4, scorpion)

# ---------- 8 どくどくスライム ----------
def pslime(c):
    slime(c, base='g', sh='G', dk='D', hi='j')
    for (x,y,r) in ((16,42,3),(44,26,2.5),(48,46,3),(26,52,2),(36,18,1.5)): c.ell(x,y,r,r,'G'); c.px(x-1,y-1,'D')
    for (x,y) in ((28,58),(12,52),(48,57)): c.path([(x,y),(x,y+4)], 'P', 2); c.px(x,y+5,'p')
    c.ell(40, 46, 2, 2, 'j'); c.px(39,45,'w')
add('pslime','どくどくスライム',4, pslime)

# ---------- 9 メタルスライム ----------
def mslime(c):
    slime(c, base='e', sh='a', dk='u', hi='w')
    c.path([(18,26),(13,38)], 'w', 2); c.path([(17,30),(14,42)], 'x', 1)              # gloss streaks
    c.path([(46,52),(54,44)], 'u', 2); c.path([(50,54),(56,46)], 'U', 1)
    c.rect(24, 18, 2, 6, 'w'); c.px(36, 10, 'w'); c.px(37, 11, 'w')
    c.ell(36, 32, 6, 2, 'x')
add('mslime','メタルスライム',5, mslime)

# ---------- 10 ミミック ----------
def mimic(c):
    c.rect(6, 4, 52, 18, 'n'); c.rect(6, 4, 52, 3, 'N'); c.rect(6, 19, 52, 3, 'N'); c.rect(52, 6, 6, 14, 'N')   # lid
    for yy in (9, 13, 16): c.path([(10,yy),(50,yy)], 'N', 1)
    c.rect(6, 4, 52, 2, 't'); c.rect(6, 20, 52, 2, 't'); c.rect(28, 4, 8, 18, 't'); c.rect(32, 4, 4, 18, 'Y')
    c.rect(6, 4, 4, 18, 't'); c.rect(54, 4, 4, 18, 'Y')
    c.ell(18, 13, 5, 4, 'y'); c.ell(46, 13, 5, 4, 'y'); c.ell(19, 13, 2.5, 2.5, 'k'); c.ell(47, 13, 2.5, 2.5, 'k'); c.px(17,12,'w'); c.px(45,12,'w')
    c.rect(4, 26, 56, 36, 'n'); c.rect(4, 26, 56, 2, 'N'); c.rect(4, 60, 56, 2, 'N'); c.rect(54, 26, 6, 36, 'N')   # box
    c.rect(4, 26, 4, 36, 't'); c.rect(56, 26, 4, 36, 'Y'); c.rect(4, 58, 56, 4, 't'); c.rect(28, 54, 8, 8, 't'); c.rect(32, 54, 4, 8, 'Y')
    c.rect(8, 22, 48, 32, 'R'); c.rect(8, 22, 48, 6, 'k')                                                         # mouth cavity
    for x in range(8, 56, 8): c.poly([(x,22),(x+8,22),(x+4,34)], 'w')                                              # upper teeth
    for x in range(12, 56, 8): c.poly([(x,54),(x+8,54),(x+4,44)], 'x')                                             # lower teeth
    c.ell(32, 46, 10, 5, 'M'); c.ell(31, 45, 8, 3.5, 'm')                                                           # tongue
    c.rect(30, 24, 4, 1, 'u')
    c.rect(2, 60, 6, 3, 'Y'); c.rect(56, 60, 6, 3, 'Y')                                                             # feet/corners
add('mimic','ミミック',5, mimic)

# ---------- 11 ゴーレム ----------
def golem(c):
    c.rect(18, 4, 28, 20, 'n'); c.rect(40, 6, 6, 18, 'N'); c.rect(18, 4, 28, 2, 's')                              # head
    c.rect(22, 9, 8, 7, 'y'); c.rect(34, 9, 8, 7, 'y'); c.rect(24, 11, 4, 3, 'f'); c.rect(36, 11, 4, 3, 'f')      # glowing eyes
    c.rect(26, 19, 12, 2, 'z')
    c.rect(4, 26, 56, 22, 'n'); c.rect(4, 26, 56, 2, 's'); c.rect(48, 28, 12, 20, 'N')                             # torso
    c.rect(1, 28, 12, 30, 'n'); c.rect(51, 28, 12, 30, 'n'); c.rect(9, 30, 4, 28, 'N'); c.rect(58, 30, 5, 28, 'N')  # arms
    c.rect(1, 54, 12, 6, 'N'); c.rect(51, 54, 12, 6, 'z'); c.rect(2, 56, 3, 3, 'n')
    c.rect(14, 48, 16, 14, 'n'); c.rect(34, 48, 16, 14, 'n'); c.rect(24, 50, 6, 12, 'N'); c.rect(44, 50, 6, 12, 'N')  # legs
    c.rect(14, 60, 16, 2, 'z'); c.rect(34, 60, 16, 2, 'z')
    for (x0,y0,x1,y1) in ((8,34,16,40),(26,30,30,38),(38,40,46,44),(22,8,24,14),(30,56,34,60),(54,36,58,44)):   # cracks
        c.path([(x0,y0),(x1,y1)], 'z', 1)
    for yy in (33, 40): c.path([(16,yy),(46,yy)], 'N', 1)                                                           # block lines
    for xx in (22, 36): c.path([(xx,28),(xx,33)], 'N'); c.path([(xx+6,33),(xx+6,40)], 'N')
    for (x,y) in ((6,30),(20,44),(44,32),(16,52)): c.ell(x, y, 2, 1.5, 'g'); c.px(x+2, y, 'G')                   # moss
add('golem','ゴーレム',6, golem)

# ---------- 12 リザードマン (右向きに描いて flip) ----------
def lizard(c):
    c.polyshade([(26,38),(10,52),(2,60),(6,54),(16,50),(26,46)], 'G', 'D', 0.2)                                    # tail
    c.sphere(30, 40, 11, 14, 'g', 'G', 'D', 'j')                                                                    # torso
    c.rect(26, 30, 6, 24, 'j'); c.rect(29, 30, 2, 24, 'g')                                                            # belly stripe
    for yy in range(33, 52, 4): c.rect(26, yy, 6, 1, 'G')
    c.sphere(30, 16, 12, 10, 'g', 'G', 'D', 'j')                                                                    # head
    c.poly([(38,12),(54,16),(38,24)], 'g'); c.poly([(38,18),(54,16),(38,24)], 'G')                                   # snout
    c.rect(43, 17, 2, 3, 'w'); c.rect(48, 16, 2, 2, 'w')                                                             # teeth
    c.ell(33, 13, 3, 3, 'y'); c.ell(34, 13, 1.5, 2, 'k'); c.px(32,12,'w')                                             # eye
    for x, h in ((22,6),(27,8),(32,6)): c.poly([(x,8),(x+4,8),(x+2,8-h)], 'G')                                        # crest
    c.rect(38, 30, 8, 6, 'g'); c.rect(44, 24, 6, 10, 'g'); c.ell(47, 24, 4, 3, 'G')                                   # sword arm
    c.rect(51, 2, 5, 34, 'e'); c.rect(51, 2, 2, 34, 'w'); c.poly([(51,2),(56,2),(53.5,0)], 'e')                       # sword
    c.rect(46, 36, 15, 3, 't'); c.rect(52, 39, 3, 6, 'N'); c.rect(51, 45, 5, 2, 'Y')
    c.rect(16, 34, 10, 5, 'g'); c.ell(16, 36, 4, 3, 'G')                                                             # other arm
    c.rect(20, 52, 8, 10, 'G'); c.rect(32, 52, 8, 10, 'G'); c.rect(18, 60, 11, 3, 'D'); c.rect(30, 60, 11, 3, 'D')   # legs
    c.px(17, 61, 'w'); c.px(41, 61, 'w')
    c.scales('G', 20, 28, 42, 52, only='g', step=5)
add('lizard','リザードマン',6, lizard, flip=True)

# ---------- 13 キメラ ----------
def chimera(c):
    c.polyshade([(1,4),(24,22),(24,40),(2,32),(4,20)], 'b', 'B', 0.0); c.poly([(1,4),(24,22),(24,40),(2,32),(4,20)], 'b')
    c.polyshade([(62,4),(40,22),(40,40),(61,32),(59,20)], 'b', 'B', 0.5)
    for pts in (((23,22),(2,6)),((23,28),(2,20)),((23,36),(3,31))): c.path(pts, 'B', 2); c.path(pts, 'l', 1)
    for pts in (((41,22),(61,6)),((41,28),(61,20)),((41,36),(60,31))): c.path(pts, 'L', 2)
    c.sphere(33, 42, 17, 12, 'y', 't', 'Y', 'h')                                                                    # body
    c.sphere(24, 22, 11, 10, 'y', 't', 'Y', 'h')                                                                    # head
    c.ell(24, 14, 13, 5, 'd'); c.ell(24, 14, 13, 5, 'd'); c.ell(26, 13, 9, 3, 'O'); c.ell(22, 12, 6, 2, 'f')         # mane
    for x in range(12, 38, 4): c.poly([(x,16),(x+4,16),(x+2,10)], 'd')
    c.poly([(16,22),(4,25),(16,29)], 'o'); c.poly([(16,25),(4,25),(16,29)], 'd')                                     # beak
    c.ell(21, 20, 3, 3, 'k'); c.px(20,19,'w'); c.ell(28, 20, 2, 2, 'k'); c.px(27,19,'w')
    c.rect(20, 50, 7, 10, 'y'); c.rect(40, 50, 7, 10, 't'); c.rect(18, 58, 10, 4, 'd'); c.rect(38, 58, 10, 4, 'O')   # legs
    for x in (19, 22, 25, 39, 42, 45): c.px(x, 62, 'w')
    c.path([(48,44),(56,52),(60,46),(58,40)], 'g', 4); c.sphere(58, 38, 4, 3, 'g', 'G', None, 'j')                  # snake tail
    c.px(61, 37, 'r'); c.px(62, 36, 'r'); c.px(57, 37, 'k')
    c.dots('t', 20, 34, 48, 54, only='y', seed=5, every=9)
add('chimera','キメラ',7, chimera)

# ---------- 14 おおめだま ----------
def eye(c):
    c.sphere(32, 28, 25, 23, 'w', 'x', 'X', None, t1=0.3, t2=0.8)                                                  # eyeball
    c.ell(32, 12, 26, 9, 'P'); c.ell(32, 10, 24, 7, 'p'); c.ell(32, 9, 20, 4, 'P')                                   # upper lid
    c.ell(32, 16, 25, 5, 'w'); c.ell(32, 18, 23, 6, 'w')
    c.sphere(29, 30, 12, 12, 'b', 'L', 'B', 'l')                                                                    # iris
    c.ell(29, 30, 6, 6, 'k'); c.ell(26, 26, 2.5, 2.5, 'w'); c.px(33, 34, 'w')                                        # pupil + glint
    for pts in (((8,30),(16,34)),((10,40),(18,38)),((50,24),(57,20)),((48,40),(56,42)),((20,46),(24,42))): c.path(pts, 'r', 1)   # veins
    c.ell(32, 48, 20, 5, 'P')                                                                                        # base
    for i, (x, dx) in enumerate(((12,-6),(20,-3),(28,0),(36,1),(44,4),(52,7))):                                      # tentacles
        c.path([(x,50),(x+dx//2,56),(x+dx,62)], 'P', 4); c.path([(x,50),(x+dx//2,56),(x+dx,62)], 'p', 1)
        c.px(x+dx//2+1, 55, 'i'); c.px(x+dx, 60, 'i')
add('eye','おおめだま',7, eye)

# ---------- 15 よろいのきし (右向きに描いて flip) ----------
def knight(c):
    c.rect(30, 0, 5, 8, 'r'); c.rect(28, 2, 3, 5, 'R'); c.rect(35, 2, 3, 5, 'R')                                    # plume
    c.rect(20, 8, 26, 18, 'E'); c.rect(20, 8, 26, 2, 'a'); c.rect(40, 10, 6, 16, 'u'); c.rect(22, 10, 2, 14, 'a')   # helm
    c.poly([(20,8),(46,8),(44,4),(22,4)], 'a')
    c.rect(22, 14, 22, 5, 'k'); c.rect(26, 15, 4, 3, 'F'); c.rect(36, 15, 4, 3, 'F'); c.px(26,15,'w'); c.px(36,15,'w')   # visor
    for yy in (21, 24): c.path([(24,yy),(42,yy)], 'u', 1)
    c.rect(14, 28, 36, 22, 'E'); c.rect(42, 30, 8, 20, 'u'); c.rect(14, 28, 36, 2, 'a'); c.rect(16, 30, 2, 18, 'a')   # torso
    c.ell(14, 30, 8, 5, 'a'); c.ell(50, 30, 8, 5, 'E'); c.ell(12, 29, 4, 2, 'e')                                    # pauldrons
    c.rect(28, 30, 8, 16, 'r'); c.rect(24, 34, 16, 6, 'r'); c.rect(32, 30, 4, 16, 'R'); c.rect(32, 34, 8, 6, 'R')     # cross tabard
    c.rect(8, 32, 8, 16, 'E'); c.rect(48, 32, 8, 16, 'u')                                                            # arms
    c.rect(2, 30, 12, 22, 'u'); c.rect(3, 31, 10, 20, 'E'); c.rect(4, 32, 4, 18, 'a'); c.rect(6, 38, 4, 6, 'r')     # shield
    c.px(3,31,'w'); c.px(12,31,'w'); c.px(3,50,'w'); c.px(12,50,'w')
    c.rect(16, 50, 12, 12, 'E'); c.rect(34, 50, 12, 12, 'E'); c.rect(24, 52, 4, 10, 'u'); c.rect(42, 52, 4, 10, 'u')   # legs
    c.rect(14, 60, 15, 3, 'u'); c.rect(33, 60, 15, 3, 'U')
    c.rect(56, 0, 6, 40, 'e'); c.rect(56, 0, 2, 40, 'w'); c.poly([(56,0),(62,0),(59,-2)], 'e')                        # sword
    c.rect(50, 40, 14, 3, 't'); c.rect(57, 43, 4, 8, 'N'); c.rect(56, 51, 6, 2, 'Y')
    c.rect(52, 36, 6, 6, 'E')                                                                                        # gauntlet
    for (x,y) in ((18,32),(18,46),(40,32),(40,46)): c.px(x, y, 'w')                                                   # rivets
add('knight','よろいのきし',8, knight, flip=True)

# ---------- 16 ようじゅつし ----------
def wizard(c):
    c.polyshade([(32,2),(12,32),(52,32)], 'R', 'r', 0.0); c.poly([(32,2),(12,32),(52,32)], 'R')                      # hood
    c.poly([(32,2),(32,32),(52,32)], 'q'); c.poly([(31,3),(31,32),(42,32)], 'R')
    c.poly([(32,8),(20,30),(44,30)], 'k')                                                                            # face shadow
    c.ell(27, 22, 3, 3, 'w'); c.ell(37, 22, 3, 3, 'w'); c.ell(27.5, 22.5, 1.5, 1.5, 'F'); c.ell(37.5, 22.5, 1.5, 1.5, 'F')
    c.polyshade([(16,32),(48,32),(56,62),(8,62)], 'R', 'q', 0.6)                                                     # robe
    c.rect(29, 34, 6, 28, 't'); c.rect(32, 34, 3, 28, 'Y'); c.rect(20, 36, 24, 2, 't'); c.rect(20, 37, 24, 1, 'Y')
    for pts in (((22,40),(16,60)),((42,40),(48,60))): c.path(pts, 'q', 1)
    c.rect(4, 20, 5, 42, 'N'); c.rect(4, 20, 2, 42, 'n'); c.rect(3, 30, 7, 2, 't')                                   # staff
    c.sphere(6, 15, 6, 6, 'P', 'q', None, 'i'); c.px(4, 13, 'w'); c.px(5, 13, 'w')                                   # orb
    c.ell(12, 44, 5, 3, 's'); c.ell(13, 45, 3, 2, 'S'); c.ell(50, 46, 5, 3, 's'); c.ell(51, 47, 3, 2, 'S')           # hands
    c.rect(14, 36, 6, 8, 'q'); c.rect(44, 36, 6, 8, 'Q')                                                             # sleeves
    c.ell(32, 46, 4, 4, 'x'); c.ell(31, 45, 1, 1.5, 'k'); c.ell(34, 45, 1, 1.5, 'k')                                  # skull buckle
add('wizard','ようじゅつし',8, wizard)

# ---------- 17 トロル (右向きに描いて flip) ----------
def troll(c):
    c.rect(50, 4, 9, 40, 'N'); c.rect(50, 4, 3, 40, 'n'); c.ell(54, 6, 7, 5, 'N'); c.ell(52, 5, 3, 2, 'n')           # club
    for (x,y) in ((48,10),(60,14),(49,20),(61,24),(50,30)): c.rect(x, y, 2, 2, 'e')
    c.sphere(26, 16, 14, 13, 'p', 'P', 'q', 'i')                                                                    # head
    c.poly([(14,10),(10,2),(18,8)], 'i'); c.poly([(38,10),(42,2),(34,8)], 'i'); c.px(11,3,'w'); c.px(41,3,'w')       # horns
    c.ell(20, 14, 3, 3, 'k'); c.ell(32, 14, 3, 3, 'k'); c.px(19,13,'w'); c.px(31,13,'w')                             # eyes
    c.ell(26, 20, 2, 1.5, 'q')
    c.rect(17, 23, 18, 4, 'q'); c.rect(18, 23, 3, 4, 'w'); c.rect(31, 23, 3, 4, 'w'); c.rect(24, 24, 2, 3, 'w')      # mouth + fangs
    c.rect(8, 30, 40, 22, 'p'); c.rect(36, 32, 12, 20, 'P'); c.rect(8, 30, 40, 2, 'i'); c.rect(10, 32, 4, 18, 'i')  # torso
    c.rect(2, 32, 8, 20, 'p'); c.rect(46, 30, 8, 16, 'p'); c.ell(50, 30, 4, 3, 'P')                                  # arms
    c.rect(2, 50, 8, 5, 'P'); c.rect(48, 44, 7, 5, 'P')
    c.rect(12, 40, 32, 10, 'n'); c.rect(12, 40, 32, 2, 'N'); c.rect(18, 42, 4, 4, 'N'); c.rect(30, 44, 4, 4, 'N'); c.rect(40, 42, 4, 6, 'N')   # loincloth
    c.rect(10, 50, 14, 12, 'P'); c.rect(30, 50, 14, 12, 'P'); c.rect(18, 52, 6, 10, 'q'); c.rect(38, 52, 6, 10, 'q')   # legs
    c.rect(8, 60, 17, 3, 'q'); c.rect(28, 60, 17, 3, 'Q')
    for (x,y) in ((14,34),(30,36),(22,38),(40,34)): c.px(x, y, 'P'); c.px(x+1, y, 'P')                                # warts
add('troll','トロル',9, troll, flip=True)

# ---------- 18 ドラゴン (右向きに描いて flip) ----------
def dragon(c):
    c.polyshade([(4,2),(26,24),(18,36),(2,36),(0,20)], 'R', 'r', 0.0); c.poly([(4,2),(26,24),(18,36),(2,36),(0,20)], 'R')   # wing
    c.poly([(4,2),(26,24),(14,24)], 'r')
    for pts in (((25,24),(4,3)),((24,27),(1,20)),((22,32),(3,35))): c.path(pts, 'R', 2); c.path(pts, 'f', 1)
    c.sphere(30, 42, 21, 12, 'g', 'G', 'D', 'j')                                                                    # body
    c.ell(32, 47, 16, 6, 'j'); c.ell(33, 48, 14, 4, 'j')
    for yy in range(44, 54, 3): c.rect(18, yy, 28, 1, 'G')
    c.polyshade([(12,40),(2,52),(1,60),(6,56),(14,50),(18,46)], 'g', 'G', 0.0); c.poly([(12,40),(2,52),(1,60),(6,56),(14,50),(18,46)], 'g')   # tail
    c.px(2, 58, 'G'); c.px(3, 57, 'G')
    c.poly([(40,20),(52,18),(50,36),(38,36)], 'g'); c.poly([(46,20),(52,18),(50,36),(46,36)], 'G')                    # neck
    c.sphere(50, 16, 11, 9, 'g', 'G', 'D', 'j')                                                                     # head
    c.poly([(54,12),(63,16),(54,24)], 'g'); c.poly([(54,18),(63,16),(54,24)], 'G')                                    # snout
    c.rect(57, 18, 2, 3, 'w'); c.rect(60, 17, 2, 2, 'w'); c.rect(55, 20, 1, 2, 'w')                                  # fangs
    c.ell(48, 13, 3, 3, 'y'); c.ell(49, 13, 1.5, 2.5, 'k'); c.px(47, 12, 'w')                                        # eye
    c.poly([(42,8),(44,2),(47,9)], 'G'); c.poly([(50,8),(54,2),(55,9)], 'G')                                          # horns
    for x in range(14, 44, 5): c.poly([(x,32),(x+5,32),(x+2.5,26)], 'G')                                              # back spikes
    c.rect(18, 52, 8, 9, 'g'); c.rect(36, 52, 8, 9, 'G'); c.rect(16, 59, 11, 3, 'G'); c.rect(34, 59, 11, 3, 'D')     # legs
    for x in (15, 18, 21, 33, 36, 39): c.px(x, 62, 'w')
    c.scales('G', 12, 32, 50, 46, only='g', step=5)
add('dragon','ドラゴン',9, dragon, flip=True)
add('ddragon','あんこくドラゴン',10, dragon, flip=True, map={'g':'P','j':'p','G':'q','D':'Q','R':'E','r':'a','f':'e','y':'F'})

# ---------- 20 まおう ----------
def maou(c):
    c.polyshade([(2,2),(10,0),(22,14),(14,20)], 't', 'Y', 0.6); c.polyshade([(62,2),(54,0),(42,14),(50,20)], 't', 'Y', 0.6)   # horns
    c.path([(6,3),(18,15)], 'T', 1); c.path([(58,3),(46,15)], 'T', 1)
    c.poly([(4,30),(60,30),(63,63),(1,63)], 'R'); c.poly([(40,30),(60,30),(63,63),(44,63)], 'r')                      # cape
    for pts in (((14,34),(10,62)),((28,34),(26,62)),((50,34),(54,62))): c.path(pts, 'M', 1)
    c.rect(4, 30, 56, 2, 'r')
    c.sphere(32, 17, 13, 12, 'P', 'q', 'Q', 'i')                                                                    # head
    c.rect(22, 12, 8, 4, 'F'); c.rect(34, 12, 8, 4, 'F'); c.rect(24, 13, 3, 2, 'y'); c.rect(36, 13, 3, 2, 'y')     # eyes
    c.rect(24, 21, 16, 4, 'k'); c.rect(25, 21, 3, 3, 'w'); c.rect(36, 21, 3, 3, 'w'); c.rect(30, 22, 3, 3, 'w')      # fanged mouth
    c.rect(14, 30, 36, 26, 'P'); c.rect(40, 32, 10, 24, 'q'); c.rect(14, 30, 36, 2, 'i'); c.rect(16, 32, 3, 22, 'i')   # body armor
    c.ell(14, 32, 10, 6, 'q'); c.ell(50, 32, 10, 6, 'Q'); c.poly([(6,30),(8,22),(12,30)], 'i'); c.poly([(58,30),(56,22),(52,30)], 'i')   # pauldrons + spikes
    c.rect(26, 34, 12, 18, 'q'); c.sphere(32, 42, 4, 5, 'y', 't', 'Y', 'h'); c.px(31, 40, 'w')                        # chest plate + gem
    c.rect(26, 34, 12, 1, 't'); c.rect(26, 51, 12, 1, 't')
    c.rect(6, 36, 8, 18, 'P'); c.rect(50, 36, 8, 18, 'q')                                                            # arms
    for x in (4, 7, 10): c.poly([(x,54),(x+3,54),(x+1.5,60)], 'i')                                                    # claws
    for x in (51, 54, 57): c.poly([(x,54),(x+3,54),(x+1.5,60)], 'i')
    c.rect(18, 56, 12, 7, 'q'); c.rect(34, 56, 12, 7, 'Q')                                                           # legs
    c.rect(20, 46, 24, 2, 't'); c.rect(20, 47, 24, 1, 'Y')                                                           # belt
add('maou','まおう',10, maou)

# ---------- 出力 ----------
assert len(M) == 20
used = set()
for m in M:
    assert len(m['art']) == 64, m['id']
    for r in m['art']:
        assert len(r) == 64, (m['id'], len(r))
        used.update(ch for ch in r if ch != '.')
    if m.get('map'): used.update(m['map'].values())
missing = used - set(PAL)
assert not missing, missing
palused = dict(PAL)

def js():
    out = ['var PAL=' + json.dumps(palused, ensure_ascii=False, separators=(',', ':')).replace('"', "'") + ';', 'var MONS=[']
    for i, m in enumerate(M):
        head = "  { id:'%s', name:'%s', lv:%d" % (m['id'], m['name'], m['lv'])
        if m.get('flip'): head += ', flip:true'
        if m.get('map'): head += ', map:' + json.dumps(m['map'], separators=(',', ':')).replace('"', "'")
        head += ', art:['
        rows = ',\n'.join("    '%s'" % r for r in m['art'])
        out.append(head + '\n' + rows + ' ] }' + (',' if i < len(M)-1 else ''))
    out.append('];')
    return '\n'.join(out) + '\n'

base = r'C:\Users\Lavie3\AppData\Local\Temp\claude\C--Users-Lavie3\bd8de114-94fb-450c-a867-309e176b871f\scratchpad'
io.open(base + r'\monsters3.js', 'w', encoding='utf-8').write(js())

def svg(m, size):
    s = ''
    for y, row in enumerate(m['art']):
        x = 0
        while x < 64:
            ch = row[x]
            if ch == '.': x += 1; continue
            x1 = x
            while x1 < 64 and row[x1] == ch: x1 += 1
            cc = m['map'][ch] if m.get('map') and ch in m['map'] else ch
            s += '<rect x="%d" y="%d" width="%d" height="1" fill="%s"/>' % (x, y, x1-x, PAL[cc])
            x = x1
    if m.get('flip'): s = '<g transform="translate(64,0) scale(-1,1)">' + s + '</g>'
    return '<svg viewBox="0 0 64 64" shape-rendering="crispEdges" width="%d" height="%d">%s</svg>' % (size, size, s)

for size, name in ((200, 'monsters3_preview.html'), (100, 'monsters3_small.html')):
    html = '<!doctype html><meta charset="utf-8"><body style="margin:0;background:#0e0e24;color:#fff;font:13px sans-serif"><div style="display:grid;grid-template-columns:repeat(5,%dpx);gap:10px;padding:10px">' % (size+20)
    for m in M:
        html += '<div style="text-align:center">%s<div>%d %s</div></div>' % (svg(m, size), m['lv'], m['name'])
    html += '</div></body>'
    io.open(base + '\\' + name, 'w', encoding='utf-8').write(html)
print('ok: 20 monsters 64x64, palette', ''.join(sorted(used)))
