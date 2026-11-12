"""Landscape botanical collages, rebuilt with her textures. python collage.py START COUNT"""
import os, sys, math, random, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
HERE=os.path.dirname(os.path.abspath(__file__))
W,H=3600,1950
def hx(h): return np.array([int(h[i:i+2],16) for i in (0,2,4)],np.float32)
PAL={ # background, then ink set
 "cream":("F4F1EA",["9FC3E6","CDD69C","6B4C7A","1F2A1C","4A7DB5","6CA673","C3D66A","1C2A50","C8B6E2"]),
 "navy": ("1C2A50",["2F6A2E","4A7DB5","6B4C7A","CDD69C","9FC3E6","6CA673","C3D66A","C8B6E2","F4F1EA"]),
 "lilac":("C8B6E2",["4A7DB5","CDD69C","2F6A2E","1F2A1C","1C2A50","6CA673","C3D66A","6B4C7A","F4F1EA"]),
}
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def noise(g,n,amp):
    a=g.normal(0,1,(int(n*H/W)+3,n+3)).astype(np.float32); return np.asarray(Image.fromarray(a,"F").resize((W,H),Image.BICUBIC))*amp
def L(): return Image.new("L",(W,H),0)
def B(m): return np.asarray(m)>127

def ikat(A,r,amp=5,streaks=700):
    off=np.zeros(H,int); y=0
    while y<H: run=r.randint(2,9); off[y:y+run]=r.randint(-amp,amp); y+=run
    Bm=np.zeros_like(A)
    for y in range(H):
        o=off[y]
        if o>0: Bm[y,o:]=A[y,:-o]
        elif o<0: Bm[y,:o]=A[y,-o:]
        else: Bm[y]=A[y]
    Lr=Bm[:,:-1]&~Bm[:,1:]; R=~Bm[:,:-1]&Bm[:,1:]; ys,xs=np.nonzero(Lr|R)
    for k in r.sample(range(len(ys)),min(streaks,len(ys))) if len(ys) else []:
        y,x=ys[k],xs[k]; ln=r.randint(20,140); th=r.randint(1,4); right=Lr[y,x]
        seg=np.arange(ln); keep=np.random.default_rng(k).random(ln)>np.linspace(0,.9,ln)
        cols=((x+1+seg) if right else (x-seg))[keep]; cols=cols[(cols>=0)&(cols<W)]; Bm[y:y+th,cols]=True
    return Bm
def torn(A,g):
    d=ndi.distance_transform_edt(A)-ndi.distance_transform_edt(~A); rough=noise(g,90,5)+noise(g,300,2)
    core=(d+rough)>0; fib=((d+rough+11)>0)&~core; return core,fib

def blob(r,cx,cy,R,irr=.35,sy=.8):
    n=9; rr=[R*r.uniform(1-irr,1+irr) for _ in range(n)]; rr.append(rr[0]); pts=[]
    for i in range(360):
        t=i/360*n; j=int(t); f=t-j; f=f*f*(3-2*f); RR=rr[j]*(1-f)+rr[j+1]*f; a=i/360*6.283
        pts.append((cx+RR*math.cos(a),cy+RR*math.sin(a)*sy))
    m=L(); ImageDraw.Draw(m).polygon(pts,fill=255); return B(m)
def vine(r,w0,w1,curl=True):
    m=L(); d=ImageDraw.Draw(m); side=r.choice(["l","b","t"])
    x,y={"l":(-100,r.uniform(.3,1)*H),"b":(r.uniform(0,.5)*W,H+100),"t":(r.uniform(0,.6)*W,-100)}[side]
    a={"l":r.uniform(-.5,.2),"b":r.uniform(-1.2,-.5),"t":r.uniform(.2,.8)}[side]; n=r.randint(380,520); pts=[]
    for i in range(n):
        a+=r.gauss(0,.025); x+=9*math.cos(a); y+=9*math.sin(a); w=w0+(w1-w0)*i/n; d.ellipse([x-w,y-w,x+w,y+w],fill=255); pts.append((x,y,a))
    if curl:  # passion flower tendril at the tip
        R0=r.uniform(60,140); s=r.choice([-1,1])
        for i in range(260):
            t=i/260*4*math.pi; R=R0*(1-i/300); a2=a+s*t; x+=R*.08*math.cos(a2); y+=R*.08*math.sin(a2); d.ellipse([x-w1,y-w1,x+w1,y+w1],fill=255)
    return B(m),pts
