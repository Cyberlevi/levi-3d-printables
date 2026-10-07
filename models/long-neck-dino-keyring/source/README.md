# Long-neck dinosaur keyring generator

AI-assisted design by Levi / Cyberlevi. Source and model are licensed under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

Tested with Python 3.14 and the geometry dependency versions in `requirements.txt`.
From this directory, install the dependencies in a virtual environment and run:

```sh
python -m pip install -r requirements.txt
python generate.py --output generated
```

Generation uses a dense implicit field and may take a few minutes. The output
folder contains `green-body.stl`, `white-eyes.stl`, `black-details.stl`,
`single-colour.stl`, and `geometry-report.json`. Dimensions are in millimetres;
the metal split ring is not included.

The colored parts reproduce the original geometry. The single-colour union uses
a **0.001 mm simplification tolerance** to remove microscopic nonmanifold contacts
at the eyes and smile. Generation validates each STL after loading it back from
disk. It does not render, slice, or start a print; mesh validation does not certify
a physically tested print.
