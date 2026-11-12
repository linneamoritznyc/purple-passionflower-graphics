"""Leaf x torn band explorations. python combine.py SEED COUNT"""
import sys, os, math, random, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage import measure
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import ikatgen as IK
W,H=1800,3680
def hx(h): return np.array([int(h[i:i+2],16) for i in (0,2,4)],np.float32)
PAIRS=[("6B4C7A","F4F1EA"),("1A2C52","C8B6E2"),("22371F","A8B49A"),("561C34","F4F1EA"),("156826","F4F1EA"),("3780B8","D6E28C"),
       ("4F3433","C89B7B"),("6B4C7A","A8B49A"),("C45C28","F4F1EA"),("3A2248","C8B6E2"),("22371F","D6E28C"),("1A2C52","E9DCC4")]
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)

def noise(g,n,amp):
    a=g.normal(0,1,(int(n*H/W)+3,n+3)).astype(np.float32); return np.asarray(Image.fromarray(a,"F").resize((W,H),Image.BICUBIC))*amp
def leaf(r,cx=None,cy=None,ax=None,ay=None,rot=None):
    cx=cx if cx is not None else r.uniform(.55,1.05)*W; cy=cy if cy is not None else H*r.uniform(.4,.6)
    ax=ax or r.uniform(800,1300); ay=ay or r.uniform(1500,2100); rot=rot if rot is not None else r.uniform(-.4,.4)
    m=Image.new("L",(W,H),0); t=np.linspace(0,2*np.pi,500)
    X=ax*np.cos(t)*(1+.12*np.cos(t)); Y=ay*np.sin(t)
    ImageDraw.Draw(m).polygon(list(zip(cx+X*math.cos(rot)-Y*math.sin(rot),cy+X*math.sin(rot)+Y*math.cos(rot))),fill=255)
    return np.asarray(m)>127,(cx,cy,ax,ay,rot)
def band(r,w=None,x=None,a=None):
    m=Image.new("L",(W,H),0); d=ImageDraw.Draw(m); x=x if x is not None else r.uniform(.25,.75)*W; a=a if a is not None else math.pi/2+r.uniform(-.45,.45); w=w or r.uniform(450,900)
    p,ws,_=IK.walk(r,x,-300,a,w,620,.02,1.0); IK.path(d,p,ws); return np.asarray(m)>127,p,w
def stripes_in(M,r,n=None,gap=None,th=None):
    d=ndi.distance_transform_edt(M); n=n or r.randint(1,3); gap=gap or r.uniform(60,140); th=th or r.uniform(12,26)
    out=np.zeros_like(M)
    for k in range(1,n+1): out|=np.abs(d-k*gap)<th/2
    return out
def fringe(M,r,length=None,th=None,step=None,side=None):
    sm=M[::4,::4].astype(float); cs=measure.find_contours(sm,.5); im=Image.new("L",(W,H),0); d=ImageDraw.Draw(im)
    dist=ndi.gaussian_filter(M.astype(float),20); gy,gx=np.gradient(dist)
    L=length or r.uniform(90,240); th=th or r.randint(22,44); step=step or r.choice([5,6,8,10])
    for c in cs:
        for y,x in c[::step]:
            X,Y=x*4,y*4; iy,ix=int(min(H-1,Y)),int(min(W-1,X)); nx,ny=-gx[iy,ix],-gy[iy,ix]; nn=math.hypot(nx,ny)+1e-9; nx,ny=nx/nn,ny/nn
            if side is not None and not side(X,Y,nx,ny): continue
            d.line([(X-nx*20,Y-ny*20),(X+nx*L,Y+ny*L)],fill=255,width=th)
    return np.asarray(im)>127
def ring(cx,cy,rx,ry,th):
    im=Image.new("L",(W,H),0); ImageDraw.Draw(im).ellipse([cx-rx,cy-ry,cx+rx,cy+ry],outline=255,width=int(th)); return np.asarray(im)>127
def torn_edge(M,g,depth=10):
    d=ndi.distance_transform_edt(M)-ndi.distance_transform_edt(~M); rough=noise(g,60,5)+noise(g,200,2)
    core=(d+rough)>0; fib=((d+rough+depth)>0)&~core; return core,fib
