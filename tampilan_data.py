"""Grafik dan tabel interaktif yang digambar langsung di Canvas (tanpa matplotlib/numpy)."""
import math
import tkinter as tk

import customtkinter as ctk

from komponen import Palet, blend, fnt, label, rr_titik
from numerik import safe_eval

FONT = "Segoe UI"
_WARNA = dict(                                        # (terang, gelap)
    kartu=("#FFFFFF", "#23211C"), grid=("#EFE3BC", "#37332A"), teks=("#6B7280", "#A8A292"),
    teks_kuat=("#1F2937", "#F3EEDC"), neg=("#E11D48", "#FB7185"), pos=("#2563EB", "#60A5FA"),
    nol=("#16A34A", "#4ADE80"), kuning=("#FACC15", "#FACC15"), kuning_tua=("#A16207", "#FDE68A"),
    garis_nol=("#CA8A04", "#CA9A04"), tip_bg=("#1F2937", "#FEF3C7"), tip_fg=("#FFFBEB", "#1F2937"),
    baris_b=("#FFFBEB", "#2A2722"), pilih=("#FEF08A", "#5A4A10"), akar_bg=("#FEF9C3", "#33290F"),
    pill_akar_bg=("#FDE047", "#CA9A04"), pill_akar_fg=("#713F12", "#1F1500"), pill_dekat_bg=("#FEF3C7", "#4A3F12"),
    pill_dekat_fg=("#92400E", "#FDE68A"), kepala_fg=("#1E293B", "#F3EEDC"))
TEMA = {m: {k: v[i] for k, v in _WARNA.items()} for i, m in enumerate(("Light", "Dark"))}


def ticks(a, b, n=6):
    """Posisi garis sumbu yang 'bulat' (1, 2, 2.5, 5 x 10^k) di antara a dan b."""
    mag = 10 ** math.floor(math.log10((b - a) / n))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if (b - a) / n <= m * mag)
    v, out = math.ceil(a / step) * step, []
    while v <= b + 1e-9:
        out.append(round(v, 10))
        v += step
    return out


def segmen(sx, sy):
    """Pecah kurva jadi potongan bertanda sama; titik potong sumbu x disisipkan tepat di y = 0."""
    segs, cur, prev = [], [], None
    for x, y in zip(sx, sy):
        if y != y:                                    # NaN: kurva terputus
            segs += [cur] if len(cur) > 1 else []
            cur, prev = [], None
            continue
        if prev and (prev[1] < 0) != (y < 0):
            xc = prev[0] + (x - prev[0]) * (0 - prev[1]) / (y - prev[1])
            segs.append(cur + [(xc, 0.0)])
            cur = [(xc, 0.0)]
        cur.append((x, y))
        prev = (x, y)
    return segs + ([cur] if len(cur) > 1 else [])


def warna_nilai(t, y):
    """Hijau bila nol, merah bila negatif, biru bila positif."""
    return t["nol"] if abs(y) < 1e-9 else (t["neg"] if y < 0 else t["pos"])


def pil(c, cx, cy, teks, bg, fg, ukuran=9, pad=14, lebar=None):
    """Label berbentuk pil: ukurannya mengikuti teks; huruf dikecilkan bila lebih lebar dari 'lebar'."""
    tid = c.create_text(cx, cy, text=teks, fill=fg, font=(FONT, ukuran, "bold"))
    x1, _, x2, _ = c.bbox(tid)
    if lebar and (x2 - x1) + 2 * pad > lebar:
        c.itemconfigure(tid, font=(FONT, ukuran - 1, "bold"))
    elif not lebar:                                   # jaga agar tidak keluar dari kanvas
        c.move(tid, 6 - (x1 - pad) if x1 - pad < 6 else min(0, (c.winfo_width() - 6) - (x2 + pad)), 0)
    x1, y1, x2, y2 = c.bbox(tid)
    if lebar:                                         # pil di tabel: tinggi tetap 24 px
        y1, y2 = cy - 6, cy + 6
    c.tag_lower(c.create_polygon(rr_titik(x1 - pad, y1 - 6, x2 + pad, y2 + 6, (y2 - y1 + 12) / 2), smooth=True,
                                 fill=bg, outline=""), tid)


