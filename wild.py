"""Wild one-off concepts, one per seed. python wild.py START COUNT [full]"""
import os, sys, math, random, colorsys, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy import ndimage as ndi
HERE=os.path.dirname(os.path.abspath(__file__))

def hsv(h,s,v): return tuple(int(c*255) for c in colorsys.hsv_to_rgb(h%1,s,v))
class C:
    def __init__(c,seed,full):
        c.r=random.Random(seed); c.g=np.random.default_rng(seed); c.W,c.H=(1800,3680) if full else (600,1226); c.k=c.W/1800
        c.yy,c.xx=np.mgrid[0:c.H,0:c.W].astype(np.float32)
    def noise(c,n,amp=1.):
        a=c.g.normal(0,1,(int(n*c.H/c.W)+3,n+3)).astype(np.float32); return np.asarray(Image.fromarray(a,"F").resize((c.W,c.H),Image.BICUBIC))*amp
    def photo(c,zoom=None,rot=None):
        p=Image.open(os.path.join(HERE,"plates/passiflora.png")).convert("RGB"); sc=(zoom or c.r.uniform(9,13))*c.k
        p=p.resize((int(p.width*sc),int(p.height*sc)),Image.LANCZOS).rotate(rot if rot is not None else c.r.uniform(0,360),Image.BICUBIC)
        can=Image.new("RGB",(c.W,c.H)); can.paste(p,(int(c.W/2-p.width/2),int(c.H/2-p.height/2))); return can
    def done(c,img,gr=.04):
        a=np.asarray(img,np.float32); n=c.g.normal(0,1,a.shape[:2])[...,None]; return Image.fromarray(np.clip(a*(1+gr*n),0,255).astype(np.uint8))
    def hue(c): return c.r.random()

def pixelsort(c):
    a=np.asarray(c.photo(),np.uint8).copy(); L=a.mean(2); thr=c.r.uniform(60,120)
    for y in range(c.H):
        row=a[y]; m=L[y]>thr; idx=np.flatnonzero(np.diff(np.r_[0,m.astype(int),0]))
        for s,e in zip(idx[::2],idx[1::2]):
            seg=row[s:e]; row[s:e]=seg[np.argsort(seg.mean(1))]
    im=Image.fromarray(a)
    return c.done(im.transpose(Image.ROTATE_90).resize((c.W,c.H)) if c.r.random()<.0 else im)
