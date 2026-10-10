"""Sema geometry, periodic interpolation, 2x antialiasing, and linear-light bloom.
Run with Python containing numpy and opencv-python-headless. Requires sema and ffmpeg.
"""
from pathlib import Path
import subprocess, numpy as np, cv2, json, time, math
ROOT=Path(__file__).resolve().parent
SIZE=1920; SUPER=3840; FPS=30; FRAMES=240; KEYS=48
PALETTE=np.array([[250,204,21],[34,211,238],[185,155,224]],dtype=np.float32)

def read_keys(name):
    src=ROOT/(name+'-loop.sema')
    subprocess.run(['sema','compile',str(src)],check=True)
    keys=[]; kinds=None
    with (ROOT/(name+'-generation.log')).open('w') as err:
        p=subprocess.Popen(['sema','--no-llm',str(src.with_suffix('.semac'))],stdout=subprocess.PIPE,stderr=err)
        block=[]; inside=False
        for line in p.stdout:
            if line.strip()==b'BEGIN': inside=True;block=[]
            elif line.strip()==b'END':
                if kinds is None: kinds=np.array([x[:1]==b'C' for x in block])
                assert len(block)==len(kinds)
                a=np.fromstring(b' '.join(x[2:].strip() for x in block).decode(),sep=' ',dtype=np.float32).reshape(-1,6)
                assert np.isfinite(a).all()
                if keys: assert np.array_equal(a[:,4:],keys[0][:,4:])
                keys.append(a)
                if len(keys)%8==0: print(name,'keyframes',len(keys),'/',KEYS,flush=True)
                inside=False
            elif inside: block.append(line)
        assert p.wait()==0,(name,'Sema failed; inspect generation log')
    assert len(keys)==KEYS
    return np.stack(keys),kinds

def interpolate(keys,t):
    i=int(math.floor(t));u=t-i
    a,b,c,d=[keys[j%KEYS] for j in (i-1,i,i+1,i+2)]
    return .5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u)

