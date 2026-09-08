"""Blender 5.2 catalog refinement, revision 4.

Run: blender -b --python scripts/modeling/build_refined.py -- bass
Run each ID in a fresh process to bound memory. Existing .blend archives are
never opened for writing. References and artistic limits: docs/model-review/v4.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Reuse the original mesh primitives, species roster, and pigment functions.
# These files only define functions; their historical builders are not invoked.
for _script in (
    "build_fish.py",
    "build_tackle.py",
    "build_sportfish.py",
    "build_sporttackle.py",
    "build_realistic.py",
):
    exec(compile((HERE / _script).read_text(), str(HERE / _script), "exec"))
ROOT = str(HERE.parent.parent)
V4 = Path(ROOT) / "assets/blender/v4"
REVIEW = Path(ROOT) / "docs/model-review/v4"
V4.mkdir(parents=True, exist_ok=True)
REVIEW.mkdir(parents=True, exist_ok=True)
_LEGACY_SKIN = skin_maps
_LEGACY_TACKLE = build_sporttackle
_PRIMITIVE_OVAL = _BASE_OVAL
_PRIMITIVE_MAT = _BASE_MAT
_PRIMITIVE_LINE = _BASE_LINE
_PRIMITIVE_TUBE = tapered_tube
_CURRENT = ""
_FIN_CACHE = {}


def packed_image(name, rgb, noncolor=False):
    h, w = rgb.shape[:2]
    rgba = rgb if rgb.shape[2] == 4 else np.dstack((rgb, np.ones((h, w))))
    im = bpy.data.images.new("v4 " + name, width=w, height=h, alpha=True)
    if noncolor:
        im.colorspace_settings.name = "Non-Color"
    im.pixels.foreach_set(np.asarray(rgba, dtype=np.float32).ravel())
    im.pack()
    return im


def mat(name, color, metal=0, rough=0.42):
    m = _PRIMITIVE_MAT("v4 " + name, color, metal, rough)
    p = m.node_tree.nodes.get("Principled BSDF")
    if any(w in name for w in ("skin", "jaw", "lip")):
        p.inputs["Metallic"].default_value = 0
        p.inputs["Roughness"].default_value = 0.43
        p.inputs["Coat Weight"].default_value = 0.20
        p.inputs["Coat Roughness"].default_value = 0.24
    if any(w in name for w in ("iris", "pupil", "eye black")):
        p.inputs["Metallic"].default_value = 0.04
        p.inputs["Roughness"].default_value = 0.18
        p.inputs["Coat Weight"].default_value = 0.55
        p.inputs["Coat Roughness"].default_value = 0.10
    if any(w in name for w in ("lure finish", "red lure", "pearl belly")):
        p.inputs["Coat Weight"].default_value = 0.65
        p.inputs["Coat Roughness"].default_value = 0.14
        p.inputs["Roughness"].default_value = 0.27
    return m


def oval(name, loc, scale, material):
    return _PRIMITIVE_OVAL(name, loc, scale, material)


def line(name, pts, radius, material):
    return _PRIMITIVE_LINE(name, pts, radius, material)


def tapered_tube(name, points, radii, material):
    if "raised clitellum" in name:
        radii = [
            float(r) * (0.82 + 0.18 * math.sin(math.pi * i / (len(points) - 1)) ** 0.55)
            for i, r in enumerate(radii)
        ]
    if 2 < len(points) < 6 and not any(w in name for w in ("ray", "spine")):
        # Catmull-Rom interpolation gives soft skirts and curved barbels.
        ps = [Vector(p) for p in points]
        rs = list(radii)
        points = []
        radii = []
        for i in range(len(ps) - 1):
            p0, p1, p2, p3 = (
                ps[max(0, i - 1)],
                ps[i],
                ps[i + 1],
                ps[min(len(ps) - 1, i + 2)],
            )
            for t in np.linspace(0, 1, 12, endpoint=i == len(ps) - 2):
                t = float(t)
                points.append(
                    tuple(
                        0.5
                        * (
                            (2 * p1)
                            + (-p0 + p2) * t
                            + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                            + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t
                        )
                    )
                )
                radii.append(float(rs[i] * (1 - t) + rs[i + 1] * t))
    if "skirt" in name:
        verts = []
        faces = []
        for i, p in enumerate(points):
            p = Vector(p)
            r = float(radii[i])
            twist = 0.35 * math.sin(i * 0.23)
            for y, z in ((-r, -0.0015), (r, -0.0015), (r, 0.0015), (-r, 0.0015)):
                verts.append(
                    tuple(
                        p
                        + Vector(
                            (
                                0,
                                y * math.cos(twist) - z * math.sin(twist),
                                y * math.sin(twist) + z * math.cos(twist),
                            )
                        )
                    )
                )
        for i in range(len(points) - 1):
            for j in range(4):
                a = i * 4 + j
                b = i * 4 + (j + 1) % 4
                faces.append((a, b, b + 4, a + 4))
        return mesh(name, verts, faces, material)
    sides = 8 if max(radii) < 0.012 else 20
    verts = []
    faces = []
    for i, p in enumerate(points):
        tangent = (
            Vector(points[min(i + 1, len(points) - 1)]) - Vector(points[max(0, i - 1)])
        ).normalized()
        u = tangent.cross(Vector((0, 0, 1)))
        if u.length < 0.001:
            u = tangent.cross(Vector((0, 1, 0)))
        u.normalize()
        v = tangent.cross(u).normalized()
        for a in np.linspace(0, 2 * math.pi, sides, endpoint=False):
            verts.append(
                tuple(Vector(p) + float(radii[i]) * (u * math.cos(a) + v * math.sin(a)))
            )
    for i in range(len(points) - 1):
        for j in range(sides):
            a = i * sides + j
            b = i * sides + (j + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    faces.extend(
        [
            tuple(range(sides - 1, -1, -1)),
            tuple((len(points) - 1) * sides + j for j in range(sides)),
        ]
    )
    o = mesh(name, verts, faces, material)
    uv = o.data.uv_layers.new(name="UVMap")
    for poly in o.data.polygons:
        js = [o.data.loops[l].vertex_index % sides for l in poly.loop_indices]
        seam = max(js) - min(js) > sides / 2
        for l in poly.loop_indices:
            i, j = divmod(o.data.loops[l].vertex_index, sides)
            uv.data[l].uv = (i / (len(points) - 1), 1 if seam and j == 0 else j / sides)
    return o


def ring(name, center, radius, material, axis="Y"):
    split = "split" in name
    pts = []
    for t in np.linspace(0, math.pi * (3.75 if split else 2), 100 if split else 65):
        offset = 0.007 * (t / math.pi - 1.8) if split else 0
        p = (
            (radius * math.cos(t), offset, radius * math.sin(t))
            if axis == "Y"
            else (
                (offset, radius * math.cos(t), radius * math.sin(t))
                if axis == "X"
                else (radius * math.cos(t), radius * math.sin(t), offset)
            )
        )
        pts.append(tuple(Vector(center) + Vector(p)))
    return line(name, pts, 0.0045 if split else 0.006, material)


def hook(x, y, z, size, steel):
    pts = [(x, y, z), (x + size * 0.55, y, z - 0.01)]
    pts += [
        (
            x + size * 0.55 + size * 0.28 * math.sin(t),
            y,
            z + size * 0.28 * (1 - math.cos(t)),
        )
        for t in np.linspace(0, math.pi, 30)
    ]
    pts += [
        (x + size * 0.35, y, z + size * 0.54),
        (x + size * 0.22, y, z + size * 0.52),
    ]
    tapered_tube(
        "forged single hook",
        pts,
        [0.009] * (len(pts) - 3) + [0.008, 0.004, 0.0007],
        steel,
    )


def treble(center, size, steel):
    ring("wound split ring", center, 0.030, steel)
    x, y, z = center
    ring("treble closed eye", (x, 0, z - 0.040), 0.018, steel, axis="X")
    line("treble shank", [(x, y, z - 0.05), (x, y, z - size * 0.65)], 0.0065, steel)
    for angle in (0, 2 * math.pi / 3, 4 * math.pi / 3):
        pts = [(0, 0, -size * 0.18), (0, 0, -size * 0.64)]
        pts += [
            (
                size * 0.30 * (1 - math.cos(t)),
                0,
                -size * 0.64 - size * 0.30 * math.sin(t),
            )
            for t in np.linspace(0, math.pi, 27)
        ]
        pts += [(size * 0.60, 0, -size * 0.38), (size * 0.54, 0, -size * 0.29)]
        p = [
            (x + a * math.cos(angle), y + a * math.sin(angle), z + c) for a, _, c in pts
        ]
        tapered_tube(
            "tempered treble hook",
            p,
            [0.0068] * (len(p) - 3) + [0.006, 0.0035, 0.0005],
            steel,
        )
        a = size * 0.585
        b = (x + a * math.cos(angle), y + a * math.sin(angle), z - size * 0.41)
        e = (
            x + (a - 0.027) * math.cos(angle),
            y + (a - 0.027) * math.sin(angle),
            z - size * 0.47,
        )
        tapered_tube("small hook barb", [b, e], [0.004, 0.0005], steel)


def image_input(material, image, socket):
    nt = material.node_tree
    p = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    nt.links.new(tex.outputs["Color"], p.inputs[socket])
    return tex


def normal_input(material, image, strength=0.38):
    nt = material.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    n = nt.nodes.new("ShaderNodeNormalMap")
    n.inputs["Strength"].default_value = strength
    nt.links.new(tex.outputs["Color"], n.inputs["Color"])
    nt.links.new(n.outputs["Normal"], nt.nodes.get("Principled BSDF").inputs["Normal"])


def setup(name):
    s = bpy.data.scenes.new("Fishdex v4 " + _CURRENT + " editable")
    bpy.context.window.scene = s
    s["model_revision"] = 4
    s["fishdex_generated"] = True
    s.render.engine = "CYCLES"
    s.cycles.samples = 48
    s.cycles.use_denoising = True
    s.world = bpy.data.worlds.new("v4 neutral studio")
    s.world.use_nodes = True
    bg = s.world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.32, 0.36, 0.40, 1)
    bg.inputs[1].default_value = 0.45
    s.view_settings.view_transform = "AgX"
    s.render.resolution_x = 1400
    s.render.resolution_y = 850
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGBA"
    s.render.film_transparent = True
    return s


def skin_material(kind, spec):
    pigment_spec = (
        (*spec[:5], "plain", spec[6])
        if kind
        in (
            "rock-bass",
            "pumpkinseed",
            "green-sunfish",
            "brook-trout",
            "lake-trout",
            "black-bullhead",
        )
        else spec
    )
    color, normal = _LEGACY_SKIN(kind, pigment_spec)
    h, w = color.size[1], color.size[0]
    rgba = np.empty(w * h * 4, np.float32)
    color.pixels.foreach_get(rgba)
    rgb = rgba.reshape(h, w, 4)[:, :, :3].copy()
    u, v = np.meshgrid((np.arange(w) + 0.5) / w, (np.arange(h) + 0.5) / h)
    t = v * 2 * np.pi
    z = np.sin(t)
    side = 1 - np.abs(z) ** 5
    seed = sum(map(ord, kind))
    n = noise2(u * 47, np.cos(t) * 31 + np.sin(t) * 27, seed)
    micro = noise2(u * 330, np.cos(t) * 190 + np.sin(t) * 171, seed + 3)
    # Patches vary within each scale instead of repeating a uniform tiled sheen.
    rgb *= (1 + (n - 0.5) * 0.20 + (micro - 0.5) * 0.055)[..., None]
    if kind in ("bass", "smallmouth", "walleye", "yellow-perch"):
        flecks = np.clip(
            (noise2(u * 175, np.cos(t) * 68 + np.sin(t) * 89, seed + 12) - 0.59) * 3,
            0,
            1,
        )
        rgb *= (1 - flecks * 0.42 * side * np.clip((u - 0.28) * 9, 0, 1))[..., None]
    if kind == "black-crappie":
        calico = np.clip(
            (noise2(u * 85, np.cos(t) * 33 + np.sin(t) * 39, seed) - 0.46) * 4, 0, 1
        )
        rgb *= (1 - calico * 0.77 * side * np.clip((u - 0.15) * 8, 0, 1))[..., None]
    if kind == "rock-bass":
        # Pigment at the base of scales forms rows of dark flank spots.
        rows = v * 44
        cols = u * 65 + (np.floor(rows) % 2) * 0.5
        dots = np.exp(
            -(((cols % 1 - 0.52) / 0.21) ** 2) - ((rows % 1 - 0.50) / 0.26) ** 2
        )
        rgb *= (1 - dots * 0.47 * side * np.clip((u - 0.22) * 8, 0, 1))[..., None]
    if kind in ("pumpkinseed", "green-sunfish"):
        marks = (
            np.clip(
                (noise2(u * 155, np.cos(t) * 61 + np.sin(t) * 67, seed) - 0.58) * 4,
                0,
                1,
            )
            * side
        )
        pigment = np.array(
            (0.70, 0.26, 0.065) if kind == "pumpkinseed" else (0.16, 0.50, 0.48)
        )
        rgb = rgb * (1 - marks[..., None] * 0.7) + pigment * marks[..., None] * 0.7
        cheek = np.clip((0.31 - u) * 9, 0, 1) * side
        streak = (
            np.exp(-((np.sin(t * 19 + u * 29 + (n - 0.5) * 0.6) / 0.17) ** 2)) * cheek
        )
        rgb = (
            rgb * (1 - streak[..., None] * 0.75)
            + np.array((0.12, 0.49, 0.54)) * streak[..., None] * 0.75
        )
    if kind == "white-bass":
        # Six strong, mostly continuous horizontal stripes; no rings on the back.
        rgb = np.broadcast_to(np.array((0.61, 0.67, 0.65)), (h, w, 3)).copy()
        back = np.clip((z - 0.05) * 1.1, 0, 1)[..., None]
        rgb = rgb * (1 - back * 0.72) + np.array((0.08, 0.15, 0.13)) * back * 0.72
        belly = np.clip((-z - 0.28) * 1.5, 0, 1)[..., None]
        rgb = rgb * (1 - belly) + np.array((0.91, 0.91, 0.85)) * belly
        marks = np.zeros_like(z)
        for level in (-0.52, -0.29, -0.05, 0.19, 0.42, 0.62):
            marks = np.maximum(
                marks, np.exp(-(((z - level - (n - 0.5) * 0.017) / 0.025) ** 4))
            )
        rgb *= (1 - marks * 0.75 * np.clip((u - 0.25) * 12, 0, 1))[..., None]
    if kind in ("pike", "muskie"):
        # Mottling in the unscaled lower operculum keeps the head distinct.
        rgb *= (1 - 0.13 * n * np.clip((0.28 - u) * 10, 0, 1) * side)[..., None]
    if kind in ("brook-trout", "lake-trout"):
        rng = np.random.default_rng(seed)
        pale = np.zeros_like(u)
        for _ in range(200 if kind == "lake-trout" else 110):
            pu = rng.uniform(0.17, 0.95)
            pv = rng.uniform(0, 1)
            dv = np.minimum(abs(v - pv), 1 - abs(v - pv))
            d = ((u - pu) / rng.uniform(0.004, 0.009)) ** 2 + (
                dv / rng.uniform(0.006, 0.012)
            ) ** 2
            pale = np.maximum(pale, np.exp(-d * d * 1.5))
        mask = pale * (0.4 + 0.6 * side)
        rgb = (
            rgb * (1 - mask[..., None] * 0.85)
            + np.array((0.81, 0.82, 0.63)) * mask[..., None] * 0.85
        )
        if kind == "brook-trout":
            vermiculation = np.exp(
                -((np.sin(u * 155 + np.sin(t * 24) * 2 + (n - 0.5) * 5) / 0.21) ** 2)
            ) * np.clip((z - 0.18) * 2, 0, 1)
            rgb = (
                rgb * (1 - vermiculation[..., None] * 0.78)
                + np.array((0.64, 0.68, 0.40)) * vermiculation[..., None] * 0.78
            )
            for sidecenter in (0, 0.5):
                for _ in range(27):
                    pu = rng.uniform(0.25, 0.87)
                    pv = (sidecenter + rng.uniform(-0.105, 0.10)) % 1
                    dv = np.minimum(abs(v - pv), 1 - abs(v - pv))
                    d = ((u - pu) / 0.006) ** 2 + (dv / 0.010) ** 2
                    halo = np.exp(-d * 0.62) * 0.9
                    rgb = (
                        rgb * (1 - halo[..., None])
                        + np.array((0.10, 0.30, 0.56)) * halo[..., None]
                    )
                    spot = np.exp(-d * 2.6) * 0.95
                    rgb = (
                        rgb * (1 - spot[..., None])
                        + np.array((0.72, 0.065, 0.023)) * spot[..., None]
                    )
    color.pixels.foreach_set(
        np.dstack((np.clip(rgb, 0, 1), np.ones((h, w)))).astype(np.float32).ravel()
    )
    color.pack()
    m = mat(kind + " skin", spec[3])
    image_input(m, color, "Base Color")
    normal_input(m, normal, 0.28 if spec[0] == "catfish" else 0.55)
    rough = 0.46 + (n - 0.5) * 0.08 + (micro - 0.5) * 0.04 - np.clip(-z, 0, 1) * 0.055
    image_input(
        m,
        packed_image(
            kind + " skin roughness", np.repeat(rough[::2, ::2, None], 3, axis=2), True
        ),
        "Roughness",
    )
    return m


def fin(name, base, edge, material, rays):
    """Curved, tapered membranes, with rays following actual fin topology."""
    kind = _CURRENT
    n = len(edge)
    steps = 10
    key = (
        material.name,
        (
            "caudal"
            if "caudal" in name
            else (
                "lower"
                if any(x in name for x in ("pelvic", "pectoral", "anal"))
                else "soft dorsal" if "soft" in name else "dorsal"
            )
        ),
    )
    if key not in _FIN_CACHE:
        m = material.copy()
        m.name = material.name + " " + key[1] + " membrane"
        p = m.node_tree.nodes.get("Principled BSDF")
        rgb = np.array(p.inputs["Base Color"].default_value[:3])
        u, v = np.meshgrid(np.linspace(0, 1, 512), np.linspace(0, 1, 256))
        fibers = np.exp(-((np.sin(u * np.pi * (n - 1)) / 0.16) ** 2))
        variation = noise2(u * 31, v * 12, sum(map(ord, kind)))
        tex = np.broadcast_to(rgb, (256, 512, 3)).copy()
        tex *= (0.95 + 0.45 * v - 0.20 * fibers + 0.10 * (variation - 0.5))[..., None]
        if kind in (
            "pike",
            "muskie",
            "black-crappie",
            "white-crappie",
            "rock-bass",
            "yellow-perch",
            "brook-trout",
            "lake-trout",
        ):
            spots = np.clip((noise2(u * 34, v * 16, 7) - 0.52) * 3, 0, 1)
            tex *= (1 - spots * 0.55 * v)[..., None]
        if kind == "brook-trout" and key[1] == "lower":
            tex = np.where((u < 0.16)[..., None], np.array((0.025, 0.038, 0.034)), tex)
            tex = np.where((u < 0.075)[..., None], np.array((0.90, 0.91, 0.82)), tex)
        if kind == "lake-trout" and key[1] == "lower":
            tex = np.where((u < 0.08)[..., None], np.array((0.86, 0.87, 0.77)), tex)
        if kind == "green-sunfish":
            tex = (
                tex * (1 - np.clip((v - 0.86) * 7, 0, 1)[..., None])
                + np.array((0.78, 0.68, 0.30))
                * np.clip((v - 0.86) * 7, 0, 1)[..., None]
            )
        if kind == "bluegill" and key[1] == "soft dorsal":
            spot = np.exp(-(((u - 0.65) / 0.15) ** 4) - ((v - 0.73) / 0.22) ** 4)
            tex *= (1 - 0.92 * spot)[..., None]
        if kind == "walleye" and key[1] == "dorsal":
            spot = np.exp(-(((u - 0.86) / 0.18) ** 4) - ((v - 0.42) / 0.60) ** 4)
            tex *= (1 - 0.94 * spot)[..., None]
        alpha = 0.88 - 0.20 * v + 0.10 * fibers
        texnode = image_input(
            m,
            packed_image(
                kind + " " + key[1] + " fin",
                np.dstack((np.clip(tex, 0, 1), np.clip(alpha, 0, 1))),
            ),
            "Base Color",
        )
        m.node_tree.links.new(texnode.outputs["Alpha"], p.inputs["Alpha"])
        p.inputs["Metallic"].default_value = 0
        p.inputs["Roughness"].default_value = 0.48
        p.inputs["Coat Weight"].default_value = 0.08
        m.use_backface_culling = False
        _FIN_CACHE[key] = m
    membrane = _FIN_CACHE[key]
    verts = []
    faces = []

    def point(i, t):
        b = Vector(base(i / (n - 1)))
        e = Vector(edge[i])
        p = b.lerp(e, t)
        p.y += 0.0055 * math.sin(t * math.pi) * math.sin(i * 0.95)
        return p

    spiny = "spiny" in name
    for i in range(n):
        verts.extend(tuple(point(i, j / (steps - 1))) for j in range(steps))
        if (spiny and i % 2 == 0) or (not spiny and i % 2 == 0):
            pts = [tuple(point(i, t)) for t in np.linspace(0, 1, 10)]
            tapered_tube(
                name + " ray",
                pts,
                [0.00165 * (1 - t * 0.78) for t in np.linspace(0, 1, 10)],
                rays,
            )
            if not spiny and i > 1 and i < n - 2:
                # Soft rays bifurcate toward their outer ends.
                b = point(i, 0.59)
                for off in (-0.32, 0.32):
                    e = point(i, 1).lerp(point(i + (1 if off > 0 else -1), 1), abs(off))
                    tapered_tube(
                        name + " ray branch",
                        [tuple(b.lerp(e, t)) for t in np.linspace(0, 1, 5)],
                        [0.0008 * (1 - t * 0.68) for t in np.linspace(0, 1, 5)],
                        rays,
                    )
    for i in range(n - 1):
        for j in range(steps - 1):
            a = i * steps + j
            faces.append((a, a + steps, a + steps + 1, a + 1))
    o = mesh(name, verts, faces, membrane)
    uv = o.data.uv_layers.new(name="FinUV")
    for lp in o.data.loops:
        idx = lp.vertex_index
        uv.data[lp.index].uv = (idx // steps / (n - 1), idx % steps / (steps - 1))
    return o


# Distinct head and shoulder contours. x, half-width, half-depth; a separate
# longitudinal centerline below gives asymmetric back and belly outlines.
PROFILES = {
    "bass": [
        (-1.12, 0.039, 0.047),
        (-1.02, 0.09, 0.10),
        (-0.83, 0.153, 0.205),
        (-0.61, 0.193, 0.285),
        (-0.35, 0.205, 0.31),
        (0, 0.187, 0.283),
        (0.43, 0.122, 0.205),
        (0.78, 0.052, 0.085),
        (0.94, 0.035, 0.055),
    ],
    "smallmouth": [
        (-1.08, 0.025, 0.038),
        (-0.96, 0.078, 0.104),
        (-0.76, 0.153, 0.229),
        (-0.48, 0.19, 0.283),
        (-0.15, 0.19, 0.286),
        (0.25, 0.151, 0.238),
        (0.57, 0.097, 0.161),
        (0.80, 0.045, 0.069),
        (0.94, 0.033, 0.052),
    ],
    "bluegill": [
        (-1.0, 0.014, 0.023),
        (-0.91, 0.052, 0.112),
        (-0.75, 0.122, 0.275),
        (-0.53, 0.165, 0.399),
        (-0.23, 0.182, 0.44),
        (0.10, 0.165, 0.399),
        (0.47, 0.102, 0.266),
        (0.76, 0.04, 0.079),
        (0.90, 0.025, 0.045),
    ],
    "pumpkinseed": [
        (-1.0, 0.014, 0.023),
        (-0.9, 0.055, 0.117),
        (-0.73, 0.117, 0.282),
        (-0.48, 0.162, 0.422),
        (-0.13, 0.175, 0.465),
        (0.17, 0.151, 0.39),
        (0.48, 0.095, 0.259),
        (0.77, 0.034, 0.07),
        (0.91, 0.026, 0.05),
    ],
    "green-sunfish": [
        (-1.02, 0.03, 0.042),
        (-0.91, 0.07, 0.138),
        (-0.71, 0.152, 0.263),
        (-0.4, 0.191, 0.335),
        (0, 0.177, 0.328),
        (0.45, 0.107, 0.223),
        (0.78, 0.042, 0.079),
        (0.92, 0.028, 0.051),
    ],
    "rock-bass": [
        (-1.02, 0.03, 0.048),
        (-0.9, 0.09, 0.14),
        (-0.68, 0.156, 0.267),
        (-0.39, 0.19, 0.358),
        (-0.02, 0.18, 0.334),
        (0.42, 0.119, 0.244),
        (0.79, 0.042, 0.076),
        (0.93, 0.027, 0.05),
    ],
}


def profile(kind):
    family, ws, hs, *_ = SPECS[kind]
    cfg = PROFILES.get(kind, [(x, w * ws, h * hs) for x, w, h in FAMILIES[family]])
    if kind == "flathead-catfish":
        cfg = [
            (x, w * (1.17 if x < -0.55 else 1), h * (0.62 if x < -0.6 else 0.90))
            for x, w, h in cfg
        ]
    if "bullhead" in kind:
        cfg = [(x * 0.87, w, h * 0.94) for x, w, h in cfg]
    if family == "pike":
        cfg = [(x, w * 0.89, h * 0.90) for x, w, h in cfg]
    if family == "crappie":
        cfg = [(x, w * 0.86, h) for x, w, h in cfg]
    if family == "trout":
        cfg = [(x, w * 0.93, h * 0.92) for x, w, h in cfg]

    def dims(x):
        x = max(cfg[0][0], min(cfg[-1][0], x))
        for idx, (a, b) in enumerate(zip(cfg, cfg[1:])):
            if a[0] <= x <= b[0]:
                dt = b[0] - a[0]
                t = (x - a[0]) / dt
                out = []
                for k in (1, 2):
                    slope = (b[k] - a[k]) / dt
                    prev = (
                        (a[k] - cfg[idx - 1][k]) / (a[0] - cfg[idx - 1][0])
                        if idx
                        else slope
                    )
                    nxt = (
                        (cfg[idx + 2][k] - b[k]) / (cfg[idx + 2][0] - b[0])
                        if idx < len(cfg) - 2
                        else slope
                    )
                    m0 = 2 * prev * slope / (prev + slope) if prev * slope > 0 else 0
                    m1 = 2 * nxt * slope / (nxt + slope) if nxt * slope > 0 else 0
                    out.append(
                        (2 * t**3 - 3 * t * t + 1) * a[k]
                        + (t**3 - 2 * t * t + t) * dt * m0
                        + (-2 * t**3 + 3 * t * t) * b[k]
                        + (t**3 - t * t) * dt * m1
                    )
                return out
        return cfg[-1][1:]

    def center(x):
        return (0.035 if family not in ("pike", "catfish") else 0.009) * math.exp(
            -(((x + 0.66) / 0.38) ** 2)
        )

    def surf(x, z, side):
        w, h = dims(x)
        q = (z - center(x)) / h
        y = w * math.sqrt(max(0.003, 1 - q * q))
        relief = (
            0.009
            * math.exp(-(((x + 0.48) / 0.145) ** 4))
            * math.exp(-((q / 0.85) ** 4))
        )
        return Vector((x, side * (y + relief), z))

    return cfg, dims, center, surf


def build_refined_fish(kind):
    family, ws, hs, rgb, belly, pattern, spines = SPECS[kind]
    scene = setup(kind)
    scene["species_id"] = kind
    cfg, dims, center, surf = profile(kind)
    shadow = mat(kind + " gill shadow", (0.006, 0.012, 0.009), 0, 0.62)
    shadow.node_tree.nodes.get("Principled BSDF").inputs[
        "Specular IOR Level"
    ].default_value = 0.23
    lip = mat(kind + " lip", tuple(np.array(rgb) * 0.57), 0, 0.47)
    finrgb = np.array(rgb) * (0.61 if family != "catfish" else 0.64)
    membrane = mat(kind + " fins", tuple(finrgb), 0, 0.46)
    lowrgb = (
        (0.48, 0.205, 0.07)
        if kind in ("brook-trout", "yellow-perch")
        else (0.32, 0.25, 0.16) if kind == "lake-trout" else tuple(finrgb)
    )
    lower = (
        mat(kind + " lower fins", lowrgb, 0, 0.46)
        if lowrgb != tuple(finrgb)
        else membrane
    )
    rays = mat(
        kind + " fin rays",
        tuple(finrgb * (1.25 if kind == "black-bullhead" else 0.64)),
        0,
        0.5,
    )
    bodymat = skin_material(kind, SPECS[kind])
    nx, nr = 176, 80
    vs = []
    fs = []
    for i in range(nx + 1):
        x = cfg[0][0] + (cfg[-1][0] - cfg[0][0]) * i / nx
        w, h = dims(x)
        for j in range(nr):
            t = j * 2 * math.pi / nr
            z = center(x) + h * math.sin(t)
            relief = (
                0.009
                * math.exp(-(((x + 0.48) / 0.145) ** 4))
                * math.exp(-((math.sin(t) / 0.85) ** 4))
            )
            vs.append((x, (w + relief) * math.cos(t), z))
    for i in range(nx):
        for j in range(nr):
            a = i * nr + j
            b = i * nr + (j + 1) % nr
            fs.append((a, b, b + nr, a + nr))
    fs.extend([tuple(range(nr - 1, -1, -1)), tuple(nx * nr + j for j in range(nr))])
    body = mesh(kind + " body", vs, fs, bodymat)
    uv = body.data.uv_layers.new(name="SpecimenUV")
    for p in body.data.polygons:
        js = [body.data.loops[l].vertex_index % nr for l in p.loop_indices]
        seam = max(js) - min(js) > nr / 2
        for l in p.loop_indices:
            idx = body.data.loops[l].vertex_index
            i, j = divmod(idx, nr)
            uv.data[l].uv = (i / nx, 1 if seam and j == 0 else j / nr)
    ex = {
        "sunfish": -0.805,
        "bass": -0.86,
        "perch": -0.89,
        "pike": -0.89,
        "crappie": -0.83,
        "catfish": -0.93,
        "trout": -0.90,
    }[family]
    if "bullhead" in kind:
        ex *= 0.87
    ez = center(ex) + dims(ex)[1] * (0.48 if family != "catfish" else 0.46)
    er = (
        0.049
        if kind == "walleye"
        else (
            0.027
            if family == "catfish"
            else 0.040 if family in ("sunfish", "crappie") else 0.037
        )
    )
    iris = mat(
        kind + " iris",
        (0.63, 0.16, 0.055) if kind == "rock-bass" else (0.52, 0.48, 0.25),
        0.04,
        0.20,
    )
    u, v = np.meshgrid(np.linspace(-1, 1, 256), np.linspace(-1, 1, 256))
    r = np.sqrt(u * u + v * v)
    a = np.arctan2(v, u)
    fibers = (
        0.7
        + 0.28 * np.sin(a * 93 + np.sin(r * 39)) ** 2
        + 0.10 * np.sin(a * 173 + r * 43)
    )
    irisrgb = (
        np.array(
            iris.node_tree.nodes.get("Principled BSDF")
            .inputs["Base Color"]
            .default_value[:3]
        )
        * fibers[..., None]
    )
    irisrgb *= (1 - 0.74 * np.clip((r - 0.83) * 7, 0, 1))[..., None]
    image_input(
        iris, packed_image(kind + " radial iris", np.clip(irisrgb, 0, 1)), "Base Color"
    )
    pupil = mat(kind + " pupil", (0.003, 0.008, 0.009), 0, 0.13)
    for side in (-1, 1):
        ep = surf(ex, ez, side)
        normal = Vector((-0.35, side, 0.24)).normalized()
        for nm, offset, scale, material in [
            ("eye socket", -0.002, (er * 1.13, 0.007, er * 1.13), shadow),
            ("iris", 0.002, (er, 0.011, er), iris),
            ("pupil", 0.014, (er * 0.59, 0.006, er * 0.63), pupil),
        ]:
            o = oval(kind + " " + nm, ep + normal * offset, scale, material)
            o.rotation_mode = "QUATERNION"
            o.rotation_quaternion = Vector((0, side, 0)).rotation_difference(normal)
            if nm == "iris":
                for loop in o.data.loops:
                    co = o.data.vertices[loop.vertex_index].co
                    o.data.uv_layers.active.data[loop.index].uv = (
                        co.x / er * 0.5 + 0.5,
                        co.z / er * 0.5 + 0.5,
                    )
        gx = -0.49 if family != "pike" else -0.56
        points = []
        for t in np.linspace(-1.16, 1.12, 52):
            x = gx + 0.10 * math.cos(t)
            z = center(x) + dims(gx)[1] * 0.86 * math.sin(t)
            p = surf(x, z, side)
            p.y += side * 0.0015
            points.append(tuple(p))
        line(kind + " opercular margin", points, 0.0018, shadow)
        # A second, short preopercular contour describes the cheek plate.
        points = []
        for t in np.linspace(0, 1, 34):
            x = ex + 0.07 + 0.15 * math.sin(t * math.pi / 2)
            z = ez - 0.04 - 0.20 * t
            p = surf(x, z, side)
            p.y += side * 0.001
            points.append(tuple(p))
        line(kind + " preoperculum", points, 0.0009, lip)
        if kind == "smallmouth":
            for streak in range(3):
                pts = []
                for t in np.linspace(0, 1, 30):
                    x = ex + 0.03 + 0.23 * t
                    z = ez - 0.04 - streak * 0.038 - 0.073 * t
                    p = surf(x, z, side)
                    p.y += side * 0.0018
                    pts.append(tuple(p))
                line("smallmouth bronze cheek streak", pts, 0.0022, lip)
        end = ex + (
            0.145
            if kind == "bass"
            else (
                0.07
                if family in ("trout", "pike", "crappie") or kind == "green-sunfish"
                else -0.01
            )
        )
        if kind in ("bluegill", "pumpkinseed"):
            end = -0.865
        drop = (
            0.105
            if kind == "bass"
            else 0.074 if family in ("bass", "trout", "perch", "crappie") else 0.025
        )
        jaw = []
        top = []
        bottom = []
        for t in np.linspace(0, 1, 48):
            x = cfg[0][0] + (end - cfg[0][0]) * t
            z = center(x) + 0.006 - drop * t
            p = surf(x, z, side)
            p.y += side * 0.0015
            gap = (0.008 if family != "catfish" else 0.006) * (1 - t) ** 0.5
            top.append((p.x, p.y, p.z + gap))
            bottom.append((p.x - 0.010 * (1 - t), p.y, p.z - gap))
            jaw.append(tuple(p))
        mesh(
            kind + " recessed mouth",
            top + bottom,
            [(i, i + 1, 48 + i + 1, 48 + i) for i in range(47)],
            shadow,
        )
        line(kind + " upper maxilla", top, 0.0024, lip)
        line(kind + " lower jaw rim", bottom, 0.0030, lip)
        # Paired nostril openings, smaller than the eyes.
        x = ex - 0.084
        z = center(x) + dims(x)[1] * 0.52
        p = surf(x, z, side)
        oval(kind + " naris", p, (0.009, 0.002, 0.004), shadow)
        if kind in ("bluegill", "pumpkinseed", "green-sunfish"):
            pt = surf(-0.44, 0.072, side)
            pt.y += side * 0.005
            oval(kind + " opercular flap", pt, (0.062, 0.006, 0.036), shadow)
            if kind == "pumpkinseed":
                red = mat("pumpkinseed red ear", (0.68, 0.095, 0.021), 0, 0.47)
                oval(
                    "red ear crescent",
                    (pt.x + 0.047, pt.y + side * 0.004, pt.z),
                    (0.017, 0.004, 0.029),
                    red,
                )
        # Pectoral leading edge fans back from the shoulder, with a pointed tip.
        px = -0.45 if family != "catfish" else -0.59
        pw, ph = dims(px)
        length = (
            0.49
            if kind in ("bluegill", "pumpkinseed")
            else 0.34 if family != "catfish" else 0.28
        )
        edge = []
        for t in np.linspace(0, 1, 19):
            extent = math.sin(t * math.pi) ** 0.70
            edge.append(
                (
                    px + 0.06 + length * extent,
                    side * (pw + 0.028 + 0.070 * extent),
                    -0.07 - 0.16 * t,
                )
            )
        fin(
            kind + " pectoral",
            lambda t: (px + 0.04 * t, side * (pw * 0.98), -0.05 - 0.06 * t),
            edge,
            lower,
            rays,
        )
        px = 0.03 if family in ("trout", "pike", "catfish") else -0.19
        pw, ph = dims(px)
        edge = [
            (
                px + 0.025 + 0.26 * math.sin(t * math.pi) ** 0.7,
                side * (pw * 0.70 + 0.08),
                center(px) - ph - 0.14 * t,
            )
            for t in np.linspace(0, 1, 15)
        ]
        fin(
            kind + " pelvic",
            lambda t: (px + 0.08 * t, side * pw * 0.54, center(px) - ph * 0.87),
            edge,
            lower,
            rays,
        )
        if family == "catfish":
            darkbarbel = mat(kind + " maxillary barbels", (0.12, 0.13, 0.09), 0, 0.46)
            chin = mat(
                kind + " chin barbels",
                (
                    (0.78, 0.74, 0.55)
                    if kind == "yellow-bullhead"
                    else (0.12, 0.13, 0.095)
                ),
                0,
                0.48,
            )
            nose = cfg[0][0]
            for idx in range(4):
                x = nose + 0.05 + idx * 0.025
                w, h = dims(x)
                z = center(x) + (0.052 if idx == 0 else -0.035 if idx > 1 else 0)
                p = surf(x, z, side)
                p.y *= 0.55 if idx > 1 else 0.95
                reach = 0.34 if idx == 1 else 0.16
                pts = []
                for t in np.linspace(0, 1, 25):
                    pts.append(
                        (
                            x + 0.19 * t,
                            p.y + side * reach * (t - 0.17 * t * t),
                            z - 0.07 * t - 0.06 * t * t,
                        )
                    )
                tapered_tube(
                    kind
                    + " "
                    + ("nasal" if idx == 0 else "maxillary" if idx == 1 else "chin")
                    + " barbel",
                    pts,
                    [
                        0.0045 * (1 - t * 0.95) if idx == 1 else 0.003 * (1 - t * 0.93)
                        for t in np.linspace(0, 1, 25)
                    ],
                    chin if idx > 1 else darkbarbel,
                )

    def dorsal(start, end, height, count=0):
        edge = []
        for i in range(count * 2 - 1 if count else 27):
            t = i / (count * 2 - 2 if count else 26)
            x = start + (end - start) * t
            raiseh = height * (
                (0.12 + 0.88 * math.sin(t * math.pi) ** 0.8)
                if count
                else (math.sin(t * math.pi) ** 0.62)
            )
            if count and i % 2:
                raiseh *= 0.70
            edge.append((x, 0, center(x) + dims(x)[1] + raiseh + 0.002))
        return fin(
            kind + (" spiny" if count else " soft") + " dorsal",
            lambda t: (
                start + (end - start) * t,
                0,
                center(start + (end - start) * t)
                + dims(start + (end - start) * t)[1] * 0.965,
            ),
            edge,
            membrane,
            rays,
        )

    if family == "pike":
        dorsal(0.43, 0.85, 0.21)
    elif family in ("catfish", "trout"):
        if family == "catfish":
            start, end = -0.43, -0.11
            edge = [
                (
                    start + (end - start) * t,
                    0,
                    center(start + (end - start) * t)
                    + dims(start + (end - start) * t)[1]
                    + 0.29 * (t / 0.17 if t < 0.17 else ((1 - t) / 0.83) ** 0.8),
                )
                for t in np.linspace(0, 1, 25)
            ]
            fin(
                kind + " dorsal spine",
                lambda t: (
                    start + (end - start) * t,
                    0,
                    center(start + (end - start) * t)
                    + dims(start + (end - start) * t)[1] * 0.96,
                ),
                edge,
                membrane,
                rays,
            )
        else:
            dorsal(-0.17, 0.24, 0.22)
        start, end = (0.36, 0.74) if family == "catfish" else (0.59, 0.77)
        pts = [
            (start, 0, center(start) + dims(start)[1] * 0.94),
            (end, 0, center(end) + dims(end)[1] * 0.94),
        ] + [
            (
                end - (end - start) * t,
                0,
                center(end - (end - start) * t)
                + dims(end - (end - start) * t)[1]
                + 0.072 * math.sin(math.pi * t) ** 0.7,
            )
            for t in np.linspace(0, 1, 26)
        ]
        ob = mesh(
            kind + " rayless adipose fin", pts, [tuple(range(len(pts)))], membrane
        )
        ob.modifiers.new("adipose thickness", "SOLIDIFY").thickness = 0.007
    elif family == "perch":
        dorsal(-0.57, 0.02, 0.21, spines)
        dorsal(0.17, 0.66, 0.19)
    elif family == "bass":
        dorsal(-0.53, 0.055, 0.125 if kind == "bass" else 0.16, spines)
        dorsal(0.055, 0.69, 0.21)
    else:
        dorsal(-0.32 if family == "crappie" else -0.53, 0.13, 0.17, spines)
        dorsal(0.13, 0.72, 0.21)
    start = 0.10 if family == "crappie" else 0.02 if family == "catfish" else 0.33
    end = 0.79
    if family == "pike":
        start, end = 0.48, 0.86
    if "bullhead" in kind:
        start, end = 0.10, 0.71
    height = 0.215 if family == "crappie" else 0.14 if family == "catfish" else 0.16
    edge = [
        (
            start + (end - start) * t,
            0,
            center(start + (end - start) * t)
            - dims(start + (end - start) * t)[1]
            - height * math.sin(t * math.pi) ** 0.65,
        )
        for t in np.linspace(0, 1, 29)
    ]
    fin(
        kind + " anal",
        lambda t: (
            start + (end - start) * t,
            0,
            center(start + (end - start) * t)
            - dims(start + (end - start) * t)[1] * 0.95,
        ),
        edge,
        lower,
        rays,
    )
    if family in ("sunfish", "bass", "perch", "crappie"):
        count = (
            6
            if kind == "rock-bass"
            else (
                6
                if family == "crappie"
                else 3 if family in ("sunfish", "bass") or kind == "white-bass" else 2
            )
        )
        for i in range(count):
            t = 0.045 + i * 0.018
            b = Vector(
                (
                    start + (end - start) * t,
                    0,
                    center(start + (end - start) * t)
                    - dims(start + (end - start) * t)[1] * 0.96,
                )
            )
            e = Vector(edge[min(8, 2 + i)])
            tapered_tube(
                kind + " anal spine", [tuple(b), tuple(e)], [0.0022, 0.0003], rays
            )
    tx = cfg[-1][0]
    th = 0.265 if family not in ("pike", "trout") else 0.225
    fork = (
        0.18
        if kind in ("channel-catfish", "lake-trout", "white-bass")
        else 0.085 if family in ("pike", "perch") else 0.045
    )
    if kind == "flathead-catfish" or "bullhead" in kind or kind == "brook-trout":
        fork = -0.022
    edge = []
    for t in np.linspace(0, 1, 33):
        s = 2 * t - 1
        # Rounded lobe tips and slight inter-ray scalloping.
        edge.append(
            (
                tx
                + 0.245
                + fork * abs(s) ** 1.3
                - 0.035 * abs(s) ** 9
                + 0.004 * math.cos(t * math.pi * 32),
                0.004 * math.sin(t * math.pi),
                s * th,
            )
        )
    fin(
        kind + " caudal",
        lambda t: (tx - 0.016, 0, (t - 0.5) * 0.095),
        edge,
        membrane,
        rays,
    )
    if kind == "walleye":
        pale = mat("walleye white tail tip", (0.91, 0.90, 0.79), 0, 0.48)
        fin(
            "walleye lower tail tip",
            lambda t: (tx + 0.26, 0, -th + 0.05),
            edge[:5],
            pale,
            pale,
        )
        line(
            "walleye white anal tip",
            [
                (
                    start + 0.075,
                    0,
                    center(start + 0.075) - dims(start + 0.075)[1] - 0.055,
                ),
                (start + 0.15, 0, center(start + 0.15) - dims(start + 0.15)[1] - 0.13),
            ],
            0.005,
            pale,
        )
    return sport_finish(scene, kind)


def studio(scene, kind):
    bpy.ops.object.camera_add(location=(-0.19, -4.2, 0.19))
    cam = bpy.context.object
    cam.name = kind + " review camera"
    cam.rotation_euler = (
        (Vector((0, 0, 0.025)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    )
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.94
    scene.camera = cam
    for name, loc, power, size in [
        ("key", (-1.3, -2.8, 3.8), 210, 3.5),
        ("rim", (0.9, 1.9, 2.0), 240, 2.0),
        ("fill", (0.3, -2.1, -1.3), 70, 3.0),
    ]:
        bpy.ops.object.light_add(type="AREA", location=loc)
        o = bpy.context.object
        o.name = kind + " " + name
        o.data.energy = power
        o.data.shape = "DISK"
        o.data.size = size
        o.rotation_euler = (-o.location).to_track_quat("-Z", "Y").to_euler()


def lure_skin(kind):
    u, v = np.meshgrid(np.linspace(0, 1, 1024), np.linspace(0, 1, 512))
    z = np.sin(v * 2 * np.pi)
    back = np.clip((z + 0.02) * 1.4, 0, 1)[..., None]
    pearl = np.array((0.80, 0.81, 0.73))
    olive = np.array((0.065, 0.115, 0.052))
    rgb = pearl * (1 - back) + olive * back
    if kind == "jerkbait":
        olive = np.array((0.065, 0.14, 0.19))
        rgb = pearl * (1 - back) + olive * back
    # Painted scale foil conforms to the body, including the pearl belly.
    row = v * 42
    col = u * 66 + np.floor(row) % 2 * 0.5
    arc = np.sqrt(((col % 1 - 0.5) * 1.2) ** 2 + ((row % 1 - 0.5) * 0.9) ** 2)
    scales = np.exp(-(((arc - 0.46) / 0.05) ** 2)) * (1 - np.abs(z) ** 3)
    rgb *= (1 - 0.20 * scales)[..., None]
    stripe = np.exp(-(((z - 0.36) / 0.22) ** 4)) * np.clip((u - 0.20) * 10, 0, 1)
    rgb = (
        rgb * (1 - stripe[..., None] * 0.25)
        + np.array((0.45, 0.50, 0.12)) * stripe[..., None] * 0.25
    )
    if kind != "jerkbait":
        bars = (
            np.maximum(0, np.cos((u - 0.12) * np.pi * 12)) ** 12
            * np.clip((z + 0.12) * 3, 0, 1)
            * np.clip((u - 0.18) * 9, 0, 1)
        )
        rgb *= (1 - bars * 0.60)[..., None]
    noise = noise2(u * 470, v * 360, 5)
    rgb *= (0.97 + 0.045 * noise)[..., None]
    m = mat(kind + " coated lure finish", (0.4, 0.5, 0.2), 0.30, 0.26)
    image_input(
        m, packed_image(kind + " painted scale foil", np.clip(rgb, 0, 1)), "Base Color"
    )
    return m


def build_hard_lure(kind):
    scene = setup(kind)
    scene["bait_id"] = kind
    steel = mat("polished stainless", (0.54, 0.57, 0.60), 1, 0.19)
    paint = lure_skin(kind)
    eye = mat("lure iris", (0.58, 0.37, 0.055), 0.46, 0.18)
    black = mat("lure pupil", (0.003, 0.006, 0.006), 0, 0.15)
    red = mat("popper cup red lacquer", (0.55, 0.036, 0.017), 0.10, 0.26)
    if kind == "crankbait":
        cfg = [
            (-0.66, 0.003, 0.012),
            (-0.59, 0.115, 0.165),
            (-0.40, 0.194, 0.245),
            (-0.14, 0.205, 0.25),
            (0.18, 0.16, 0.197),
            (0.45, 0.085, 0.10),
            (0.62, 0.010, 0.013),
        ]
    elif kind == "jerkbait":
        cfg = [
            (-0.93, 0.004, 0.012),
            (-0.78, 0.086, 0.12),
            (-0.55, 0.117, 0.152),
            (-0.05, 0.106, 0.131),
            (0.46, 0.073, 0.094),
            (0.9, 0.008, 0.014),
        ]
    else:
        cfg = [
            (-0.66, 0.17, 0.195),
            (-0.55, 0.185, 0.207),
            (-0.26, 0.167, 0.183),
            (0.10, 0.139, 0.143),
            (0.46, 0.085, 0.09),
            (0.67, 0.018, 0.025),
        ]

    def dims(x):
        for idx, (a, b) in enumerate(zip(cfg, cfg[1:])):
            if a[0] <= x <= b[0]:
                dt = b[0] - a[0]
                t = (x - a[0]) / dt
                out = []
                for k in (1, 2):
                    slope = (b[k] - a[k]) / dt
                    prev = (
                        (a[k] - cfg[idx - 1][k]) / (a[0] - cfg[idx - 1][0])
                        if idx
                        else slope
                    )
                    nxt = (
                        (cfg[idx + 2][k] - b[k]) / (cfg[idx + 2][0] - b[0])
                        if idx < len(cfg) - 2
                        else slope
                    )
                    m0 = 2 * prev * slope / (prev + slope) if prev * slope > 0 else 0
                    m1 = 2 * nxt * slope / (nxt + slope) if nxt * slope > 0 else 0
                    out.append(
                        (2 * t**3 - 3 * t * t + 1) * a[k]
                        + (t**3 - 2 * t * t + t) * dt * m0
                        + (-2 * t**3 + 3 * t * t) * b[k]
                        + (t**3 - t * t) * dt * m1
                    )
                return out
        return cfg[-1][1:]

    nx, nr = 110, 64
    verts = []
    faces = []
    for i in range(nx + 1):
        x = cfg[0][0] + (cfg[-1][0] - cfg[0][0]) * i / nx
        w, h = dims(x)
        for j in range(nr):
            a = j * 2 * math.pi / nr
            verts.append((x, w * math.cos(a), 0.08 + h * math.sin(a)))
    for i in range(nx):
        for j in range(nr):
            a = i * nr + j
            b = i * nr + (j + 1) % nr
            faces.append((a, b, b + nr, a + nr))
    if kind != "popper":
        faces.append(tuple(range(nr - 1, -1, -1)))
    faces.append(tuple(nx * nr + j for j in range(nr)))
    body = mesh(kind + " molded body", verts, faces, paint)
    uv = body.data.uv_layers.new(name="UVMap")
    for p in body.data.polygons:
        js = [body.data.loops[l].vertex_index % nr for l in p.loop_indices]
        seam = max(js) - min(js) > nr / 2
        for l in p.loop_indices:
            i, j = divmod(body.data.loops[l].vertex_index, nr)
            uv.data[l].uv = (i / nx, 1 if seam and j == 0 else j / nr)
    ex = cfg[0][0] + (0.23 if kind != "jerkbait" else 0.25)
    w, h = dims(ex)
    for side in (-1, 1):
        for name, off, scale, m in [
            ("recessed lure eye", 0.002, (0.043, 0.009, 0.043), eye),
            ("lure pupil", 0.012, (0.024, 0.006, 0.027), black),
        ]:
            oval(
                name,
                (ex, side * (w * math.sqrt(1 - (0.05 / h) ** 2) + off), 0.13),
                scale,
                m,
            )
        pts = []
        for t in np.linspace(-1, 1, 31):
            x = ex + 0.15 + 0.045 * math.cos(t)
            w, h = dims(x)
            z = 0.08 + h * 0.65 * math.sin(t)
            pts.append(
                (x, side * (w * math.sqrt(1 - ((z - 0.08) / h) ** 2) + 0.001), z)
            )
        line("molded gill relief", pts, 0.0013, black)
    if kind != "popper":
        clear = mat("clear polycarbonate bill", (0.84, 0.89, 0.92), 0, 0.16)
        p = clear.node_tree.nodes.get("Principled BSDF")
        p.inputs["Transmission Weight"].default_value = 0.86
        p.inputs["IOR"].default_value = 1.49
        p.inputs["Coat Weight"].default_value = 0.25
        # Broad crankbait bill, short jerkbait lip, seated into the nose.
        bill = blade(
            "transparent diving lip",
            (cfg[0][0] - 0.055, 0, -0.044),
            0.38 if kind == "crankbait" else 0.21,
            0.13 if kind == "crankbait" else 0.088,
            clear,
        )
        bill.rotation_euler[1] = -0.48
        ring("nose line eye", (cfg[0][0] - 0.023, 0, 0.07), 0.025, steel)
    else:
        # A recessed bowl replaces the old flat face and floating mouth ring.
        verts = []
        faces = []
        nx, nr = 12, 64
        for i in range(nx + 1):
            r = 0.001 + 0.999 * i / nx
            for j in range(nr):
                a = j * 2 * math.pi / nr
                verts.append(
                    (
                        -0.66 + 0.12 * (1 - r * r),
                        0.17 * r * math.cos(a),
                        0.08 + 0.195 * r * math.sin(a),
                    )
                )
        for i in range(nx):
            for j in range(nr):
                a = i * nr + j
                b = i * nr + (j + 1) % nr
                faces.append((a, b, b + nr, a + nr))
        mesh("recessed concave popper mouth", verts, faces, red)
        ring("cup line eye", (-0.561, 0, 0.08), 0.026, steel)
    for x in (-0.06, cfg[-1][0] - 0.06):
        w, h = dims(x)
        z = 0.08 - h - 0.018
        ring("screw eye hanger", (x, 0, z + 0.005), 0.018, steel, axis="X")
        treble((x, 0, z - 0.034), 0.265 if kind != "jerkbait" else 0.23, steel)
    return sport_finish(scene, kind)


def refine_tackle(scene, kind):
    """Surface and assembly details for the remaining original tackle meshes."""
    for o in scene.objects:
        if o.type == "MESH" and not o.data.uv_layers:
            uv = o.data.uv_layers.new(name="UVMap")
            xs = [v.co.x for v in o.data.vertices]
            ys = [v.co.y for v in o.data.vertices]
            dx = max(xs) - min(xs) or 1
            dy = max(ys) - min(ys) or 1
            for loop in o.data.loops:
                p = o.data.vertices[loop.vertex_index].co
                uv.data[loop.index].uv = ((p.x - min(xs)) / dx, (p.y - min(ys)) / dy)
    for m in {m for o in scene.objects for m in getattr(o.data, "materials", []) if m}:
        p = m.node_tree.nodes.get("Principled BSDF")
        if not p:
            continue
        if "brass" in m.name or "stainless" in m.name:
            p.inputs["Metallic"].default_value = 1
            p.inputs["Roughness"].default_value = 0.23 if "brass" in m.name else 0.20
        if ("brass" in m.name or "pearl belly" in m.name) and kind in (
            "spoon",
            "spinner",
            "spinnerbait",
        ):
            p.inputs["Metallic"].default_value = 1
            u, v = np.meshgrid(np.linspace(0, 1, 512), np.linspace(0, 1, 256))
            noise = noise2(u * 110, v * 37, 31)
            scratch = 0.24 + 0.035 * (noise - 0.5) + 0.010 * np.sin(u * 950 + v * 5)
            image_input(
                m,
                packed_image(
                    kind + " brushed metal roughness",
                    np.repeat(scratch[..., None], 3, axis=2),
                    True,
                ),
                "Roughness",
            )
        if kind in ("frog", "jig", "spinnerbait") and any(
            w in m.name for w in ("olive lure", "pearl belly")
        ):
            p.inputs["Metallic"].default_value = 0
            p.inputs["Roughness"].default_value = 0.46
            p.inputs["Coat Weight"].default_value = 0.16
        if "rubber" in m.name or "worm skin" in m.name:
            u, v = np.meshgrid(np.linspace(0, 1, 1024), np.linspace(0, 1, 256))
            n = noise2(u * 91, v * 23, 9)
            rgb = np.array(p.inputs["Base Color"].default_value[:3])
            color = (
                np.broadcast_to(rgb, (256, 1024, 3)).copy()
                * (0.78 + 0.40 * n)[..., None]
            )
            if kind == "worm":
                color *= (1 - 0.17 * np.exp(-((np.sin(u * np.pi * 98) / 0.17) ** 2)))[
                    ..., None
                ]
                vein = np.exp(-(((np.sin(v * 2 * np.pi) - 0.88) / 0.07) ** 2))
                color *= (1 - 0.23 * vein)[..., None]
            else:
                fleck = np.clip((noise2(u * 440, v * 150, 12) - 0.70) * 6, 0, 1)
                color *= (1 - fleck * 0.88)[..., None]
            image_input(
                m,
                packed_image(kind + " organic surface", np.clip(color, 0, 1)),
                "Base Color",
            )
            p.inputs["Roughness"].default_value = 0.39
            p.inputs["Coat Weight"].default_value = 0.25
    if kind == "worm":
        collar = mat("worm smooth clitellum", (0.38, 0.135, 0.085), 0, 0.41)
        for o in scene.objects:
            if o.name.startswith("raised clitellum"):
                o.data.materials.clear()
                o.data.materials.append(collar)
    if kind == "spinnerbait":
        for o in scene.objects:
            if o.name.startswith("willow blade"):
                o.rotation_euler[0] = 0.65
    if kind == "spinner":
        steel = next(m for m in bpy.data.materials if "v4 polished stainless" in m.name)
        ring("blade attachment eye", (-0.73, 0, 0.205), 0.023, steel, axis="X")
        for o in scene.objects:
            if o.name.startswith("inline wire shaft"):
                o.data.splines[0].points[-1].co.x = 0.66
    if kind == "spoon":
        for o in list(scene.objects):
            if o.name.startswith("red painted spoon stripe"):
                bpy.data.objects.remove(o, do_unlink=True)
            elif o.name.startswith("concave casting spoon"):
                for loop in o.data.loops:
                    i, j = divmod(loop.vertex_index, 17)
                    o.data.uv_layers.active.data[loop.index].uv = (i / 30, j / 16)
                u, v = np.meshgrid(np.linspace(0, 1, 1024), np.linspace(0, 1, 512))
                mask = np.clip(
                    (0.17 - np.abs((u - 0.5) + 0.30 * (v - 0.5))) * 160, 0, 1
                )
                color = (
                    np.array((0.69, 0.72, 0.75)) * (1 - mask[..., None])
                    + np.array((0.58, 0.022, 0.012)) * mask[..., None]
                )
                finish = mat("spoon painted steel", (0.6, 0.6, 0.6), 1, 0.24)
                image_input(
                    finish, packed_image("spoon enamel band", color), "Base Color"
                )
                image_input(
                    finish,
                    packed_image(
                        "spoon metal mask",
                        np.repeat((1 - mask * 0.96)[..., None], 3, axis=2),
                        True,
                    ),
                    "Metallic",
                )
                o.data.materials.clear()
                o.data.materials.append(finish)
    if kind == "soft-plastic":
        for o in list(scene.objects):
            if o.name.startswith("embedded fleck"):
                bpy.data.objects.remove(o, do_unlink=True)
    if kind == "frog":
        # Pressed double-hook tips taper and rest against the hollow body.
        steel = next(m for m in bpy.data.materials if "v4 polished stainless" in m.name)
        for o in list(scene.objects):
            if o.name.startswith("double weedless hook"):
                bpy.data.objects.remove(o, do_unlink=True)
        for side in (-1, 1):
            pts = [
                (-0.02, side * 0.21, -0.10),
                (0.22, side * 0.24, -0.07),
                (0.38, side * 0.25, 0.05),
                (0.29, side * 0.22, 0.145),
                (0.12, side * 0.20, 0.15),
            ]
            tapered_tube(
                "tapered weedless frog hook",
                pts,
                [0.009, 0.009, 0.009, 0.005, 0.0006],
                steel,
            )
    if kind in ("jig", "spinnerbait"):
        collar = mat("skirt binding collar", (0.028, 0.041, 0.027), 0, 0.6)
        oval(
            "rubber skirt collar",
            (-0.285, 0, -0.20 if kind == "spinnerbait" else 0.08),
            (0.045, 0.065, 0.065),
            collar,
        )
        # A fine bristle guard emerges from the head and protects the single hook.
        for j in range(5):
            z = -0.20 if kind == "spinnerbait" else 0.08
            line(
                "nylon weed guard",
                [
                    (-0.39, j * 0.005 - 0.01, z + 0.065),
                    (-0.18, j * 0.006 - 0.012, z + 0.285),
                    (0.03, j * 0.007 - 0.014, z + 0.30),
                ],
                0.002,
                collar,
            )


def build_minnow():
    kind = "minnow"
    scene = setup(kind)
    scene["bait_id"] = kind
    u, v = np.meshgrid(np.linspace(0, 1, 1024), np.linspace(0, 1, 512))
    z = np.sin(v * 2 * np.pi)
    dorsal = np.clip((z + 0.1) * 1.5, 0, 1)[..., None]
    rgb = (
        np.array((0.73, 0.79, 0.77)) * (1 - dorsal)
        + np.array((0.10, 0.18, 0.15)) * dorsal
    )
    stripe = np.exp(-(((z - 0.04) / 0.13) ** 4)) * np.clip((u - 0.14) * 10, 0, 1)
    rgb *= (1 - stripe * 0.65)[..., None]
    rows = v * 40
    cols = u * 75 + np.floor(rows) % 2 * 0.5
    margin = np.exp(
        -(
            (
                (
                    np.sqrt(
                        ((cols % 1 - 0.5) * 1.2) ** 2 + ((rows % 1 - 0.5) * 0.85) ** 2
                    )
                    - 0.46
                )
                / 0.04
            )
            ** 2
        )
    )
    rgb *= (1 - margin * 0.16)[..., None]
    skin = mat("minnow silver skin", (0.57, 0.65, 0.59), 0.08, 0.39)
    image_input(
        skin,
        packed_image("minnow countershaded scales", np.clip(rgb, 0, 1)),
        "Base Color",
    )
    dy, dx = np.gradient(-margin * 0.15)
    normal = np.stack((-dx, -dy, np.ones_like(dx)), axis=2)
    normal /= np.linalg.norm(normal, axis=2, keepdims=True)
    normal_input(
        skin, packed_image("minnow scale relief", normal * 0.5 + 0.5, True), 0.32
    )
    nx, nr = 130, 48
    verts = []
    faces = []

    def dims(t):
        return (
            0.012 + 0.11 * math.sin(math.pi * t) ** 0.70,
            0.014 + 0.17 * math.sin(math.pi * t) ** 0.85,
        )

    for i in range(nx + 1):
        t = i / nx
        w, h = dims(t)
        for j in range(nr):
            a = j * 2 * math.pi / nr
            verts.append((-0.91 + 1.68 * t, w * math.cos(a), h * math.sin(a)))
    for i in range(nx):
        for j in range(nr):
            a = i * nr + j
            b = i * nr + (j + 1) % nr
            faces.append((a, b, b + nr, a + nr))
    faces.extend((tuple(range(nr - 1, -1, -1)), tuple(nx * nr + j for j in range(nr))))
    o = mesh("minnow body", verts, faces, skin)
    uv = o.data.uv_layers.new(name="UVMap")
    for p in o.data.polygons:
        js = [o.data.loops[l].vertex_index % nr for l in p.loop_indices]
        seam = max(js) - min(js) > nr / 2
        for l in p.loop_indices:
            i, j = divmod(o.data.loops[l].vertex_index, nr)
            uv.data[l].uv = (i / nx, 1 if seam and j == 0 else j / nr)
    membrane = mat("minnow delicate fins", (0.42, 0.50, 0.43), 0, 0.48)
    rays = mat("minnow soft rays", (0.23, 0.30, 0.23), 0, 0.48)
    iris = mat("minnow iris", (0.66, 0.61, 0.35), 0.05, 0.20)
    black = mat("minnow pupil", (0.004, 0.009, 0.008), 0, 0.16)
    for side in (-1, 1):
        oval("minnow eye", (-0.72, side * 0.072, 0.044), (0.029, 0.008, 0.029), iris)
        oval(
            "minnow pupil", (-0.723, side * 0.081, 0.045), (0.020, 0.005, 0.021), black
        )
        line(
            "minnow gill cover",
            [
                (-0.52, side * 0.104, 0.10),
                (-0.48, side * 0.116, 0.03),
                (-0.51, side * 0.09, -0.10),
            ],
            0.0015,
            black,
        )
        line(
            "minnow mouth",
            [(-0.914, side * 0.012, 0), (-0.79, side * 0.056, -0.017)],
            0.0015,
            black,
        )
        fin(
            "minnow pectoral",
            lambda t: (-0.49, side * 0.105, -0.01),
            [
                (
                    -0.46 + 0.24 * math.sin(t * math.pi) ** 0.6,
                    side * (0.13 + 0.025 * t),
                    -0.035 - 0.12 * t,
                )
                for t in np.linspace(0, 1, 15)
            ],
            membrane,
            rays,
        )
        fin(
            "minnow pelvic",
            lambda t: (0.02 + 0.07 * t, side * 0.065, -0.13),
            [
                (0.055 + 0.18 * math.sin(t * math.pi), side * 0.11, -0.15 - 0.085 * t)
                for t in np.linspace(0, 1, 13)
            ],
            membrane,
            rays,
        )
    fin(
        "minnow dorsal",
        lambda t: (-0.18 + 0.36 * t, 0, 0.16),
        [
            (-0.18 + 0.36 * t, 0, 0.16 + 0.17 * math.sin(t * math.pi) ** 0.65)
            for t in np.linspace(0, 1, 21)
        ],
        membrane,
        rays,
    )
    fin(
        "minnow anal",
        lambda t: (0.35 + 0.22 * t, 0, -0.115),
        [
            (0.35 + 0.22 * t, 0, -0.115 - 0.105 * math.sin(t * math.pi))
            for t in np.linspace(0, 1, 15)
        ],
        membrane,
        rays,
    )
    fin(
        "minnow caudal",
        lambda t: (0.76, 0, (t - 0.5) * 0.035),
        [
            (0.94 + 0.12 * abs(2 * t - 1), 0, (2 * t - 1) * 0.19)
            for t in np.linspace(0, 1, 27)
        ],
        membrane,
        rays,
    )
    return sport_finish(scene, kind)


def sport_finish(scene, kind):
    if kind not in SPECS and kind not in ("crankbait", "jerkbait", "popper", "minnow"):
        refine_tackle(scene, kind)
    studio(scene, kind)
    for o in scene.objects:
        o["fishdex_revision"] = 4
        if o.type == "MESH" and o.data.uv_layers.active:
            o.data.uv_layers.active.name = "UVMap"
    scene.render.filepath = str(Path(ROOT) / "assets/specimens" / (kind + ".png"))
    bpy.ops.render.render(write_still=True)
    # An additional oblique view exposes depth, paired fins, and hardware joins.
    cam = scene.camera
    original = cam.location.copy()
    rotation = cam.rotation_euler.copy()
    cam.location = (-1.5, -4, 0.95)
    cam.rotation_euler = (
        (Vector((0, 0, 0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    )
    scene.render.filepath = str(REVIEW / (kind + "-angle.png"))
    bpy.ops.render.render(write_still=True)
    cam.location = original
    cam.rotation_euler = rotation
    source = V4 / (kind + ".blend")
    bpy.data.libraries.write(str(source), {scene}, fake_user=True, compress=True)
    bpy.ops.scene.new(type="FULL_COPY")
    runtime = bpy.context.scene
    runtime.name = "Fishdex v4 " + kind + " runtime"
    objects = [o for o in runtime.objects if o.type in ("MESH", "CURVE")]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = kind + " specimen"
    # Multiple UV names from body/fins become one active map during a join.
    bpy.ops.export_scene.gltf(
        filepath=ROOT + "/assets/models/" + kind + ".glb",
        export_format="GLB",
        use_selection=True,
        use_active_scene=True,
        export_yup=True,
        export_image_format="JPEG",
        export_jpeg_quality=90,
        export_extras=True,
    )
    path = Path(ROOT) / "assets/models" / (kind + ".glb")
    data = path.read_bytes()
    size = int.from_bytes(data[12:16], "little")
    gltf = json.loads(data[20 : 20 + size])
    record = {
        "asset": kind,
        "revision": 4,
        "blender": bpy.app.version_string,
        "source": source.name,
        "source_bytes": source.stat().st_size,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "glb_bytes": path.stat().st_size,
        "glb_sha256": hashlib.sha256(data).hexdigest(),
        "primitives": sum(len(m["primitives"]) for m in gltf["meshes"]),
        "triangles": sum(
            gltf["accessors"][p["indices"]]["count"] // 3
            for m in gltf["meshes"]
            for p in m["primitives"]
        ),
        "scene": scene.name,
    }
    (V4 / (kind + ".json")).write_text(json.dumps(record, indent=2) + "\n")
    print("FISHDEX_COMPLETE " + json.dumps(record), flush=True)
    return record


def build_refined(kind):
    global _CURRENT, _ACTIVE_KIND, _FIN_CACHE
    _CURRENT = kind
    _ACTIVE_KIND = kind
    _FIN_CACHE = {}
    if kind in SPECS:
        return build_refined_fish(kind)
    if kind in ("crankbait", "jerkbait", "popper"):
        return build_hard_lure(kind)
    if kind == "minnow":
        return build_minnow()
    return _LEGACY_TACKLE(kind)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else ["bass"]
    for kind in args:
        build_refined(kind)
