"""Seeded cases in many print and textile styles. python stylegen.py START COUNT [full]"""
import os, sys, math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import ikatgen as IG

def hx(h): return np.array([int(h[i:i+2],16) for i in (0,2,4)],np.float32)
INK=["22371F","6B4C7A","156826","3780B8","4F3433","3A2248","561C34","1A2C52","C45C28","59A66C","183E6E","8A2F2A"]
PAPER=["F4F1EA","A8B49A","C8B6E2","D6E28C","C89B7B","B0AC96","E9DCC4","96C4E8"]

class S:
    def __init__(s,seed,full):
        s.r=random.Random(seed); s.g=np.random.default_rng(seed); s.W,s.H=(1800,3680) if full else (600,1226); s.k=s.W/1800
        s.yy,s.xx=np.mgrid[0:s.H,0:s.W].astype(np.float32)
    def noise(s,n,amp=1.):
        a=s.g.normal(0,1,(int(n*s.H/s.W)+3,n+3)).astype(np.float32)
        return np.asarray(Image.fromarray(a,"F").resize((s.W,s.H),Image.BICUBIC))*amp
    def shape(s,pool=None):
        m=Image.new("L",(1800,3680),0); d=ImageDraw.Draw(m)
        f=s.r.choice(pool or IG.SHAPES)
        f(d,s.r,m) if f is IG.s_flower else f(d,s.r)
        if s.r.random()<.3: m=m.transpose(Image.FLIP_LEFT_RIGHT)
        z=getattr(s,"zoom",1.0)
        if z!=1.0:
            sm=m.resize((int(1800*z),int(3680*z)),Image.BILINEAR); m=Image.new("L",(1800,3680),0); m.paste(sm,((1800-sm.width)//2,(3680-sm.height)//2))
        return np.asarray(m.resize((s.W,s.H),Image.BILINEAR))>127
    def grain(s,img,a=.06):
        n=s.g.normal(0,1,img.shape[:2])[...,None]; return Image.fromarray(np.clip(img*(1+a*n),0,255).astype(np.uint8))
    def flat(s,bg): img=np.empty((s.H,s.W,3),np.float32); img[:]=bg; return img
    def ink(s): return hx(s.r.choice(INK))
    def paper(s): return hx(s.r.choice(PAPER))

def linocut(s):
    M=s.shape(); bg,fg=s.paper(),s.ink(); img=s.flat(bg)
    d=ndi.distance_transform_edt(M)+ndi.distance_transform_edt(~M)*-1
    per=s.r.uniform(22,40)*s.k; lines=np.abs(((d+s.noise(4,6*s.k))/per)%1-.5)<s.r.uniform(.12,.22)
    gouge=(np.abs(((s.yy*.3+s.xx+s.noise(3,40*s.k))/(per*.8))%1-.5)<.08)&(s.g.random((s.H,s.W))<.0)  # reserved
    ink=(M&~(lines&(d>per*.6)))|((~M)&lines&(d>-per*3.2)&(d<-per*.5))
    img[ink]=fg; return s.grain(img,.07)
def riso(s):
    a,b=s.shape(),s.shape(); bg=hx("F4F1EA"); c1,c2=s.ink(),s.ink(); img=s.flat(bg)
    off=int(s.r.uniform(6,16)*s.k); b=np.roll(b,(off,-off),(0,1))
    def tone(m): return m&(s.g.random(m.shape)<s.r.uniform(.8,.95))
    t1,t2=tone(a),tone(b); img[t1]*=c1/255; img[t2]*=c2/255; return s.grain(img,.04)
def stitch(s):
    M=s.shape(); bg,fg=s.paper(),s.ink(); im=Image.fromarray(s.flat(bg).astype(np.uint8)); d=ImageDraw.Draw(im)
    step=s.r.uniform(9,16)*s.k; ln=step*s.r.uniform(2.5,4); ang=s.r.uniform(0,math.pi); dark=tuple(int(v*.7) for v in fg); lite=tuple(int(min(255,v*1.25)) for v in fg)
    for y in np.arange(0,s.H,step):
        for x in np.arange((y/step%2)*step/2,s.W,step):
            if M[int(y),int(x)]:
                a=ang+s.r.gauss(0,.08); dx,dy=ln/2*math.cos(a),ln/2*math.sin(a); w=max(1,int(step*.55))
                d.line([(x-dx+1,y-dy+1),(x+dx+1,y+dy+1)],fill=dark,width=w); d.line([(x-dx,y-dy),(x+dx,y+dy)],fill=tuple(int(v) for v in fg),width=w)
                d.line([(x-dx*.6,y-dy*.6-1),(x+dx*.2,y+dy*.2-1)],fill=lite,width=max(1,w//3))
    return s.grain(np.asarray(im,np.float32),.04)
def torn(s):
    M=s.shape(); bg,fg=s.paper(),s.ink(); img=s.flat(bg)
    d=ndi.distance_transform_edt(M)-ndi.distance_transform_edt(~M); rough=s.noise(60,5*s.k)+s.noise(200,2*s.k)
    core=(d+rough)>0; fiber=((d+rough+s.r.uniform(8,16)*s.k)>0)&~core
    img[fiber]=hx("FBF8F2"); img[core]=fg
    sh=np.roll(core|fiber,(int(6*s.k),int(4*s.k)),(0,1))&~(core|fiber); img[sh]*=.82; return s.grain(img,.05)
def cyanotype(s):
    M=s.shape([IG.s_flower,IG.s_roots,IG.s_tendril,IG.s_leaf,IG.s_corona]); blue=hx("1B4A86"); img=s.flat(blue)
    expo=np.clip(s.noise(5,.15)+s.noise(30,.05),-.3,.3); img*=(1+expo)[...,None]
    soft=ndi.gaussian_filter(M.astype(np.float32),3*s.k+.5); white=hx("E8EEF2")
    img=img*(1-soft[...,None])+white*soft[...,None]*(1+s.noise(40,.04))[...,None]; return s.grain(img,.05)
def batik(s):
    M=s.shape(); bg,fg=s.paper(),s.ink(); img=s.flat(bg); img[M]=fg
    n=s.r.randint(60,160); pts=np.c_[s.g.uniform(0,s.W,n),s.g.uniform(0,s.H,n)]
    from scipy.spatial import cKDTree
    q=np.c_[s.xx.ravel()+s.noise(20,6*s.k).ravel(),s.yy.ravel()]; dd,_=cKDTree(pts).query(q,2)
    crack=((dd[:,1]-dd[:,0])<s.r.uniform(1.5,3)*s.k).reshape(s.H,s.W)
    img[crack]=fg*.75 if s.r.random()<.5 else fg; img[crack&M]=bg*.9; return s.grain(img,.05)
def shibori(s):
    bg,fg=hx("F4F1EA"),s.ink(); img=s.flat(bg); kind=s.r.choice(["rad","lin","grid"])
    if kind=="rad":
        cx,cy=s.r.uniform(0,s.W),s.r.uniform(0,s.H); u=np.hypot(s.xx-cx,s.yy-cy)/(s.r.uniform(80,160)*s.k)
    elif kind=="lin": u=(s.yy+s.noise(2,60*s.k))/(s.r.uniform(120,240)*s.k)
    else: u=np.minimum(np.abs(((s.xx/(200*s.k))%1)-.5),np.abs(((s.yy/(200*s.k))%1)-.5))*4
    v=np.abs((u%1)-.5)*2; t=.45+s.noise(40,.12)+s.noise(8,.1); dye=v>t
    soft=ndi.gaussian_filter(dye.astype(np.float32),2*s.k+.3)*(.8+s.noise(30,.15)); soft=np.clip(soft,0,1)
    img=img*(1-soft[...,None])+fg*soft[...,None]; return s.grain(img,.05)
def marble(s):
    cs=[s.paper(),s.ink(),s.ink()]; img=s.flat(cs[0]); x,y=s.xx.copy(),s.yy.copy()
    for _ in range(s.r.randint(3,7)):
        cx,cy,R=s.r.uniform(0,s.W),s.r.uniform(0,s.H),s.r.uniform(200,600)*s.k
        r2=(x-cx)**2+(y-cy)**2; f=np.sqrt(np.maximum(0,1-R*R/np.maximum(r2,1))); x=cx+(x-cx)*f; y=cy+(y-cy)*f
    rings=np.hypot(x-s.W/2,y-s.H/2)
    comb=s.r.uniform(60,160)*s.k*np.sin(s.xx/(s.r.uniform(80,200)*s.k)); rings=rings+comb
    band=((rings/(s.r.uniform(30,70)*s.k))%3).astype(int); img=np.array(cs,np.float32)[band]; return s.grain(img,.04)
def spray(s):
    M=s.shape(); bg,fg=s.paper(),s.ink(); img=s.flat(bg)
    soft=np.clip(ndi.gaussian_filter(M.astype(np.float32),s.r.uniform(20,60)*s.k)*1.6,0,1); hit=s.g.random((s.H,s.W))<soft**1.5
    img[hit|M]=fg; return s.grain(img,.05)
def knit(s):
    M=s.shape(); a,b=s.paper(),s.ink(); cols=s.r.randint(36,60); cw=s.W/cols; rows=int(s.H/(cw*.8))
    small=np.asarray(Image.fromarray(M.astype(np.uint8)*255).resize((cols,rows),Image.BOX))>127
    im=Image.new("RGB",(s.W,s.H),tuple(int(v*.6) for v in a)); d=ImageDraw.Draw(im)
    for j in range(rows):
        for i in range(cols):
            c=b if small[j,i] else a; x,y=i*cw,j*cw*.8; sh=tuple(int(v*.8) for v in c); c=tuple(int(v) for v in c)
            for side in (-1,1):
                pts=[(x+cw/2,y+cw*.95),(x+cw/2+side*cw*.48,y+cw*.15),(x+cw/2+side*cw*.3,y),(x+cw/2,y+cw*.6)]
                d.polygon(pts,fill=c,outline=sh)
    return s.grain(np.asarray(im,np.float32),.04)
def topo(s):
    ph=Image.open(os.path.join(HERE,"plates/passiflora.png")).convert("L"); sc=s.r.uniform(9,12)*s.k
    ph=ph.resize((int(ph.width*sc),int(ph.height*sc)),Image.LANCZOS).rotate(s.r.uniform(0,360),Image.BICUBIC)
    can=Image.new("L",(s.W,s.H),0); can.paste(ph,(int(s.W/2-ph.width/2),int(s.H/2-ph.height/2)))
    h=ndi.gaussian_filter(np.asarray(can,np.float32),s.r.uniform(4,9)*s.k)/255
    lv=s.r.randint(10,22); f=np.abs((h*lv)%1-.5); bg,fg=s.paper(),s.ink(); img=s.flat(bg)
    gy,gx=np.gradient(h*lv); gm=np.hypot(gx,gy)+1e-4; img[f*2/gm<1.6*s.k*2]=fg
    if s.r.random()<.5: img[(h*lv%2)>1]=img[(h*lv%2)>1]*.0+(fg*.25+bg*.75)
    return s.grain(img,.05)
def moire(s):
    M=s.shape(); bg,fg=s.paper(),s.ink(); img=s.flat(bg); p=s.r.uniform(30,50)*s.k; a1=s.r.uniform(0,math.pi); a2=a1+s.r.uniform(.04,.15)
    l1=np.abs(((s.xx*math.cos(a1)+s.yy*math.sin(a1))/p)%1-.5)<.2; l2=np.abs(((s.xx*math.cos(a2)+s.yy*math.sin(a2)+s.noise(2,30*s.k))/p)%1-.5)<.2
    img[np.where(M,l2,l1)]=fg; return s.grain(img,.04)
def woodgrain(s):
    bg,fg=s.paper(),s.ink(); img=s.flat(bg); cx=s.r.uniform(-.5,1.5)*s.W
    u=(np.hypot((s.xx-cx)*s.r.uniform(1,3),s.yy*.15)+s.noise(3,s.r.uniform(80,200)*s.k)+s.noise(6,4*s.k))/(s.r.uniform(45,80)*s.k)
    img[np.abs(u%1-.5)<s.r.uniform(.1,.25)]=fg; return s.grain(img,.06)


def tear(s,M,fg,img,fiber=hx("FBF8F2")):
    d=ndi.distance_transform_edt(M)-ndi.distance_transform_edt(~M); rough=s.noise(60,5*s.k)+s.noise(200,2*s.k)
    core=(d+rough)>0; fb=((d+rough+s.r.uniform(8,16)*s.k)>0)&~core
    sh=np.roll(core|fb,(int(6*s.k),int(4*s.k)),(0,1))&~(core|fb); img[sh]*=.82; img[fb]=fiber; img[core]=fg; return img
def collage(s):
    img=s.flat(s.paper())
    for _ in range(s.r.randint(2,3)): img=tear(s,s.shape(),s.ink() if s.r.random()<.7 else s.paper(),img)
    return s.grain(img,.05)
def flowermask(s,thr=.4):
    ph=Image.open(os.path.join(HERE,"plates/passiflora.png")).convert("RGB"); sc=s.r.uniform(9.5,12.5)*s.k
    ph=ph.resize((int(ph.width*sc),int(ph.height*sc)),Image.LANCZOS).rotate(s.r.uniform(0,360),Image.BICUBIC)
    can=Image.new("RGB",(s.W,s.H)); can.paste(ph,(int(s.W/2-ph.width/2),int(s.H/2-ph.height/2)))
    a=np.asarray(can,np.float32)/255; lum=.3*a[...,0]+.59*a[...,1]+.11*a[...,2]
    lum[(a[...,1]>a[...,0])&(a[...,1]>a[...,2])&(lum<.45)]=0; return lum
def jacquard(s):
    lum=flowermask(s); a,b=s.paper(),s.ink(); M=ndi.gaussian_filter(lum,4*s.k)>s.r.uniform(.3,.45)
    s2=S.__new__(S); s2.__dict__.update(s.__dict__); s2.shape=lambda pool=None:M; return knit(s2)
def halftone(s):
    lum=ndi.gaussian_filter(flowermask(s),3*s.k); bg,fg=s.paper(),s.ink(); im=Image.new("RGB",(s.W,s.H),tuple(int(v) for v in bg)); d=ImageDraw.Draw(im)
    cell=s.r.uniform(18,34)*s.k; ang=math.radians(s.r.choice([0,15,45])); ca,sa=math.cos(ang),math.sin(ang); R=int(max(s.W,s.H)*.8)
    for i in np.arange(-R,R,cell):
        for j in np.arange(-R,R,cell):
            x=s.W/2+i*ca-j*sa; y=s.H/2+i*sa+j*ca
            if 0<=x<s.W and 0<=y<s.H:
                v=lum[int(y),int(x)]
                if v>.05: r=cell*.62*v**.7; d.ellipse([x-r,y-r,x+r,y+r],fill=tuple(int(c) for c in fg))
    return s.grain(np.asarray(im,np.float32),.05)
def rug(s):
    M=s.shape(); bg,fg=s.paper(),s.ink(); im=Image.fromarray(s.flat(bg*.85).astype(np.uint8)); d=ImageDraw.Draw(im)
    n=int(s.W*s.H/(14*s.k+2)**2*1.6); ys=s.g.uniform(0,s.H,n); xs=s.g.uniform(0,s.W,n); L=s.r.uniform(8,16)*s.k
    for x,y in zip(xs,ys):
        c=fg if M[int(y),int(x)] else bg; t=s.g.uniform(.8,1.15); a=s.g.uniform(0,6.283)
        d.line([(x,y),(x+L*math.cos(a),y+L*math.sin(a))],fill=tuple(int(min(255,v*t)) for v in c),width=max(2,int(5*s.k)))
    return s.grain(np.asarray(im,np.float32),.03)

STYLES=[linocut,riso,stitch,torn,cyanotype,batik,shibori,marble,spray,knit,topo,moire,woodgrain]
STYLES_V1=list(STYLES); NEW=[collage,jacquard,halftone,rug,torn,knit,moire]
def make(seed,full=False,zoom=1.0):
    st=STYLES[seed%len(STYLES)] if seed<=26 else (STYLES+NEW)[seed%len(STYLES+NEW)]; o=S(seed,full); o.zoom=zoom; return st(o),st.__name__

if __name__=="__main__":
    s0,c=int(sys.argv[1]),int(sys.argv[2]); full=len(sys.argv)>3; out=os.path.join(HERE,"styles"); os.makedirs(out,exist_ok=True)
    sh=Image.new("RGB",(6*330+10,((c+5)//6)*700+10),"#2a2a2a"); d=ImageDraw.Draw(sh)
    for i,sd in enumerate(range(s0,s0+c)):
        im,name=make(sd,full)
        if full: im.save(os.path.join(out,f"seed{sd:03d}.png"))
        t=im.resize((300,613),Image.LANCZOS); mk=Image.new("L",t.size,0); ImageDraw.Draw(mk).rounded_rectangle([0,0,299,612],40,fill=255)
        x,y=20+(i%6)*330,20+(i//6)*700; sh.paste(t,(x,y),mk); d.text((x,y+625),f"{sd}  {name}",fill=(220,220,220),font_size=20)
    sh.save(f"/tmp/work/style_sheet_{s0}.png"); print("ok")