class GrafikInteraktif(tk.Canvas):
    """Kurva berwarna menurut tanda f(x), tooltip, dan klik titik untuk memilih baris tabel."""
    L, R, T, B = 56, 24, 38, 40

    def __init__(self, master, saat_klik, mode="Light"):
        self.t = TEMA[mode]
        super().__init__(master, bg=self.t["kartu"], highlightthickness=0, height=300)
        self._cb, self._f, self._data, self._pilih, self._siap, self._titik = saat_klik, None, None, None, False, []
        self._pesan = "Grafik tampil setelah perhitungan"
        self.bind("<Configure>", lambda _e: self._gambar())
        self.bind("<Motion>", self._gerak)
        self.bind("<Leave>", lambda _e: self.delete("dinamis"))
        self.bind("<Button-1>", self._klik)

    def kosong(self, pesan="Grafik tampil setelah perhitungan"):
        self._f, self._data, self._pesan = None, None, pesan
        self._gambar()

    def tampilkan(self, f, data):
        self._f, self._data, self._pilih = f, data, None
        self._gambar()

    def sorot(self, i):
        self._pilih = i
        self._lapis_pilih()

    def set_tema(self, mode):
        self.t = TEMA[mode]
        self.configure(bg=self.t["kartu"])
        self._gambar()

    def _gambar(self):
        self.delete("all")
        self._siap, self._titik = False, []
        W, H, t = self.winfo_width(), self.winfo_height(), self.t
        if W < 150 or H < 110:
            return
        if self._data is None:
            return self.create_text(W / 2, H / 2, text=self._pesan, fill=t["teks"], font=(FONT, 11))
        xs, ys, roots = self._data["xs"], self._data["ys"], self._data["roots"]
        x0, x1 = min(xs[0], xs[-1]), max(xs[0], xs[-1])
        sx = [x0 + (x1 - x0) * k / 320 for k in range(321)]
        sy = [safe_eval(self._f, x) for x in sx]
        v = sorted([y for y in sy if y == y] + list(ys) + [0.0])
        lo, hi = v[0], v[-1]
        if hi - lo > 1e4:                             # fungsi meledak (mis. tan): potong ekor
            lo, hi = min(v[int(.02 * (len(v) - 1))], 0.0), max(v[int(.98 * (len(v) - 1))], 0.0)
        pad = (hi - lo) * .1 or 1.0
        lo, hi = lo - pad, hi + pad
        L, R, T, B = self.L, self.R, self.T, self.B
        pw, ph = W - L - R, H - T - B
        px = lambda x: L + (x - x0) / (x1 - x0) * pw
        py = lambda y: T + (hi - y) / (hi - lo) * ph
        cl = lambda y: max(T, min(T + ph, py(y)))
        self._g, self._dasar = (x0, x1, W, H, cl), T + ph

        for v in ticks(lo, hi, 5):                    # kisi dan angka sumbu
            self.create_line(L, py(v), W - R, py(v), fill=t["grid"])
            self.create_text(L - 8, py(v), text=f"{(v or 0):g}", anchor="e", fill=t["teks"], font=(FONT, 8))
        for v in ticks(x0, x1, 7):
            self.create_line(px(v), T + ph, px(v), T + ph + 4, fill=t["teks"])
            self.create_text(px(v), T + ph + 14, text=f"{(v or 0):g}", fill=t["teks"], font=(FONT, 8))
        for r in roots:                               # pita interval tempat akar terjepit
            if r["kind"] == "interval":
                self.create_rectangle(px(xs[r["j"]]), T, px(xs[r["j"] + 1]), T + ph,
                                      fill=blend(t["kuning"], t["kartu"], .14), outline="")
        y0px = py(0.0)
        for seg in segmen(sx, sy):                    # area dan garis kurva, merah bila negatif, biru bila positif
            pts = [(px(x), cl(y)) for x, y in seg]
            w = t["neg"] if any(p[1] < 0 for p in seg) else t["pos"]
            self.create_polygon([pts[0][0], y0px] + [c for p in pts for c in p] + [pts[-1][0], y0px],
                                fill=blend(w, t["kartu"], .16), outline="")
            self.create_line(*[c for p in pts for c in p], fill=w, width=3.5, capstyle="round", joinstyle="round",
                             tags="kurva")
        self.create_line(L, y0px, W - R, y0px, fill=t["garis_nol"], width=1.6)
        self.create_line(L, T, L, T + ph, fill=t["grid"], width=1.5)
        self.create_line(L, T + ph, W - R, T + ph, fill=t["grid"], width=1.5)
        self.create_text(W - R, T + ph + 28, text="x", anchor="e", fill=t["teks"], font=(FONT, 9, "italic"))
        self.create_text(L - 8, T - 16, text="f(x)", anchor="e", fill=t["teks"], font=(FONT, 9, "italic"))
        self.tag_raise("kurva")

        r = 3.6 if len(xs) <= 40 else (2.6 if len(xs) <= 80 else 1.8)
        self._siap, self._titik = True, [(px(x), cl(y), i) for i, (x, y) in enumerate(zip(xs, ys))]
        for cx, cy, i in self._titik:                 # titik xi
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=warna_nilai(t, ys[i]), outline=t["kartu"], width=1.5)
        for rt in roots:                              # penanda akar
            cx, cy, w = px(rt["x"]), cl(rt["y"]), t["kuning_tua"]
            self.create_line(cx, cy, cx, self._dasar, fill=w, width=1.2, dash=(2, 3))
            self.create_oval(cx - 12, cy - 12, cx + 12, cy + 12, outline=t["kuning"], width=2)
            self.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill=t["kartu"], outline=w, width=3)
            self.create_oval(cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5, fill=w, outline="")
            if len(roots) <= 4:
                pil(self, cx, max(18, cy - 28), f"x ≈ {rt['x']:.{min(self._data['xdec'], 4)}f}",
                    t["pill_akar_bg"], t["pill_akar_fg"])
        self._lapis_pilih()

    def _lapis_pilih(self):
        self.delete("pilih")
        if self._pilih is not None and 0 <= self._pilih < len(self._titik):
            cx, cy, _ = self._titik[self._pilih]
            w = self.t["kuning_tua"]
            self.create_line(cx, cy, cx, self._dasar, dash=(3, 3), fill=w, width=1.5, tags="pilih")
            self.create_oval(cx - 11, cy - 11, cx + 11, cy + 11, outline=w, width=3, tags="pilih")
            self.tag_raise("dinamis")

    def _tip(self, x, y, baris):
        t, W = self.t, self.winfo_width()
        ids = [self.create_text(0, 0, anchor="nw", text=s, fill=t["tip_fg"], tags="dinamis",
                                font=(FONT, 9, "bold" if k == 0 else "normal")) for k, s in enumerate(baris)]
        kotak = [self.bbox(i) for i in ids]
        tb = max(b[3] - b[1] for b in kotak) + 3      # tinggi satu baris
        w, h = max(b[2] - b[0] for b in kotak) + 28, tb * len(ids) + 18
        bx, by = min(x + 14, W - w - 6), max(6, y - h - 12)
        for k, i in enumerate(ids):
            self.coords(i, bx + 14, by + 9 + k * tb)
        self.tag_lower(self.create_polygon(rr_titik(bx, by, bx + w, by + h, 10), smooth=True, fill=t["tip_bg"],
                                           outline="", tags="dinamis"), ids[0])

    def _titik_dekat(self, x, y):
        dekat = [(math.hypot(cx - x, cy - y), i) for cx, cy, i in self._titik]
        return min(dekat)[1] if dekat and min(dekat)[0] <= 12 else None

    def _gerak(self, e):
        self.delete("dinamis")
        if not self._siap:
            return
        x0, x1, W, H, cl = self._g
        t, L, R, T, B = self.t, self.L, self.R, self.T, self.B
        dalam = L <= e.x <= W - R and T <= e.y <= H - B
        i = self._titik_dekat(e.x, e.y) if dalam else None
        self.configure(cursor="hand2" if i is not None else "crosshair" if dalam else "")
        if i is not None:                             # kursor di dekat titik xi
            cx, cy, _ = self._titik[i]
            self.create_oval(cx - 9, cy - 9, cx + 9, cy + 9, outline=t["kuning_tua"], width=2, tags="dinamis")
            self._tip(cx, cy, [f"i = {i}", f"x = {self._data['xs'][i]:.4f}", f"f(x) = {self._data['ys'][i]:.5f}"])
        elif dalam:                                   # kursor di tempat lain: nilai f(x) pada kurva
            xv = x0 + (e.x - L) / (W - L - R) * (x1 - x0)
            yv = safe_eval(self._f, xv)
            if yv == yv:
                self.create_line(e.x, T, e.x, H - B, dash=(3, 3), fill=t["teks"], tags="dinamis")
                self.create_oval(e.x - 5, cl(yv) - 5, e.x + 5, cl(yv) + 5, fill=t["kuning"],
                                 outline=t["kuning_tua"], width=2, tags="dinamis")
                self._tip(e.x, cl(yv), [f"x = {xv:.4f}", f"f(x) = {yv:.5f}"])

    def _klik(self, e):
        i = self._titik_dekat(e.x, e.y) if self._siap else None
        if i is not None:
            self._cb(i)