def rgbsplit(c):
    p=np.asarray(ImageOps.autocontrast(c.photo().convert("L")),np.float32); o=int(c.r.uniform(15,40)*c.k)
    cols=[hsv(c.hue(),1,1) for _ in range(3)]; out=np.zeros((c.H,c.W,3),np.float32)
    for i,(dx,dy) in enumerate([(-o,0),(0,o//2),(o,0)]):
        out+=np.roll(p,(dy,dx),(0,1))[...,None]/255*np.array(cols[i])
    return c.done(np.clip(out,0,255))
def aurora(c):
    cols=np.array([hsv(c.hue(),c.r.uniform(.4,.9),c.r.uniform(.5,1)) for _ in range(4)],np.float32)
    w=np.stack([np.exp(c.noise(2,1.6)) for _ in range(4)]); w/=w.sum(0); img=np.tensordot(w.transpose(1,2,0),cols,1)
    return c.done(img,.07)
def swiss(c):
    n=c.r.choice([4,5,6]); cell=c.W/n; rows=int(c.H/cell); bg=hsv(c.hue(),.1,.95); im=Image.new("RGB",(c.W,c.H),bg); d=ImageDraw.Draw(im)
    h0=c.hue(); skip=(c.r.randrange(n),c.r.randrange(rows))
    for j in range(rows):
        for i in range(n):
            if (i,j)==skip: continue
            col=hsv(h0+(i+j)*.04,.75,.8-.3*(j/rows)); m=cell*.08; d.ellipse([i*cell+m,j*cell+m,(i+1)*cell-m,(j+1)*cell-m],fill=col)
    return c.done(im)
def reaction(c):
    w,h=c.W//2,c.H//2; U=np.ones((h,w),np.float32); V=np.zeros((h,w),np.float32)
    for _ in range(30):
        x,y=c.r.randrange(w-20),c.r.randrange(h-20); V[y:y+12,x:x+12]=.5; U[y:y+12,x:x+12]=.25
    F,K=c.r.choice([(.037,.06),(.03,.062),(.025,.06),(.055,.062),(.042,.063)])
    lap=lambda Z: np.roll(Z,1,0)+np.roll(Z,-1,0)+np.roll(Z,1,1)+np.roll(Z,-1,1)-4*Z
    for _ in range(int(4000)):
        uvv=U*V*V; U+=.16*lap(U)-uvv+F*(1-U); V+=.08*lap(V)+uvv-(F+K)*V
    v=np.asarray(Image.fromarray(V).resize((c.W,c.H),Image.BICUBIC)); m=v>v.mean()+.02
    a,b=hsv(c.hue(),.5,.25),hsv(c.hue(),.35,.92); img=np.where(m[...,None],np.array(b,np.float32),np.array(a,np.float32)); return c.done(img)
def flow(c):
    bg=hsv(c.hue(),.3,.12); im=Image.new("RGB",(c.W,c.H),bg); d=ImageDraw.Draw(im); F=c.noise(3,math.pi*2)
    h0=c.hue()
    for _ in range(int(2500)):
        x,y=c.r.uniform(0,c.W),c.r.uniform(0,c.H); pts=[(x,y)]
        for _ in range(80):
            a=F[int(y)%c.H,int(x)%c.W]; x+=4*c.k*math.cos(a); y+=4*c.k*math.sin(a)
            if not(0<=x<c.W and 0<=y<c.H): break
            pts.append((x,y))
        if len(pts)>2: d.line(pts,fill=hsv(h0+c.r.uniform(-.06,.06),.6,c.r.uniform(.6,1)),width=max(1,int(2*c.k)))
    return c.done(im)
def stained(c):
    n=c.r.randint(40,120); pts=np.c_[c.g.uniform(0,c.W,n),c.g.uniform(0,c.H,n)]
    from scipy.spatial import cKDTree
    d,i=cKDTree(pts).query(np.c_[c.xx.ravel(),c.yy.ravel()],2); i0=i[:,0].reshape(c.H,c.W); edge=((d[:,1]-d[:,0])<5*c.k).reshape(c.H,c.W)
    h0=c.hue(); pal=np.array([hsv(h0+c.r.uniform(-.15,.15),c.r.uniform(.4,.9),c.r.uniform(.4,.95)) for _ in range(n)],np.float32)
    img=pal[i0]; img[edge]=(25,22,20); return c.done(img)
def truchet(c):
    t=c.r.uniform(80,180)*c.k; bg,fg=hsv(c.hue(),.4,.9),hsv(c.hue(),.8,.35); im=Image.new("RGB",(c.W,c.H),bg); d=ImageDraw.Draw(im); lw=int(t*c.r.uniform(.15,.35))
    for y in np.arange(0,c.H,t):
        for x in np.arange(0,c.W,t):
            if c.r.random()<.5: arcs=[((x-t/2,y-t/2,x+t/2,y+t/2),0,90),((x+t/2,y+t/2,x+1.5*t,y+1.5*t),180,270)]
            else: arcs=[((x+t/2,y-t/2,x+1.5*t,y+t/2),90,180),((x-t/2,y+t/2,x+t/2,y+1.5*t),270,360)]
            for b,a0,a1 in arcs: d.arc(b,a0,a1,fill=fg,width=lw)
    return c.done(im)
def slitscan(c):
    p=np.asarray(c.photo(),np.float32); col=c.r.randrange(c.W//3,2*c.W//3)
    band=p[:,col-int(40*c.k):col+int(40*c.k)]; img=np.asarray(Image.fromarray(band.astype(np.uint8)).resize((c.W,c.H),Image.BICUBIC),np.float32)
    return c.done(img)
def kaleido(c):
    p=c.photo().crop((0,0,c.W//2,c.H//2)); q=Image.new("RGB",(c.W,c.H)); a=p; b=ImageOps.mirror(p)
    q.paste(a,(0,0)); q.paste(b,(c.W//2,0)); q.paste(ImageOps.flip(a),(0,c.H//2)); q.paste(ImageOps.flip(b),(c.W//2,c.H//2)); return c.done(q)
def thermal(c):
    import matplotlib; cm=matplotlib.colormaps[c.r.choice(["inferno","magma","plasma","viridis","twilight","cividis"])]
    L=np.asarray(c.photo().convert("L").filter(ImageFilter.GaussianBlur(2*c.k)),np.float32)/255; return c.done(cm(L)[...,:3]*255)
def xerox(c):
    L=np.asarray(ImageOps.autocontrast(c.photo().convert("L")),np.float32); L+=c.noise(80,25)+c.g.normal(0,18,L.shape); th=c.r.uniform(90,140)
    img=np.where((L>th)[...,None],np.array([235,232,225],np.float32),np.array([20,20,22],np.float32)); return c.done(img,.02)
def albers(c):
    cols=[hsv(c.hue(),c.r.uniform(.3,.8),c.r.uniform(.3,.95)) for _ in range(4)]; im=Image.new("RGB",(c.W,c.H),cols[0]); d=ImageDraw.Draw(im)
    for i,col in enumerate(cols[1:],1):
        m=c.W*.12*i; d.rectangle([m,m*1.6+i*c.H*.04,c.W-m,c.H-m*.9],fill=col)
    return c.done(im)
def dotfade(c):
    bg,fg=hsv(c.hue(),.2,.95),hsv(c.hue(),.8,.45); im=Image.new("RGB",(c.W,c.H),bg); d=ImageDraw.Draw(im); cell=c.r.uniform(30,60)*c.k
    for y in np.arange(cell/2,c.H,cell):
        for x in np.arange(cell/2,c.W,cell):
            v=(y/c.H)**c.r.choice([.6,1,2])*(1+.3*math.sin(x/c.W*6)); r=cell*.48*min(1,v); d.ellipse([x-r,y-r,x+r,y+r],fill=fg)
    return c.done(im)
def packing(c):
    bg=hsv(c.hue(),.3,.15); im=Image.new("RGB",(c.W,c.H),bg); d=ImageDraw.Draw(im); circ=[]; h0=c.hue()
    for _ in range(6000):
        x,y=c.r.uniform(0,c.W),c.r.uniform(0,c.H); r=min([math.hypot(x-a,y-b)-rr for a,b,rr in circ]+[300*c.k])-2*c.k
        if r>4*c.k: circ.append((x,y,r)); d.ellipse([x-r,y-r,x+r,y+r],fill=hsv(h0+c.r.uniform(-.08,.08),.55,c.r.uniform(.5,.95)))
        if len(circ)>500: break
    return c.done(im)
def interference(c):
    s=[(c.r.uniform(0,c.W),c.r.uniform(0,c.H)) for _ in range(c.r.randint(2,3))]; per=c.r.uniform(40,90)*c.k
    v=sum(np.sin(np.hypot(c.xx-x,c.yy-y)/per*2*np.pi) for x,y in s); q=np.digitize(v,[-1,0,1]); pal=np.array([hsv(c.hue(),.6,b) for b in (.2,.45,.7,.95)],np.float32)
    return c.done(pal[q])
def lsystem(c):
    bg,fg=hsv(c.hue(),.25,.92),hsv(c.hue(),.7,.3); im=Image.new("RGB",(c.W,c.H),bg); d=ImageDraw.Draw(im)
    s="X"; rules={"X":"F+[[X]-X]-F[-FX]+X","F":"FF"}
    for _ in range(6): s="".join(rules.get(ch,ch) for ch in s)
    x,y,a=c.W/2,c.H,-90.; st=[]; L=c.r.uniform(4,7)*c.k; da=c.r.uniform(20,28)
    for ch in s:
        if ch=="F": nx,ny=x+L*math.cos(math.radians(a)),y+L*math.sin(math.radians(a)); d.line([(x,y),(nx,ny)],fill=fg,width=max(1,int(2*c.k))); x,y=nx,ny
        elif ch=="+": a+=da+c.r.gauss(0,3)
        elif ch=="-": a-=da+c.r.gauss(0,3)
        elif ch=="[": st.append((x,y,a))
        elif ch=="]": x,y,a=st.pop()
    return c.done(im)
def mosaic(c):
    t=int(c.r.uniform(60,160)*c.k); p=c.photo().resize((c.W//t+1,c.H//t+1),Image.BOX).resize((c.W,c.H),Image.NEAREST)
    a=np.asarray(p,np.float32); a[(c.yy%t<2*c.k)|(c.xx%t<2*c.k)]=240; return c.done(a)
def stacked(c):
    cols=[hsv(c.hue(),c.r.uniform(.5,.9),c.r.uniform(.3,.95)) for _ in range(5)]; im=Image.new("RGB",(c.W,c.H),cols[0]); d=ImageDraw.Draw(im); R=c.W/2
    for j,y in enumerate(np.arange(0,c.H+R,R)):
        for i in (0,1):
            col=cols[1+(i+j)%4]; d.pieslice([i*R-R*(i==0)*0,y-R,i*R+R*2*(1-i)+R*(i==1),y+R],0 if (i+j)%2 else 180,180 if (i+j)%2 else 360,fill=col)
    return c.done(im)
def stringart(c):
    bg,fg=hsv(c.hue(),.4,.1),hsv(c.hue(),.6,.95); im=Image.new("RGB",(c.W,c.H),bg); d=ImageDraw.Draw(im); n=c.r.randint(80,160)
    per=[(c.W*t,0) for t in np.linspace(0,1,n)]+[(c.W,c.H*t) for t in np.linspace(0,1,n*2)]+[(c.W*(1-t),c.H) for t in np.linspace(0,1,n)]+[(0,c.H*(1-t)) for t in np.linspace(0,1,n*2)]
    N=len(per); k=c.r.randint(N//5,N//2)
    for i in range(0,N,2): d.line([per[i],per[(i*c.r.choice([1,2,3])+k)%N]],fill=fg,width=1)
    return c.done(im)
def sunset(c):
    f=c.yy/c.H+c.noise(2,.12); q=np.clip((f*c.r.randint(5,9)).astype(int),0,9); h0=c.hue()
    pal=np.array([hsv(h0+i*.04,.7,.95-i*.08) for i in range(10)],np.float32); return c.done(pal[q])
def attractor(c):
    a,b,cc,dd=[c.r.uniform(-2,2) for _ in range(4)]; x=y=.1; N=int(1.5e6*c.k); xs=np.empty(N); ys=np.empty(N)
    import math as m
    X=np.zeros(200000); Y=np.zeros(200000); x=np.full(200000,.1)+np.random.default_rng(1).normal(0,.1,200000); y=x.copy()
    H2=np.zeros((c.H,c.W))
    for _ in range(40):
        x,y=np.sin(a*y)+cc*np.cos(a*x),np.sin(b*x)+dd*np.cos(b*y)
        h,_,_=np.histogram2d(y,x,bins=(c.H,c.W),range=[[-3,3],[-1.6,1.6]]); H2+=h
    v=np.log1p(H2); v/=v.max()+1e-9; bg=np.array(hsv(c.hue(),.4,.08),np.float32); fg=np.array(hsv(c.hue(),.5,1),np.float32)
    return c.done(bg*(1-v[...,None])+fg*v[...,None])

IDEAS=[pixelsort,rgbsplit,aurora,swiss,reaction,flow,stained,truchet,slitscan,kaleido,thermal,xerox,albers,dotfade,packing,interference,lsystem,mosaic,stacked,stringart,sunset,attractor]
def make(seed,full=False): f=IDEAS[seed%len(IDEAS)]; return f(C(seed,full)),f.__name__
if __name__=="__main__":
    s0,c=int(sys.argv[1]),int(sys.argv[2]); full=len(sys.argv)>3; out=os.path.join(HERE,"wild"); os.makedirs(out,exist_ok=True)
    sh=Image.new("RGB",(6*330+10,((c+5)//6)*700+10),"#2a2a2a"); d=ImageDraw.Draw(sh)
    for i,sd in enumerate(range(s0,s0+c)):
        im,name=make(sd,full)
        if full: im.save(os.path.join(out,f"seed{sd:03d}.png"))
        t=im.resize((300,613),Image.LANCZOS); mk=Image.new("L",t.size,0); ImageDraw.Draw(mk).rounded_rectangle([0,0,299,612],40,fill=255)
        x,y=20+(i%6)*330,20+(i//6)*700; sh.paste(t,(x,y),mk); d.text((x,y+625),f"{sd}  {name}",fill=(220,220,220),font_size=20)
    sh.save(f"/tmp/work/wild_sheet_{s0}.png"); print("ok")
