"""Version 3 specimen studies. Load after the four existing modeling scripts.
Preserves every previous scene. Builds editable source scenes separately from
joined runtime copies; no scene/data deletion. Deterministic original textures.
"""
import json, hashlib
from pathlib import Path
_BASE_SETUP = setup
_BASE_MAT = mat
_BASE_OVAL = oval
_BASE_LINE = line
_ACTIVE_KIND = ''
_FIN_MATERIALS = {}
_MATERIAL_BY_NAME = {}


def noise2(u, v, seed=0):
    """Smooth deterministic lattice noise, periodic around the body seam."""
    x=np.floor(u); y=np.floor(v); a=u-x; b=v-y
    a=a*a*(3-2*a); b=b*b*(3-2*b)
    def h(i,j):
        q=np.sin(i*127.1+j*311.7+seed*74.7)*43758.5453
        return q-np.floor(q)
    return (h(x,y)*(1-a)+h(x+1,y)*a)*(1-b)+(h(x,y+1)*(1-a)+h(x+1,y+1)*a)*b


def packed_image(name, rgb, noncolor=False):
    H,W=rgb.shape[:2]
    rgba=np.concatenate([rgb,np.ones((H,W,1))],axis=2).astype(np.float32)
    image=bpy.data.images.new('Fishdex v3 '+name,width=W,height=H)
    if noncolor:image.colorspace_settings.name='Non-Color'
    image.pixels.foreach_set(rgba.ravel());image.pack()
    return image


