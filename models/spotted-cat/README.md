# Spotted Cat · Pöttyös cica

A 140 mm sitting cat with soft cheeks, cupped ears, plump white paws, a wrapped
round tail, sleepy eyes, and a small heart on its flank.

**v0.3.0 · V3 geometry · First print in progress · Completion unverified**

![CAD render of the supplied spotted cat geometry](images/preview.png)

*Digital render of the distributed model. No completed physical print is shown.*

## Download

- [Two-colour 3MF assembly](files/spotted-cat.3mf)
- [Single-colour STL](files/single-colour.stl)
- Separate parts: [white body](files/white-body.stl), [black details](files/black-details.stl)
- [Other views](images/views.png) · [Editable source](source/)
- [Digital validation](validation.json) · [Portable print notes](print-settings.json)

On GitHub, use **Download raw file**. The 3MF contains standard geometry and display
colours only: no sliced G-code, printer configuration, or material preset. Import
both coloured STL files together as **one multipart object**, preserving their
shared coordinates. Do not move or drop the black details separately onto the bed.
Assign white and black manually if your slicer ignores the 3MF display colours.

## Dimensions and printing

| Detail | Value |
|---|---|
| Overall size, X × Y × Z | 84.013 × 88.305 × 140 mm |
| Orientation | Upright, flat base at Z = 0; front faces negative Y |
| Material and colours | PLA, white body and black details |
| ECO starting point | 0.16 mm layers, 2 walls, 8% gyroid |
| Solid layers | 5 top, 4 bottom |
| First-run slicer estimate | 104.08 g total, 6 h 55 min 58 s |

The ECO values describe the first ongoing print on an Anycubic Kobra X, not a
finished, verified profile for every printer. Estimated time and filament use are
slicer predictions, not measured results. Printer-internal purging has not been
independently quantified. Use your own calibrated PLA temperature and flow settings.

The first run uses automatic tree supports at a 30° threshold, with supports allowed
to start on the model as well as on the build plate. Support contact gaps are 0.16 mm above/below and 0.35 mm in
XY; supports use white filament. It also uses a 3 mm brim with a 0.1 mm gap. Inspect
support placement under the head, paws, and tail, and check the complete toolpath,
including purge structures. Support removal and the resulting finish are unverified.
More settings and the directional purge-volume example are in `print-settings.json`.

## Verification and provenance

All three supplied STL files pass watertightness, winding, and degenerate-triangle
checks after reloading from disk. The complete sculpture and the white body each
form one connected body. The 11 black regions are intentional embedded colour
volumes; they are not loose accessories. The smallest black region is about 30 mm³.
The white and black volumes have numerically zero overlap; their union agrees with
the full model to within 0.003 mm³. See `validation.json` for measurements and hashes.

The rounded tail cap, projecting forearms, padded paws, and shallow tail/body groove
are actual geometry. The head, facial expression, ears, and heart motif carry over
from the preceding design revision. Digital validation does not establish physical
print quality or durability. As of 2026-10-08 the first print is in progress and its
completion has not been verified.

Original procedural geometry designed by Levi / Cyberlevi with AI assistance.
Model, design source, and renders: [CC BY-NC-SA 4.0](../../LICENSE).

## Röviden magyarul

14 cm magas pöttyös cica, pufi fehér mancsokkal, körbefutó farokkal és fekete
szívfolttal. A két színrészt egy tárgy alkatrészeiként importáld, közös helyzetük
megtartásával. Az első nyomtatás folyamatban van; a befejezés és a kész felület még
nem igazolt. A képek a tényleges modell renderjei, nem kész nyomatról készült fotók.
