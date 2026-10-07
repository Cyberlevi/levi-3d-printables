# BACKSTAGE · Lightning Pick

A large pick-shaped door or wall sign with raised lettering and a lightning motif.

**v0.1.0 · Experimental · Physical print unverified**

![CAD render of the BACKSTAGE sign](images/preview.png)

*Digital render of the supplied geometry. No physical print is shown.*

## Download

- [Two-colour 3MF assembly](files/backstage-pick.3mf)
- [Single-colour STL](files/single-colour.stl)
- Separate parts: [black base](files/black-base.stl), [white lettering and lightning](files/white-detail.stl)
- [Editable source](source/) · [Digital validation report](validation.json)

For a file on GitHub, use **Download raw file**. The 3MF contains geometry/display colours only; assign your own printer and filament settings.

## Dimensions and print notes

| Detail | Value |
|---|---|
| Overall size, X × Y × Z | 240 × 250 × 4.2 mm |
| Flat base | 3 mm |
| Raised black detail | 0.6 mm |
| White top detail | Z = 3.6–4.2 mm |
| Mounting holes | Two 5 mm holes; 130 mm centre spacing |
| Intended orientation | Flat back on the bed, lettering upwards |
| Supports | Not expected in this orientation; inspect your sliced layers |

**Suggested starting point:** 0.4 mm nozzle, 0.2 mm layers, 3 walls, 15% gyroid infill, PETG. Use the filament manufacturer's temperature range and your printer's calibrated profile. An earlier local slicing run used 230 °C nozzle / 75 °C bed, but that print was cancelled before model layers; these settings have not been verified by a finished print.

A 260 × 260 mm bed leaves little space for a brim or purge tower. Check the complete toolpath, not only model dimensions. At the original scale and 0.2 mm layer height, white starts at Z = 3.6 mm, so a slicer-controlled manual colour change can be an alternative to a multicolour feeder. Verify the transition in layer preview.

Import both coloured STL parts as **one multipart object**; preserve their coordinates. Do not drop the white letters separately to the bed. Mounting hardware is not included; choose a fixing suitable for the surface.

## Verification and provenance

Every distributed STL was checked after export/reload. The single-colour model is one closed, connected body. White letters and lightning intentionally form multiple separate detail islands supported by the base. Full results are in `validation.json`; no physical print or mounting-strength test has been verified.

Original procedural pick/lightning layout with DejaVu Sans Bold Oblique lettering. Designed by Levi / Cyberlevi with AI assistance. Model files and design source: [CC BY-NC-SA 4.0](../../LICENSE).
