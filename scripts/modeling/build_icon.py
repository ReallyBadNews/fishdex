# Original vector-like field-guide fish emblem rendered in Blender.
import bpy,math
ROOT='/Users/clawd/github.com/ReallyBadNews/fishdex'
s=bpy.data.scenes.new('Fishdex app emblem');bpy.context.window.scene=s
s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1024;s.render.resolution_y=1024;s.render.resolution_percentage=100;s.render.film_transparent=False
s.view_settings.view_transform='Standard'
def emission(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
def linear(v):return ((v+.055)/1.055)**2.4 if v>.04045 else v/12.92
forest=emission('emblem forest',tuple(linear(v/255) for v in [24,63,53]));paper=emission('emblem paper',tuple(linear(v/255) for v in [244,242,232]))
def shape(name,coords,depth,material):
 me=bpy.data.meshes.new(name);me.from_pydata([(x,depth,z) for x,z in coords],[],[tuple(range(len(coords)))]);me.materials.append(material);ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob)
shape('background',[(-2,-2),(2,-2),(2,2),(-2,2)],.2,forest)
outline=[(-.64,.06),(-.57,.15),(-.43,.23),(-.28,.28),(-.21,.41),(-.13,.30),(-.04,.43),(.03,.29),(.13,.37),(.20,.25),(.34,.19),(.45,.10),(.7,.29),(.63,0),(.7,-.29),(.45,-.10),(.29,-.21),(.20,-.24),(.11,-.39),(.02,-.29),(-.18,-.32),(-.40,-.25),(-.57,-.11)]
shape('fish silhouette',outline,0,paper)
shape('eye',[(-.43+.035*math.cos(i*2*math.pi/48),.065+.035*math.sin(i*2*math.pi/48)) for i in range(48)],-.01,forest)
# A fine circular field stamp.
N=256;vs=[];fs=[]
for i in range(N):
 t=i*2*math.pi/N
 for r in [.87,.88]:vs.append((r*math.cos(t),.05,r*math.sin(t)))
for i in range(N):a=i*2;b=((i+1)%N)*2;fs.append((a,b,b+1,a+1))
me=bpy.data.meshes.new('stamp');me.from_pydata(vs,[],fs);me.materials.append(paper);ob=bpy.data.objects.new('stamp',me);s.collection.objects.link(ob)
bpy.ops.object.camera_add(location=(0,-4,0));cam=bpy.context.object;cam.rotation_euler=(math.pi/2,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=2.1;s.camera=cam
s.render.filepath=ROOT+'/assets/images/icon.png';bpy.ops.render.render(write_still=True)
print('Rendered original Fishdex app icon')
