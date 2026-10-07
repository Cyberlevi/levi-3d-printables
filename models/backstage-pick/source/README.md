# BACKSTAGE pick generator

AI-assisted design by Levi / Cyberlevi. Source and model are licensed under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

Tested with Python 3.14 and the geometry dependency versions in `requirements.txt`.
From this directory, install the dependencies in a virtual environment and run:

```sh
python -m pip install -r requirements.txt
python generate.py --output generated
```

The output folder contains `black-base.stl`, `white-detail.stl`,
`single-colour.stl`, and `geometry-report.json`. Dimensions are in millimetres.
Generation validates each STL after loading it back from disk. It does not render,
slice, or start a print. Matplotlib's bundled DejaVu font keeps lettering consistent
across systems.
