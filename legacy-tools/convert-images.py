"""Convert Sema's legacy PPM intermediate images to viewable, lossless PNGs."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
count=0
for p in root.rglob('*.ppm'):
 with Image.open(p) as im:
  im=im.convert('RGB'); output=p.with_suffix('.png'); im.save(output)
  with Image.open(output) as check:
   assert check.size==im.size and check.convert('RGB').tobytes()==im.tobytes()
 p.unlink(); count+=1
print(f'Converted and verified {count} PNGs; removed only their PPM intermediates.')
