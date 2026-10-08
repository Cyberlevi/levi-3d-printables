# Spotted cat generator and renderer

Original procedural design by Levi / Cyberlevi with AI assistance.
Source and model: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

The published V3 geometry was generated and verified using Python 3.14.7 and the
geometry dependency versions in `requirements.txt`. From this directory:

```sh
python -m pip install -r requirements.txt
python build_cat.py --step .32 --output generated
python render_views.py generated --output renders --backend software
```

Generation takes a few minutes and uses a dense implicit field. The output folder
contains `white-body.stl`, `black-details.stl`, `single-colour.stl`, a digital
validation report, and intermediate body/inner meshes. It checks exported STL files
after reloading them. Units are millimetres; final height is 140 mm. The source
preserves the published geometry formulas and changes only output handling and
public filenames. Floating-point ordering and recorded run times can vary between
environments; do not expect identical report or file hashes from every system.

Use a separate output directory: generation overwrites matching output filenames.
Normal release reproduction should not use the development flags `--cached` or
`--rough`; cached intermediate meshes are not included in the public package.

The software renderer needs no OpenGL. It may be slower and shade details differently
from the included previews. For accelerated rendering, optionally install `pyrender`
and the operating system's EGL or OSMesa libraries, then omit `--backend software`.
The default renderer tries EGL, OSMesa, and finally software. Keep the single-colour
mesh beside both coloured parts so the OpenGL path can use its exterior normals.
The included images are digital renders, not photographs of a finished print.

These scripts generate and render geometry only. They contain no network, printer
control, slicing, or upload operations. The first physical print is in progress;
completion, surface finish, support removal, and durability remain unverified.
