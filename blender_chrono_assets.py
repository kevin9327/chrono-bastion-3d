import math
import os
import bpy

BASE_DIR = "/Users/kevin/contest_submissions/70_saaskr_ai_webgame_awards"
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def pbr_mat(name, color, metallic=0.6, roughness=0.3, emission=None, emission_strength=0.0):
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return m


def smooth_bevel(obj, width=0.025, segments=2):
    bev = obj.modifiers.new(name="Bevel", type="BEVEL")
    bev.width = width
    bev.segments = segments
    for p in obj.data.polygons:
        p.use_smooth = True


def export_glb(filename):
    out_p = os.path.join(MODEL_DIR, filename)
    bpy.ops.export_scene.gltf(
        filepath=out_p,
        export_format="GLB",
        export_apply=True,
        export_yup=True,
        export_materials="EXPORT",
    )
    print(f"[Blender GLB] Exported {out_p} ({os.path.getsize(out_p)//1024} KB)")


# 1. BASTION CITADEL (Central Time-Core Spire with Astrolabe Rings)
def build_bastion_citadel():
    reset_scene()
    m_obsidian = pbr_mat("Obsidian", (0.07, 0.09, 0.14), metallic=0.75, roughness=0.28)
    m_gold = pbr_mat("ChronoGold", (0.94, 0.74, 0.30), metallic=0.92, roughness=0.18)
    m_core = pbr_mat("AmberCore", (1.0, 0.65, 0.15), metallic=0.1, roughness=0.1, emission=(1.0, 0.58, 0.12), emission_strength=8.0)
    m_cyan = pbr_mat("CyanTrim", (0.15, 0.90, 1.0), metallic=0.2, roughness=0.15, emission=(0.15, 0.85, 1.0), emission_strength=5.0)

    # Stepped octagonal base
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.25, depth=0.36, location=(0, 0, 0.18))
    b1 = bpy.context.active_object
    b1.data.materials.append(m_obsidian)
    smooth_bevel(b1, 0.03)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.95, depth=0.45, location=(0, 0, 0.52))
    b2 = bpy.context.active_object
    b2.data.materials.append(m_obsidian)
    smooth_bevel(b2, 0.03)

    # Glowing energy ring groove
    bpy.ops.mesh.primitive_torus_add(major_radius=1.02, minor_radius=0.045, location=(0, 0, 0.38))
    rg = bpy.context.active_object
    rg.data.materials.append(m_cyan)

    # 4 Armored Buttress Pillars around the Crystal
    for i in range(4):
        ang = i * (math.pi / 2.0) + math.pi / 4.0
        px, py = math.cos(ang) * 0.72, math.sin(ang) * 0.72
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, py, 1.15), rotation=(0, math.radians(-12), ang))
        pil = bpy.context.active_object
        pil.scale = (0.22, 0.18, 1.25)
        pil.data.materials.append(m_gold if i % 2 == 0 else m_obsidian)
        smooth_bevel(pil, 0.02)

    # Central Levitating Chronos Crystal (Octahedron-like dual cones)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.48, location=(0, 0, 1.55))
    cr = bpy.context.active_object
    cr.scale = (0.85, 0.85, 1.45)
    cr.data.materials.append(m_core)

    # Two Interlocking Golden Astrolabe Rings
    for tilt, rad in [(32, 0.82), (-38, 0.96)]:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=rad,
            minor_radius=0.035,
            location=(0, 0, 1.55),
            rotation=(math.radians(tilt), math.radians(18), 0),
        )
        ring = bpy.context.active_object
        ring.data.materials.append(m_gold)

    export_glb("bastion_citadel.glb")


# 2. COMMAND DRONE VALKYRIE (Player Controlled Tactical Drone)
def build_drone_valkyrie():
    reset_scene()
    m_hull = pbr_mat("ValkyrieHull", (0.92, 0.95, 1.0), metallic=0.65, roughness=0.22)
    m_gold = pbr_mat("ValkyrieGold", (0.95, 0.76, 0.28), metallic=0.90, roughness=0.18)
    m_dark = pbr_mat("ValkyrieDark", (0.10, 0.13, 0.20), metallic=0.80, roughness=0.30)
    m_thruster = pbr_mat("ValkyrieCyan", (0.12, 0.92, 1.0), metallic=0.1, roughness=0.1, emission=(0.1, 0.88, 1.0), emission_strength=9.0)

    # Sleek central fuselage
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=18, radius=0.42, location=(0, 0, 0.35))
    body = bpy.context.active_object
    body.scale = (0.95, 1.35, 0.55)
    body.data.materials.append(m_hull)

    # Glowing cockpit visor
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.26, location=(0, -0.22, 0.42))
    visor = bpy.context.active_object
    visor.scale = (0.9, 1.0, 0.55)
    visor.data.materials.append(m_thruster)

    # Swept wings + twin rotor pods
    for s in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(s * 0.58, 0.06, 0.35), rotation=(0, 0, math.radians(s * -18)))
        wing = bpy.context.active_object
        wing.scale = (0.65, 0.26, 0.06)
        wing.data.materials.append(m_gold)
        smooth_bevel(wing, 0.015)

        bpy.ops.mesh.primitive_torus_add(major_radius=0.24, minor_radius=0.045, location=(s * 0.88, 0.12, 0.36))
        pod = bpy.context.active_object
        pod.data.materials.append(m_dark)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.05, location=(s * 0.88, 0.12, 0.34))
        glow = bpy.context.active_object
        glow.data.materials.append(m_thruster)

        # Twin forward pulse barrels
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.45, location=(s * 0.22, -0.52, 0.26), rotation=(math.radians(90), 0, 0))
        gun = bpy.context.active_object
        gun.data.materials.append(m_dark)

    export_glb("drone_valkyrie.glb")