def skin_maps(kind,spec):
    family,_,_,rgb,bellyrgb,pattern,_=spec
    W,H=1536,768
    U,V=np.meshgrid((np.arange(W)+.5)/W,(np.arange(H)+.5)/H)
    T=V*2*np.pi; Z=np.sin(T); side=1-np.abs(Z)**4
    seed=sum(map(ord,kind)); rng=np.random.default_rng(seed)
    # Low-frequency, asymmetric pigment breakup keeps field marks readable.
    n=noise2(U*23,np.cos(T)*7+np.sin(T)*9,seed)
    fine=noise2(U*165,np.cos(T)*71+np.sin(T)*93,seed+7)
    warp=(n-.5)*.016
    base=np.broadcast_to(np.array(rgb),(H,W,3)).copy()
    def mix(c,m):
        nonlocal base
        a=np.clip(m,0,1)[...,None];base=base*(1-a)+np.array(c)*a
    mix(np.array(rgb)*.28,np.clip((Z-.18)*1.25,0,1)*.88)
    mix(np.maximum(np.array(bellyrgb),(.79,.76,.61)),np.clip((-Z-.12)*1.55,0,1))
    if kind in ('bluegill','pumpkinseed','brook-trout'):
        mix(bellyrgb,np.clip((-Z-.25)*1.25,0,1)*np.exp(-((U-.35)/.28)**4)*.85)
    if pattern=='bass':
        stripe=np.exp(-((Z+.015+(n-.5)*.15)/.14)**4)
        blocks=.52+.48*np.clip((noise2(U*33,np.cos(T)*4,seed)-.32)*3,0,1)
        mix((.075,.115,.075),stripe*blocks*.91)
        mix((.12,.18,.09),np.exp(-((Z-.26)/.3)**2)*(n>.62)*.18)
    if pattern in ('bluegill','smallmouth','perch','white-crappie'):
        count={'bluegill':7,'smallmouth':8,'perch':7,'white-crappie':8}[pattern]
        bars=np.maximum(0,np.cos((U+warp-.12)*2*np.pi*count))**(3 if pattern=='perch' else 5)
        fade=np.clip((U-.15)*8,0,1)*np.clip((.96-U)*12,0,1)
        bars*=.60+.40*noise2(U*55,np.sin(T)*16,seed+9)
        if pattern=='perch':fade*=np.clip((Z+.6)*1.5,0,1)
        mix(np.array(rgb)*.22,bars*fade*side*(.9 if pattern=='perch' else .63))
    if pattern=='white-bass':
        bands=np.exp(-((np.sin(T*11+warp*3))/.15)**2)*side*np.clip((U-.2)*9,0,1)
        mix((.14,.19,.18),bands*.80)
    if pattern in ('pike','muskie','channel','black-crappie','rock','lake','brook','pumpkinseed','green'):
        marks=np.zeros_like(U)
        count=210 if pattern=='black-crappie' else (115 if pattern in ('lake','rock') else 72)
        for _ in range(count):
            x=rng.uniform(.19,.96);v=rng.uniform(0,1)
            rx=rng.uniform(.005,.014);ry=rng.uniform(.009,.019)
            if pattern=='pike':rx*=1.4;ry*=.75
            if pattern=='muskie':rx*=.6;ry*=2.5
            delta=np.minimum(np.abs(V-v),1-np.abs(V-v))
            d=((U+warp-x)/rx)**2+(delta/ry)**2
            marks=np.maximum(marks,np.exp(-d*d*1.6))
        if pattern in ('pike','lake','brook'):mix((.83,.82,.60),marks*side*.95)
        elif pattern=='pumpkinseed':mix((.75,.29,.11),marks*side*.85)
        elif pattern=='green':mix((.22,.63,.58),marks*side*.75)
        else:mix(np.array(rgb)*.15,marks*side*.88)
    if pattern in ('flathead','brown-bullhead','walleye','black-bullhead'):
        mix(np.array(rgb)*.25,np.clip((n-.43)*2.4,0,1)*side*(.20 if pattern=='walleye' else .72))
        mix(np.array(rgb)*1.35,np.clip((.39-n)*2,0,1)*side*(.12 if pattern=='walleye' else .4))
    if pattern=='brook':
        worms=np.exp(-(np.sin(U*137+np.sin(T*23)*2.5+(n-.5)*7)/.21)**2)
        mix((.68,.69,.43),worms*np.clip((Z-.03)*1.8,0,1)*.80)
        for _ in range(30):
            x=rng.uniform(.24,.88);v=rng.choice([rng.uniform(.01,.12),rng.uniform(.38,.49)])
            d=((U-x)/.007)**2+((V-v)/.013)**2
            mix((.31,.51,.65),np.exp(-d)*side)
            mix((.81,.17,.075),np.exp(-d*3.5)*side)
    cheek=np.clip((.30-U)*10,0,1)*side
    if pattern=='bluegill':mix((.07,.29,.36),cheek*.8)
    if pattern in ('pumpkinseed','green'):
        streak=np.exp(-(np.sin(T*24+U*32+warp*30)/.22)**2)
        mix((.20,.63,.61),cheek*streak*.9)
    base*= (1+(n-.5)*.12+(fine-.5)*.045)[...,None]
    # Fine overlapping scale margins follow the flank, fading over the head.
    rows=V*(90 if family=='trout' else 52)
    cols=U*(105 if family in ('pike','trout') else 68)+(np.floor(rows)%2)*.5
    cx=cols%1-.5;cy=rows%1-.5
    arc=np.sqrt((cx*1.16)**2+(cy*.83)**2)
    margin=np.exp(-((arc-.45)/.035)**2)
    scales=np.clip((U-.23)*9,0,1) if family!='catfish' else np.zeros_like(U)
    base*=(1-margin*scales*.085)[...,None]
    lateral=np.exp(-((Z-.02)/.009)**2)*np.clip((U-.26)*12,0,1)
    if family!='catfish':base*=1-lateral[...,None]*.12
    # Tangent-space relief, supported by both Blender and offline glTF.
    height=(-margin*.15+np.exp(-((arc-.36)/.16)**2)*.10)*scales+(fine-.5)*.045
    height=height[::2,::2]
    dy,dx=np.gradient(height)
    normal=np.stack([-dx*1.8,-dy*1.8,np.ones_like(dx)],axis=2)
    normal/=np.linalg.norm(normal,axis=2,keepdims=True)
    return packed_image(kind+' pigment',np.clip(base,0,1)),packed_image(kind+' microrelief',normal*.5+.5,True)


