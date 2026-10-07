# Provenance and verification

Maintainer: Levi / Cyberlevi. First public collection: 7 October 2026.

These designs were developed from the maintainer's design requests with AI assistance for modeling code, design iteration, renders and documentation. Public sources are portable copies of the geometry generators. They do not include printer access code, private project paths or sliced jobs.

## BACKSTAGE pick sign

The pick outline, lightning shape, dimensions and mounting arrangement are defined in the model's Python source. Lettering is generated using **DejaVu Sans Bold Oblique**, not a band logo. The font is supplied by the user's Matplotlib installation and is not bundled here. [DejaVu license](https://dejavu-fonts.github.io/License.html). Python dependencies retain their upstream licenses.

The preview is rendered from the actual meshes. An earlier local slicing run was completed, but the print was cancelled before model layers were produced. No successful physical print is claimed.

## Long-neck dinosaur keyring

The figure is constructed procedurally from implicit shapes and mesh operations, with an integrated loop. It is an original generic dinosaur design, not a trace of a third-party character. The preview is a CAD render; its metal split ring is illustrative and is not included in the model files.

No successful physical print or durability test has been verified. The neck, loop and small face details need real print testing. See the model page for the currently distributed variants.

## What the checks establish

The published STL files are reloaded from disk and checked for finite coordinates, closed surfaces, consistent winding and positive volume. Bounds and connected components are recorded in each model's `validation.json`. 3MF packages are created from those parts, then their packaged meshes are checked separately.

These checks do not establish material strength, minimum printable features, support removal quality, colour fidelity or suitability for children. Those need physical tests. Mesh components may be disconnected within a colour part, because separate letters, pupils or details are intentional.