# 3. FOUR SPECIALIZED TURRETS
def build_turrets():
    # 3A: Arc Prism Obelisk
    reset_scene()
    m_base = pbr_mat("TurretSteel", (0.11, 0.15, 0.22), metallic=0.82, roughness=0.26)
    m_brass = pbr_mat("TurretBrass", (0.90, 0.70, 0.28), metallic=0.88, roughness=0.20)
    m_cyan = pbr_mat("PrismGlow", (0.10, 0.95, 0.92), metallic=0.1, roughness=0.1, emission=(0.10, 0.95, 0.90), emission_strength=8.5)

    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.58, depth=0.26, location=(0, 0, 0.13))
    ped = bpy.context.active_object
    ped.data.materials.append(m_base)
    smooth_bevel(ped, 0.02)

    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.36, radius2=0.14, depth=0.85, location=(0, 0, 0.68))
    pyl = bpy.context.active_object
    pyl.data.materials.append(m_base)
    smooth_bevel(pyl, 0.015)

    for zc in (0.45, 0.72, 0.98):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.30 * (1.25 - zc * 0.4), minor_radius=0.03, location=(0, 0, zc))
        coil = bpy.context.active_object
        coil.data.materials.append(m_brass)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.24, location=(0, 0, 1.35))
    gem = bpy.context.active_object
    gem.scale = (0.85, 0.85, 1.35)
    gem.data.materials.append(m_cyan)
    export_glb("turret_prism.glb")

    # 3B: Singularity Gravity-Well Mortar
    reset_scene()
    m_base = pbr_mat("GravSteel", (0.12, 0.11, 0.20), metallic=0.82, roughness=0.28)
    m_violet = pbr_mat("VoidGlow", (0.72, 0.28, 1.0), metallic=0.1, roughness=0.1, emission=(0.68, 0.22, 1.0), emission_strength=8.5)
    m_silver = pbr_mat("SilverTrim", (0.78, 0.82, 0.90), metallic=0.9, roughness=0.2)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.62, depth=0.28, location=(0, 0, 0.14))
    ped = bpy.context.active_object
    ped.data.materials.append(m_base)
    smooth_bevel(ped, 0.02)

    for i in range(3):
        ang = i * (2 * math.pi / 3.0)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(math.cos(ang) * 0.38, math.sin(ang) * 0.38, 0.62), rotation=(0, math.radians(-22), ang))
        claw = bpy.context.active_object
        claw.scale = (0.18, 0.14, 0.72)
        claw.data.materials.append(m_silver)
        smooth_bevel(claw, 0.015)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.30, location=(0, 0, 0.88))
    orb = bpy.context.active_object
    orb.data.materials.append(m_violet)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.44, minor_radius=0.04, location=(0, 0, 0.88), rotation=(math.radians(22), 0, 0))
    ring = bpy.context.active_object
    ring.data.materials.append(m_base)
    export_glb("turret_gravity.glb")

    # 3C: Chrono-Stasis Spire
    reset_scene()
    m_base = pbr_mat("ChronoBase", (0.10, 0.16, 0.24), metallic=0.8, roughness=0.25)
    m_gold = pbr_mat("GearGold", (0.94, 0.76, 0.32), metallic=0.92, roughness=0.18)
    m_ice = pbr_mat("StasisIce", (0.35, 0.78, 1.0), metallic=0.1, roughness=0.08, emission=(0.30, 0.72, 1.0), emission_strength=8.0)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.58, depth=0.24, location=(0, 0, 0.12))
    ped = bpy.context.active_object
    ped.data.materials.append(m_base)

    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.16, depth=1.15, location=(0, 0, 0.72))
    sp = bpy.context.active_object
    sp.data.materials.append(m_ice)

    for z_g, r_g in [(0.42, 0.46), (0.82, 0.38), (1.18, 0.28)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r_g, depth=0.06, location=(0, 0, z_g))
        gear = bpy.context.active_object
        gear.data.materials.append(m_gold)
    export_glb("turret_chrono.glb")

    # 3D: Twin Orbital Railgun
    reset_scene()
    m_dark = pbr_mat("RailSteel", (0.12, 0.13, 0.17), metallic=0.86, roughness=0.24)
    m_crimson = pbr_mat("RailCore", (1.0, 0.32, 0.18), metallic=0.1, roughness=0.1, emission=(1.0, 0.28, 0.12), emission_strength=8.5)
    m_copper = pbr_mat("RailCopper", (0.88, 0.52, 0.24), metallic=0.90, roughness=0.20)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.62, depth=0.30, location=(0, 0, 0.15))
    ped = bpy.context.active_object
    ped.data.materials.append(m_dark)
    smooth_bevel(ped, 0.02)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.08, 0.62))
    tur = bpy.context.active_object
    tur.scale = (0.58, 0.62, 0.42)
    tur.data.materials.append(m_dark)
    smooth_bevel(tur, 0.02)

    for s in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(s * 0.16, -0.45, 0.66))
        rail = bpy.context.active_object
        rail.scale = (0.10, 0.95, 0.14)
        rail.data.materials.append(m_copper)
        smooth_bevel(rail, 0.01)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.92, location=(0, -0.42, 0.66), rotation=(math.radians(90), 0, 0))
    core = bpy.context.active_object
    core.data.materials.append(m_crimson)
    export_glb("turret_railgun.glb")


