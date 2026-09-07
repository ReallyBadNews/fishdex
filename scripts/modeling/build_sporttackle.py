"""Brand-free original bait and lure models. Load common fish helpers first."""
def ring(name,center,radius,material,axis='Y'):
 pts=[]
 for t in np.linspace(0,2*math.pi,49):
  offset=(radius*math.cos(t),0,radius*math.sin(t)) if axis=='Y' else ((0,radius*math.cos(t),radius*math.sin(t)) if axis=='X' else (radius*math.cos(t),radius*math.sin(t),0))
  pts.append(tuple(Vector(center)+Vector(offset)))
 return line(name,pts,.009,material)
def tapered_tube(name,points,radii,material):
 vertices=[];faces=[];sides=16
 for i,p in enumerate(points):
  tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
  tangent.normalize();u=tangent.cross(Vector((0,0,1)))
  if u.length<.001:u=tangent.cross(Vector((0,1,0)))
  u.normalize();v=tangent.cross(u).normalized()
  for a in np.linspace(0,2*math.pi,sides,endpoint=False):vertices.append(tuple(Vector(p)+radii[i]*(u*math.cos(a)+v*math.sin(a))))
 for i in range(len(points)-1):
  for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;faces.append((a,b,b+sides,a+sides))
 faces.extend([tuple(range(sides-1,-1,-1)),tuple((len(points)-1)*sides+j for j in range(sides))])
 return mesh(name,vertices,faces,material)
def treble(center,size,steel):
 ring('split ring',center,.037,steel)
 x,y,z=center;line('treble shaft',[(x,y,z-.025),(x,y,z-size*.64)],.009,steel)
 for angle in [0,2*math.pi/3,4*math.pi/3]:
  pts=[(0,0,-size*.15),(0,0,-size*.64)]
  pts += [(size*.34*(1-math.cos(t)),0,-size*.64-size*.34*math.sin(t)) for t in np.linspace(0,math.pi,22)]
  pts += [(size*.68,0,-size*.37),(size*.62,0,-size*.31)]
  transformed=[(x+a*math.cos(angle),y+a*math.sin(angle),z+c) for a,_,c in pts]
  tapered_tube('treble bend',transformed,[.010]*(len(pts)-3)+[.008,.004,.001],steel)
def blade(name,center,length,width,material):
 vs=[];fs=[];nx=30;ny=16
 for i in range(nx+1):
  t=i/nx;x=(t-.5)*length;w=width*math.sin(math.pi*t)**.7
  for j in range(ny+1):
   s=2*j/ny-1;vs.append((x,w*s,.06*(1-s*s)*math.sin(math.pi*t)))
 for i in range(nx):
  for j in range(ny):a=i*(ny+1)+j;fs.append((a,a+ny+1,a+ny+2,a+1))
 o=mesh(name,vs,fs,material);o.location=center;o.modifiers.new('pressed metal thickness','SOLIDIFY').thickness=.009;return o

