"""Jendela utama: merangkai input, perhitungan (numerik.py), dan tampilan (komponen.py, tampilan_data.py)."""
import customtkinter as ctk

from komponen import KartuStat, KolomInput, Nailong, Palet, fnt, kartu, label, pilih, tombol
from numerik import MAX_N, InputError, compile_function, parse_int, parse_number, ringkasan, table_method
from tampilan_data import GrafikInteraktif, TabelInteraktif

INFO = ("Variabel x, pangkat ^, konstanta e dan pi. Fungsi: sin, cos, tan, exp, sqrt, abs, "
        "ln (natural), log (basis 10). Contoh: x^2+e^(-x)-2")
SAPA = "Halo! Isi fungsinya ya, nanti aku bantu cari akarnya."
STATUS = "Klik baris tabel atau titik di grafik untuk menyorotnya. Panah atas/bawah memindahkan pilihan."
RUMUS_H = "h = (Xatas - Xbawah) / N"


def judul_kartu(master, teks, **pack):
    label(master, "●  " + teks, 13, True, Palet.AKSEN).pack(**pack)


class KalkulatorMetodeTabel(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.mode, self._jadwal, self._pesan, self._data = "Light", None, "", None
        self.title("Kalkulator Metode Tabel")
        self.geometry("1200x840")
        self.minsize(1040, 720)
        self.configure(fg_color=Palet.BG)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._bangun_header()
        self._bangun_kiri()
        self._bangun_kanan()
        for kolom in (self.in_fx, self.in_xb, self.in_xa, self.in_n):
            kolom.entry.bind("<KeyRelease>", self._ketik)
        self.bind("<Return>", lambda _e: self.hitung())
        self.hitung()

    def _bangun_header(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=26, pady=(18, 12))
        label(bar, "Metode Tabel", 30, True).pack(side="left")
        label(bar, "Komputasi Numerik", 11, True, Palet.TEKS_KUNING, fg_color=Palet.KUNING, corner_radius=14,
              padx=14, pady=4).pack(side="left", padx=14, pady=(10, 0))
        self.sakelar = ctk.CTkSwitch(bar, text="Mode gelap", font=fnt(12), text_color=Palet.TEKS,
                                     progress_color=Palet.KUNING, button_color=Palet.AKSEN,
                                     button_hover_color=Palet.AKSEN_HOVER, command=self._ganti_tema)
        self.sakelar.pack(side="right")

    def _bangun_kiri(self):
        kiri = ctk.CTkFrame(self, fg_color="transparent", width=390)
        kiri.grid(row=1, column=0, sticky="ns", padx=(26, 12), pady=(0, 22))
        kiri.pack_propagate(False)
        box = kartu(kiri)
        box.pack(fill="x")
        judul_kartu(box, "Isi Data", anchor="w", padx=20, pady=(18, 8))
        self.in_fx = KolomInput(box, "Fungsi f(x)", "x^2+3*x-4", "contoh: x^2 + 3x - 4")
        self.in_fx.pack(fill="x", padx=20)
        self.lbl_info = label(box, INFO, 10, warna=Palet.REDUP, justify="left", wraplength=330)
        self.lbl_info.pack(anchor="w", padx=20, pady=(6, 10))
        baris = ctk.CTkFrame(box, fg_color="transparent")
        baris.pack(fill="x", padx=20)
        baris.grid_columnconfigure((0, 1), weight=1)
        self.in_xb, self.in_xa = KolomInput(baris, "X bawah", "0"), KolomInput(baris, "X atas", "3")
        self.in_xb.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.in_xa.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.in_n = KolomInput(box, f"Jumlah pembagi N (1 sampai {MAX_N})", "10")
        self.in_n.pack(fill="x", padx=20, pady=(12, 0))
        self.slider = ctk.CTkSlider(box, from_=2, to=100, number_of_steps=98, command=self._geser_n,
                                    progress_color=Palet.KUNING, button_color=Palet.AKSEN,
                                    button_hover_color=Palet.AKSEN_HOVER)
        self.slider.set(10)
        self.slider.pack(fill="x", padx=20, pady=(10, 0))
        label(box, "Geser untuk mengubah N dan lihat titiknya berubah langsung", 10, warna=Palet.REDUP).pack(anchor="w", padx=20)
        self.lbl_h = label(box, RUMUS_H, 12, True, fg_color=Palet.KUNING_LEMBUT, corner_radius=14, padx=14, pady=5)
        self.lbl_h.pack(anchor="w", padx=20, pady=(12, 16))
        tmb = ctk.CTkFrame(box, fg_color="transparent")
        tmb.pack(fill="x", padx=20, pady=(0, 22))
        tmb.grid_columnconfigure((0, 1), weight=1)
        tombol(tmb, "Hitung", self.hitung).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        tombol(tmb, "Reset", self.reset, utama=False).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        bg, maskot = pilih(Palet.BG, self.mode), ctk.CTkFrame(kiri, fg_color="transparent")
        maskot.pack(fill="x", pady=(14, 0))
        self.maskot = [Nailong(maskot, bg), Nailong(maskot, bg, flip=True)]
        self.maskot[0].pack(side="left")
        self.maskot[1].pack(side="right")
        self.gelembung = label(maskot, SAPA, 11, True, fg_color=Palet.KUNING_LEMBUT, corner_radius=18,
                               wraplength=150, justify="center", padx=12, pady=10)
        self.gelembung.pack(side="left", expand=True, fill="x", padx=6)

    def _bangun_kanan(self):
        kanan = ctk.CTkFrame(self, fg_color="transparent")
        kanan.grid(row=1, column=1, sticky="nsew", padx=(12, 26), pady=(0, 22))
        kanan.grid_columnconfigure(0, weight=1)
        kanan.grid_rowconfigure(2, weight=5, minsize=300)
        kanan.grid_rowconfigure(3, weight=2, minsize=170)
        stat = ctk.CTkFrame(kanan, fg_color="transparent")
        stat.grid(row=0, column=0, sticky="ew")
        stat.grid_columnconfigure((0, 1, 2), weight=1)
        self.stats = [KartuStat(stat, "Jumlah akar"), KartuStat(stat, "Akar terdekat (x)", sorot=True),
                      KartuStat(stat, "f(x) di akar")]
        for kol, kt in enumerate(self.stats):
            kt.grid(row=0, column=kol, sticky="ew", padx=(0 if kol == 0 else 6, 6))
        self.lbl_ringkas = label(kanan, "", 12, justify="left", anchor="w", wraplength=700)
        self.lbl_ringkas.grid(row=1, column=0, sticky="ew", pady=10)
        kanan.bind("<Configure>", lambda e: self.lbl_ringkas.configure(wraplength=max(300, e.width - 20)))

        k_grafik = kartu(kanan)
        k_grafik.grid(row=2, column=0, sticky="nsew")
        judul_kartu(k_grafik, "Grafik f(x)", anchor="w", padx=20, pady=(14, 0))
        self.grafik = GrafikInteraktif(k_grafik, self._saat_pilih, self.mode)
        self.grafik.pack(fill="both", expand=True, padx=14, pady=(4, 6))
        label(k_grafik, "Geser kursor di grafik untuk melihat nilai f(x). Klik sebuah titik untuk memilih barisnya.",
              10, warna=Palet.REDUP).pack(pady=(0, 10))
        k_tabel = kartu(kanan)
        k_tabel.grid(row=3, column=0, sticky="nsew", pady=(14, 0))
        judul_kartu(k_tabel, "Tabel xi dan yi", anchor="w", padx=20, pady=(14, 6))
        self.tabel = TabelInteraktif(k_tabel, self._saat_pilih, self.mode)
        self.tabel.pack(fill="both", expand=True, padx=18, pady=(0, 14))
        self.tabel.set_status(STATUS)

    def _periksa(self):
        """Baca & periksa semua isian; kolom yang salah diberi garis merah. None bila belum lengkap/valid."""
        pesan, galat = [], set()

        def coba(kunci, kolom, fungsi):
            if kolom.get().strip():
                try:
                    return fungsi(kolom.get())
                except InputError as err:
                    galat.add(kunci)
                    pesan.append(str(err))

        f = coba("fx", self.in_fx, compile_function)
        xb = coba("xb", self.in_xb, lambda t: parse_number(t, "X bawah"))
        xa = coba("xa", self.in_xa, lambda t: parse_number(t, "X atas"))
        n = coba("n", self.in_n, lambda t: parse_int(t, "Jumlah pembagi N"))
        if n is not None and not 1 <= n <= MAX_N:
            galat.add("n")
            pesan.append(f"Jumlah pembagi N harus bilangan bulat antara 1 sampai {MAX_N}.")
            n = None
        if xb is not None and xb == xa:
            galat.add("xa")
            pesan.append("X bawah dan X atas tidak boleh sama (h akan bernilai 0).")
            xa = None
        for kunci, kolom in (("fx", self.in_fx), ("xb", self.in_xb), ("xa", self.in_xa), ("n", self.in_n)):
            kolom.tandai(kunci in galat)
        lengkap = f is not None and None not in (xb, xa, n)
        self._pesan = pesan[0] if pesan else "" if lengkap else "Lengkapi fungsi, X bawah, X atas, dan N."
        self.lbl_info.configure(text=pesan[0] if pesan else INFO, text_color=Palet.MERAH if pesan else Palet.REDUP)
        self.lbl_h.configure(text=f"{RUMUS_H} = {(xa - xb) / n:.6f}" if None not in (xb, xa, n) else "h = -")
        return (f, xb, xa, n) if lengkap else None

    def _ketik(self, _event=None):
        """Hasil dihitung ulang otomatis sebentar setelah berhenti mengetik."""
        try:
            self.slider.set(min(100, max(2, int(self.in_n.get()))))
        except ValueError:
            pass
        if self._jadwal:
            self.after_cancel(self._jadwal)
        self._jadwal = self.after(400, lambda: self.hitung(manual=False))

    def _geser_n(self, nilai):
        self.in_n.set(str(int(round(nilai))))
        self._ketik()

    def hitung(self, manual=True):
        if self._jadwal:
            self.after_cancel(self._jadwal)
            self._jadwal = None
        hasil = self._periksa()
        if hasil is None:
            return self._galat(self._pesan) if manual else None
        f, xb, xa, n = hasil
        try:
            data = table_method(f, xb, xa, n)
        except InputError as err:
            return self._galat(str(err)) if manual else self.lbl_info.configure(text=str(err), text_color=Palet.MERAH)
        roots, xdec = data["roots"], data["xdec"]
        self._data = data
        self.lbl_h.configure(text=f"{RUMUS_H} = {data['h']:.6f}")
        if roots:
            a = roots[0]
            nilai = (str(len(roots)), f"{a['x']:.{xdec}f}" + (f"  (+{len(roots) - 1})" if len(roots) > 1 else ""),
                     f"{a['y']:.6f}")
            judul = f"Akar terdekat (x)  ·  iterasi ke-{a['k']}"
        else:
            nilai, judul = ("0", "-", "-"), None
        for kt, v in zip(self.stats, nilai):
            kt.set(v)
        self.stats[1].set_judul(judul)
        teks, ada = ringkasan(data, xb, xa)
        self.lbl_ringkas.configure(text=teks, text_color=Palet.TEKS if ada else Palet.MERAH)
        self.tabel.isi(data)
        self.grafik.tampilkan(f, data)
        self.gelembung.configure(text=("Yeay, ketemu! Ada %d akar." % len(roots) if len(roots) > 1 else
                                       "Yeay, akarnya ketemu!") if ada else
                                 "Hmm, belum ketemu. Coba ubah batas atau perbesar N.")
        if ada:
            self._saat_pilih(roots[0]["k"])
        else:
            self.tabel.set_status(STATUS)

    def _kosongkan(self):
        for kt in self.stats:
            kt.set("-")
        self.stats[1].set_judul()
        self.tabel.kosong()
        self.grafik.kosong()
        self._data = None
        self.tabel.set_status(STATUS)

    def _galat(self, pesan):
        self._kosongkan()
        self.lbl_ringkas.configure(text="Perhatian: " + pesan, text_color=Palet.MERAH)
        self.gelembung.configure(text="Eh, ada yang kurang pas. Cek isiannya ya.")

    def reset(self):
        for kolom in (self.in_fx, self.in_xb, self.in_xa, self.in_n):
            kolom.set("")
            kolom.tandai(False)
        self._kosongkan()
        self.slider.set(10)
        self.lbl_h.configure(text=RUMUS_H)
        self.lbl_info.configure(text=INFO, text_color=Palet.REDUP)
        self.lbl_ringkas.configure(text="Isi fungsi, X bawah, X atas, dan N. Hasil muncul otomatis.", text_color=Palet.REDUP)
        self.gelembung.configure(text=SAPA)
        self.focus_set()

    def _saat_pilih(self, i):
        """Dipanggil saat baris tabel atau titik grafik dipilih: keduanya ikut tersinkron."""
        if self._data:
            d = self._data
            self.tabel.pilih(i)
            self.grafik.sorot(i)
            self.tabel.set_status(f"Baris i = {i}:  x = {d['xs'][i]:.{d['xdec']}f},  f(x) = {d['ys'][i]:.6f}")

    def _ganti_tema(self):
        self.mode = "Dark" if self.sakelar.get() else "Light"
        ctk.set_appearance_mode(self.mode)
        for widget in self.maskot:
            widget.configure(bg=pilih(Palet.BG, self.mode))
        self.tabel.set_tema(self.mode)
        self.grafik.set_tema(self.mode)
