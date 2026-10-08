#!/usr/bin/env python3
"""Render co-registered white-body.stl and black-details.stl without a desktop or network.

Usage:
  python render_views.py /path/to/generated --output renders

Writes preview-3quarter.png, preview-front.png, preview-back.png,
preview-side.png, and preview-contact-sheet.png. Front is negative Y; Z is up.
EGL is preferred, with a fresh-process OSMesa attempt and a software fallback.
Design/render source by Levi / Cyberlevi with AI assistance.
SPDX-License-Identifier: CC-BY-NC-SA-4.0
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import trimesh


BACKGROUND = np.array([0.925, 0.898, 0.850])
WHITE = np.array([0.965, 0.955, 0.930])
BLACK = np.array([0.022, 0.020, 0.020])
# Camera positions are directions away from the model center.
VIEWS = (
    ("3quarter", "Front three-quarter", np.array([0.65, -1.0, 0.37])),
    ("front", "Front", np.array([0.0, -1.0, 0.07])),
    ("reference-angle", "Near front", np.array([0.3, -1.0, 0.15])),
    ("back", "Back", np.array([0.0, 1.0, 0.07])),
    ("side", "Right side", np.array([1.0, 0.0, 0.07])),
)


def load_meshes(directory: Path):
    meshes = []
    for filename, color in (("white-body.stl", WHITE), ("black-details.stl", BLACK)):
        path = directory / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required mesh is missing: {path}")
        mesh = trimesh.load(str(path), force="mesh", process=True)
        if mesh.is_empty or len(mesh.faces) == 0:
            raise ValueError(f"Mesh contains no triangles: {path}")
        if not np.isfinite(mesh.vertices).all():
            raise ValueError(f"Mesh has non-finite vertices: {path}")
        # Deliberately keep both meshes in their original shared coordinates.
        meshes.append((mesh, color))
    vertices = np.concatenate([mesh.vertices for mesh, _ in meshes])
    bounds = np.array([vertices.min(axis=0), vertices.max(axis=0)])
    span = float(np.max(bounds[1] - bounds[0]))
    if span <= 0:
        raise ValueError("Mesh bounds have zero size")
    return meshes, vertices, bounds, span


def look_at(eye, target):
    backward = np.asarray(eye, dtype=float) - np.asarray(target, dtype=float)
    backward /= np.linalg.norm(backward)
    right = np.cross([0.0, 0.0, 1.0], backward)
    right /= np.linalg.norm(right)
    up = np.cross(backward, right)
    pose = np.eye(4)
    pose[:3, :3] = np.column_stack((right, up, backward))
    pose[:3, 3] = eye
    return pose


def camera_for(vertices, bounds, span, direction):
    center = bounds.mean(axis=0)
    direction = direction / np.linalg.norm(direction)
    pose = look_at(center + direction * span * 3.5, center)
    projected = (vertices - center) @ pose[:3, :3]
    low, high = projected.min(axis=0), projected.max(axis=0)
    # Center each view by its projected silhouette, preserving some floor room.
    pose[:3, 3] += pose[:3, 0] * (low[0] + high[0]) * 0.5
    pose[:3, 3] += pose[:3, 1] * ((low[1] + high[1]) * 0.5 - span * 0.014)
    half_size = max(high[0] - low[0], high[1] - low[1]) * 0.615
    return pose, half_size


def render_opengl(directory, out, size, backend):
    # Called only in its own process: OpenGL's platform cannot safely be changed
    # after importing pyrender/PyOpenGL.
    os.environ["PYOPENGL_PLATFORM"] = backend
    os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
    # pyrender 0.1.x still uses this NumPy alias in its scene-bounds code.
    if not hasattr(np, "infty"):
        np.infty = np.inf
    import pyrender

    meshes, vertices, bounds, span = load_meshes(directory)
    # Colour partitions have inward-facing interface walls. Averaging those
    # into surface vertex normals creates false serrated highlights at seams.
    # Transfer the smooth unpartitioned sculpture's exterior normals instead.
    reference_path = directory / "single-colour.stl"
    if reference_path.is_file():
        from scipy.spatial import cKDTree
        reference = trimesh.load(str(reference_path), force="mesh", process=True)
        # Area weighting prevents nearly collapsed tiny triangles from dominating a
        # smooth normal; geometry and triangle coordinates stay unchanged.
        area_normals=np.zeros_like(reference.vertices)
        face_vectors=reference.face_normals*reference.area_faces[:,None]
        for corner in range(3):
            np.add.at(area_normals,reference.faces[:,corner],face_vectors)
        area_normals/=np.maximum(np.linalg.norm(area_normals,axis=1,keepdims=True),1e-12)
        reference.vertex_normals=area_normals
        tree = cKDTree(reference.vertices)
        for mesh, _ in meshes:
            distances, indices = tree.query(mesh.vertices, k=min(8, len(reference.vertices)))
            if distances.ndim == 1:
                distances, indices = distances[:, None], indices[:, None]
            weights = 1.0 / np.maximum(distances, span * 1e-7) ** 2
            normal = (reference.vertex_normals[indices] * weights[:, :, None]).sum(axis=1)
            normal /= np.maximum(np.linalg.norm(normal, axis=1, keepdims=True), 1e-12)
            mesh.vertex_normals = normal

    scene = pyrender.Scene(
        bg_color=np.append(BACKGROUND, 1.0),
        ambient_light=[0.38, 0.38, 0.38],
    )
    for mesh, color in meshes:
        material = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=np.append(color, 1.0),
            metallicFactor=0.0,
            roughnessFactor=0.70,
            doubleSided=False,
        )
        scene.add(pyrender.Mesh.from_trimesh(mesh, material=material, smooth=True))

    renderer = pyrender.OffscreenRenderer(size, size)
    center = bounds.mean(axis=0)
    try:
        for name, _, direction in VIEWS:
            pose, half_size = camera_for(vertices, bounds, span, direction)
            camera = pyrender.OrthographicCamera(
                xmag=half_size, ymag=half_size,
                znear=span * 0.01, zfar=span * 15.0,
            )
            camera_node = scene.add(camera, pose=pose)
            right = pose[:3, 0]
            forward = direction / np.linalg.norm(direction)
            key = center + span * (forward * 1.7 - right * 1.5 + np.array([0, 0, 2.6]))
            fill = center + span * (forward * 1.4 + right * 2.0 + np.array([0, 0, 1.0]))
            rim = center + span * (-forward * 1.5 + np.array([0, 0, 2.2]))
            light_nodes = []
            for position, intensity, color in (
                (key, 1.3, [1.0, 0.975, 0.94]),
                (fill, 0.65, [0.94, 0.97, 1.0]),
                (rim, 0.45, [1.0, 1.0, 1.0]),
            ):
                light_nodes.append(scene.add(
                    pyrender.DirectionalLight(color=color, intensity=intensity),
                    pose=look_at(position, center),
                ))
            pixels, depth = renderer.render(
                scene, flags=pyrender.RenderFlags.RGBA,
            )
            pixels = pixels.copy()
            # Composite a restrained soft contact shadow on the seamless studio
            # backdrop. Pyrender's infinite-ground shadow maps have hard borders;
            # this also avoids a horizon/platform edge in near-level views.
            ground = bounds.mean(axis=0)
            ground[2] = bounds[0, 2]
            ground_camera = (ground - pose[:3, 3]) @ pose[:3, :3]
            gx = size * (0.5 + ground_camera[0] / (half_size * 2))
            gy = size * (0.5 - ground_camera[1] / (half_size * 2))
            yy, xx = np.mgrid[0:size, 0:size]
            shadow = np.exp(-0.5 * (((xx - gx) / (size * 0.205)) ** 2 + ((yy - gy) / (size * 0.023)) ** 2))
            backdrop = np.uint8(np.clip(BACKGROUND * (1 - 0.16 * shadow[:, :, None]), 0, 1) * 255)
            pixels[:, :, :3][depth == 0] = backdrop[depth == 0]
            Image.fromarray(pixels[:, :, :3]).save(out / f"preview-{name}.png")
            for node in light_nodes:
                scene.remove_node(node)
            scene.remove_node(camera_node)
    finally:
        renderer.delete()


def render_software(directory, out, size):
    """Pure NumPy z-buffer fallback with interpolated normals and studio light.

    OpenGL is unnecessary. This is slower and uses an approximate soft ground
    shadow, but preserves visibility between the white body and black details.
    """
    meshes, vertices, bounds, span = load_meshes(directory)
    for name, _, direction in VIEWS:
        pose, half_size = camera_for(vertices, bounds, span, direction)
        rgb = np.broadcast_to(BACKGROUND, (size, size, 3)).copy()
        depth = np.full((size, size), np.inf)
        # Ground contact shadow: restrained and soft, behind the actual geometry.
        ground = bounds.mean(axis=0)
        ground[2] = bounds[0, 2]
        ground_camera = (ground - pose[:3, 3]) @ pose[:3, :3]
        gx = size * (0.5 + ground_camera[0] / (half_size * 2))
        gy = size * (0.5 - ground_camera[1] / (half_size * 2))
        yy, xx = np.mgrid[0:size, 0:size]
        shadow = np.exp(-0.5 * (((xx - gx) / (size * 0.20)) ** 2 + ((yy - gy) / (size * 0.028)) ** 2))
        rgb *= (1 - 0.15 * shadow[:, :, None])
        light = np.array([-0.55, 0.65, 0.8])
        light /= np.linalg.norm(light)
        half_vector = light + np.array([0.0, 0.0, 1.0])
        half_vector /= np.linalg.norm(half_vector)
        for mesh, color in meshes:
            view = (mesh.vertices - pose[:3, 3]) @ pose[:3, :3]
            screen = np.column_stack((
                size * (0.5 + view[:, 0] / (half_size * 2)),
                size * (0.5 - view[:, 1] / (half_size * 2)),
                -view[:, 2],
            ))
            normals = mesh.vertex_normals @ pose[:3, :3]
            for face in mesh.faces:
                p = screen[face]
                x0 = max(0, int(np.floor(p[:, 0].min())))
                x1 = min(size - 1, int(np.ceil(p[:, 0].max())))
                y0 = max(0, int(np.floor(p[:, 1].min())))
                y1 = min(size - 1, int(np.ceil(p[:, 1].max())))
                if x0 > x1 or y0 > y1:
                    continue
                denominator = (p[1, 1] - p[2, 1]) * (p[0, 0] - p[2, 0]) + (p[2, 0] - p[1, 0]) * (p[0, 1] - p[2, 1])
                if abs(denominator) < 1e-12:
                    continue
                py, px = np.mgrid[y0:y1 + 1, x0:x1 + 1]
                px, py = px + 0.5, py + 0.5
                a = ((p[1, 1] - p[2, 1]) * (px - p[2, 0]) + (p[2, 0] - p[1, 0]) * (py - p[2, 1])) / denominator
                b = ((p[2, 1] - p[0, 1]) * (px - p[2, 0]) + (p[0, 0] - p[2, 0]) * (py - p[2, 1])) / denominator
                c = 1 - a - b
                z = a * p[0, 2] + b * p[1, 2] + c * p[2, 2]
                target_depth = depth[y0:y1 + 1, x0:x1 + 1]
                visible = (a >= -1e-8) & (b >= -1e-8) & (c >= -1e-8) & (z < target_depth)
                if not visible.any():
                    continue
                weights = np.stack((a[visible], b[visible], c[visible]), axis=1)
                normal = weights @ normals[face]
                normal /= np.maximum(np.linalg.norm(normal, axis=1, keepdims=True), 1e-12)
                diffuse = np.maximum(normal @ light, 0)
                specular = np.maximum(normal @ half_vector, 0) ** 42
                # Input materials are displayed colors; lift black slightly so
                # curved surfaces remain legible at ordinary preview sizes.
                shaded = color * (0.63 + 0.37 * diffuse[:, None]) + 0.13 * specular[:, None]
                rgb[y0:y1 + 1, x0:x1 + 1][visible] = np.clip(shaded, 0, 1)
                target_depth[visible] = z[visible]
        Image.fromarray(np.uint8(np.clip(rgb, 0, 1) * 255)).save(out / f"preview-{name}.png")


def contact_sheet(out, size):
    gap = max(16, size // 40)
    label_height = max(40, size // 16)
    sheet = Image.new("RGB", (size * 2 + gap * 3, (size + label_height) * 2 + gap * 3), tuple((BACKGROUND * 255).astype(int)))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", max(18, size // 36))
    except OSError:
        font = ImageFont.load_default()
    for index, (name, label, _) in enumerate(v for v in VIEWS if v[0] != "reference-angle"):
        x = gap + (index % 2) * (size + gap)
        y = gap + (index // 2) * (size + label_height + gap)
        with Image.open(out / f"preview-{name}.png") as picture:
            sheet.paste(picture.convert("RGB"), (x, y))
        draw.text((x + size / 2, y + size + label_height / 2), label, font=font, anchor="mm", fill=(65, 61, 55))
    sheet.save(out / "preview-contact-sheet.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("directory", nargs="?", type=Path, default=Path.cwd(), help="Directory containing white-body.stl and black-details.stl (default: current directory)")
    parser.add_argument("--output", type=Path, help="Output directory (default: mesh directory)")
    parser.add_argument("--size", type=int, default=1000, help="Square image size in pixels (default: 1000)")
    parser.add_argument("--backend", choices=("auto", "egl", "osmesa", "software"), default="auto")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.size < 128 or args.size > 4096:
        parser.error("--size must be between 128 and 4096")
    directory = args.directory.expanduser().resolve()
    out = (args.output or directory).expanduser().resolve()
    load_meshes(directory)  # Fail clearly before spawning any renderer.
    out.mkdir(parents=True, exist_ok=True)
    if args.worker:
        render_opengl(directory, out, args.size, args.backend)
        return
    rendered = False
    backends = ("egl", "osmesa") if args.backend == "auto" else (() if args.backend == "software" else (args.backend,))
    for backend in backends:
        command = [sys.executable, str(Path(__file__).resolve()), str(directory), "--output", str(out), "--size", str(args.size), "--backend", backend, "--worker"]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            print(f"{backend} render timed out; trying fallback.", file=sys.stderr)
            continue
        if result.returncode == 0:
            print(f"Rendered with {backend}.")
            rendered = True
            break
        error_lines = (result.stderr or result.stdout).strip().splitlines()
        detail = error_lines[-1] if error_lines else f"exit code {result.returncode}"
        print(f"{backend} unavailable: {detail}", file=sys.stderr)
    if not rendered:
        print("Using the NumPy software renderer (approximate ground shadow).")
        render_software(directory, out, args.size)
    contact_sheet(out, args.size)
    for name, _, _ in VIEWS:
        print(out / f"preview-{name}.png")
    print(out / "preview-contact-sheet.png")


if __name__ == "__main__":
    main()
