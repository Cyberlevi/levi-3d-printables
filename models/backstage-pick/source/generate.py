#!/usr/bin/env python3
"""Generate the 240 × 250 mm BACKSTAGE pick plaque as three STL files.

AI-assisted design by Levi / Cyberlevi.
SPDX-License-Identifier: CC-BY-NC-SA-4.0

Install requirements.txt, then run:
    python generate.py --output ./generated
Coordinates and dimensions are in millimetres. Rendering and slicing are separate.
"""

import argparse
import json
from pathlib import Path

import matplotlib
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as DrawingPath
from matplotlib.textpath import TextPath
from shapely import affinity
from shapely.geometry import Point, Polygon
import trimesh


def extrude(shape, height, z=0):
    parts = list(shape.geoms) if hasattr(shape, "geoms") else [shape]
    meshes = []
    for part in parts:
        mesh = trimesh.creation.extrude_polygon(
            part.simplify(0.01), height, engine="earcut"
        )
        mesh.apply_translation([0, 0, z])
        meshes.append(mesh)
    return trimesh.util.concatenate(meshes)


def build_meshes():
    vertices = [
        (0, -125), (-25, -125), (-120, 7), (-120, 70),
        (-120, 110), (-75, 125), (0, 125), (75, 125),
        (120, 110), (120, 70), (120, 7), (25, -125), (0, -125),
    ]
    outline = DrawingPath(
        vertices, [DrawingPath.MOVETO] + [DrawingPath.CURVE4] * 12
    )
    base = Polygon(outline.to_polygons()[0])
    x0, y0, x1, y1 = base.bounds
    base = affinity.scale(
        base, xfact=240 / (x1 - x0), yfact=250 / (y1 - y0), origin=(0, 0)
    )
    for x in [-65, 65]:
        base = base.difference(Point(x, 92).buffer(2.5, quad_segs=32))

    # Use Matplotlib's bundled font to avoid platform-dependent font substitution.
    font_file = (
        Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans-BoldOblique.ttf"
    )
    font = FontProperties(fname=str(font_file))
    letters = Polygon()
    for polygon in TextPath((0, 0), "BACKSTAGE", size=30, prop=font).to_polygons():
        letters = letters.symmetric_difference(Polygon(polygon))
    x0, y0, x1, y1 = letters.bounds
    scale = 205 / (x1 - x0)
    letters = affinity.scale(letters, xfact=scale, yfact=scale, origin=(0, 0))
    x0, y0, x1, y1 = letters.bounds
    letters = affinity.translate(letters, xoff=-(x0 + x1) / 2, yoff=37 - y0)
    bolt = Polygon([
        (5, 17), (-25, -32), (-6, -32), (-14, -70),
        (28, -13), (7, -13), (18, 17),
    ])
    white_shape = letters.union(bolt)
    assert base.contains(white_shape)

    # White faces occupy only the last 0.6 mm; the black supports are below them.
    rim = base.buffer(-7).difference(base.buffer(-9))
    black = trimesh.boolean.union([
        extrude(base, 3), extrude(rim, 0.6, 3), extrude(white_shape, 0.6, 3)
    ], engine="manifold")
    white = extrude(white_shape, 0.6, 3.6)
    whole = trimesh.boolean.union([black, white], engine="manifold")
    assert whole.is_watertight and len(whole.split()) == 1
    return black, white, whole


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Output folder")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    black, white, whole = build_meshes()
    for name, mesh in [
        ("black-base", black), ("white-detail", white),
        ("single-colour", whole),
    ]:
        path = args.output / f"{name}.stl"
        mesh.export(path)
        stored = trimesh.load(path, force="mesh")
        if not stored.is_watertight or not stored.is_winding_consistent:
            raise RuntimeError(f"Exported mesh failed validation: {path.name}")
    whole = trimesh.load(args.output / "single-colour.stl", force="mesh")
    white = trimesh.load(args.output / "white-detail.stl", force="mesh")
    report = {
        "dimensions_mm": whole.extents.tolist(),
        "white_solid_volume_cm3": white.volume / 1000,
        "mounting_holes_mm": 5,
        "mounting_spacing_mm": 130,
        "watertight": bool(whole.is_watertight),
        "connected_components": len(whole.split()),
        "validated_after_stl_reload": True,
    }
    (args.output / "geometry-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
