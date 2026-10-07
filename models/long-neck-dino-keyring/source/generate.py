#!/usr/bin/env python3
"""Generate a roughly 50 mm long-neck dinosaur keyring as multipart STL files.

AI-assisted design by Levi / Cyberlevi.
SPDX-License-Identifier: CC-BY-NC-SA-4.0

Install requirements.txt, then run:
    python generate.py --output ./generated
Coordinates and dimensions are in millimetres. The metal split ring is not included.
Generation uses a dense implicit field and may take a few minutes.
"""

import argparse
from io import BytesIO
import json
from pathlib import Path

import numpy as np
import manifold3d
from shapely.geometry import Point
from skimage.measure import marching_cubes
import trimesh


def smooth_min(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def ellipsoid(center, radii, subdivisions=3):
    mesh = trimesh.creation.icosphere(subdivisions=subdivisions)
    mesh.vertices = mesh.vertices * np.array(radii) + np.array(center)
    return mesh


def clean(mesh, minimum_volume=1e-5):
    return trimesh.util.concatenate([
        part for part in mesh.split() if abs(part.volume) > minimum_volume
    ])


def build_body():
    """Build the original full-size body before its STL-roundtrip and scaling."""
    step = 0.5
    xs = np.arange(-34, 34.01, step, dtype=np.float32)
    ys = np.arange(-78, 66.01, step, dtype=np.float32)
    zs = np.arange(-3, 140.01, step, dtype=np.float32)
    x, y, z = np.meshgrid(xs, ys, zs, indexing="ij", sparse=True)
    field = np.full((len(xs), len(ys), len(zs)), 1000, dtype=np.float32)

    def add_ellipsoid(center, radii, blend=3):
        nonlocal field
        distance = (
            np.sqrt(
                ((x - center[0]) / radii[0]) ** 2
                + ((y - center[1]) / radii[1]) ** 2
                + ((z - center[2]) / radii[2]) ** 2
            ) - 1
        ) * min(radii)
        field = smooth_min(field, distance, blend)

    # Torso, four short planted legs, and broad feet.
    add_ellipsoid((0, 0, 31), (22, 30, 24), 4)
    for leg_x in [-16, 16]:
        for leg_y in [-17, 18]:
            add_ellipsoid((leg_x, leg_y, 16), (8, 9, 19), 4)
            add_ellipsoid((leg_x, leg_y + 1, 4.4), (9.4, 11, 5.2), 2)

    # Rounded tail, with its end resting on the print bed.
    for tail_y, tail_z, radius in [
        (-26, 27, 11), (-32, 23, 9.6), (-38, 18.5, 8.1), (-44, 14, 6.8),
        (-50, 10, 5.5), (-56, 6.7, 4.7), (-62, 4.4, 3.9), (-67, 3.2, 3.4),
    ]:
        add_ellipsoid((0, tail_y, tail_z), (radius, radius * 1.2, radius), 3)

    # A thick-rooted neck blended from overlapping ellipsoids.
    for neck_y, neck_z, radius in [
        (23, 39, 13), (27, 47, 11.8), (28, 56, 10.4), (27.5, 65, 9.4),
        (26.5, 74, 8.8), (26.5, 83, 8.5), (27.5, 92, 8.8),
        (29.5, 101, 9.4), (32, 108, 10.2),
    ]:
        add_ellipsoid((0, neck_y, neck_z), (radius, radius, 9), 4)
    add_ellipsoid((0, 35.5, 116), (13, 13, 13), 3)
    add_ellipsoid((0, 45, 111), (12, 12, 8), 3)

    for leg_x in [-16, 16]:
        for leg_y in [-17, 18]:
            for dx in [-4.5, 0, 4.5]:
                add_ellipsoid((leg_x + dx, leg_y + 9.0, 3.0), (2.4, 3, 3.6), 0.8)
    field = np.maximum(field, -z)
    vertices, faces, _, _ = marching_cubes(
        field, level=0, spacing=(step, step, step), allow_degenerate=False
    )
    vertices += np.array([xs[0], ys[0], zs[0]])
    green_base = trimesh.Trimesh(vertices, faces, process=True)
    green_base.fix_normals()
    assert green_base.is_watertight

    # Eyes and smile are embedded colored volumes, not separate glued decorations.
    whites = [
        ellipsoid((sign * 8.4, 44.8, 121), (4.6, 4.5, 5.5)) for sign in [-1, 1]
    ]
    pupils = [
        ellipsoid((sign * 8.4, 48.35, 121.4), (2.3, 2.15, 3.15))
        for sign in [-1, 1]
    ]
    smile = []
    for smile_x in np.linspace(-8.5, 8.5, 31):
        smile_z = 106.9 + 0.04 * smile_x * smile_x
        smile_y = 45 + 12 * np.sqrt(max(
            0.05, 1 - (smile_x / 12) ** 2 - ((smile_z - 111) / 8) ** 2
        )) - 0.1
        smile.append(ellipsoid((smile_x, smile_y, smile_z), (0.78, 0.78, 0.78), 2))
    black = trimesh.boolean.union(pupils + smile, engine="manifold")
    white_full = trimesh.boolean.union(whites, engine="manifold")
    white = trimesh.boolean.difference([white_full, black], engine="manifold")
    green = trimesh.boolean.difference([green_base, white_full, black], engine="manifold")
    return dict(zip(["green", "white", "black"], map(clean, [green, white, black])))


def build_meshes():
    meshes = {}
    for color, mesh in build_body().items():
        # Preserve the binary-STL quantization in the original two-stage workflow.
        # Roundtrip in memory: no pre-existing mesh files or private paths required.
        mesh = trimesh.load(BytesIO(mesh.export(file_type="stl")), file_type="stl", force="mesh")
        mesh.apply_scale(50 / 129)
        meshes[color] = mesh

    # Vertical loop with a horizontal bore: 4.2 mm bore, 2.4 mm radial wall, 4.4 mm thickness.
    ring_outline = Point(0, 0).buffer(4.5, quad_segs=64).difference(
        Point(0, 0).buffer(2.1, quad_segs=64)
    )
    ring = trimesh.creation.extrude_polygon(ring_outline, 4.4, engine="earcut")
    ring.vertices = np.column_stack([
        ring.vertices[:, 2] - 2.2, ring.vertices[:, 0] - 1,
        ring.vertices[:, 1] + 24.3,
    ])
    ring.fix_normals()
    meshes["green"] = trimesh.boolean.union([meshes["green"], ring], engine="manifold")
    whole = clean(trimesh.boolean.union(list(meshes.values()), engine="manifold"), 1e-7)
    assert whole.is_watertight and len(whole.split()) == 1
    for mesh in meshes.values():
        assert mesh.is_watertight
    # Microscopic eye/smile contacts in the direct union merge into nonmanifold
    # edges when binary STL is loaded. Simplify only the single-color union;
    # Manifold bounds the surface change to less than 0.001 mm. Colored parts
    # retain the exact geometry of the original multipart model.
    solid = manifold3d.Manifold(manifold3d.Mesh(
        vert_properties=np.array(whole.vertices, dtype=np.float32),
        tri_verts=np.array(whole.faces, dtype=np.uint32),
    ))
    simplified = solid.simplify(0.001).to_mesh()
    whole = trimesh.Trimesh(
        vertices=simplified.vert_properties[:, :3],
        faces=simplified.tri_verts,
        process=False,
    )
    return meshes, whole


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Output folder")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    meshes, whole = build_meshes()
    filenames = {
        "green": "green-body.stl",
        "white": "white-eyes.stl",
        "black": "black-details.stl",
    }
    for color, mesh in meshes.items():
        path = args.output / filenames[color]
        mesh.export(path)
        stored = trimesh.load(path, force="mesh")
        if not stored.is_watertight or not stored.is_winding_consistent:
            raise RuntimeError(f"Exported mesh failed validation: {path.name}")
    whole_path = args.output / "single-colour.stl"
    whole.export(whole_path)
    whole = trimesh.load(whole_path, force="mesh")
    if not whole.is_watertight or not whole.is_winding_consistent or len(whole.split()) != 1:
        raise RuntimeError("Single-color STL failed validation after reload")
    report = {
        "size_mm": whole.extents.tolist(),
        "ring_hole_mm": 4.2,
        "ring_wall_mm": 2.4,
        "ring_thickness_mm": 4.4,
        "watertight": bool(whole.is_watertight),
        "connected_components": len(whole.split()),
        "validated_after_stl_reload": True,
        "single_color_simplification_tolerance_mm": 0.001,
        "physically_tested": False,
    }
    (args.output / "geometry-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
