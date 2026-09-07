"""Original species studies for the Michigan inland sport-fish catalog.
Run through Blender MCP after build_fish.py. Dimensions are normalized artistic
proportions; specimens are not sexed individuals or scientific reconstructions.
Reference field marks and source links are recorded in docs/CATALOG.md.
"""
FAMILIES = {
 'sunfish': [(-1,.028,.04),(-.87,.10,.19),(-.66,.17,.34),(-.30,.205,.44),(.12,.19,.41),(.48,.12,.28),(.78,.046,.09),(.91,.035,.055)],
 'bass': [(-1.10,.045,.075),(-.97,.125,.18),(-.74,.20,.275),(-.40,.22,.325),(.02,.205,.30),(.44,.145,.215),(.78,.055,.09),(.94,.036,.065)],
 'perch': [(-1.09,.023,.035),(-.94,.10,.145),(-.68,.16,.255),(-.3,.18,.29),(.12,.16,.25),(.49,.11,.165),(.79,.045,.06),(.96,.025,.04)],
 'pike': [(-1.30,.080,.028),(-1.12,.112,.055),(-.93,.132,.105),(-.65,.15,.16),(-.27,.155,.18),(.14,.14,.16),(.55,.09,.115),(.83,.043,.052),(.98,.028,.036)],
 'crappie': [(-1.03,.025,.075),(-.86,.09,.21),(-.60,.15,.35),(-.22,.17,.41),(.16,.155,.37),(.52,.10,.25),(.81,.037,.075),(.94,.026,.053)],
 'catfish': [(-1.10,.115,.04),(-.99,.185,.135),(-.75,.235,.205),(-.43,.22,.25),(-.05,.19,.25),(.34,.14,.2),(.70,.065,.115),(.92,.029,.05)],
 'trout': [(-1.11,.025,.045),(-.96,.10,.135),(-.70,.17,.22),(-.30,.20,.265),(.14,.18,.255),(.50,.12,.19),(.79,.046,.071),(.96,.03,.05)],
}
# family, width scale, depth scale, body RGB, belly RGB, marking, dorsal spines
SPECS = {
 'bluegill':('sunfish',1,1,(.28,.40,.20),(.80,.43,.13),'bluegill',10),
 'bass':('bass',1,1,(.30,.42,.20),(.75,.77,.54),'bass',10),
 'pike':('pike',1,1,(.30,.40,.22),(.80,.81,.58),'pike',0),
 'smallmouth':('bass',.92,.94,(.48,.40,.23),(.78,.73,.51),'smallmouth',10),
 'yellow-perch':('perch',.95,1,(.68,.60,.20),(.88,.78,.43),'perch',13),
 'walleye':('perch',1.02,.86,(.43,.44,.23),(.83,.83,.62),'walleye',13),
 'pumpkinseed':('sunfish',.93,1.08,(.41,.51,.27),(.86,.43,.12),'pumpkinseed',10),
 'green-sunfish':('sunfish',1.10,.83,(.23,.40,.30),(.75,.72,.41),'green',10),
 'rock-bass':('sunfish',1.05,.85,(.42,.40,.25),(.80,.78,.60),'rock',11),
 'black-crappie':('crappie',1,1,(.62,.67,.52),(.87,.89,.79),'black-crappie',7),
 'white-crappie':('crappie',.98,.90,(.66,.70,.56),(.89,.91,.82),'white-crappie',6),
 'channel-catfish':('catfish',.86,.85,(.40,.48,.47),(.82,.84,.72),'channel',1),
 'flathead-catfish':('catfish',1.15,1.05,(.49,.43,.23),(.83,.77,.52),'flathead',1),
 'brown-bullhead':('catfish',1,1,(.38,.31,.20),(.79,.68,.44),'brown-bullhead',1),
 'yellow-bullhead':('catfish',.98,1,(.55,.45,.22),(.89,.80,.49),'yellow-bullhead',1),
 'black-bullhead':('catfish',1,.95,(.23,.27,.19),(.73,.72,.47),'black-bullhead',1),
 'muskie':('pike',1.02,1.05,(.61,.60,.39),(.85,.83,.64),'muskie',0),
 'brook-trout':('trout',.93,.90,(.29,.40,.28),(.86,.44,.22),'brook',0),
 'lake-trout':('trout',1,.95,(.34,.42,.35),(.84,.85,.69),'lake',0),
 'white-bass':('perch',1.05,1.18,(.64,.69,.64),(.90,.91,.84),'white-bass',9),
}
def color_image(kind, spec):
 family,_,_,rgb,bellyrgb,pattern,_=spec
 W,H=1536,768
 U,V=np.meshgrid((np.arange(W)+.5)/W,(np.arange(H)+.5)/H)
 T=V*2*np.pi; Z=np.sin(T); belly=np.clip((-Z-.15)*1.8,0,1)
 back=np.clip((Z-.05)*1.15,0,1)
 base=np.broadcast_to(np.array(rgb),(H,W,3)).copy()
 def mix(color,mask):
  nonlocal base
  a=np.clip(mask,0,1)[...,None];base=base*(1-a)+np.array(color)*a
 mix(bellyrgb,belly)
 mix(np.array(rgb)*.32,back*.83)
 side=1-np.abs(Z)**3
 if pattern=='bass':
  stripe=np.exp(-((Z+.02)/.18)**4)*(.70+.30*np.sin(U*90)**2)
  mix((.075,.105,.049),stripe*.92)
 if pattern in ('bluegill','smallmouth','perch','white-crappie'):
  count={'bluegill':7,'smallmouth':9,'perch':7,'white-crappie':8}[pattern]
  bars=np.maximum(0,np.cos((U-.12)*2*np.pi*count))**6
  fade=np.clip((U-.13)*7,0,1)*np.clip((.97-U)*10,0,1)
  if pattern=='perch':fade*=np.clip((Z+.80)*1.1,0,1)
  if pattern=='white-crappie':bars*=.5+.5*np.sin(T*31+U*112)**2
  mix(np.array(rgb)*.25,bars*fade*side*(.78 if pattern=='perch' else .5))
 if pattern=='white-bass':
  bands=np.exp(-((np.sin(T*11))/.16)**2)*side*np.clip((U-.18)*9,0,1)
  mix((.19,.23,.22),bands*.75)
 rng=np.random.default_rng(sum(ord(c) for c in kind))
 if pattern in ('pike','muskie','channel','black-crappie','rock','lake','brook','pumpkinseed','green','flathead','brown-bullhead','walleye'):
  count=100 if pattern in ('black-crappie','rock','lake') else 65
  if pattern in ('flathead','brown-bullhead','walleye'):
   m=(np.sin(U*31+np.sin(T*9))*np.sin(T*19+np.sin(U*48)))**2
   mix(np.array(rgb)*.42,np.clip((m-.35)*1.4,0,1)*side*.58)
  else:
   marks=np.zeros_like(U)
   for _ in range(count):
    x=rng.uniform(.20,.94);v=rng.uniform(0,1)
    rx=.009 if pattern in ('channel','rock','green') else .014
    ry=.012 if pattern=='pike' else .018
    if pattern=='muskie':rx=.006;ry=.035
    d=((U-x)/rx)**2+((V-v)/ry)**2
    marks=np.maximum(marks,np.exp(-(d**2)*2))
   if pattern in ('pike','lake','brook'):
    mix((.88,.86,.57),marks*side*.95)
   elif pattern=='pumpkinseed':mix((.78,.32,.13),marks*side*.8)
   elif pattern=='green':mix((.23,.68,.62),marks*side*.8)
   else:mix(np.array(rgb)*.20,marks*side*.95)
 if pattern=='brook':
  worms=np.exp(-(np.sin(U*140+np.sin(T*20)*2.4+np.sin(U*51+T*13)*1.5)/.22)**2)
  mix((.72,.72,.44),worms*np.clip((Z-.05)*1.8,0,1)*.7)
  for _ in range(26):
   x=rng.uniform(.26,.84);v=rng.choice([rng.uniform(.02,.13),rng.uniform(.36,.48)])
   d=((U-x)/.011)**2+((V-v)/.018)**2
   mix((.32,.55,.67),np.exp(-d)*side)
   mix((.86,.21,.11),np.exp(-d*3)*side)
 if pattern in ('bluegill','pumpkinseed','green'):
  cheek=np.clip((.29-U)*10,0,1)*side
  if pattern=='bluegill':mix((.08,.30,.36),cheek*.85)
  else:
   streak=np.exp(-(np.sin(T*23+U*28)/.20)**2)
   mix((.20,.66,.66),cheek*streak*.95)
 # Overlapping scales, removed entirely on scaleless catfish.
 rows=V*(95 if family=='trout' else 47);cols=U*(110 if family=='pike' else 61)+(np.floor(rows)%2)*.5
 arc=np.sqrt(((cols%1-.5)*1.15)**2+((rows%1-.5)*.85)**2)
 border=np.exp(-((arc-.45)/.035)**2);glint=np.exp(-((arc-.40)/.05)**2)
 if family!='catfish':base*=((1-.15*border+.08*glint)*(1-.012*np.cos(U*1300+T*410)))[...,None]
 # Subtle lateral line, interrupted at the head.
 lateral=np.exp(-((Z-.03)/.010)**2)*np.clip((U-.26)*10,0,1)
 if family!='catfish':base*=1-.12*lateral[...,None]
 rgba=np.concatenate([np.clip(base,0,1),np.ones((H,W,1))],axis=2).astype(np.float32)
 tex=bpy.data.images.new('Fishdex '+kind+' original pattern',width=W,height=H);tex.pixels.foreach_set(rgba.ravel());tex.pack()
 return tex

