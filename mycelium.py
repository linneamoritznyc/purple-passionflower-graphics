"""Mycelium networks. python mycelium.py START COUNT"""
import os, sys, math, random, numpy as np
from PIL import Image, ImageDraw
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import ikatgen as IK
W,H=1800,3680
def hx(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))
PAL=[("1C2A50","F4F1EA"),("F4F1EA","561C34"),("22371F","D6E28C"),("C8B6E2","3A2248"),("A8B49A","22371F"),("4F3433","C89B7B"),("F4F1EA","1A2C52"),("6B4C7A","F4F1EA")]

def grow(r,seeds,maxseg=26000,step=7,bp=.022,turn=.09,w0=9):
    cell=10; occ={}; segs=[]; tips=[]
    for i,(x,y) in enumerate(seeds):
        for a in np.linspace(0,2*math.pi,r.randint(4,8),endpoint=False): tips.append([x,y,a+r.uniform(-.3,.3),w0*r.uniform(.8,1.2),i*1000+len(tips),0])
    n=0
    while tips and n<maxseg:
        new=[]
        for t in tips:
            x,y,a,w,tid,age=t; a+=r.gauss(0,turn); nx,ny=x+step*math.cos(a),y+step*math.sin(a)
            if not(-50<nx<W+50 and -50<ny<H+50): continue
            key=(int(nx//cell),int(ny//cell)); hit=occ.get(key)
            segs.append((x,y,nx,ny,w)); n+=1
            if hit is not None and abs(hit[0]-tid)>0 and hit[1]<age-3 or (hit is not None and hit[0]!=tid and age>6): continue  # fused
            occ[key]=(tid,age); w2=max(1.2,w*.9985)
            new.append([nx,ny,a,w2,tid,age+1])
            if r.random()<bp and w2>1.6:
                new.append([nx,ny,a+r.choice([-1,1])*r.uniform(.45,1.0),w2*r.uniform(.55,.8),r.randrange(10**9),0])
        tips=new
    return segs

def draw(segs,bg,fg,scale=1):
    im=Image.new("RGB",(W,H),bg); d=ImageDraw.Draw(im)
    for x,y,nx,ny,w in segs: d.line([(x,y),(nx,ny)],fill=fg,width=max(1,int(round(w*scale))))
    for x,y,nx,ny,w in segs[::1]:
        if w>2.5: rr=w*scale/2; d.ellipse([nx-rr,ny-rr,nx+rr,ny+rr],fill=fg)
    return im

def make(seed):
    r=random.Random(seed); bg,fg=PAL[seed%len(PAL)]; bg,fg=hx(bg),hx(fg); mode=seed%4
    if mode==0: seeds=[(r.uniform(.3,.7)*W,r.uniform(.4,.6)*H)]                       # one spore, radiating
    elif mode==1: seeds=[(r.uniform(0,W),r.uniform(0,H)) for _ in range(r.randint(3,6))] # several colonies meeting
    elif mode==2: seeds=[(r.uniform(0,W),H+20) for _ in range(r.randint(2,4))]           # rising from the soil edge
    else: seeds=[(W/2,H/2)]
    segs=grow(r,seeds,maxseg=r.randint(45000,80000),turn=r.uniform(.07,.14),bp=r.uniform(.03,.05),w0=r.uniform(11,18))
    im=draw(segs,bg,fg)
    arr=np.asarray(im,np.float32)
    if mode==3:  # ikat version: the network goes through the ikat streak treatment
        M=np.all(np.abs(arr-np.array(fg))<30,2); B=IK.ikat(Image.fromarray(M.astype(np.uint8)*255),seed,amp=4,streaks=900)
        arr=np.empty((H,W,3),np.float32); arr[:]=bg; arr[B]=fg
    if mode==0 and r.random()<.7:  # spore at the centre
        ImageDraw.Draw(im)
    n=np.random.default_rng(seed).normal(0,1,(H,W))[...,None]
    return Image.fromarray(np.clip(arr*(1+.05*n),0,255).astype(np.uint8)),["spore","colonies","rising","ikat"][mode]

if __name__=="__main__":
    s0,c=int(sys.argv[1]),int(sys.argv[2]); out=os.path.join(HERE,"mycelium"); os.makedirs(out,exist_ok=True)
    sh=Image.new("RGB",(4*330+10,((c+3)//4)*700+10),"#2a2a2a"); d=ImageDraw.Draw(sh)
    for i,s in enumerate(range(s0,s0+c)):
        im,n=make(s); im.save(os.path.join(out,f"seed{s:03d}.png"))
        t=im.resize((300,613),Image.LANCZOS); mk=Image.new("L",t.size,0); ImageDraw.Draw(mk).rounded_rectangle([0,0,299,612],40,fill=255)
        x,y=20+(i%4)*330,20+(i//4)*700; sh.paste(t,(x,y),mk); d.text((x,y+625),f"{s}  {n}",fill=(220,220,220),font_size=20)
    sh.save(f"/tmp/work/myc_sheet_{s0}.png"); print("ok")
