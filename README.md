# Kalkulator Metode Tabel

Aplikasi desktop (Python + CustomTkinter) untuk mencari akar persamaan non linear `f(x) = 0`
dengan **Metode Tabel**, dibuat untuk mata kuliah Komputasi Numerik.

## Fitur
- Pembaca fungsi yang aman: `x^2+3x-4`, `x*e^-x`, `sin`, `cos`, `tan`, `exp`, `sqrt`, `abs`, `ln`, `log`, `pi`, `e`
- Hasil dihitung ulang otomatis saat mengetik, dan slider N mengubah jumlah titik secara langsung
- Validasi langsung: kolom yang salah diberi garis merah dan pesan penjelasan
- Grafik buatan sendiri di Canvas: kurva berwarna menurut tanda f(x), cincin penanda akar,
  tooltip saat kursor digeser, dan klik titik untuk memilih barisnya
- Tabel bulat berwarna dengan klik, panah atas/bawah, scrollbar, dan filter **Hanya baris akar**
- Mode terang dan gelap, tampilan bulat berwarna kuning, serta maskot Nailong yang berubah ekspresi dan bicara lewat gelembung ucapan

## Algoritma (sesuai modul)
1. Definisikan `f(x)`, `Xbawah`, `Xatas`, dan jumlah pembagi `N`
2. Hitung `h = (Xatas - Xbawah) / N`
3. Untuk `i = 0..N`: `xi = Xbawah + i·h`, `yi = f(xi)`
4. Jika `f(xi) = 0` maka `xi` adalah penyelesaian
5. Jika `f(xi)·f(xi+1) < 0`: akar ada di antara `xi` dan `xi+1`. Bila `|f(xi)| < |f(xi+1)|` akar lebih dekat ke `xi`, bila tidak ke `xi+1`

## Cara menjalankan
```bash
python -m pip install -r requirements.txt
python main.py
```
Butuh Python 3.9 atau lebih baru. Satu-satunya library tambahan adalah CustomTkinter (numpy dan matplotlib tidak lagi dipakai).

## Struktur file
| File | Isi |
|---|---|
| `main.py` | Titik masuk aplikasi |
| `aplikasi.py` | Jendela utama dan alur interaksi |
| `komponen.py` | Palet warna, kolom input, kartu, dan maskot Nailong |
| `tampilan_data.py` | Grafik dan tabel interaktif (digambar di Canvas) |
| `numerik.py` | Pembaca fungsi dan algoritma Metode Tabel (tanpa GUI) |
