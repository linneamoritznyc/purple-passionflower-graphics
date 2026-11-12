"""Seeded case generator. python gen.py START COUNT [full]"""
import sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os as _o; sys.path.insert(0,_o.path.dirname(_o.path.abspath(__file__))); import dots as Dm

PAL = [(172,186,160),(34,55,31),(107,76,122),(204,168,136),(70,40,38),(240,236,228),(48,108,46),(74,126,178),
       (104,168,108),(200,182,226),(58,34,74),(214,226,140),(88,28,52),(176,172,150),(26,44,82),(150,196,232),
       (91,107,46),(18,16,20),(196,92,40),(236,214,170)]
def lumi(c): return .3*c[0]+.59*c[1]+.11*c[2]
def pick_pal(g,n):
    while True:
        cs=[PAL[i] for i in g.choice(len(PAL),n,replace=False)]
        L=sorted(lumi(c) for c in cs)
        if L[-1]-L[0]>70 and all(L[i+1]-L[i]>22 for i in range(n-1)): return cs

class G:
    def __init__(s,seed,w,h):
        s.g=np.random.default_rng(seed); s.w,s.h=w,h; s.k=w/1800
        s.yy,s.xx=np.mgrid[0:h,0:w].astype(np.float32)
    def noise(s,n,amp=1.0):
        r=s.g.normal(0,1,(int(n*s.h/s.w)+3,n+3)).astype(np.float32)
        return np.asarray(Image.fromarray(r,"F").resize((s.w,s.h),Image.BICUBIC))*amp
    def fbm(s,n,oct=3):
        return sum(s.noise(n*2**i,.5**i) for i in range(oct))

def ikat_h(G,m,reach=90,amt=.4):
    r=max(2,int(reach*G.k)); c=np.cumsum(np.pad(m.astype(np.float32),((0,0),(r,r)),mode="edge"),1)
    b=(c[:,2*r:]-c[:,:-2*r])/(2*r); rows=G.g.uniform(-1,1,(G.h//max(1,int(4*G.k))+2,1)).repeat(max(1,int(4*G.k)),0)[:G.h]
    return b>.5+amt*rows

# ---------- families: each returns an index map (int) into palette, and palette size
def f_zigzag(G):
    f=G.fbm(G.g.integers(2,4),2); p=G.g.uniform(14,30)*G.k; a=G.g.uniform(.25,.6)
    tri=np.abs(((G.xx/p+G.noise(8,.3))%1)-.5)*2-.5
    return (f+a*tri*G.g.choice([1,-1])>0).astype(int),2
def f_contour(G):
    per=G.g.uniform(14,26)*G.k; ang=G.g.uniform(0,np.pi)
    u=(G.yy*np.cos(ang)+G.xx*np.sin(ang)+G.noise(2,G.g.uniform(120,260)*G.k)+G.noise(4,50*G.k))/per
    t=.36+G.noise(3,.1); f=np.abs(u-np.round(u)); return (f<t*.5).astype(int),2
def f_hikat(G):
    f=G.fbm(G.g.integers(1,4),2); return ikat_h(G,f>G.g.uniform(-.3,.3)).astype(int),2
def f_honey(G):
    v=np.clip(G.fbm(2,3)*.6+.5,0,1); cell=G.g.uniform(12,24)*G.k; out=Image.new("L",(G.w*2,G.h*2),0); d=ImageDraw.Draw(out)
    y,row=cell/2,0
    while y<G.h:
        x=cell/2+(cell/2 if row%2 else 0)
        while x<G.w:
            q=v[int(y),int(x)]
            if q>.08: r=cell*.5*q**.6*2; d.ellipse([x*2-r,y*2-r,x*2+r,y*2+r],fill=255)
            x+=cell
        y+=cell*.866; row+=1
    return (np.asarray(out.resize((G.w,G.h),Image.BOX))>127).astype(int),2
def f_levels(G):
    f=G.fbm(G.g.integers(1,3),3); q=np.quantile(f,[.33,.66])
    idx=(f>q[0]).astype(int)+(f>q[1]); 
    if G.g.random()<.6:
        a=ikat_h(G,idx>=1); b=ikat_h(G,idx>=2); idx=a.astype(int)+(a&b)
    return idx,3
def f_zebra(G):
    per=G.g.uniform(260,520)*G.k; ang=G.g.uniform(0,np.pi)
    u=(G.yy*np.cos(ang)+G.xx*np.sin(ang)+G.noise(2,G.g.uniform(200,500)*G.k))/per
    return (np.sin(u*2*np.pi)+G.noise(3,.4)>0).astype(int),2
def f_corona(G):
    cx=G.g.uniform(-.2,1.2)*G.w; cy=G.g.uniform(.1,.9)*G.h; n=G.g.integers(40,110)
    a=np.arctan2(G.yy-cy,G.xx-cx); r=np.hypot(G.yy-cy,G.xx-cx); R=G.g.uniform(250,700)*G.k
    ray=(np.cos(a*n)>G.g.uniform(.2,.6))&(r>R*1.15)&(r<R*G.g.uniform(2,4))
    return np.where(r<R,2,ray.astype(int)),3
def f_flower(G):
    a=Dm.place(Image.open(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),"plates/passiflora.png")).convert("RGB"),1,0,(.5,.5))  # placeholder size
    ph=Image.open(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),"plates/passiflora.png")).convert("RGB")
    sc=G.g.uniform(9.5,12)*G.k; ph=ph.resize((int(ph.width*sc),int(ph.height*sc)),Image.LANCZOS).rotate(G.g.uniform(0,360),Image.BICUBIC)
    can=Image.new("RGB",(G.w,G.h)); can.paste(ph,(int(G.w/2-ph.width/2),int(G.h/2-ph.height/2)))
    m=Dm.mask(np.asarray(can,float)/255); m=np.asarray(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6*G.k+1)))>90
    return ikat_h(G,m).astype(int) if G.g.random()<.5 else m.astype(int),2