def color_image(kind,spec):
    color,normal=skin_maps(kind,spec)
    material=_MATERIAL_BY_NAME[kind+' skin']
    nt=material.node_tree;p=nt.nodes.get('Principled BSDF')
    tex=nt.nodes.new('ShaderNodeTexImage');tex.image=normal
    normal_node=nt.nodes.new('ShaderNodeNormalMap');normal_node.inputs['Strength'].default_value=.30
    nt.links.new(tex.outputs['Color'],normal_node.inputs['Color']);nt.links.new(normal_node.outputs['Normal'],p.inputs['Normal'])
    return color


def mat(name,color,metal=0,rough=.38):
    if _ACTIVE_KIND=='lake-trout' and 'lower fin membrane' in name:color=(.25,.33,.30)
    m=_BASE_MAT('v3 '+name,color,metal,rough);p=m.node_tree.nodes.get('Principled BSDF')
    if 'skin' in name or 'jaw' in name:
        p.inputs['Metallic'].default_value=.02
        p.inputs['Roughness'].default_value=.36
        p.inputs['Coat Weight'].default_value=.18;p.inputs['Coat Roughness'].default_value=.20
    if 'iris' in name or 'pupil' in name:
        p.inputs['Metallic'].default_value=.06;p.inputs['Roughness'].default_value=.15
        p.inputs['Coat Weight'].default_value=.50;p.inputs['Coat Roughness'].default_value=.08
    if 'polished stainless' in name:
        p.inputs['Base Color'].default_value=(.64,.68,.70,1);p.inputs['Metallic'].default_value=1;p.inputs['Roughness'].default_value=.19
    if 'brass' in name:p.inputs['Metallic'].default_value=.95;p.inputs['Roughness'].default_value=.25
    if any(s in name for s in ('lure finish','red lure','pearl belly')):
        p.inputs['Coat Weight'].default_value=.65;p.inputs['Coat Roughness'].default_value=.13
        p.inputs['Roughness'].default_value=.29;p.inputs['Metallic'].default_value=.12 if 'pearl' not in name else .35
    if 'rubber' in name:p.inputs['Coat Weight'].default_value=.18;p.inputs['Roughness'].default_value=.39
    _MATERIAL_BY_NAME[name]=m
    return m


def setup(name):
    s=_BASE_SETUP(name.replace('v2 ','v3 '));s['model_revision']=3
    s.world.node_tree.nodes['Background'].inputs[0].default_value=(.36,.40,.46,1)
    return s


def line(name,pts,radius,material):
    if any(s in name for s in ('operculum','mouth crease','cheek streak')):radius*=.65
    return _BASE_LINE(name,pts,radius,material)


def oval(name,loc,scale,material):
    if 'iris' in name or 'pupil' in name:
        scale=(scale[0],scale[1]*1.45,scale[2])
    o=_BASE_OVAL(name,loc,scale,material)
    if 'iris' in name and _ACTIVE_KIND in SPECS:
        nt=material.node_tree;p=nt.nodes.get('Principled BSDF')
        if not any(n.type=='TEX_IMAGE' for n in nt.nodes):
            U,V=np.meshgrid(np.linspace(-1,1,128),np.linspace(-1,1,128));r=np.sqrt(U*U+V*V);a=np.arctan2(V,U)
            fibers=(np.sin(a*61+np.sin(r*31)*.6)*.5+.5)*(.6+.4*np.sin(a*113+r*47)**2)
            base=np.array(p.inputs['Base Color'].default_value[:3])
            rgb=np.broadcast_to(base,(128,128,3)).copy()*(.60+.50*fibers[...,None])
            rgb*= (1-.70*np.clip((r-.82)*6,0,1))[...,None]
            tex=nt.nodes.new('ShaderNodeTexImage');tex.image=packed_image(_ACTIVE_KIND+' iris fibers',np.clip(rgb,0,1));nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
        uv=o.data.uv_layers.active
        for loop in o.data.loops:
            co=o.data.vertices[loop.vertex_index].co
            uv.data[loop.index].uv=(co.x/scale[0]*.5+.5,co.z/scale[2]*.5+.5)
    return o