def sport_finish(scene,kind):
 objects=[o for o in scene.objects if o.type in ('MESH','CURVE')]
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name=kind+' specimen'
 bpy.ops.export_scene.gltf(filepath=ROOT+'/assets/models/'+kind+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_image_format='JPEG',export_jpeg_quality=88)
 bpy.ops.object.camera_add(location=(-.1,-4,.22));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.01))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.95;scene.camera=cam
 for loc,power,size in [((-1.8,-2.5,3),220,3),((1,1,2),160,2),((0,-1,-2),70,2)]:
  bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
 scene.cycles.samples=16;scene.cycles.use_denoising=True
 scene.render.resolution_x=1000;scene.render.resolution_y=620
 scene.render.filepath=ROOT+'/assets/specimens/'+kind+'.png'
 bpy.ops.render.render(write_still=True)
 return {'asset':kind,'objects':len(objects),'bytes':os.path.getsize(ROOT+'/assets/models/'+kind+'.glb')}

def build_sportfish(kind):
 spec=SPECS[kind];family,ws,hs,rgb,belly,pattern,spines=spec
 scene=setup('v2 '+kind);scene['fishdex_generated']=True;scene['species_id']=kind
 cfg=[(x,w*ws,h*hs) for x,w,h in FAMILIES[family]]
 if kind=='flathead-catfish':cfg=[(x,w*(1.15 if x<-.6 else 1),h*(.70 if x<-.6 else 1)) for x,w,h in cfg]
 if 'bullhead' in kind:cfg=[(x*.90,w,h) for x,w,h in cfg]
 def dims(x):
  x=max(cfg[0][0],min(cfg[-1][0],x))
  for idx,(a,b) in enumerate(zip(cfg,cfg[1:])):
   if a[0]<=x<=b[0]:
    dx=b[0]-a[0];t=(x-a[0])/dx;out=[]
    for k in (1,2):
     slope=(b[k]-a[k])/dx
     prev=(a[k]-cfg[idx-1][k])/(a[0]-cfg[idx-1][0]) if idx else slope
     nxt=(cfg[idx+2][k]-b[k])/(cfg[idx+2][0]-b[0]) if idx<len(cfg)-2 else slope
     m0=2*prev*slope/(prev+slope) if prev*slope>0 else 0
     m1=2*nxt*slope/(nxt+slope) if nxt*slope>0 else 0
     out.append((2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*dx*m0+(-2*t**3+3*t*t)*b[k]+(t**3-t*t)*dx*m1)
    return out
  return cfg[-1][1:]
 def surface(x,z,side):
  w,h=dims(x);return Vector((x,side*w*math.sqrt(max(.005,1-(z/h)**2)),z))
 dark=mat(kind+' shadow',(.025,.035,.026),0,.5)
 skin=mat(kind+' jaw',tuple(np.array(rgb)*.76),.08,.40)
 pale=mat(kind+' fin edge',(.88,.89,.70),.05,.48)
 fincolor=tuple(np.array(rgb)*.74)
 finmat=mat(kind+' fin membrane',fincolor,.05,.50)
 lowerfin=mat(kind+' lower fin membrane',(.52,.26,.10),.05,.50) if family=='trout' or kind=='yellow-perch' else finmat
 rays=mat(kind+' fin rays',tuple(np.array(fincolor)*.56),.05,.46)
 bodymat=mat(kind+' skin',rgb,.12 if family!='catfish' else .03,.46)
 nt=bodymat.node_tree;shader=nt.nodes.get('Principled BSDF');image=nt.nodes.new('ShaderNodeTexImage');image.image=color_image(kind,spec);nt.links.new(image.outputs['Color'],shader.inputs['Base Color'])
 verts=[];faces=[];nx=128;nr=64
 for i in range(nx+1):
  x=cfg[0][0]+(cfg[-1][0]-cfg[0][0])*i/nx;w,h=dims(x)
  for j in range(nr):
   a=j*2*math.pi/nr;verts.append((x,w*math.cos(a),h*math.sin(a)))
 for i in range(nx):
  for j in range(nr):a=i*nr+j;b=i*nr+(j+1)%nr;faces.append((a,b,b+nr,a+nr))
 faces.extend([tuple(range(nr-1,-1,-1)),tuple(nx*nr+j for j in range(nr))])
 body=mesh(kind+' body',verts,faces,bodymat);uv=body.data.uv_layers.new(name='SpecimenUV')
 for polygon in body.data.polygons:
  js=[body.data.loops[l].vertex_index%nr for l in polygon.loop_indices];seam=max(js)-min(js)>nr/2
  for l in polygon.loop_indices:
   index=body.data.loops[l].vertex_index;i=index//nr;j=index%nr;uv.data[l].uv=(i/nx,1 if seam and j==0 else j/nr)
 ex= {'sunfish':-.80,'bass':-.85,'perch':-.88,'pike':-.89,'crappie':-.82,'catfish':-.91,'trout':-.89}[family]
 if 'bullhead' in kind:ex*=.90
 ez=dims(ex)[1]*(.46 if family!='catfish' else .35)
 er=.045 if kind=='walleye' else (.025 if family=='catfish' else .034)
 iris=mat(kind+' iris',(.56,.13,.035) if kind=='rock-bass' else ((.56,.58,.46) if kind=='walleye' else (.50,.39,.16)),.3,.32)
 pupil=mat(kind+' pupil',(.006,.011,.014),.05,.16)
 for side in (-1,1):
  ep=surface(ex,ez,side);normal=Vector((-.28,side,.22)).normalized()
  # Eye shells sit in the head surface instead of projecting from its full width.
  for name,offset,size,material in [('eye socket',-.003,(er*1.18,.010,er*1.18),dark),('iris',.002,(er,.008,er),iris),('pupil',.010,(er*.60,.005,er*.66),pupil)]:
   eye=oval(kind+' '+name,ep+normal*offset,size,material);eye.rotation_mode='QUATERNION';eye.rotation_quaternion=Vector((0,side,0)).rotation_difference(normal)
  gx=-.52 if family!='pike' else -.59
  gill=[]
  for t in np.linspace(-1.15,1.15,48):
   x=gx+.12*math.cos(t);z=dims(gx)[1]*.82*math.sin(t);pt=surface(x,z,side);pt.y+=side*.0025;gill.append(tuple(pt))
  line(kind+' operculum',gill,.0021,dark)
  mouthend=ex+(.13 if kind=='bass' or family in ('pike','trout') else -.005)
  if kind in ('bluegill','pumpkinseed'):mouthend=-.875
  jaw=[]
  for t in np.linspace(0,1,36):
   x=cfg[0][0]+(mouthend-cfg[0][0])*t
   drop=.12 if kind=='bass' else (.08 if family in ('bass','trout','perch','crappie') else .04)
   z=.012-drop*t**.8;pt=surface(x,z,side);pt.y+=side*.002;jaw.append(tuple(pt))
  line(kind+' mouth crease',jaw,.0032,dark)
  line(kind+' lower lip',[(x,y,z-.007) for x,y,z in jaw[:29]],.0035,skin)
  # Gill tabs on sunfish lie flush with the gill cover.
  if kind in ('bluegill','pumpkinseed','green-sunfish'):
   pt=surface(-.48,.06,side);pt.y+=side*.003
   oval(kind+' ear flap',pt,(.061,.006,.037),dark)
   if kind=='pumpkinseed':oval(kind+' red ear tip',(pt.x+.046,pt.y+side*.003,pt.z),(.019,.005,.028),mat('red ear',(.74,.15,.04)))
  if kind=='smallmouth':
   for n in range(3):
    pts=[]
    for t in np.linspace(0,1,30):
     x=ex+.025+.24*t;z=ez-.035-n*.045-.075*t;pt=surface(x,z,side);pt.y+=side*.002;pts.append(tuple(pt))
    line('bronze cheek streak',pts,.0035,skin)
  px=-.45 if family!='catfish' else -.58;pw,ph=dims(px)
  length=.35 if family!='catfish' else .27
  tip=[(px+.04+length*t,side*(pw+.025+.095*math.sin(t*math.pi)),-.065-.20*math.sin(t*math.pi*.80)) for t in np.linspace(0,1,13)]
  fin(kind+' pectoral',lambda t:(px+.025*t,side*pw*.97,-.055-.055*t),tip,lowerfin,rays)
  px=.02 if family in ('pike','trout','catfish') else -.18;pw,ph=dims(px)
  edge=[(px+.04+t*.23,side*(pw*.65+.08),-ph-.14*math.sin(t*math.pi)) for t in np.linspace(0,1,11)]
  fin(kind+' pelvic',lambda t:(px+t*.10,side*pw*.53,-ph*.85),edge,lowerfin,rays)
  if family=='trout':line('white pelvic leading edge',[tuple(Vector((px,side*pw*.53,-ph*.85)).lerp(Vector(edge[2]),t)) for t in np.linspace(0,1,8)],.006,pale)
  if family=='catfish':
   whisker=mat(kind+' chin barbels',(.76,.73,.52) if kind=='yellow-bullhead' else (.14,.15,.10),0,.58)
   # Four pairs: nasal, maxillary, and two pairs on the chin.
   nose=cfg[0][0];nw,nh=dims(nose+.10)
   for idx in range(4):
    x=nose+.045+idx*.043;z=.052 if idx==0 else (-.035 if idx>1 else .005);yw=nw*(.55 if idx>1 else .88)
    reach=.30 if idx==1 else .15
    line(kind+' sensory barbel',[(x,side*yw,z),(x+.035,side*(yw+reach*.45),z-.035),(x+.15,side*(yw+reach),z-.12)],.005 if idx==1 else .0037,whisker)
 # Soft-rayed dorsal sections and true separate spiny dorsal in perch/white bass.
 def dorsal(start,end,height,spine_count=0):
  if spine_count:
   edge=[]
   for i in range(spine_count*2-1):
    t=i/(spine_count*2-2);x=start+(end-start)*t;raiseh=height*(.35+.65*math.sin(t*math.pi)**.6)*(1 if i%2==0 else .78)
    edge.append((x,0,dims(x)[1]+raiseh))
  else:edge=[(start+(end-start)*t,0,dims(start+(end-start)*t)[1]+height*math.sin(t*math.pi)**.55+.006) for t in np.linspace(0,1,18)]
  fin(kind+' dorsal',lambda t:(start+(end-start)*t,0,dims(start+(end-start)*t)[1]*.96),edge,finmat,rays)
 if family=='pike':dorsal(.42,.83,.25)
 elif family=='catfish':
  dorsal(-.43,-.11,.28,3)
  # Adipose fins have a smooth, rayless membrane.
  pts=[(.35,0,dims(.35)[1]*.94),(.72,0,dims(.72)[1]*.94)]+[(.72-.37*t,0,dims(.72-.37*t)[1]+.065*math.sin(math.pi*t)**.6) for t in np.linspace(0,1,24)]
  ob=mesh(kind+' adipose',pts,[tuple(range(len(pts)))],finmat);ob.modifiers.new('adipose thickness','SOLIDIFY').thickness=.01
 elif family=='trout':
  dorsal(-.16,.24,.26)
  pts=[(.58,0,dims(.58)[1]*.94),(.78,0,dims(.78)[1]*.94)]+[(.78-.20*t,0,dims(.78-.20*t)[1]+.075*math.sin(math.pi*t)**.65) for t in np.linspace(0,1,24)]
  ob=mesh(kind+' adipose',pts,[tuple(range(len(pts)))],finmat);ob.modifiers.new('adipose thickness','SOLIDIFY').thickness=.01
 elif family=='perch':
  dorsal(-.57,.01,.20,spines);dorsal(.16,.66,.20)
 elif family=='bass':
  dorsal(-.56,.05,.14,spines);dorsal(.05,.69,.23)
 else:
  start=-.35 if family=='crappie' else -.55
  dorsal(start,.12,.15,spines);dorsal(.12,.72,.22)
 ast=.15 if family=='crappie' else (.03 if family=='catfish' else .34);end=.80
 if family=='pike':ast=.48;end=.86
 ah=.22 if family=='crappie' else .17
 edge=[(ast+(end-ast)*t,0,-dims(ast+(end-ast)*t)[1]-ah*math.sin(t*math.pi)**.7) for t in np.linspace(0,1,20)]
 fin(kind+' anal',lambda t:(ast+(end-ast)*t,0,-dims(ast+(end-ast)*t)[1]*.96),edge,lowerfin,rays)
 if family=='trout' or kind=='walleye':line(kind+' anal white edge',[(ast,0,-dims(ast)[1]),edge[2],edge[4]],.006,pale)
 tx=cfg[-1][0];th=.27 if family!='pike' else .23
 fork=.18 if kind in ('channel-catfish','lake-trout','white-bass') else (.11 if family in ('pike','perch') else .065)
 if kind=='flathead-catfish' or 'bullhead' in kind or kind=='brook-trout':fork=.018
 edge=[(tx+.22+fork*abs(2*t-1),0,(2*t-1)*th) for t in np.linspace(0,1,27)]
 fin(kind+' caudal',lambda t:(tx-.02,0,(t-.5)*.09),edge,finmat,rays)
 if kind=='walleye':
  fin('white lower tail tip',lambda t:(tx+.22+fork-.08,0,-th+.055),edge[:5],pale,pale)
 if kind=='bluegill':
  for side in (-1,1):oval('soft dorsal dark spot',(.53,side*.004,dims(.53)[1]+.095),(.047,.003,.032),dark)
 if kind=='walleye':
  for side in (-1,1):oval('spiny dorsal dark patch',(-.065,side*.004,dims(-.065)[1]+.055),(.041,.003,.046),dark)
 return sport_finish(scene,kind)