def render(name):
    started=time.time();keys,kinds=read_keys(name)
    lines=~kinds
    # Use a fixed viewport covering the entire cycle, with room for interpolation.
    xs=np.concatenate([keys[:,lines,0].ravel(),keys[:,lines,2].ravel(),(keys[:,kinds,0]-keys[:,kinds,2]).ravel(),(keys[:,kinds,0]+keys[:,kinds,2]).ravel()])
    ys=np.concatenate([keys[:,lines,1].ravel(),keys[:,lines,3].ravel(),(keys[:,kinds,1]-keys[:,kinds,2]).ravel(),(keys[:,kinds,1]+keys[:,kinds,2]).ravel()])
    cx=(xs.min()+xs.max())/2;cy=(ys.min()+ys.max())/2
    scale=SUPER*.83/max(np.ptp(xs),np.ptp(ys));del xs,ys
    levels=keys[0,:,4].astype(int);inks=keys[0,:,5].astype(int)
    groups=[]
    for circle in (False,True):
        for level in np.unique(levels):
            for ink in range(3):
                ix=np.flatnonzero((kinds==circle)&(levels==level)&(inks==ink))
                if not len(ix): continue
                color=PALETTE[(ink+level//2)%3]*min(1,.52+.09*level)
                width=max(1,round(2.4-.17*level))
                if circle:
                    segments=max(8,min(1024,int(800/(3**int(level)))))
                    theta=np.linspace(0,2*np.pi,segments,endpoint=False,dtype=np.float32)
                    unit=np.stack([np.cos(theta),np.sin(theta)],axis=-1)
                else: unit=None
                groups.append((circle,ix,tuple(map(float,color)),width,unit))
    bg=((np.array([10,10,11],np.float32)/255)**2.2)
    # Encode directly from RAM; intermediate full-resolution frames are not stored.
    out=ROOT/(name+'-1920-loop.mp4')
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{SIZE}x{SIZE}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
    first=None; movement=None
    def raster(g):
        layer=np.zeros((SUPER,SUPER,3),dtype=np.uint8)
        for circle,ix,color,width,unit in groups:
            q=g[ix]
            if circle:
                paths=q[:,None,:2]+q[:,None,2:3]*unit[None,:,:]
            else: paths=q[:,:4].reshape(-1,2,2)
            paths=(paths-np.array([cx,cy],np.float32))*scale+SUPER/2
            paths=np.rint(paths).astype(np.int32)
            cv2.polylines(layer,paths,circle,color,width,lineType=cv2.LINE_AA)
        base=cv2.resize(layer,(SIZE,SIZE),interpolation=cv2.INTER_AREA).astype(np.float32)/255
        linear=base**2.2
        small=cv2.resize(linear,(480,480),interpolation=cv2.INTER_AREA)
        glow=(cv2.GaussianBlur(small,(0,0),1.1)*.9+
              cv2.GaussianBlur(small,(0,0),5)*.55+
              cv2.GaussianBlur(small,(0,0),17)*.28)
        light=linear*1.18+cv2.resize(glow,(SIZE,SIZE),interpolation=cv2.INTER_LINEAR)+bg
        # Gentle highlight compression keeps bright intersections from clipping.
        light=np.where(light>.8,.8+.2*(1-np.exp(-(light-.8)/.2)),light)
        return np.rint(np.clip(light,0,1)**(1/2.2)*255).astype(np.uint8)
    try:
        for f in range(FRAMES):
            g=interpolate(keys,f*KEYS/FRAMES);image=raster(g)
            if f==0:
                first=image.copy();cv2.imwrite(str(ROOT/(name+'-1920-still.png')),cv2.cvtColor(image,cv2.COLOR_RGB2BGR))
            if f==FRAMES//2: movement=float(np.abs(image.astype(float)-first).mean())
            ff.stdin.write(image.tobytes())
            if (f+1)%30==0: print(name,'rendered',f+1,'/',FRAMES,flush=True)
        ff.stdin.close();assert ff.wait()==0
    except BaseException:
        ff.kill();ff.wait();raise
    # The periodic spline has identical values and tangents at both endpoints.
    seam_error=float(np.max(np.abs(interpolate(keys,0)-interpolate(keys,KEYS))))
    assert seam_error==0 and movement>0.1
    epsilon=.001
    v0=(interpolate(keys,epsilon)-interpolate(keys,-epsilon))/(2*epsilon)
    v1=(interpolate(keys,KEYS+epsilon)-interpolate(keys,KEYS-epsilon))/(2*epsilon)
    tangent_error=float(np.max(np.abs(v0-v1)));assert tangent_error<.01
    print(name,'encoding GIF preview',flush=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(out),'-filter_complex','fps=15,scale=640:640:flags=lanczos,split[a][b];[a]palettegen=stats_mode=full:max_colors=256[p];[b][p]paletteuse=dither=sierra2_4a','-loop','0',str(ROOT/(name+'-preview.gif'))],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','stream=width,height,nb_read_frames,r_frame_rate:format=duration','-of','json',str(out)]))
    assert probe['streams'][0]['width']==SIZE and int(probe['streams'][0]['nb_read_frames'])==FRAMES
    return {'name':name,'sema_keyframes':KEYS,'frames':FRAMES,'fps':FPS,'resolution':[SIZE,SIZE],
            'duration_seconds':float(probe['format']['duration']),'supersampling':[SUPER,SUPER],
            'endpoint_geometry_error':seam_error,'endpoint_tangent_error':tangent_error,
            'mean_pixel_change_at_half_cycle':movement,'seconds_to_render':round(time.time()-started,1),
            'mp4_bytes':out.stat().st_size}

if __name__=='__main__':
    reports=[]
    for name in ['address-lace','signed-braid','phase-coral']:
        reports.append(render(name))
        (ROOT/'high-fidelity-verification.json').write_text(json.dumps(reports,indent=2))
        print(name,'finished',flush=True)
