"""Weird pods: plum on cream. python pods.py START COUNT"""
import sys, os, math, random, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from combine import leaf, fringe, ring, render, hx, stripes_in, band, W, H, yy, xx
FG,BG=hx("561C34"),hx("F4F1EA")

def pod(r,cx,cy,a,b,rot=None,hair=None,eye=True,eyes=1):
    L,(cx,cy,ax,ay,rot)=leaf(r,cx=cx,cy=cy,ax=a,ay=b,rot=rot if rot is not None else r.uniform(-1.4,1.4))
    hl=hair if hair is not None else r.uniform(.12,.3)*min(a,b)
    F=fringe(L,r,length=hl,th=max(10,int(min(a,b)*.05)),step=r.choice([4,5,6])) if hl>0 else np.zeros_like(L)
    E=np.zeros_like(L)
    if eye:
        for k in range(eyes):
            ex=cx+(r.uniform(-.35,.35)*a if eyes>1 else 0); ey=cy+(r.uniform(-.5,.5)*b if eyes>1 else 0); s=r.uniform(.18,.3)
            E|=ring(ex,ey,a*s*1.6,a*s*.8,max(14,a*.06))
    return L|F,E

def chain(r):        # many pods, shrinking down a wavy line
    M=np.zeros((H,W),bool); E=np.zeros((H,W),bool); n=r.randint(4,8); y=-100
    for k in range(n):
        s=r.uniform(.6,1.1)*(1.3-k/n); a,b=320*s,380*s; y+=b*1.7; x=W/2+math.sin(k*1.3)*W*.25
        P,e=pod(r,x,y,a,b); M=M|P; E=E|e
    return [("ikat",M&~E,FG)]
def spawn(r):        # frogspawn: dozens of small pods packed, one eye each
    M=np.zeros((H,W),bool); E=np.zeros((H,W),bool); pts=[]
    for _ in range(400):
        x,y,rad=r.uniform(0,W),r.uniform(0,H),r.uniform(110,260)
        if all(math.hypot(x-a,y-b)>rad+c+30 for a,b,c in pts): pts.append((x,y,rad))
        if len(pts)>=r.randint(14,30): break
    for x,y,rad in pts:
        P,e=pod(r,x,y,rad*.85,rad,hair=rad*.25); M=M|P; E=E|e
    return [(r.choice(["ikat","torn"]),M&~E,FG)]
def mitosis(r):      # one pod splitting into two, joined by a neck
    a,b=r.uniform(500,650),r.uniform(650,800); y1,y2=H*.32,H*.68
    P1,e1=pod(r,W/2,y1,a,b,rot=0); P2,e2=pod(r,W/2,y2,a,b,rot=0)
    neck=(np.abs(xx-W/2)<r.uniform(80,180))&(yy>y1)&(yy<y2)
    return [("ikat",(P1|P2|neck)&~(e1|e2),FG)]
def many_eyes(r):    # one huge cropped pod covered in eyes
    P,E=pod(r,W*r.uniform(.6,.9),H/2,1300,2000,rot=r.uniform(-.2,.2),eyes=r.randint(6,14),hair=200)
    return [("torn",P&~E,FG)]
def nested(r):       # pod inside pod inside pod
    M=np.zeros((H,W),bool); a,b=1100,1700; ins=[]
    for k in range(4):
        P,_=pod(r,W/2,H/2,a*(1-.24*k),b*(1-.24*k),rot=0,eye=False,hair=90 if k==0 else 0)
        M=M^P if k else P
    _,E=pod(r,W/2,H/2,a*.2,b*.2,rot=0,hair=0)
    return [("ikat",M,FG),("flat",E,FG)]
def bald_eyes(r):    # only the eyes and the hair are left, the bodies are gone
    M=np.zeros((H,W),bool)
    for k in range(r.randint(3,6)):
        a=r.uniform(250,500); L,(cx,cy,ax,ay,rot)=leaf(r,cx=r.uniform(.15,.85)*W,cy=r.uniform(.1,.9)*H,ax=a,ay=a*1.3)
        M|=fringe(L,r,length=a*.4,th=22,step=4)&~L; M|=ring(cx,cy,a*.45,a*.22,30)
    return [("ikat",M,FG)]
def legs(r):         # pods with long fringe only underneath, like creatures walking
    M=np.zeros((H,W),bool); E=np.zeros((H,W),bool)
    for k in range(r.randint(2,3)):
        cy=H*(.2+.3*k)+r.uniform(-80,80); a=r.uniform(380,600); L,(cx,_,_,_,_)=leaf(r,cx=r.uniform(.3,.7)*W,cy=cy,ax=a,ay=a*.6,rot=0)
        F=fringe(L,r,length=r.uniform(250,500),th=24,step=5,side=lambda X,Y,nx,ny: ny>.35)
        M|=L|F; E|=ring(cx+a*.3,cy-a*.1,a*.22,a*.12,26)
    return [("torn",M&~E,FG)]
