"""Original Fishdex reference models. Blender 5.2; DNR anatomical field marks.
These first-pass models require further anatomical/art review, not scientific certification.
Run in Blender through MCP. Each asset gets its own scene; existing scenes are preserved.
"""
import bpy, math, os, random
import numpy as np
from mathutils import Vector
ROOT='/Users/clawd/github.com/ReallyBadNews/fishdex'
random.seed(7)
def mat(name,color,metal=0.0,rough=.38):
 m=bpy.data.materials.new('Fishdex '+name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 return m
def mesh(name,verts,faces,material):
 me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob); me.materials.append(material)
 for p in me.polygons:p.use_smooth=True
 return ob
def oval(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc); o=bpy.context.object;o.name=name;o.scale=scale; o.data.materials.append(material)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 return o
def line(name,pts,radius,material):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=radius;cu.bevel_resolution=2
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(material);return o
def fin(name,base,edge,material,rays):
 # Fan of flexible rays with curved membrane between them.
 vs=[];fs=[];N=len(edge)
 for i,e in enumerate(edge):
  b=Vector(base(i/(N-1)));v=Vector(e)
  for j in range(5):
   t=j/4;pt=b.lerp(v,t);pt.y+=.009*math.sin(t*math.pi);vs.append(tuple(pt))
  line(name+' ray', [tuple(b.lerp(v,t/4)) for t in range(5)],.0024,rays)
 for i in range(N-1):
  for j in range(4):a=i*5+j;fs.append((a,a+5,a+6,a+1))
 ob=mesh(name,vs,fs,material);sol=ob.modifiers.new('Fin membrane','SOLIDIFY');sol.thickness=.0015
 return ob
def setup(name):
 scene=bpy.data.scenes.new('Fishdex '+name);bpy.context.window.scene=scene
 scene.render.engine='CYCLES';scene.cycles.samples=24
 scene.world=bpy.data.worlds.new('Fishdex studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.38,.3,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
 scene.render.resolution_x=1200;scene.render.resolution_y=760;scene.render.resolution_percentage=100;scene.render.film_transparent=True
 scene.view_settings.view_transform='AgX'
 return scene
def finish(scene,name):
 objects=[o for o in scene.objects if o.type in ('MESH','CURVE')]
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.object.convert(target='MESH')
 bpy.ops.export_scene.gltf(filepath=ROOT+'/assets/models/'+name+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_attributes=True,export_image_format='JPEG',export_jpeg_quality=90)
 bpy.ops.object.camera_add(location=(-.15,-3.8,.48));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.02))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.9;scene.camera=cam
 for loc,power,size in [((-1.8,-2.5,3),190,3),((1,1,2),150,2),((0,-1,-2),45,2)]:
  bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=ROOT+'/assets/specimens/'+name+'.png'
 bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/assets/models/fishdex-source.blend',copy=True)
 bpy.ops.render.render(write_still=True)
 return {'asset':name,'objects':len(objects),'glb_bytes':os.path.getsize(ROOT+'/assets/models/'+name+'.glb')}