def rosette(r,cx,cy,size,n=None):
    m=L(); d=ImageDraw.Draw(m); n=n or r.randint(9,15)
    for k in range(n):
        a=-math.pi/2+r.uniform(-1.35,1.35); ln=size*r.uniform(.55,1.05); w=size*r.uniform(.06,.1); bend=r.uniform(-.25,.25)
        pts=[]
        for t in np.linspace(0,1,40):
            aa=a+bend*t*t; px=cx+ln*t*math.cos(aa); py=cy+ln*t*math.sin(aa); ww=w*(1-t)**.9; pts.append((px,py,aa,ww))
        poly=[(p[0]+p[3]*math.cos(p[2]+1.57),p[1]+p[3]*math.sin(p[2]+1.57)) for p in pts]+[(p[0]-p[3]*math.cos(p[2]+1.57),p[1]-p[3]*math.sin(p[2]+1.57)) for p in pts[::-1]]
        d.polygon(poly,fill=255)
    return B(m)
def spore(r,cx,cy,R):
    m=L(); d=ImageDraw.Draw(m); d.ellipse([cx-R*.55,cy-R*.55,cx+R*.55,cy+R*.55],fill=255)
    for a in np.linspace(0,2*math.pi,r.randint(70,130),endpoint=False):
        d.line([(cx+R*.5*math.cos(a),cy+R*.5*math.sin(a)),(cx+R*math.cos(a),cy+R*math.sin(a))],fill=255,width=max(4,int(R*.03)))
    return B(m)
def lumpy_ring(r,cx,cy,R):
    m=L(); d=ImageDraw.Draw(m); pts=[]
    for i in range(200):
        a=i/200*6.283; RR=R*(1+.12*math.sin(a*5+r.uniform(0,.3))+r.uniform(-.04,.04)); pts.append((cx+RR*math.cos(a),cy+RR*math.sin(a)*.85))
    d.line(pts+[pts[0]],fill=255,width=int(R*.28),joint="curve")
    for _ in range(r.randint(4,9)):  # holes in the ring wall
        a=r.uniform(0,6.283); hx_,hy=cx+R*math.cos(a),cy+R*.85*math.sin(a); h=R*r.uniform(.05,.1); d.ellipse([hx_-h,hy-h,hx_+h,hy+h],fill=0)
    return B(m)
def splatter(r,cx,cy,R):
    m=L(); d=ImageDraw.Draw(m)
    for _ in range(r.randint(18,40)):
        a=r.uniform(0,6.283); dist=R*r.random()**.6; s=r.uniform(6,40)*(1-dist/R*.6); x,y=cx+dist*math.cos(a),cy+dist*math.sin(a)
        d.ellipse([x-s,y-s*r.uniform(.6,1.4),x+s,y+s],fill=255)
    return B(m)
def worm(r,cx,cy,ln):
    m=L(); d=ImageDraw.Draw(m); a=r.uniform(0,6.283); ph=r.uniform(0,6)
    for i in range(300):
        t=i/299; px=cx+(t-.5)*ln*math.cos(a)+math.sin(t*2*math.pi+ph)*ln*.15*math.sin(a); py=cy+(t-.5)*ln*math.sin(a)-math.sin(t*2*math.pi+ph)*ln*.15*math.cos(a)
        w=ln*.04*math.sin(math.pi*t)**.7+3; d.ellipse([px-w,py-w,px+w,py+w],fill=255)
    return B(m)

