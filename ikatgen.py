"""Seeded two-colour ikat cases. python ikatgen.py START COUNT -> ikat/seedNNN.png + ikat_sheet_START.png"""
import os, sys, math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE=os.path.dirname(os.path.abspath(__file__))
W,H=1800,3680
def hx(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))

def ikat(m,seed,amp=7,streaks=1400):
    r=np.random.default_rng(seed); A=(np.asarray(m)>127)
    off=np.zeros(H,int); y=0
    while y<H:
        run=r.integers(2,10); off[y:y+run]=r.integers(-amp,amp+1); y+=run
    B=np.zeros_like(A)
    for y in range(H):
        o=off[y]
        if o>0: B[y,o:]=A[y,:-o]
        elif o<0: B[y,:o]=A[y,-o:]
        else: B[y]=A[y]
    L=B[:,:-1]&~B[:,1:]; R=~B[:,:-1]&B[:,1:]
    ys,xs=np.nonzero(L|R)
    if len(ys):
        for k in r.choice(len(ys),min(streaks,len(ys)),replace=False):
            y,x=ys[k],xs[k]; ln=int(r.integers(20,160)); th=int(r.integers(1,5)); right=L[y,x]
            seg=np.arange(ln); keep=r.random(ln)>np.linspace(0,0.9,ln)
            cols=((x+1+seg) if right else (x-seg))[keep]; cols=cols[(cols>=0)&(cols<W)]
            B[y:y+th,cols]=True
            if r.random()<0.4:
                bc=((x-np.arange(int(r.integers(10,70)))) if right else (x+1+np.arange(int(r.integers(10,70)))))[::2]
                bc=bc[(bc>=0)&(bc<W)]; B[y:y+th,bc]=False
    return B