def build_fish(kind):
 scene=setup(kind)
 dark=mat('dark olive',(.018,.032,.022));gold=mat('iris',(.38,.29,.09),.45);pupil=mat('pupil',(.004,.007,.009),.05,.15);silver=mat('gill highlight',(.26,.34,.23),.25)
 finmat=mat('amber fin',(.27,.25,.10),.05,.5);rays=mat('fin rays',(.11,.14,.055),.12,.4)
 configs={
 'bluegill':[(-1.0,.025,.025),(-.86,.14,.22),(-.64,.23,.37),(-.30,.25,.46),(.1,.22,.43),(.48,.13,.29),(.78,.055,.09),(.93,.035,.06)],
 'bass':[(-1.13,.035,.09),(-.99,.14,.19),(-.76,.22,.28),(-.44,.24,.34),(0,.21,.32),(.42,.14,.24),(.76,.065,.105),(.94,.04,.075)],
 'pike':[(-1.25,.06,.04),(-1.12,.11,.065),(-.91,.14,.12),(-.67,.15,.18),(-.32,.17,.20),(.15,.155,.18),(.55,.10,.135),(.83,.05,.06),(.98,.035,.04)]}
 cfg=configs[kind]
 def dims(x):
  for a,b in zip(cfg,cfg[1:]):
   if a[0]<=x<=b[0]:
    idx=cfg.index(a);dx=b[0]-a[0];t=(x-a[0])/dx;out=[]
    for k in [1,2]:
     slope=(b[k]-a[k])/dx
     prev=(a[k]-cfg[max(0,idx-1)][k])/(a[0]-cfg[max(0,idx-1)][0]) if idx else slope
     nxt=(cfg[min(len(cfg)-1,idx+2)][k]-b[k])/(cfg[min(len(cfg)-1,idx+2)][0]-b[0]) if idx<len(cfg)-2 else slope
     m0=2*prev*slope/(prev+slope) if prev*slope>0 else 0
     m1=2*nxt*slope/(nxt+slope) if nxt*slope>0 else 0
     out.append((2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*dx*m0+(-2*t**3+3*t*t)*b[k]+(t**3-t*t)*dx*m1)
    return tuple(out)
  return cfg[-1][1:]
 bodymat=mat(kind+' scales',(.3,.4,.2),.08,.52);nt=bodymat.node_tree;p=nt.nodes.get('Principled BSDF');attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='Color';nt.links.new(attr.outputs['Color'],p.inputs['Base Color'])
 verts=[];faces=[];cols=[];nx=180;nr=80
 for i in range(nx+1):
  x=cfg[0][0]+(cfg[-1][0]-cfg[0][0])*i/nx;w,h=dims(x)
  for j in range(nr):
   t=2*math.pi*j/nr;y=w*math.cos(t);z=h*math.sin(t);verts.append((x,y,z))
   v=math.sin(t); belly=max(0,min(1,(-v-.05)*1.8));back=max(0,v)
   base=Vector((.26,.33,.105)) if kind=='bluegill' else Vector((.19,.27,.10))
   base=base.lerp(Vector((.60,.60,.36)),belly).lerp(Vector((.042,.075,.031)),back*.85)
   # Tiny overlapping scale cells, baked as vertex colors for fully offline rendering.
   scale=.91+.09*math.sin(x*160+math.sin(t*40))**2;base*=scale
   if kind=='bluegill':
    bars=max(0,math.cos((x+.10)*24))**10; base*=1-.38*bars*(1-abs(v)*.5)
    if x<-.48 and v<.4:base=base.lerp(Vector((.08,.27,.28)),.6*(1-belly))
    if -.6<x<.2:base=base.lerp(Vector((.56,.28,.052)),belly*.72)
   elif kind=='bass':
    stripe=math.exp(-((v+.02)/.18)**4)*(.7+.3*math.sin(x*46)**2);base*=1-.77*stripe
   else:
    spots=max(0,math.cos(x*42+math.sin(t*7)*1.4))*max(0,math.cos(t*18+x*3));spot=max(0,min(1,(spots-.52)*5))*(1-abs(v)**3)
    base=base.lerp(Vector((.65,.64,.32)),spot*.9)
   cols.append((*base,1))
 for i in range(nx):
  for j in range(nr):a=i*nr+j;b=i*nr+(j+1)%nr;faces.append((a,b,b+nr,a+nr))
 faces.extend([tuple(range(nr-1,-1,-1)),tuple(nx*nr+j for j in range(nr))])
 body=mesh(kind+' body',verts,faces,bodymat);attribute=body.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
 for i,c in enumerate(cols):attribute.data[i].color=c
 # Bake original detailed scale coloration to a compact UV texture.
 W,H=2048,1024;U,V=np.meshgrid((np.arange(W)+.5)/W,(np.arange(H)+.5)/H)
 X=cfg[0][0]+(cfg[-1][0]-cfg[0][0])*U;T=V*2*np.pi;v=np.sin(T)
 belly=np.clip((-v-.05)*1.8,0,1)[...,None];back=np.clip(v,0,1)[...,None]
 base=np.broadcast_to(np.array([.26,.33,.105] if kind=='bluegill' else [.19,.27,.10]),(H,W,3)).copy()
 base=base*(1-belly)+np.array([.66,.65,.40])*belly
 base=base*(1-back*.85)+np.array([.035,.064,.024])*back*.85
 if kind=='bluegill':
  bars=np.maximum(0,np.cos((X+.1)*21))**8;base*=1-.48*bars[...,None]*(1-np.abs(v[...,None])*.5)
  cheek=(np.clip((-.30-X)/.35,0,1)*np.clip((.55-v)/.45,0,1))[...,None]*.62*(1-belly);base=base*(1-cheek)+np.array([.035,.22,.29])*cheek
  chest=np.exp(-((X+.28)/.49)**4)[...,None]*belly*.8;base=base*(1-chest)+np.array([.70,.29,.035])*chest
 elif kind=='bass':
  stripe=np.exp(-((v+.02)/.18)**4)*(.78+.22*np.sin(X*46)**2);base*=1-.82*stripe[...,None]
 else:
  spot=np.clip((np.maximum(0,np.cos(X*42+np.sin(T*7)*1.4))*np.maximum(0,np.cos(T*18+X*3))-.52)*5,0,1)*(1-np.abs(v)**3)
  base=base*(1-spot[...,None]*.9)+np.array([.65,.64,.32])*spot[...,None]*.9
 rows=V*65;cols=U*(90 if kind=='pike' else 57)+(np.floor(rows)%2)*.5
 cellx=cols%1-.5;celly=rows%1-.5;arc=np.sqrt((cellx*1.2)**2+(celly*.85)**2)
 border=np.exp(-((arc-.46)/.033)**2);glint=np.exp(-((arc-.40)/.045)**2)
 base*=((1-.25*border+.14*glint)*(1-.02*np.cos(X*1300+T*410)))[...,None]
 rgba=np.concatenate([np.clip(base,0,1),np.ones((H,W,1))],axis=2).astype(np.float32)
 tex=bpy.data.images.new('Fishdex '+kind+' scale texture',width=W,height=H);tex.pixels.foreach_set(rgba.ravel());tex.pack()
 nt.links.remove(p.inputs['Base Color'].links[0]);image_node=nt.nodes.new('ShaderNodeTexImage');image_node.image=tex;nt.links.new(image_node.outputs['Color'],p.inputs['Base Color'])
 uv=body.data.uv_layers.new(name='SpecimenUV')
 for polygon in body.data.polygons:
  js=[body.data.loops[l].vertex_index%nr for l in polygon.loop_indices]
  seam=max(js)-min(js)>nr/2
  for l in polygon.loop_indices:
   index=body.data.loops[l].vertex_index;i=index//nr;j=index%nr
   uv.data[l].uv=(i/nx,1 if seam and j==0 else j/nr)
 # Symmetrical eyes, visible gill-cover margins, and jaw seam.
 ex={'bluegill':-.79,'bass':-.88,'pike':-.91}[kind];ez={'bluegill':.13,'bass':.13,'pike':.055}[kind];ew,_=dims(ex)
 for side in [-1,1]:
  eye=oval('eye', (ex,side*(ew+.008),ez),(.047,.020,.047),gold)
  oval('pupil',(ex-.004,side*(ew+.030),ez),(.028,.008,.029),pupil)
  oval('eye reflection',(ex-.017,side*(ew+.04),ez+.02),(.006,.003,.007),silver)
  gx={'bluegill':-.53,'bass':-.49,'pike':-.57}[kind];gw,gh=dims(gx)
  gill=[]
  for t in [-1.1+i*2.2/40 for i in range(41)]:
   xg=gx+.13*math.cos(t);wg,hg=dims(xg);zg=gh*math.sin(t)*.78;yg=wg*math.sqrt(max(.01,1-(zg/hg)**2))+.004;gill.append((xg,side*yg,zg))
  line('gill cover',gill,.0028,dark)
  if kind=='bluegill':oval('black ear flap',(-.49,side*.241,.08),(.065,.006,.043),dark)
  mouthend=ex+.10 if kind!='bluegill' else -.86
  jaw=[]
  for i in range(30):
   tj=i/29;xj=cfg[0][0]+(mouthend-cfg[0][0])*tj;wj,hj=dims(xj);zj=-.015-.045*math.sin(tj*math.pi)+.05*tj;yj=wj*math.sqrt(max(.01,1-(zj/hj)**2))+.003;jaw.append((xj,side*yj,zj))
  line('jaw seam',jaw,.0035,dark)
  # Long pectorals and paired pelvic fins.
  px=-.47 if kind!='pike' else -.5;pw,ph=dims(px)
  fin('pectoral',lambda t:(px,side*pw,-.045),[(px+.08+.38*t,side*(pw+.07+.07*math.sin(t*math.pi)),-.06-.18*math.sin(t*math.pi*.8)) for t in [i/10 for i in range(11)]],finmat,rays)
  px=-.12 if kind!='pike' else .07;pw,ph=dims(px)
  fin('pelvic',lambda t:(px+t*.12,side*pw*.55,-ph*.85),[(px+.08+t*.20,side*(pw+.09),-ph-.13*math.sin(t*math.pi)) for t in [i/8 for i in range(9)]],finmat,rays)
 # Species-specific dorsal: bluegill connected, bass deep notch, pike far rear.
 start,end={'bluegill':(-.56,.71),'bass':(-.58,.72),'pike':(.40,.83)}[kind]
 N=28 if kind!='pike' else 15;edge=[]
 for i in range(N):
  t=i/(N-1);x=start+(end-start)*t;h=dims(x)[1]
  if kind=='bluegill':height=(.12+.08*math.sin(t*math.pi))*(.70 if i%2 and t<.52 else 1)
  elif kind=='bass':height=(.14 if t<.47 else (.035 if t<.57 else .23*math.sin((t-.55)/.45*math.pi))) * (.76 if i%2 and t<.5 else 1)
  else:height=.26*math.sin(t*math.pi)**.6
  edge.append((x,0,h+max(.015,height)))
 fin('dorsal',lambda t:(start+(end-start)*t,0,dims(start+(end-start)*t)[1]*.95),edge,finmat,rays)
 if kind=='bluegill':
  for side in [-1,1]:oval('dorsal dark spot',(.5,side*.005,.36),(.045,.0015,.027),dark)
 ast,aend={'bluegill':(.2,.75),'bass':(.32,.78),'pike':(.47,.86)}[kind]
 fin('anal',lambda t:(ast+(aend-ast)*t,0,-dims(ast+(aend-ast)*t)[1]*.95),[(ast+(aend-ast)*t,0,-dims(ast+(aend-ast)*t)[1]-.19*math.sin(t*math.pi)) for t in [i/12 for i in range(13)]],finmat,rays)
 tx=cfg[-1][0];height={'bluegill':.29,'bass':.28,'pike':.23}[kind]
 fin('caudal',lambda t:(tx-.015,0,(t-.5)*.10),[(tx+.23+.095*abs(2*t-1),0,(2*t-1)*height) for t in [i/20 for i in range(21)]],finmat,rays)
 return finish(scene,kind)