def render(layers,bg,g,grain=.06):
    img=np.empty((H,W,3),np.float32); img[:]=bg
    for kind,M,col in layers:
        if kind=="flat": img[M]=col
        elif kind=="ikat": img[IK.ikat(Image.fromarray(M.astype(np.uint8)*255),int(g.integers(1e6)),amp=7,streaks=1500)]=col
        elif kind=="torn":
            core,fib=torn_edge(M,g); sh=np.roll(core|fib,(6,4),(0,1))&~(core|fib); img[sh]*=.85; img[fib]=hx("FBF8F2"); img[core]=col
    n=g.normal(0,1,(H,W))[...,None]; return Image.fromarray(np.clip(img*(1+grain*n),0,255).astype(np.uint8))

# ---------- compositions
def c_torn_leaf(r,g,fg,bg):            # leaf with torn edge, fringe torn too, ring knocked out
    L,(cx,cy,ax,ay,rot)=leaf(r); F=fringe(L,r); R=ring(cx-ax*.45,cy+r.uniform(-300,300),r.uniform(220,420),r.uniform(120,200),r.uniform(30,55))
    return render([("torn",(L|F)&~R,fg)],bg,g)
def c_leaf_contours(r,g,fg,bg):        # leaf whose inside carries the band's parallel knockout lines
    L,(cx,cy,ax,ay,rot)=leaf(r); S=stripes_in(L,r,n=r.randint(2,4)); F=fringe(L,r)
    return render([("ikat",(L|F)&~S,fg)],bg,g)
def c_band_fringe(r,g,fg,bg):          # the band grows fringe on one side
    B,p,w=band(r); S=stripes_in(B,r,n=r.randint(1,2),gap=w*.18); s=r.choice([1,-1]); F=fringe(B,r,side=lambda X,Y,nx,ny: nx*s>0)
    return render([(r.choice(["torn","ikat"]),(B|F)&~S,fg)],bg,g)
def c_band_through_leaf(r,g,fg,bg):    # a paper-colour band cuts through the leaf
    L,_=leaf(r); F=fringe(L,r); B,_,_=band(r,w=r.uniform(120,260))
    return render([("ikat",L|F,fg),("torn",B&(L|F),bg)],bg,g)
def c_two_tech(r,g,fg,bg):             # ikat leaf + torn band in a third colour
    L,_=leaf(r); F=fringe(L,r); B,_,w=band(r); S=stripes_in(B,r,n=1,gap=w*.2); third=hx(r.choice(["C45C28","D6E28C","96C4E8","C8B6E2","A8B49A"]))
    return render([("ikat",L|F,fg),("torn",B&~S,third)],bg,g)
def c_leaf_outline(r,g,fg,bg):         # only a thick torn outline with fringe, ring floating
    L,(cx,cy,ax,ay,rot)=leaf(r); d=ndi.distance_transform_edt(L); O=L&(d<r.uniform(70,140)); F=fringe(L,r)
    R=ring(cx-ax*.4,cy,r.uniform(240,400),r.uniform(120,190),r.uniform(30,50))
    return render([("torn",O|F|R,fg)],bg,g)
def c_hem_fringe(r,g,fg,bg):           # a block with torn top and textile fringe hanging at the bottom
    top=r.uniform(.15,.45)*H; bot=r.uniform(.6,.8)*H; M=(yy>top+noise(g,3,90))&(yy<bot); F=np.zeros_like(M)
    im=Image.new("L",(W,H),0); d=ImageDraw.Draw(im); th=r.randint(14,30); gap=r.randint(28,60)
    for x in range(0,W,gap):
        L=r.uniform(.5,1.2)*(H-bot)*.7; d.line([(x,bot-10),(x+r.uniform(-30,30),bot+L)],fill=255,width=th)
    F=np.asarray(im)>127; S=stripes_in(M,r,n=r.randint(1,3),gap=r.uniform(80,160))
    if r.random()<.6: cx=r.uniform(.3,.7)*W; S|=ring(cx,(top+bot)/2,r.uniform(220,400),r.uniform(110,180),40)
    return render([("torn",M&~S,fg),("flat",F,fg)],bg,g)