def fin(name,base,edge,material,rays):
    # Catfish have a tall leading dorsal ray followed by shorter soft rays.
    if _ACTIVE_KIND in SPECS and SPECS[_ACTIVE_KIND][0]=='catfish' and name.endswith(' dorsal'):
        height=float(max(Vector(e).z-Vector(base(i/(len(edge)-1))).z for i,e in enumerate(edge)))
        edge=[tuple(Vector(base(float(t)))+Vector((0,0,height*(t/.18 if t<.18 else ((1-t)/.82)**.72)))) for t in np.linspace(0,1,15)]
    # Membrane and tapered rays share the same curved surface.
    key=material.name
    if key not in _FIN_MATERIALS:
        m=material.copy();m.name=material.name+' fine membrane';nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
        rgb=np.array(p.inputs['Base Color'].default_value[:3]);U,V=np.meshgrid(np.linspace(0,1,384),np.linspace(0,1,192))
        fibers=np.exp(-(np.sin(U*math.pi*28)/.20)**2)
        shade=.95+.23*V-.16*fibers*(.3+.7*V)+.035*np.sin(U*190+V*37)
        color=np.clip(rgb[None,None,:]*shade[...,None]+V[...,None]*.035,0,1)
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=packed_image(key+' fin fibers',color);nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
        p.inputs['Roughness'].default_value=.39;p.inputs['Metallic'].default_value=0
        m.use_backface_culling=False;_FIN_MATERIALS[key]=m
    material=_FIN_MATERIALS[key];vs=[];fs=[];N=len(edge);steps=9
    def point(i,t):
        b=Vector(base(i/(N-1)));v=Vector(edge[i]);pt=b.lerp(v,t)
        pt.y+=.005*math.sin(t*math.pi)*math.sin(i*1.1)
        return pt
    for i,e in enumerate(edge):
        for j in range(steps):vs.append(tuple(point(i,j/(steps-1))))
        if i%2==0:
            pts=[tuple(point(i,t)) for t in np.linspace(0,1,9)]
            tapered_tube(name+' taper ray',pts,[float(.0014*(1-t*.80)) for t in np.linspace(0,1,9)],rays)
    for i in range(N-1):
        for j in range(steps-1):a=i*steps+j;fs.append((a,a+steps,a+steps+1,a+1))
    ob=mesh(name,vs,fs,material);uv=ob.data.uv_layers.new(name='FinUV')
    for loop in ob.data.loops:
        idx=loop.vertex_index;uv.data[loop.index].uv=(idx//steps/(N-1),idx%steps/(steps-1))
    return ob


def refine_geometry(scene,kind):
    body=next((o for o in scene.objects if o.name==kind+' body' or o.name.startswith(kind+' body.')),None)
    if body:
        # Gentle cheek/opercular relief is part of the body, not a floating plate.
        gx=-.52 if SPECS[kind][0]!='pike' else -.59
        for v in body.data.vertices:
            x,y,z=v.co
            relief=.018*math.exp(-((x-(gx-.045))/.16)**4)*math.exp(-(z/.20)**4)
            v.co.y+=math.copysign(relief,y) if abs(y)>.05 else 0
        body.data.update()
        for o in scene.objects:
            if 'ear flap' in o.name or 'red ear tip' in o.name:
                x,y,z=o.location
                relief=.018*math.exp(-((x-(gx-.045))/.16)**4)*math.exp(-(z/.20)**4)
                o.location.y+=math.copysign(relief+.007,y)

        for o in scene.objects:
            if o.type=='CURVE' and any(word in o.name for word in ('operculum','mouth crease','lower lip','cheek streak')):
                for spline in o.data.splines:
                    for p in spline.points:
                        x,y,z,_=p.co
                        relief=.018*math.exp(-((x-(gx-.045))/.16)**4)*math.exp(-(z/.20)**4)
                        p.co.y+=math.copysign(relief+.001,y)

    if kind in ('crankbait','jerkbait','popper'):
        length=.90 if kind=='jerkbait' else .65;w=.115 if kind=='jerkbait' else .19;h=.15 if kind=='jerkbait' else .24
        for o in scene.objects:
            if o.type=='CURVE' and o.name.startswith('painted flank bars'):
                o.data.bevel_depth=.002
                for spline in o.data.splines:
                    start=Vector(spline.points[0].co[:3]);end=Vector(spline.points[-1].co[:3]);spline.points.add(30)
                    for i,p in enumerate(spline.points):
                        x,y,z=start.lerp(end,i/(len(spline.points)-1))
                        y=math.copysign(w*math.sqrt(max(.001,1-(x/length)**2-((z-.10)/h)**2))+.002,y)
                        p.co=(x,y,z,1)
            if o.name.startswith('diving lip'):
                m=mat(kind+' clear polycarbonate',(.69,.79,.82),0,.15)
                p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Alpha'].default_value=.48
                p.inputs['Coat Weight'].default_value=.4
                o.data.materials.clear();o.data.materials.append(m)


def sport_finish(scene,kind):
    refine_geometry(scene,kind)
    # Leave this source editable: export a separate full copy and join only there.
    scene.name='Fishdex v3 '+kind+' editable'
    for o in scene.objects:o['fishdex_revision']=3
    bpy.ops.object.camera_add(location=(-.18,-4,.28));cam=bpy.context.object
    cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.95;scene.camera=cam
    for name,loc,power,size in [('softbox',(-1.6,-2.4,3.2),190,2.6),('rim',(1.1,1.2,2.3),220,2),('fill',(.5,-2,-1.5),65,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=kind+' '+name;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
    scene.cycles.samples=48;scene.cycles.use_denoising=True
    scene.render.resolution_x=1200;scene.render.resolution_y=760;scene.render.filepath=ROOT+'/assets/specimens/'+kind+'.png'
    bpy.ops.render.render(write_still=True)
    source=Path(ROOT)/'assets/blender/v3'/ (kind+'.blend')
    bpy.ops.scene.new(type='FULL_COPY');runtime=bpy.context.scene;runtime.name='Fishdex v3 '+kind+' runtime'
    objects=[o for o in runtime.objects if o.type in ('MESH','CURVE')]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name=kind+' specimen'
    bpy.ops.export_scene.gltf(filepath=ROOT+'/assets/models/'+kind+'.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_image_format='JPEG',export_jpeg_quality=92)
    bpy.context.window.scene=scene
    revisions={s for s in bpy.data.scenes if s.get('model_revision')==3 and (s.get('species_id') or s.get('bait_id'))==kind}
    bpy.data.libraries.write(str(source),revisions,fake_user=True,compress=True)
    return {'asset':kind,'editable_objects':len(scene.objects),'glb_bytes':os.path.getsize(ROOT+'/assets/models/'+kind+'.glb'),'source_bytes':source.stat().st_size}


def restore_asset_history(kind):
    """Load previous scene revisions before rebuilding in a fresh Blender session."""
    path=Path(ROOT)/'assets/blender/v3'/(kind+'.blend')
    if path.exists():
        with bpy.data.libraries.load(str(path),link=False) as (source,destination):
            destination.scenes=[name for name in source.scenes if name not in bpy.data.scenes]


def build_realistic(kind):
    global _ACTIVE_KIND,_FIN_MATERIALS
    restore_asset_history(kind)
    _ACTIVE_KIND=kind;_FIN_MATERIALS={}
    return build_sportfish(kind) if kind in SPECS else build_sporttackle(kind)


def archive_realism():
    """Save and verify every version 3 scene, including intermediate studies."""
    records=[]
    kinds=sorted({s.get('species_id') or s.get('bait_id') for s in bpy.data.scenes if s.get('model_revision')==3} | {p.stem for p in (Path(ROOT)/'assets/blender/v3').glob('*.blend')})
    for kind in kinds:
        restore_asset_history(kind)
        scenes={s for s in bpy.data.scenes if s.get('model_revision')==3 and (s.get('species_id') or s.get('bait_id'))==kind}
        path=Path(ROOT)/'assets/blender/v3'/(kind+'.blend')
        bpy.data.libraries.write(str(path),scenes,fake_user=True,compress=True)
        with bpy.data.libraries.load(str(path)) as (source,_):saved=list(source.scenes)
        assert set(saved)=={s.name for s in scenes},kind
        records.append({'asset':kind,'file':path.name,'scenes':sorted(saved),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest={'revision':3,'blender':bpy.app.version_string,'scene_count':sum(len(r['scenes']) for r in records),'files':records}
    (Path(ROOT)/'assets/blender/v3/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return {'saved_files':len(records),'saved_scenes':manifest['scene_count']}
