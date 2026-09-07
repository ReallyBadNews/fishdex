# Load build_fish.py first in the same namespace.
def hook(x,y,z,size,steel):
 line('barbless hook',[(x,y,z),(x,y,z-size*.65)]+[(x+size*.4*(1-math.cos(t)),y,z-size*.65-size*.4*math.sin(t)) for t in [i*math.pi/24 for i in range(25)]]+[(x+size*.8,y,z-size*.3)],.012,steel)
def build_tackle(kind):
 scene=setup(kind);steel=mat('steel',(.45,.49,.51),.95,.22);red=mat('red accent',(.5,.05,.02),.25);gold=mat('brass',(.55,.35,.05),.9,.23);green=mat('green rubber',(.20,.30,.06),.0,.46);silver=mat('silver lure',(.6,.63,.58),.8,.26);black=mat('black eyes',(.006,.009,.006),.1,.2)
 if kind in ['worm','soft-plastic']:
  rubber=mat('worm skin',(.25,.07,.035) if kind=='worm' else (.17,.13,.025),0,.5)
  pts=[(-1+i/60*2,.09*math.sin(i/60*9),.22*math.sin(i/60*5)) for i in range(61)]
  line('flexible worm',pts,.065 if kind=='worm' else .10,rubber)
  for i in range(4,58):
   p=Vector(pts[i]);bpy.ops.mesh.primitive_torus_add(major_segments=16,minor_segments=6,location=p,major_radius=.066 if kind=='worm' else .10,minor_radius=.006);o=bpy.context.object;o.rotation_euler[1]=math.pi/2;o.data.materials.append(rubber)
  if kind=='worm':line('clitellum',pts[15:23],.084,rubber)
  else:hook(-.15,-.025,.13,.6,steel)
 elif kind=='minnow':
  oval('minnow',(-.08,0,0),(.77,.14,.2),silver);oval('back',(-.08,.01,.12),(.63,.11,.08),green)
  fin('tail',lambda t:(.6,0,(t-.5)*.08),[(.98-.12*(1-abs(2*t-1)),0,(2*t-1)*.29) for t in [i/10 for i in range(11)]],silver,steel)
  for side in [-1,1]:oval('eye',(-.57,side*.115,.07),(.035,.02,.035),black)
 elif kind=='jig':
  oval('painted jig head',(-.45,0,.1),(.23,.23,.23),red);hook(-.32,0,.1,.75,steel)
  for i in range(25):
   t=i*2*math.pi/25;line('skirt strand',[(-.28,.10*math.sin(t),.1+.10*math.cos(t)),(.12,.16*math.sin(t),.1+.15*math.cos(t)),(.7,.2*math.sin(t),-.13+.25*math.cos(t))],.018,green)
 elif kind=='spinner':
  line('wire shaft',[(-.95,0,0),(.8,0,0)],.014,steel)
  for x in [-.32,-.17,-.02]:oval('brass bead',(x,0,0),(.07,.07,.07),gold)
  blade=oval('spinning blade',(-.43,0,.34),(.39,.035,.2),gold);blade.rotation_euler[1]=-.45
  line('blade connection',[(-.7,0,0),(-.7,0,.17),(-.5,0,.25)],.013,steel);hook(.4,0,0,.45,steel)
 elif kind=='crankbait':
  oval('plug body',(0,0,.1),(.64,.21,.26),green);oval('belly',(0,0,-.025),(.58,.19,.15),silver)
  bill=oval('diving bill',(-.68,0,-.08),(.29,.16,.025),silver);bill.rotation_euler[1]=-.4
  for side in [-1,1]:oval('eye',(-.39,side*.182,.18),(.06,.025,.06),gold);oval('pupil',(-.405,side*.2,.18),(.03,.01,.03),black)
  for x in [.04,.57]:
   for angle in [0,2.1,4.2]:hook(x,math.sin(angle)*.03,-.15,.32,steel)
 elif kind=='frog':
  oval('frog body',(-.13,0,.02),(.48,.28,.18),green)
  for side in [-1,1]:
   oval('eye mound',(-.42,side*.17,.17),(.10,.09,.09),green);oval('eye',(-.45,side*.22,.20),(.045,.025,.04),gold);oval('pupil',(-.46,side*.237,.20),(.02,.015,.024),black)
   line('rubber leg',[(.18,side*.18,0),(.43,side*.4,.03),(.56,side*.3,-.05),(.91,side*.37,-.10)],.075,green)
   line('weedless hook',[(-.1,side*.28,0),(.31,side*.3,.1),(.19,side*.24,.18)],.012,steel)
 return finish(scene,kind)