def c_negative(r,g,fg,bg):             # field is the ink, leaf is torn paper, fringe stays ink
    L,(cx,cy,ax,ay,rot)=leaf(r); F=fringe(L,r); R=ring(cx-ax*.4,cy,r.uniform(240,400),r.uniform(120,190),45)
    return render([("flat",np.ones((H,W),bool),fg),("torn",L&~F,bg),("flat",R&L,fg)],fg,g)
def c_stacked_leaves(r,g,fg,bg):       # three small leaves stacked like a stem, each with ring
    layers=[]; M=np.zeros((H,W),bool); Rr=np.zeros_like(M)
    for k in range(3):
        L,(cx,cy,ax,ay,rot)=leaf(r,cx=W*r.uniform(.35,.65),cy=H*(.18+.32*k),ax=r.uniform(400,620),ay=r.uniform(520,700),rot=r.uniform(-1.2,1.2))
        M|=L|fringe(L,r,length=r.uniform(60,140),th=20); Rr|=ring(cx,cy,ax*.4,ay*.2,28)
    return render([(r.choice(["ikat","torn"]),M&~Rr,fg)],bg,g)
def c_split(r,g,fg,bg):                # half ikat, half torn: same leaf, edge changes technique mid-way
    L,_=leaf(r); F=fringe(L,r); M=L|F; cut=yy<H*r.uniform(.35,.65)
    S=stripes_in(L,r,n=1)
    return render([("ikat",M&cut&~S,fg),("torn",M&~cut&~S,fg)],bg,g)
def c_band_rings(r,g,fg,bg):           # band with a row of rings knocked out, like eyes along a stem
    B,p,w=band(r); R=np.zeros_like(B)
    for i in range(r.randint(2,4)):
        x,y=p[int(len(p)*(.2+.6*i/3))]; R|=ring(x,y,w*.3,w*.15,30)
    S=stripes_in(B,r,n=1,gap=w*.12)
    return render([(r.choice(["torn","ikat"]),B&~R&~S,fg)],bg,g)
def c_leaf_band_merge(r,g,fg,bg):      # the band swells into a leaf, one continuous body
    L,(cx,cy,ax,ay,rot)=leaf(r,cx=W*r.uniform(.4,.6),ax=r.uniform(700,950)); B,_,w=band(r,x=cx,w=r.uniform(250,420),a=math.pi/2)
    M=L|B; S=stripes_in(M,r,n=r.randint(1,3)); F=fringe(L,r,side=lambda X,Y,nx,ny: abs(nx)>.5)
    return render([("ikat",(M|F)&~S,fg)],bg,g)

COMPS=[c_torn_leaf,c_leaf_contours,c_band_fringe,c_band_through_leaf,c_two_tech,c_leaf_outline,c_hem_fringe,c_negative,c_stacked_leaves,c_split,c_band_rings,c_leaf_band_merge]
def make(seed):
    r=random.Random(seed); g=np.random.default_rng(seed); f=COMPS[seed%len(COMPS)]; fg,bg=PAIRS[r.randrange(len(PAIRS))]
    im=f(r,g,hx(fg),hx(bg))
    if r.random()<.3: im=im.rotate(180)
    return im,f.__name__[2:]
if __name__=="__main__":
    s0,c=int(sys.argv[1]),int(sys.argv[2]); out=os.path.join(HERE,"combine"); os.makedirs(out,exist_ok=True)
    sh=Image.new("RGB",(6*330+10,((c+5)//6)*700+10),"#2a2a2a"); d=ImageDraw.Draw(sh)
    for i,s in enumerate(range(s0,s0+c)):
        im,n=make(s); im.save(os.path.join(out,f"seed{s:03d}.png"))
        t=im.resize((300,613),Image.LANCZOS); mk=Image.new("L",t.size,0); ImageDraw.Draw(mk).rounded_rectangle([0,0,299,612],40,fill=255)
        x,y=20+(i%6)*330,20+(i//6)*700; sh.paste(t,(x,y),mk); d.text((x,y+625),f"{s}  {n}",fill=(220,220,220),font_size=20)
    sh.save(f"/tmp/work/combine_sheet_{s0}.png"); print("ok")
