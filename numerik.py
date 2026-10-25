"""Logika numerik Metode Tabel (tanpa GUI): pembaca fungsi, validasi angka, dan algoritma sesuai modul.

h = (Xatas - Xbawah)/N;  xi = Xbawah + i.h;  yi = f(xi).  f(xi) = 0 -> xi penyelesaian.  f(xj).f(xj+1) < 0 -> akar
di antara xj dan xj+1, lebih dekat ke xj bila |f(xj)| < |f(xj+1)|, bila tidak ke xj+1.
"""
import math
import re

MAX_N = 500
_FUNCS = {"sin": math.sin, "cos": math.cos, "tan": math.tan, "asin": math.asin, "acos": math.acos,
          "atan": math.atan, "exp": math.exp, "ln": math.log, "log": math.log10, "sqrt": math.sqrt, "abs": abs}
_CONSTS = {"e": math.e, "pi": math.pi}
_NUM = r"\d+\.?\d*(?:e[+-]?\d+)?|\.\d+(?:e[+-]?\d+)?"
_TOKEN = re.compile(_NUM + r"|[a-z_]\w*|\s+|.")
_OPS = {"+", "-", "*", "/", "(", ")", "^", "."}
_ULANG = "\nUbah range atau fungsinya."


class InputError(ValueError):
    """Kesalahan input yang pesannya ditampilkan ke pengguna."""


def _angka(t):
    return bool(re.fullmatch(_NUM, t))


def _nama(t):
    return bool(re.fullmatch(r"[a-z_]\w*", t))


def compile_function(text):
    """Ubah teks fungsi jadi f(x). Huruf besar/kecil boleh, ^ = pangkat, '3x' = 3*x, 'x.e^-x' = x*e^(-x)."""
    expr = text.strip().lower().replace(",", ".")
    if not expr:
        raise InputError("Fungsi f(x) belum diisi.")
    tokens = [t for t in _TOKEN.findall(expr) if not t.isspace()]
    out = []
    for i, t in enumerate(tokens):
        if not (_angka(t) or _nama(t) or t in _OPS):
            raise InputError(f"Karakter '{t}' tidak dikenali dalam fungsi.")
        if _nama(t) and t != "x" and t not in _FUNCS and t not in _CONSTS:
            raise InputError(f"Nama '{t}' tidak dikenali. Gunakan x, e, pi, sin, cos, tan, exp, ln, log, sqrt, abs "
                             f"(tulis perkalian dengan * , misalnya 2*x).")
        if t == ".":
            prev = tokens[i - 1] if i > 0 else ""
            nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
            if (_nama(prev) or prev == ")") and (_nama(nxt) or nxt == "("):
                t = "*"                               # 'x.e^-x' dibaca x * e^(-x), seperti tulisan di modul
            else:
                raise InputError("Tanda titik hanya untuk desimal (misalnya 0.5) atau perkalian antar-suku.")
        out.append("**" if t == "^" else t)
    final = []                                        # perkalian implisit: 3x, 2(x+1), (x+1)(x-1), 3sin(x)
    for t in out:
        if final:
            p = final[-1]
            if (_angka(p) or p == ")" or (_nama(p) and p not in _FUNCS)) and (_angka(t) or _nama(t) or t == "("):
                final.append("*")
        final.append(t)
    try:
        code = compile(" ".join(final), "<fungsi>", "eval")
    except SyntaxError:
        raise InputError("Sintaks fungsi tidak valid. Periksa tanda kurung dan operator.\nContoh: x^2 + e^(-x) - 2")
    env = {**_FUNCS, **_CONSTS}

    def f(x):
        env["x"] = x
        return eval(code, {"__builtins__": {}}, env)
    return f


def eval_f(f, x):
    """Hitung f(x). Bila tidak terdefinisi, laporkan sebagai kesalahan (bukan 0)."""
    try:
        v = f(x)
    except ZeroDivisionError:
        raise InputError(f"f(x) tidak terdefinisi pada x = {x:.6g} (pembagian dengan nol)." + _ULANG)
    except (ValueError, OverflowError, TypeError):
        raise InputError(f"f(x) tidak dapat dihitung pada x = {x:.6g} (di luar domain fungsi)." + _ULANG)
    if isinstance(v, complex):
        raise InputError(f"f(x) bernilai kompleks pada x = {x:.6g}." + _ULANG)
    if not math.isfinite(v := float(v)):
        raise InputError(f"f(x) tidak terhingga pada x = {x:.6g}." + _ULANG)
    return v


def safe_eval(f, x):
    try:
        return eval_f(f, x)
    except InputError:
        return float("nan")


def parse_number(text, nama):
    try:
        v = float(text.strip().replace(",", "."))
    except ValueError:
        v = math.nan
    if not math.isfinite(v):
        raise InputError(f"{nama} harus berupa angka.")
    return v


def parse_int(text, nama):
    try:
        return int(text.strip())
    except ValueError:
        raise InputError(f"{nama} harus berupa bilangan bulat.")


def table_method(f, xb, xa, n):
    """Metode tabel persis seperti algoritma dan flowchart pada modul."""
    h = (xa - xb) / n
    xs = [xb + i * h for i in range(n + 1)]
    xs[-1] = xa                                       # hindari selisih pembulatan di ujung
    ys = [eval_f(f, x) for x in xs]
    roots = [dict(kind="exact", pos=float(i), j=i, k=i, x=xs[i], y=0.0) for i in range(n + 1) if ys[i] == 0]
    for j in range(n):                                # f(xj).f(xj+1) < 0
        a, b = ys[j], ys[j + 1]
        if (a < 0 < b) or (a > 0 > b):
            k = j if abs(a) < abs(b) else j + 1
            roots.append(dict(kind="interval", pos=j + 0.5, j=j, k=k, x=xs[k], y=ys[k]))
    roots.sort(key=lambda r: r["pos"])
    xdec = 4
    if h != 0 and abs(h) < 1e-3:
        xdec = min(10, int(math.ceil(-math.log10(abs(h)))) + 1)
    return dict(h=h, n=n, xs=xs, ys=ys, roots=roots, xdec=xdec)


def ringkasan(data, xb, xa):
    """Susun teks penjelasan hasil. Mengembalikan (teks, ada_akar)."""
    xs, roots, xdec = data["xs"], data["roots"], data["xdec"]
    baris = []
    if xb > xa:
        baris.append("Catatan: X bawah > X atas, jadi h bernilai negatif dan tabel disusun menurun "
                     "(sesuai rumus modul h = (Xatas - Xbawah)/N).")
    if not roots:
        baris.append("Tidak ada penyelesaian pada tabel ini: tidak ada f(xi) = 0 dan tidak ada f(xi)·f(xi+1) < 0. "
                     "Coba ubah batas atau perbesar N.")
        return "\n".join(baris), False
    for no, r in enumerate(roots[:6], start=1):
        if r["kind"] == "exact":
            baris.append(f"Akar {no}: f(x{r['j']}) = 0, maka x{r['j']} = {r['x']:.{xdec}f} adalah penyelesaian.")
        else:
            j, k = r["j"], r["k"]
            baris.append(f"Akar {no}: di antara x{j} = {xs[j]:.{xdec}f} dan x{j + 1} = {xs[j + 1]:.{xdec}f}, "
                         f"lebih dekat ke x{k}  →  x ≈ {r['x']:.{xdec}f}, f(x) = {r['y']:.6f}")
    if len(roots) > 6:
        baris.append(f"... dan {len(roots) - 6} akar lainnya (lihat tabel).")
    return "\n".join(baris), True