def f_gingham(G):
    per=G.g.uniform(120,300)*G.k; wx=G.noise(2,G.g.uniform(60,200)*G.k); wy=G.noise(2,G.g.uniform(60,200)*G.k)
    a=np.sin((G.xx+wx)/per*np.pi)>0; b=np.sin((G.yy+wy)/per*np.pi)>0; return a.astype(int)+b.astype(int),3
def f_stipple(G):
    k=np.clip(G.fbm(2,2)*.7+.5,0,1); return (k>G.g.random((G.h,G.w))).astype(int),2
def f_linetone(G):
    per=G.g.uniform(16,34)*G.k; v=np.clip(G.fbm(2,2)*.6+.5,.05,.95)
    u=(G.yy+G.noise(2,G.g.uniform(0,150)*G.k))/per; f=np.abs(u-np.round(u))
    return (f<v*.5).astype(int),2
def f_pebbles(G):
    n=G.g.integers(14,40); pts=np.c_[G.g.uniform(0,G.w,n),G.g.uniform(0,G.h,n)]
    d=np.sort(np.stack([np.hypot(G.xx-px,G.yy-py) for px,py in pts]),0)
    gap=(d[1]-d[0])<G.g.uniform(20,60)*G.k
    owner=np.argmin(np.stack([np.hypot(G.xx-px,G.yy-py) for px,py in pts]),0)
    return np.where(gap,0,1+(owner%2)),3
def f_agate(G):
    cx,cy=G.g.uniform(0,G.w),G.g.uniform(0,G.h); r=np.hypot(G.xx-cx,G.yy-cy)+G.noise(2,G.g.uniform(150,400)*G.k)
    per=G.g.uniform(40,120)*G.k; return ((np.sin(r/per*2*np.pi)+G.noise(4,.3))>G.g.uniform(-.3,.5)).astype(int),2
def f_fringe(G):
    f=G.fbm(1,2); m=f>0; e=np.asarray(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40*G.k)),float)/255
    p=G.g.uniform(18,34)*G.k; teeth=(np.abs(((G.xx+G.yy*G.g.uniform(-.5,.5))/p)%1-.5)<.18)&(e>.15)&(e<.5)
    return (m|teeth).astype(int),2

FAM=[f_zigzag,f_contour,f_hikat,f_honey,f_levels,f_zebra,f_corona,f_flower,f_gingham,f_stipple,f_linetone,f_pebbles,f_agate,f_fringe]

def make(seed,w=600,h=1226,_force=None):
    if (w,h)!=(600,1226) and _force is None: _force=make(seed,_force="get")
    G0=G(seed,w,h); fam=FAM[seed%len(FAM)]; idx,n=fam(G0); pal=pick_pal(G0.g,n); gr=G0.g.uniform(.02,.09)
    if _force=="get": return pal,gr
    if _force: pal,gr=_force
    img=np.array(pal,np.float32)[np.clip(idx,0,n-1)]; nz=np.random.default_rng(seed).normal(0,1,(h,w))[...,None]
    return Image.fromarray(np.clip(img*(1+gr*nz),0,255).astype(np.uint8)),fam.__name__[2:]

if __name__=="__main__":
    s0,c=int(sys.argv[1]),int(sys.argv[2]); full=len(sys.argv)>3
    os.makedirs("seeds",exist_ok=True)
    if full:
        for s in range(s0,s0+c): make(s,1800,3680)[0].save(f"seeds/seed{s:03d}.png")
        sys.exit()
    cols=6; rows=(c+cols-1)//cols; sheet=Image.new("RGB",(cols*330+10,rows*700+10),"#f4f1ec"); d=ImageDraw.Draw(sheet)
    fnt=ImageFont.load_default(size=22)
    for i,s in enumerate(range(s0,s0+c)):
        im,name=make(s); im=im.resize((300,613),Image.LANCZOS)
        mk=Image.new("L",im.size,0); ImageDraw.Draw(mk).rounded_rectangle([0,0,299,612],40,fill=255)
        x,y=20+(i%cols)*330,20+(i//cols)*700; sheet.paste(im,(x,y),mk)
        d.text((x,y+625),f"{s}",fill=(60,60,60),font=fnt)
    sheet.save(f"seeds_{s0}.png"); print("ok")