def make(seed):
    r=random.Random(seed); g=np.random.default_rng(seed); key=list(PAL)[seed%3]; bgh,inks=PAL[key]; inks=inks[:]; r.shuffle(inks)
    bg=hx(bgh); img=np.empty((H,W,3),np.float32); img[:]=bg; cols=[hx(c) for c in inks]
    def put(M,col,tech="flat"):
        nonlocal img
        if tech=="ikat": M=ikat(M,r)
        if tech=="torn":
            core,fib=torn(M,g); sh=np.roll(core|fib,(8,6),(0,1))&~(core|fib); img[sh]*=.86; img[fib]=hx("FBF8F2"); img[core]=col; return
        img[M]=col
    # 1 big fields: two large blobs, one ikat edge, one torn edge
    b1=blob(r,r.uniform(.05,.3)*W,r.uniform(.2,.5)*H,r.uniform(650,950)); put(b1,cols[0],"ikat")
    b2=blob(r,r.uniform(.6,.9)*W,r.uniform(.55,.85)*H,r.uniform(750,1000)); put(b2,cols[1],r.choice(["torn","flat"]))
    if r.random()<.6: b3=blob(r,r.uniform(.35,.6)*W,r.uniform(-.05,.2)*H,r.uniform(380,560)); put(b3,cols[2],"flat")
    # 2 vines: one heavy, one fine, the paper colour cuts where the heavy vine crosses a field
    v1,_=vine(r,r.uniform(30,44),r.uniform(16,22)); put(v1,cols[3]); v2,_=vine(r,r.uniform(12,18),r.uniform(8,11)); put(v2,cols[4])
    # 3 focal rosette, low, partly off the bottom edge
    rx=r.uniform(.45,.75)*W; put(rosette(r,rx,H*r.uniform(1.0,1.08),r.uniform(850,1100)),cols[5])
    # 4 small actors: spore, lumpy ring, splatter, worm, a pebble
    put(spore(r,r.uniform(.3,.5)*W,r.uniform(.55,.8)*H,r.uniform(190,280)),cols[6])
    if r.random()<.7: put(spore(r,r.uniform(.8,.95)*W,r.uniform(.6,.9)*H,r.uniform(150,220)),cols[7])
    put(lumpy_ring(r,r.uniform(.2,.4)*W,r.uniform(.45,.7)*H,r.uniform(150,220)),cols[r.choice([3,5,7])],"torn")
    put(splatter(r,r.uniform(.75,.95)*W,r.uniform(.1,.4)*H,r.uniform(160,260)),cols[7])
    if r.random()<.6: put(worm(r,r.uniform(.5,.75)*W,r.uniform(.3,.5)*H,r.uniform(350,520)),cols[r.choice([3,4,7])])
    for _ in range(r.randint(1,3)): put(blob(r,r.uniform(.1,.9)*W,r.uniform(.1,.9)*H,r.uniform(40,90),.3,1),cols[r.choice([6,8,2])])
    n=g.normal(0,1,(H,W))[...,None]; return Image.fromarray(np.clip(img*(1+.05*n),0,255).astype(np.uint8)),key

if __name__=="__main__":
    s0,c=int(sys.argv[1]),int(sys.argv[2]); out=os.path.join(HERE,"collage"); os.makedirs(out,exist_ok=True)
    tw=600; th=int(tw*H/W); sh=Image.new("RGB",(3*(tw+20)+20,((c+2)//3)*(th+50)+20),"#2a2a2a"); d=ImageDraw.Draw(sh)
    for i,s in enumerate(range(s0,s0+c)):
        im,k=make(s); im.save(os.path.join(out,f"seed{s:03d}.png"))
        x,y=20+(i%3)*(tw+20),20+(i//3)*(th+50); sh.paste(im.resize((tw,th),Image.LANCZOS),(x,y)); d.text((x,y+th+8),f"{s}  {k}",fill=(220,220,220),font_size=20)
    sh.save(f"/tmp/work/collage_sheet_{s0}.png"); print("ok")