def compose(B,fg,bg,seed,grain=0.08):
    img=np.empty((H,W,3),float); img[:]=bg; img[B]=fg
    n=np.random.default_rng(seed+99).normal(0,1,(H,W))
    n=np.asarray(Image.fromarray(((n*40)+128).clip(0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(float)/128-1
    return Image.fromarray((img*(1+grain*n[...,None])).clip(0,255).astype(np.uint8))

# ---------- shapes: each draws onto an 'L' mask with ImageDraw d, using random r
def path(d,pts,ws,fill=255):
    for (x,y),w in zip(pts,ws): d.ellipse([x-w/2,y-w/2,x+w/2,y+w/2],fill=fill)
def walk(r,x,y,a,w,steps,turn=.035,shrink=.9993):
    pts,ws=[],[]
    for _ in range(steps):
        a+=r.gauss(0,turn); x+=8*math.cos(a); y+=8*math.sin(a); w*=shrink; pts.append((x,y)); ws.append(w)
    return pts,ws,a
def s_bands(d,r):
    for _ in range(r.randint(1,3)):
        x,y=r.uniform(0,W),-300; a=math.pi/2+r.uniform(-.7,.7)
        p,w,_=walk(r,x,y,a,r.uniform(250,700),700); path(d,p,w)
def s_roots(d,r):
    def grow(x,y,a,w,depth):
        p,ws,a2=walk(r,x,y,a,w,r.randint(120,260),.05,.996); path(d,p,ws)
        if depth<4:
            for _ in range(r.randint(1,2)):
                i=r.randint(len(p)//3,len(p)-1); grow(p[i][0],p[i][1],a2+r.uniform(-.9,.9),ws[i]*.6,depth+1)
    grow(r.uniform(.3,.7)*W,H+100,-math.pi/2+r.uniform(-.2,.2),r.uniform(220,380),0)
def s_tendril(d,r):
    cx,cy=r.uniform(.3,.7)*W,r.uniform(.3,.6)*H; R0=r.uniform(500,800); w=r.uniform(90,180); pts,ws=[],[]
    turns=r.uniform(1.6,2.8)
    for i in range(1200):
        t=i/1199*turns*2*math.pi; R=R0*(1-t/(turns*2*math.pi))**1.2+30
        pts.append((cx+R*math.cos(t),cy+R*math.sin(t)*1.3)); ws.append(w*(.35+.65*R/R0))
    tail=[(pts[0][0]+k*6*r.uniform(.9,1.1),pts[0][1]+k*9) for k in range(400)]
    path(d,pts+tail,ws+[w]*400)
def s_corona(d,r):
    cx,cy=r.choice([0,W,W*.5]),r.uniform(.3,.7)*H; R=r.uniform(450,800)
    d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=255); n=r.randint(50,110); L=r.uniform(.25,.9)*R; th=r.randint(18,44)
    for a in np.linspace(0,2*math.pi,n,endpoint=False):
        d.line([(cx+R*.95*math.cos(a),cy+R*.95*math.sin(a)),(cx+(R+L)*math.cos(a),cy+(R+L)*math.sin(a))],fill=255,width=th)
    if r.random()<.6: d.ellipse([cx-R*.45,cy-R*.45,cx+R*.45,cy+R*.45],outline=0,width=r.randint(40,80))
def s_leaf(d,r):
    cx,cy=r.uniform(.6,1.0)*W,H*.5; ax,ay=r.uniform(900,1300),r.uniform(1600,2100); rot=r.uniform(-.4,.4)
    P=lambda t,s=1:(cx+ax*s*math.cos(t)*math.cos(rot)-ay*s*math.sin(t)*math.sin(rot),cy+ax*s*math.cos(t)*math.sin(rot)+ay*s*math.sin(t)*math.cos(rot))
    d.polygon([P(i/400*6.283) for i in range(400)],fill=255)
    for i in range(0,400,r.choice([4,5,7])): t=i/400*6.283; d.line([P(t,.98),P(t,1.1)],fill=255,width=r.randint(30,50))
    ex,ey=P(r.uniform(2.4,3.6),.45); d.ellipse([ex-r.uniform(300,500),ey-200,ex+r.uniform(300,500),ey+200],outline=0,width=r.randint(50,80))
def s_flower(d,r,m):
    ph=Image.open(os.path.join(HERE,"plates/passiflora.png")).convert("RGB"); sc=r.uniform(10,13)
    ph=ph.resize((int(ph.width*sc),int(ph.height*sc)),Image.LANCZOS).rotate(r.uniform(0,360),Image.BICUBIC)
    a=np.asarray(ph,float)/255; lum=.3*a[...,0]+.59*a[...,1]+.11*a[...,2]
    k=((lum>.38)&~((a[...,1]>a[...,0])&(a[...,1]>a[...,2]))).astype(np.uint8)*255
    k=Image.fromarray(k).filter(ImageFilter.GaussianBlur(8)).point(lambda v:255 if v>110 else 0)
    m.paste(255,(int(W/2-k.width/2),int(H/2-k.height/2)),k)
def s_ripples(d,r):
    cx,cy=r.uniform(-.3,1.3)*W,r.choice([-400,H+400,r.uniform(0,H)]); gap=r.uniform(160,320); th=r.uniform(.3,.6)
    for i in range(1,30):
        R=i*gap; d.ellipse([cx-R,cy-R*1.2,cx+R,cy+R*1.2],outline=255,width=int(gap*th))
def s_blobs(d,r):
    for _ in range(r.randint(2,5)):
        cx,cy,R=r.uniform(0,W),r.uniform(0,H),r.uniform(300,750); n=10; rr=[R*r.uniform(.7,1.3) for _ in range(n)]+[0]; rr[-1]=rr[0]
        pts=[]
        for i in range(300):
            t=i/300*n; j=int(t); f=t-j; f=f*f*(3-2*f); RR=rr[j]*(1-f)+rr[j+1]*f; a=i/300*6.283
            pts.append((cx+RR*math.cos(a),cy+RR*math.sin(a)*1.3))
        d.polygon(pts,fill=255)
def s_weave(d,r):
    for k in range(r.randint(3,6)):
        vert=k%2==0; p=r.uniform(0,W if vert else H); w=r.uniform(120,320)
        pts=[(p+120*math.sin(t/500+k),t) if vert else (t,p+120*math.sin(t/400+k)) for t in range(-200,(H if vert else W)+200,8)]
        path(d,pts,[w]*len(pts))
def s_stripe_band(d,r):
    x=r.uniform(.3,.7)*W; a=math.pi/2+r.uniform(-.4,.4); w=r.uniform(500,900)
    p,ws,_=walk(r,x,-300,a,w,620,.02,1.0); path(d,p,ws)
    for _ in range(r.randint(1,3)):
        off=r.uniform(-.3,.3); q=[(px+off*w,py) for px,py in p]; path(d,q,[w*r.uniform(.05,.12)]*len(q),fill=0)
def s_nematode(d,r):
    amp,wd=r.uniform(300,650),r.uniform(400,900); N=900; ph=r.uniform(0,6); pts,ws=[],[]
    for i in range(N):
        t=i/(N-1); y=-500+t*(H+1000); x=W*.5+amp*math.sin(t*math.pi*r.choice([1.2,1.6,2.2])+ph)
        tap=min(1,t/.25,(1-t)/.12); pts.append((x,y)); ws.append(wd*max(.08,tap**.6))
    path(d,pts,ws)

SHAPES=[s_bands,s_roots,s_tendril,s_corona,s_leaf,s_flower,s_ripples,s_blobs,s_weave,s_stripe_band,s_nematode]
PAIRS=[("22371F","A8B49A"),("6B4C7A","A8B49A"),("156826","F4F1EA"),("3780B8","F4F1EA"),("4F3433","C89B7B"),("3A2248","C8B6E2"),
       ("C8B6E2","3A2248"),("22371F","D6E28C"),("6B4C7A","F4F1EA"),("561C34","B0AC96"),("1A2C52","96C4E8"),("C45C28","F4F1EA"),
       ("59A66C","22371F"),("F4F1EA","6B4C7A"),("4F3433","A8B49A"),("3780B8","D6E28C")]

def make(seed):
    r=random.Random(seed); m=Image.new("L",(W,H),0); d=ImageDraw.Draw(m)
    picks=r.sample(SHAPES,1 if r.random()<.6 else 2)
    for f in picks: f(d,r,m) if f is s_flower else f(d,r)
    if r.random()<.25: m=m.transpose(Image.FLIP_LEFT_RIGHT)
    fg,bg=PAIRS[r.randrange(len(PAIRS))]
    B=ikat(m,seed,amp=r.randint(4,12),streaks=r.randint(800,2600))
    return compose(B,hx(fg),hx(bg),seed,grain=r.uniform(.05,.1)),"+".join(f.__name__[2:] for f in picks)

if __name__=="__main__":
    s0,c=int(sys.argv[1]),int(sys.argv[2]); out=os.path.join(HERE,"ikat"); os.makedirs(out,exist_ok=True)
    cols=6; rows=(c+cols-1)//cols; sheet=Image.new("RGB",(cols*330+10,rows*700+10),"#f4f1ec"); sd=ImageDraw.Draw(sheet)
    for i,s in enumerate(range(s0,s0+c)):
        im,name=make(s); im.save(os.path.join(out,f"seed{s:03d}.png"))
        t=im.resize((300,613),Image.LANCZOS); mk=Image.new("L",t.size,0); ImageDraw.Draw(mk).rounded_rectangle([0,0,299,612],40,fill=255)
        x,y=20+(i%cols)*330,20+(i//cols)*700; sheet.paste(t,(x,y),mk); sd.text((x,y+625),f"{s}  {name}",fill=(60,60,60),font_size=20)
    sheet.save(f"/tmp/work/ikat_sheet_{s0}.png"); print("ok")