KOLOM = (("i", .07, "c"), ("xi", .17, "e"), ("f(xi)", .19, "e"), ("f(xi+1)", .19, "e"),
         ("f(xi)·f(xi+1)", .20, "e"), ("Keterangan", .18, "c"))
PASTEL = ("#FEF08A", "#BAE6FD", "#BBF7D0", "#FECDD3", "#E9D5FF", "#FBCFE8")
BARIS = 38


class TabelInteraktif(ctk.CTkFrame):
    """Tabel xi dan yi: baris bulat berwarna, klik, panah atas/bawah, scrollbar, filter baris akar."""

    def __init__(self, master, saat_pilih, mode="Light"):
        super().__init__(master, fg_color="transparent")
        self.mode, self.t, self._cb = mode, TEMA[mode], saat_pilih
        self._baris, self._tampil, self._off, self._sel = [], [], 0, None
        atas = ctk.CTkFrame(self, fg_color="transparent")
        atas.pack(fill="x", pady=(0, 6))
        self.lbl = label(atas, "", 10, warna=Palet.REDUP)
        self.lbl.pack(side="left")
        self.sakelar = ctk.CTkSwitch(atas, text="Hanya baris akar", font=fnt(11), text_color=Palet.TEKS,
                                     command=self._saring)
        self.sakelar.pack(side="right")
        self.kepala = tk.Canvas(self, height=38, highlightthickness=0, bg=self.t["kartu"])
        self.kepala.pack(fill="x")
        bawah = ctk.CTkFrame(self, fg_color="transparent")
        bawah.pack(fill="both", expand=True)
        self.bar = ctk.CTkScrollbar(bawah, command=self._geser)
        self.bar.pack(side="right", fill="y")
        self.badan = tk.Canvas(bawah, highlightthickness=0, bg=self.t["kartu"], takefocus=1, height=200)
        self.badan.pack(side="left", fill="both", expand=True)
        self.kepala.bind("<Configure>", lambda _e: self._gambar_kepala())
        self.badan.bind("<Configure>", lambda _e: self._gambar())
        self.badan.bind("<Button-1>", self._klik)
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.badan.bind(seq, lambda e: self._geser("scroll", -2 if e.num == 4 or e.delta > 0 else 2, "units"))
        self.badan.bind("<Up>", lambda _e: self._panah(-1))
        self.badan.bind("<Down>", lambda _e: self._panah(1))

    def set_status(self, teks):
        self.lbl.configure(text=teks)

    def kosong(self):
        self._baris, self._tampil, self._sel, self._off = [], [], None, 0
        self._gambar()

    def isi(self, data):
        n, xs, ys, xdec, roots = data["n"], data["xs"], data["ys"], data["xdec"], data["roots"]
        tepat = {r["j"] for r in roots if r["kind"] == "exact"}
        interval = {r["j"]: r["k"] for r in roots if r["kind"] == "interval"}
        terpilih = {r["k"] for r in roots}
        self._baris = []
        for i in range(n + 1):
            ket, kat = (("xi akar", "akar") if i in tepat else
                        (("akar dekat xi" if interval[i] == i else "akar dekat xi+1"), "akar") if i in interval else
                        ("akar terpilih", "dekat") if i in terpilih else ("", ""))
            lanjut = i < n
            self._baris.append(dict(i=i, kat=kat, ket=ket, y=ys[i], teks=[
                str(i), f"{xs[i]:.{xdec}f}", f"{ys[i]:.6f}",
                f"{ys[i + 1]:.6f}" if lanjut else "-", f"{ys[i] * ys[i + 1]:.6f}" if lanjut else "-"]))
        self._sel = None
        self._saring()

    def pilih(self, i):
        self._sel = i
        if i in self._tampil:                         # gulir seperlunya agar barisnya terlihat penuh
            pos = self._tampil.index(i)
            self._off = max(min(self._off, pos * BARIS), (pos + 1) * BARIS - self.badan.winfo_height())
        self._gambar()

    def set_tema(self, mode):
        self.mode, self.t = mode, TEMA[mode]
        self.kepala.configure(bg=self.t["kartu"])
        self.badan.configure(bg=self.t["kartu"])
        self._gambar_kepala()
        self._gambar()

    def _saring(self):
        self._tampil = [r["i"] for r in self._baris if not self.sakelar.get() or r["kat"]]
        self._off = 0
        self._gambar()

    def _geser(self, *a):                             # dipanggil scrollbar dan roda mouse
        if a[0] == "moveto":
            self._off = float(a[1]) * len(self._tampil) * BARIS
        else:
            self._off += int(a[1]) * BARIS * (1 if a[2] == "units" else 5)
        self._gambar()

    def _spans(self, W):
        x, out = 14, []
        for _, fr, _ in KOLOM:
            out.append((x, x + (W - 28) * fr))
            x += (W - 28) * fr
        return out

    def _klik(self, e):
        self.badan.focus_set()
        pos = int((e.y + self._off) // BARIS)
        if 0 <= pos < len(self._tampil):
            self._sel = self._tampil[pos]
            self._gambar()
            self._cb(self._sel)

    def _panah(self, arah):
        if self._tampil:
            sekarang = self._tampil.index(self._sel) if self._sel in self._tampil else (-1 if arah > 0 else len(self._tampil))
            self._cb(self._tampil[max(0, min(len(self._tampil) - 1, sekarang + arah))])

    def _gambar_kepala(self):
        c, t = self.kepala, self.t
        c.delete("all")
        if c.winfo_width() < 100:
            return
        for (a, b), (judul, _, _), warna in zip(self._spans(c.winfo_width()), KOLOM, PASTEL):
            isi = warna if self.mode == "Light" else blend(warna, t["kartu"], .32)
            c.create_polygon(rr_titik(a + 3, 5, b - 3, 33, 12), smooth=True, fill=isi, outline="")
            c.create_text((a + b) / 2, 19, text=judul, fill=t["kepala_fg"], font=(FONT, 10, "bold"))

    def _gambar(self):
        c, t = self.badan, self.t
        c.delete("all")
        W, H = c.winfo_width(), c.winfo_height()
        if W < 100:
            return
        if not self._tampil:
            c.create_text(W / 2, H / 2, text="Tidak ada baris akar" if self._baris else "Belum ada data",
                          fill=t["teks"], font=(FONT, 11))
            return self.bar.set(0, 1)
        total = len(self._tampil) * BARIS
        self._off = max(0, min(self._off, max(0, total - H)))
        self.bar.set(0, 1) if total <= H else self.bar.set(self._off / total, (self._off + H) / total)
        spans = self._spans(W)
        for pos in range(int(self._off // BARIS), min(len(self._tampil), int((self._off + H) // BARIS) + 1)):
            r = self._baris[self._tampil[pos]]
            y0 = pos * BARIS - self._off + 3
            y1, ym, dipilih = y0 + BARIS - 6, y0 + (BARIS - 6) / 2, r["i"] == self._sel
            isi = t["pilih"] if dipilih else t["akar_bg"] if r["kat"] else t["kartu"] if pos % 2 == 0 else t["baris_b"]
            c.create_polygon(rr_titik(6, y0, W - 6, y1, 12), smooth=True, fill=isi, width=2,
                             outline=t["kuning_tua"] if dipilih else "")
            for k, (a, b) in enumerate(spans[:5]):
                kw = dict(text=r["teks"][k], fill=warna_nilai(t, r["y"]) if k == 2 else t["teks_kuat"],
                          font=(FONT, 10, "bold" if dipilih or r["kat"] else "normal"))
                if KOLOM[k][2] == "c":
                    c.create_text((a + b) / 2, ym, **kw)
                else:
                    c.create_text(b - 12, ym, anchor="e", **kw)
            if r["ket"]:
                a, b = spans[5]
                akar = r["kat"] == "akar"
                pil(c, (a + b) / 2, ym, r["ket"], t["pill_akar_bg" if akar else "pill_dekat_bg"],
                    t["pill_akar_fg" if akar else "pill_dekat_fg"], pad=12, lebar=(b - a) - 4)
