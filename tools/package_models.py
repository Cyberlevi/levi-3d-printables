#!/usr/bin/env python3
"""Rebuild geometry-only 3MF packages and digital validation reports.

Run from any directory with the model geometry requirements installed.
SPDX-License-Identifier: MIT
"""
from pathlib import Path
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'


def check(mesh):
    assert np.isfinite(mesh.vertices).all(), 'Non-finite coordinates'
    assert mesh.is_watertight, 'Mesh has nonmanifold/open edges'
    assert mesh.is_winding_consistent and mesh.volume > 0, 'Invalid normals/volume'
    return {
        'watertight': bool(mesh.is_watertight),
        'winding_consistent': bool(mesh.is_winding_consistent),
        'vertices': len(mesh.vertices), 'triangles': len(mesh.faces),
        'connected_components': len(mesh.split(only_watertight=False)),
        'bounds_mm': mesh.bounds.tolist(),
        'dimensions_mm': mesh.extents.tolist(),
        'solid_volume_mm3': float(mesh.volume),
    }


def package(entry):
    folder = ROOT / entry['folder']
    model = ET.Element('model', {'unit': 'millimeter', 'xmlns': NS})
    ET.SubElement(model, 'metadata', {'name': 'Title'}).text = entry['name']
    ET.SubElement(model, 'metadata', {'name': 'Designer'}).text = 'Levi / Cyberlevi'
    ET.SubElement(model, 'metadata', {'name': 'LicenseTerms'}).text = 'CC BY-NC-SA 4.0'
    resources = ET.SubElement(model, 'resources')
    materials = ET.SubElement(resources, 'basematerials', {'id': '1'})
    for part in entry['parts']:
        ET.SubElement(materials, 'base', {'name': part['label'], 'displaycolor': part['colour']})
    report = {'model': entry['id'], 'version': '0.1.0', 'physical_print_verified': False,
              'units': 'millimetres', 'stl_reloaded_from_disk': {}, 'packaged_3mf_meshes': {}}
    for file in sorted((folder / 'files').glob('*.stl')):
        report['stl_reloaded_from_disk'][file.name] = check(trimesh.load(file, force='mesh'))
    for i, part in enumerate(entry['parts']):
        mesh = trimesh.load(folder / 'files' / part['file'], force='mesh')
        obj = ET.SubElement(resources, 'object', {'id': str(i + 2), 'type': 'model',
            'name': part['label'], 'pid': '1', 'pindex': str(i)})
        xm = ET.SubElement(obj, 'mesh')
        vs, ts = ET.SubElement(xm, 'vertices'), ET.SubElement(xm, 'triangles')
        for v in mesh.vertices:
            ET.SubElement(vs, 'vertex', dict(zip(('x','y','z'), [repr(float(x)) for x in v])))
        for face in mesh.faces:
            ET.SubElement(ts, 'triangle', dict(zip(('v1','v2','v3'), map(str, face))))
    assembly_id = str(len(entry['parts']) + 2)
    assembly = ET.SubElement(resources, 'object', {'id': assembly_id, 'type': 'model', 'name': entry['name']})
    components = ET.SubElement(assembly, 'components')
    for i in range(len(entry['parts'])):
        ET.SubElement(components, 'component', {'objectid': str(i + 2)})
    ET.SubElement(ET.SubElement(model, 'build'), 'item', {'objectid': assembly_id})
    output = folder / 'files' / (entry['id'] + '.3mf')
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('3D/3dmodel.model', ET.tostring(model, encoding='utf-8', xml_declaration=True))
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(output) as z:
        root = ET.fromstring(z.read('3D/3dmodel.model'))
    for obj in root.findall(f'{{{NS}}}resources/{{{NS}}}object'):
        mesh = obj.find(f'{{{NS}}}mesh')
        if mesh is None:
            continue
        vertices = [[float(v.attrib[k]) for k in ('x','y','z')] for v in mesh.find(f'{{{NS}}}vertices')]
        faces = [[int(f.attrib[k]) for k in ('v1','v2','v3')] for f in mesh.find(f'{{{NS}}}triangles')]
        report['packaged_3mf_meshes'][obj.attrib['name']] = check(trimesh.Trimesh(vertices, faces))
    (folder / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"Validated {entry['id']}")


def main():
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    for entry in catalog['models']:
        package(entry)
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts
                   and '__pycache__' not in p.parts and p.name != 'SHA256SUMS')
    (ROOT / 'SHA256SUMS').write_text(''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in files))


if __name__ == '__main__':
    main()