# 4. ENEMY MECHS (Rift Stalker & Rift Dreadnought Boss)
def build_enemies():
    # 4A: Rift Stalker (4-legged Void Spider-Mech)
    reset_scene()
    m_armor = pbr_mat("StalkerArmor", (0.14, 0.08, 0.18), metallic=0.78, roughness=0.28)
    m_eye = pbr_mat("StalkerEye", (1.0, 0.18, 0.48), metallic=0.1, roughness=0.1, emission=(1.0, 0.15, 0.45), emission_strength=9.0)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.38, location=(0, 0, 0.48))
    hull = bpy.context.active_object
    hull.scale = (1.0, 1.25, 0.72)
    hull.data.materials.append(m_armor)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.16, location=(0, -0.34, 0.50))
    eye = bpy.context.active_object
    eye.scale = (1.3, 0.6, 0.6)
    eye.data.materials.append(m_eye)

    for lx in (-1, 1):
        for ly in (-1, 1):
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(lx * 0.42, ly * 0.32, 0.26),
                rotation=(math.radians(ly * 18), math.radians(lx * 28), 0),
            )
            leg = bpy.context.active_object
            leg.scale = (0.09, 0.09, 0.52)
            leg.data.materials.append(m_armor)
            smooth_bevel(leg, 0.01)
    export_glb("enemy_stalker.glb")

    # 4B: Rift Dreadnought Boss Mech
    reset_scene()
    m_armor = pbr_mat("BossArmor", (0.18, 0.05, 0.08), metallic=0.84, roughness=0.24)
    m_gold = pbr_mat("BossTrim", (0.85, 0.45, 0.15), metallic=0.90, roughness=0.20)
    m_core = pbr_mat("BossCore", (1.0, 0.22, 0.10), metallic=0.1, roughness=0.1, emission=(1.0, 0.18, 0.08), emission_strength=11.0)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.85))
    torso = bpy.context.active_object
    torso.scale = (0.92, 0.68, 0.95)
    torso.data.materials.append(m_armor)
    smooth_bevel(torso, 0.04)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.26, location=(0, -0.32, 0.92))
    reactor = bpy.context.active_object
    reactor.data.materials.append(m_core)

    for s in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(s * 0.66, 0, 1.18), rotation=(0, math.radians(s * -15), 0))
        pauldron = bpy.context.active_object
        pauldron.scale = (0.38, 0.56, 0.42)
        pauldron.data.materials.append(m_gold)
        smooth_bevel(pauldron, 0.025)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(s * 0.30, 0, 0.28))
        leg = bpy.context.active_object
        leg.scale = (0.28, 0.38, 0.56)
        leg.data.materials.append(m_armor)
        smooth_bevel(leg, 0.02)

        bpy.ops.mesh.primitive_cone_add(radius1=0.10, radius2=0.01, depth=0.48, location=(s * 0.26, -0.10, 1.56), rotation=(0, math.radians(s * 22), 0))
        horn = bpy.context.active_object
        horn.data.materials.append(m_core)

    export_glb("enemy_colossus.glb")


if __name__ == "__main__":
    build_bastion_citadel()
    build_drone_valkyrie()
    build_turrets()
    build_enemies()
