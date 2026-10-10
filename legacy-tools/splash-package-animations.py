from pathlib import Path
from PIL import Image
import subprocess,json
r=(Path(__file__).resolve().parent.parent / 'splash-fractals')
report=[]
for name in ['folded-crown','alternating-tide','pole-garden']:
 paths=sorted((r/(name+'-frames')).glob('*.png')); assert len(paths)==32,(name,len(paths))
 frames=[Image.open(p).convert('RGB').resize((540,411),Image.Resampling.LANCZOS) for p in paths]
 sheet=Image.new('RGB',(540*8,411*4))
 for i,f in enumerate(frames): sheet.paste(f,((i%8)*540,(i//8)*411))
 palette=sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
 indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
 gif=r/(name+'.gif')
 indexed[0].save(gif,save_all=True,append_images=indexed[1:],duration=125,loop=0,optimize=False,disposal=2)
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','8','-i',str(r/(name+'-frames')/'%03d.png'),'-vf','scale=720:548:flags=lanczos','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(r/(name+'.mp4'))],check=True)
 with Image.open(gif) as check:
  assert check.n_frames==32 and check.info['loop']==0
 assert frames[0].tobytes()!=frames[16].tobytes(), 'No movement'
 report.append({'name':name,'frames':32,'gif_bytes':gif.stat().st_size,'loop':True})
 print(name+' GIF and MP4 saved',flush=True)
(r/'animation-verification.json').write_text(json.dumps(report,indent=2))