def tendril_pods(r): # pods hanging off a vine
    m=Image.new("L",(W,H),0); d=ImageDraw.Draw(m); p,ws,_=__import__("ikatgen").walk(r,W*.2,-200,math.pi/2+.2,90,560,.03,1.0); __import__("ikatgen").path(d,p,ws)
    M=np.asarray(m)>127; E=np.zeros_like(M)
    for i in range(4):
        x,y=p[int(len(p)*(.15+.2*i))]; s=r.choice([-1,1]); P,e=pod(r,x+s*380,y+120,260,340,rot=s*.6); M|=P; E|=e
        M|=(np.abs(yy-y-40)<26)&(np.minimum(x,x+s*300)<xx)&(xx<np.maximum(x,x+s*300))
    return [("ikat",M&~E,FG)]
def scatter_rain(r): # pods falling, motion streaks above each
    M=np.zeros((H,W),bool); E=np.zeros((H,W),bool)
    for _ in range(r.randint(5,9)):
        x,y,a=r.uniform(0,W),r.uniform(.15,1)*H,r.uniform(120,260); P,e=pod(r,x,y,a,a*1.25,hair=a*.2)
        trail=(np.abs(xx-x)<a*.5)&(yy<y)&(yy>y-r.uniform(400,1200))&((yy.astype(int)//18)%2==0)
        M|=P|trail; E|=e
    return [("ikat",M&~E,FG)]
def cross_section(r):# one pod cut open: rings of seeds inside
    P,_=pod(r,W/2,H/2,1000,1500,rot=0,eye=False,hair=150); E=np.zeros_like(P)
    for k,(rx,ry,n) in enumerate([(650,1050,14),(380,640,8)]):
        for t in np.linspace(0,2*math.pi,n,endpoint=False): E|=ring(W/2+rx*math.cos(t),H/2+ry*math.sin(t),70,45,18)
    E|=ring(W/2,H/2,150,95,26)
    return [("torn",P&~E,FG)]
def merged(r):       # pods melting into each other, eyes drifting
    M=np.zeros((H,W),bool); E=np.zeros((H,W),bool)
    for k in range(r.randint(3,5)):
        P,e=pod(r,r.uniform(.25,.75)*W,r.uniform(.2,.8)*H,r.uniform(400,650),r.uniform(500,800),hair=0); M|=P; E|=e
    M=ndi.binary_closing(M,iterations=40); F=fringe(M,r,length=150,th=24,step=5)
    return [("ikat",(M|F)&~E,FG)]
def inverted(r):     # cream pods on plum ground, plum eyes
    M=np.zeros((H,W),bool); E=np.zeros((H,W),bool)
    for k in range(3):
        P,e=pod(r,W*r.uniform(.35,.65),H*(.18+.32*k),r.uniform(420,600),r.uniform(520,700)); M|=P; E|=e
    return [("flat",np.ones((H,W),bool),FG),("torn",M&~E,BG)]

IDEAS=[chain,spawn,mitosis,many_eyes,nested,bald_eyes,legs,tendril_pods,scatter_rain,cross_section,merged,inverted]
def make(seed):
    r=random.Random(seed); g=np.random.default_rng(seed); f=IDEAS[seed%len(IDEAS)]
    return render(f(r),BG,g),f.__name__
if __name__=="__main__":
    s0,c=int(sys.argv[1]),int(sys.argv[2]); out=os.path.join(HERE,"pods"); os.makedirs(out,exist_ok=True)
    sh=Image.new("RGB",(6*330+10,((c+5)//6)*700+10),"#2a2a2a"); d=ImageDraw.Draw(sh)
    for i,s in enumerate(range(s0,s0+c)):
        im,n=make(s); im.save(os.path.join(out,f"seed{s:03d}.png"))
        t=im.resize((300,613),Image.LANCZOS); mk=Image.new("L",t.size,0); ImageDraw.Draw(mk).rounded_rectangle([0,0,299,612],40,fill=255)
        x,y=20+(i%6)*330,20+(i//6)*700; sh.paste(t,(x,y),mk); d.text((x,y+625),f"{s}  {n}",fill=(220,220,220),font_size=20)
    sh.save(f"/tmp/work/pods_sheet_{s0}.png"); print("ok")
