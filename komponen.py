"""Komponen dasar: palet warna, fungsi bantu, widget input, kartu angka, dan maskot Nailong."""
import customtkinter as ctk


class Palet:                                          # pasangan (terang, gelap) yang dipahami CustomTkinter
    BG, KARTU, GARIS = ("#FFF3C4", "#171613"), ("#FFFFFF", "#23211C"), ("#F6E3A1", "#3A362B")
    INPUT, TEKS, REDUP = ("#FFFDF5", "#2D2A24"), ("#1F2937", "#F3EEDC"), ("#6B7280", "#A8A292")
    AKSEN, AKSEN_HOVER = ("#B45309", "#FBBF24"), ("#92400E", "#F59E0B")
    KUNING, KUNING_HOVER = ("#FACC15", "#CA9A04"), ("#EAB308", "#E0AE0A")
    KUNING_LEMBUT, TEKS_KUNING = ("#FEF3C7", "#3A3217"), ("#3B2A05", "#1F1500")   # TEKS_KUNING: teks di tombol kuning
    MERAH = ("#DC2626", "#F87171")


def pilih(pasangan, mode):
    return pasangan[mode == "Dark"]


def blend(fg, bg, alpha):
    """Campur warna hex fg di atas bg dengan opasitas alpha (0..1)."""
    a, b = ([int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in (fg, bg))
    return "#" + "".join(f"{round(alpha * x + (1 - alpha) * y):02x}" for x, y in zip(a, b))


def rr_titik(x0, y0, x1, y1, r):
    """Titik persegi bulat; pakai create_polygon(..., smooth=True)."""
    r = max(1, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    return [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1, x1 - r, y1,
            x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]


def fnt(ukuran=12, tebal=False):
    return ctk.CTkFont(family="Segoe UI", size=ukuran, weight="bold" if tebal else "normal")


def label(master, teks, ukuran=12, tebal=False, warna=Palet.TEKS, **kw):
    return ctk.CTkLabel(master, text=teks, font=fnt(ukuran, tebal), text_color=warna, **kw)


def tombol(master, teks, perintah, utama=True):
    """Tombol bulat: 'utama' berisi kuning, selain itu hanya berbingkai kuning."""
    gaya = (dict(fg_color=Palet.KUNING, hover_color=Palet.KUNING_HOVER, text_color=Palet.TEKS_KUNING) if utama else
            dict(fg_color="transparent", border_width=2, border_color=Palet.KUNING,
                 text_color=Palet.TEKS, hover_color=Palet.KUNING_LEMBUT))
    return ctk.CTkButton(master, text=teks, height=46, corner_radius=23, font=fnt(14, utama), command=perintah, **gaya)


def kartu(master, **kw):
    kw.setdefault("corner_radius", 28)
    return ctk.CTkFrame(master, fg_color=Palet.KARTU, border_width=1, border_color=Palet.GARIS, **kw)


class KolomInput(ctk.CTkFrame):
    """Label + kolom isian bulat; garis merah bila isinya salah."""

    def __init__(self, master, judul, nilai="", placeholder=""):
        super().__init__(master, fg_color="transparent")
        label(self, judul, 12, True).pack(anchor="w")
        self.entry = ctk.CTkEntry(self, height=42, corner_radius=21, border_width=2, border_color=Palet.GARIS,
                                  fg_color=Palet.INPUT, text_color=Palet.TEKS, placeholder_text=placeholder,
                                  font=fnt(13))
        self.entry.pack(fill="x", pady=(4, 0))
        self.entry.insert(0, nilai)

    def get(self):
        return self.entry.get()

    def set(self, teks):
        self.entry.delete(0, "end")
        self.entry.insert(0, teks)

    def tandai(self, salah):
        self.entry.configure(border_color=Palet.MERAH if salah else Palet.GARIS)


class KartuStat(ctk.CTkFrame):
    """Kartu angka ringkasan. Berkedip kuning sebentar saat nilainya berubah."""

    def __init__(self, master, judul, sorot=False):
        self._bd, self._judul = (Palet.KUNING if sorot else Palet.GARIS), judul
        super().__init__(master, corner_radius=24, border_width=2 if sorot else 1, border_color=self._bd,
                         fg_color=Palet.KUNING_LEMBUT if sorot else Palet.KARTU)
        self.lbl_judul = label(self, judul, 11, warna=Palet.REDUP)
        self.lbl_judul.pack(anchor="w", padx=16, pady=(10, 0))
        self.nilai = label(self, "-", 24, True)
        self.nilai.pack(anchor="w", padx=16, pady=(0, 10))

    def set_judul(self, teks=None):
        self.lbl_judul.configure(text=teks or self._judul)

    def set(self, teks):
        if teks != self.nilai.cget("text"):
            self.nilai.configure(text=teks)
            self.configure(border_color=Palet.KUNING, border_width=3)
            self.after(500, lambda: self.configure(border_color=self._bd, border_width=1))


class Nailong(ctk.CTkCanvas):
    """Nailong berdiri dan melambai (hiasan panel kiri bawah); flip=True melambai dari sisi lain."""

    def __init__(self, master, bg, flip=False):
        super().__init__(master, width=80, height=100, bg=bg, highlightthickness=0)
        oval, k = self.create_oval, dict(fill="#FBBF24", outline="#F59E0B")
        lengan = lambda x0, y0, x1, y1, **kw: oval(*((80 - x1, y0, 80 - x0, y1) if flip else (x0, y0, x1, y1)), **kw)
        oval(15, 8, 65, 58, width=2, **k)
        oval(18, 42, 62, 92, width=2, **k)
        oval(25, 50, 55, 88, fill="#FEF08A", outline="")
        oval(22, 85, 34, 96, width=1.5, **k)
        oval(46, 85, 58, 96, width=1.5, **k)
        lengan(8, 25, 20, 42, width=1.5, **k)
        lengan(55, 35, 75, 48, width=1.5, **k)
        lengan(67, 37, 74, 45, fill="#FCA5A5", outline="")
        for x in (24, 42):                            # mata
            oval(x, 20, x + 14, 34, fill="white", outline="")
            oval(x + 2, 21, x + 12, 33, fill="#16A34A", outline="")
            oval(x + 4, 24, x + 10, 31, fill="#052E16", outline="")
            oval(x + 5, 25, x + 7, 27, fill="white", outline="")
        self.create_arc(32, 26, 48, 38, start=210, extent=120, style="arc", outline="#713F12", width=1.5)
