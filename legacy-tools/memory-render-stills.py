from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageChops
import math,json
r=(Path(__file__).resolve().parent.parent / 'memory-fractals')
palette=[(250,204,21),(34,211,238),(185,155,224)]
report=[]
for name in ['address-lace','signed-braid','phase-coral']:
 data=[]; xs=[];ys=[]
 for line in (r/(name+'.geometry')).read_text().splitlines():
  kind,*v=line.split(); x,y,a,b,level,ink=map(float,v); data.append((kind,x,y,a,b,int(level),int(ink)))
  if kind=='C': xs.extend([x-a,x+a]);ys.extend([y-a,y+a])
  else: xs.extend([x,a]);ys.extend([y,b])
 lo,hi=min(xs),max(xs); bottom,top=min(ys),max(ys); size=1800
 scale=1560/max(hi-lo,top-bottom); cx=(lo+hi)/2;cy=(top+bottom)/2
 def pt(x,y): return ((x-cx)*scale+size/2,(y-cy)*scale+size/2)
 layer=Image.new('RGB',(size,size));d=ImageDraw.Draw(layer)
 for kind,x,y,a,b,level,ink in data:
  col=palette[(ink+(level//2))%3]
  strength=min(1,0.36+0.11*level);col=tuple(int(c*strength) for c in col)
  width=2 if level<4 else 1
  if kind=='L': d.line([pt(x,y),pt(a,b)],fill=col,width=width)
  else:
   px,py=pt(x,y); rad=a*scale;d.ellipse([px-rad,py-rad,px+rad,py+rad],outline=col,width=width)
 glow=layer.filter(ImageFilter.GaussianBlur(3))
 out=ImageChops.add(Image.new('RGB',(size,size),(10,10,11)),ImageChops.add(layer,glow,scale=1.35))
 out=out.resize((1200,1200),Image.Resampling.LANCZOS);out.save(r/(name+'.png'))
 report.append({'name':name,'primitives':len(data),'bounds':[lo,bottom,hi,top]})
 print(name,len(data),flush=True)
(r/'render-report.json').write_text(json.dumps(report,indent=2))
