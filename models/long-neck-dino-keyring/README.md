# Long-Neck Dino · Keyring

A 5 cm sculpted dinosaur with a built-in loop, green body, white eyes and black face details.

**v0.1.0 · Experimental · Physical print and durability unverified**

![CAD render of the green dinosaur with an illustrative metal ring](images/preview.png)

*Digital render of the supplied coloured geometry. The metal split ring is a separate accessory and is not included in the printable files. The Hungarian image caption says “5 cm tall · actual model” and “Add the metal keyring separately”; it refers to the CAD geometry, not a physical print.*

## Download

- [Three-colour 3MF assembly](files/long-neck-dino-keyring.3mf)
- [Single-colour STL](files/single-colour.stl)
- Separate parts: [green body](files/green-body.stl), [white eyes](files/white-eyes.stl), [black details](files/black-details.stl)
- [Editable source](source/) · [Digital validation report](validation.json)

For a file on GitHub, use **Download raw file**. Larger STL files may not have an interactive GitHub preview; the downloadable file remains available. The 3MF contains geometry/display colours only, with no printer profile or sliced G-code.

## Dimensions and print notes

| Detail | Value |
|---|---|
| Overall size, X × Y × Z | 19.69 × 49.64 × 50 mm, without metal ring |
| Loop opening | 4.2 mm nominal diameter |
| Loop wall | 2.4 mm nominal radial thickness |
| Loop thickness | 4.4 mm |
| Intended orientation | Upright, feet on the bed |
| Colours | Green body, white eyes, black pupils/mouth |

**Suggested starting point:** 0.4 mm nozzle, 0.2 mm layers, 3 walls, 15% gyroid, PETG. Use calibrated filament settings. Inspect supports under the neck, chin, belly and around the loop opening. Tree supports were used in an earlier local slicing study; their removal and the surface finish have not been physically tested.

Load the three coloured STL files together as one multipart object and preserve their shared coordinates. Do not lay out the eyes and face details separately on the bed. Assign colours manually if your slicer ignores 3MF display colours. The small mouth detail is about 0.6 mm thick, so inspect whether it survives your chosen line width and slicing settings.

Allow the print to cool, remove supports carefully and check the neck and loop before fitting a metal split ring. This is a decorative keyring, not a load-bearing handle. Durability and toy safety have not been established.

## Verification and provenance

All supplied STL files pass closed-surface and winding checks after reloading from disk. The single-colour union received a **0.001 mm tolerance simplification** to remove microscopic nonmanifold contacts in the face; its exported result is one connected, closed body. Coloured parts retain the original geometry. Full measurements are in `validation.json`.

Original procedural dinosaur geometry, designed by Levi / Cyberlevi with AI assistance. Model files and design source: [CC BY-NC-SA 4.0](../../LICENSE).
