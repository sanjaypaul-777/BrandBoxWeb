from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parent.parent / "static" / "images"
logo_path = root / "logo.png"
fav_path = root / "favicon.png"

logo = Image.open(logo_path).convert("RGBA")
print("logo in:", logo.size)
pixels = logo.load()
w, h = logo.size
for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        if r < 28 and g < 28 and b < 28:
            pixels[x, y] = (r, g, b, 0)
logo.save(logo_path, optimize=True)
print("logo transparent saved")

fav = Image.open(fav_path).convert("RGBA")
print("favicon in:", fav.size)
fav.save(root / "logo-mark.png", optimize=True)

for name, size in {
    "favicon-16.png": 16,
    "favicon-32.png": 32,
    "favicon-48.png": 48,
    "apple-touch-icon.png": 180,
}.items():
    fav.resize((size, size), Image.Resampling.LANCZOS).save(root / name, optimize=True)
    print("wrote", name)

# ICO with multiple sizes
imgs = [fav.resize((s, s), Image.Resampling.LANCZOS) for s in (16, 32, 48)]
imgs[0].save(
    root / "favicon.ico",
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48)],
)
print("wrote favicon.ico")
print("done")