def build_sporttackle(kind):
 scene=setup('v2 '+kind);scene['fishdex_generated']=True;scene['bait_id']=kind
 steel=mat('polished stainless',(.42,.46,.47),.9,.22);gold=mat('hammered brass',(.65,.44,.12),.85,.27)
 green=mat('olive lure finish',(.24,.37,.11),.24,.29);silver=mat('pearl belly',(.76,.80,.70),.42,.30)
 black=mat('eye black',(.007,.01,.008),.04,.2);red=mat('red lure accent',(.60,.055,.025),.15,.38)
 def eyes(x,y,z,size=.046):
  for side in (-1,1):
   oval('lure iris',(x,side*y,z),(size,.009,size),gold)
   oval('lure pupil',(x-.008,side*(y+.008),z),(size*.53,.005,size*.6),black)
 def skirt(start):
  x,y,z=start
  for i in range(36):
   a=i*2*math.pi/36;spread=.17
   pts=[(x,y+.055*math.sin(a),z+.055*math.cos(a)),(x+.20,y+.11*math.sin(a),z+.11*math.cos(a)),(x+.65+(i%5)*.025,y+spread*math.sin(a),z-.11+spread*math.cos(a))]
   tapered_tube('silicone skirt strand',pts,[.008,.008,.004],green if i%3 else silver)
 if kind in ('worm','soft-plastic'):
  rubber=mat('natural worm skin' if kind=='worm' else 'watermelon rubber',(.33,.105,.065) if kind=='worm' else (.16,.24,.06),0,.43)
  pts=[(-1.02+2.04*t,.06*math.sin(t*8),.12*math.sin(t*5)) for t in np.linspace(0,1,121)]
  radii=[.004+(.061 if kind=='worm' else .079)*math.sin(math.pi*t)**.35 for t in np.linspace(0,1,121)]
  tapered_tube('tapered segmented body',pts,radii,rubber)
  for i in range(5,115,2):
   p=pts[i];r=radii[i]
   line('body segment seam',[(p[0],p[1]+r*math.cos(a),p[2]+r*math.sin(a)) for a in np.linspace(0,2*math.pi,24)],.0025,rubber)
  if kind=='worm':tapered_tube('raised clitellum',pts[26:43],[r*1.22 for r in radii[26:43]],rubber)
  else:
   for i in range(20,104,7):oval('embedded fleck',(pts[i][0],pts[i][1]-.072,pts[i][2]),(.007,.002,.010),black)
 elif kind=='minnow':
  pts=[(-.88+1.65*t,0,.015*math.sin(t*math.pi)) for t in np.linspace(0,1,80)]
  radii=[.01+.13*math.sin(math.pi*t)**.72 for t in np.linspace(0,1,80)]
  tapered_tube('baitfish body',pts,radii,silver)
  for side in (-1,1):line('baitfish side stripe',[(-.70,side*.073,.01),(-.25,side*.136,.01),(.35,side*.117,.01),(.70,side*.027,.01)],.013,green)
  eyes(-.69,.079,.045,.026)
  fin('minnow caudal',lambda t:(.72,0,(t-.5)*.065),[(.98+.09*abs(2*t-1),0,(2*t-1)*.22) for t in np.linspace(0,1,17)],silver,steel)
  fin('minnow dorsal',lambda t:(-.13+.40*t,0,.12),[(-.13+.40*t,0,.12+.13*math.sin(t*math.pi)) for t in np.linspace(0,1,11)],silver,steel)
  for side in (-1,1):fin('minnow pectoral',lambda t:(-.43,side*.1,0),[(-.40+.2*t,side*(.12+.07*t),-.05-.10*math.sin(t*math.pi)) for t in np.linspace(0,1,9)],silver,steel)
 elif kind in ('jig','spinnerbait'):
  z=-.20 if kind=='spinnerbait' else .08
  oval('painted weighted head',(-.45,0,z),(.18,.12,.13),green if kind=='spinnerbait' else red);eyes(-.49,.111,z+.022,.031)
  skirt((-.31,0,z));ring('jig line eye',(-.47,0,z+.16),.04,steel)
  hook(-.30,0,z,.58,steel)
  if kind=='spinnerbait':
   line('bent spinnerbait wire',[(-.45,0,z+.12),(-.80,0,.19),(-.41,0,.63),(.38,0,.54)],.012,steel)
   ring('line tie',(-.80,0,.19),.033,steel)
   blade('willow blade',(.33,0,.55),.67,.15,gold);ring('swivel',(-.03,0,.55),.035,steel)
 elif kind=='spinner':
  line('inline wire shaft',[(-.97,0,0),(.63,0,0)],.010,steel)
  for x in [-.42,-.26,-.1]:oval('spacer bead',(x,0,0),(.055,.055,.055),gold)
  oval('weighted spinner body',(.13,0,0),(.23,.072,.072),red)
  b=blade('rotating spoon blade',(-.47,0,.22),.60,.17,gold);b.rotation_euler[0]=.6
  ring('blade clevis',(-.74,0,.10),.08,steel);ring('line tie',(-.99,0,0),.044,steel);treble((.68,0,0),.33,steel)
 elif kind in ('crankbait','jerkbait','popper'):
  length=.65 if kind=='crankbait' else (.90 if kind=='jerkbait' else .65)
  width=.19 if kind!='jerkbait' else .115;height=.24 if kind!='jerkbait' else .15
  oval('hard lure body',(0,0,.10),(length,width,height),green)
  oval('pearl underside',(.02,0,.10-height*.44),(length*.91,width*.94,height*.57),silver)
  eyes(-length*.59,width*.81,.16,.041)
  if kind!='popper':
   bill=blade('diving lip',(-length-.10,0,-.05),.44 if kind=='crankbait' else .24,.135,silver);bill.rotation_euler[1]=-.35
  else:
   vs=[(-length+.09,0,.10)]+[(-length-.01,.15*math.cos(a),.10+.17*math.sin(a)) for a in np.linspace(0,2*math.pi,49)]
   mesh('cupped red popper face',vs,[(0,i,i+1) for i in range(1,49)],red)
   ring('popper mouth rim',(-length-.01,0,.10),.16,silver,axis='X')
  ring('front line tie',(-length+.025,0,.035),.035,steel)
  for x in [-.05,length*.83]:
   bodybottom=.10-height*math.sqrt(max(0,1-(x/length)**2))
   bellybottom=.10-height*.44-height*.57*math.sqrt(max(0,1-((x-.02)/(length*.91))**2))
   treble((x,0,min(bodybottom,bellybottom)-.035),.30 if kind!='jerkbait' else .25,steel)
  for i in range(6):
   x=-length*.45+i*length*.19
   for side in (-1,1):line('painted flank bars',[(x,side*width*.98,.12),(x+.025,side*width*.85,.24)],.008,black)
 elif kind=='spoon':
  b=blade('concave casting spoon',(0,0,0),1.7,.30,silver);b.rotation_euler[0]=.92
  inset=blade('red painted spoon stripe',(0,-.013,.006),1.40,.083,red);inset.rotation_euler[0]=.92
  ring('spoon line tie',(-.86,0,0),.045,steel);treble((.88,0,0),.40,steel)
 elif kind=='frog':
  oval('hollow frog lure',(-.15,0,0),(.49,.27,.18),green)
  oval('cream frog belly',(-.12,0,-.095),(.42,.245,.09),silver)
  for side in (-1,1):
   oval('raised frog eye',(-.43,side*.16,.145),(.09,.08,.075),green)
   oval('frog iris',(-.48,side*.185,.19),(.034,.018,.029),gold)
   oval('frog pupil',(-.49,side*.195,.2),(.018,.008,.019),black)
   for i in range(12):
    pts=[(.20,side*.18,0),(.53,side*(.18+i*.011),-.05),(.92+(i%3)*.055,side*(.20+i*.014),-.14)]
    tapered_tube('rubber skirt leg',pts,[.009,.009,.003],green if i%2 else silver)
   line('double weedless hook',[(-.05,side*.24,-.045),(.32,side*.28,.025),(.30,side*.24,.12),(.15,side*.22,.15)],.012,steel)
   for i in range(4):oval('frog flank marking',(-.25+i*.13,side*.23,.07),(.030,.003,.020),black)
  ring('frog line tie',(-.64,0,-.01),.042,steel)
 else:raise ValueError(kind)
 return sport_finish(scene,kind)
