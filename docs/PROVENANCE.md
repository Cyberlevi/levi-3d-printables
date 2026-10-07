# Provenance and verification

Maintainer: Levi / Cyberlevi. First public collection: 7 October 2026.

The collection contains original designs and separately identified unofficial fan art. Modeling and print preparation were carried out for the maintainer's requests with AI assistance for modeling code, design iteration, renders and documentation. Editable geometry generators are included only for the original models in `models/`. The fan-art releases in `fan-art/` contain finished meshes, not editable design sources. No printer access code, private project paths or sliced jobs are included.

Version 0.2.0 is experimental. None of the four models has a verified successful physical print.

## Eddie BACKSTAGE fan-art sign

The sign's geometry was traced from an AI-generated Eddie BACKSTAGE concept selected by the maintainer. Modeling and print preparation are credited to Levi / Cyberlevi with AI assistance; Eddie / Iron Maiden character imagery is not claimed as an original creation of this project. Selecting or generating the concept does not establish rights in the underlying character or artwork.

The distributed sign measures 213.759 × 249.970 × 3.6 mm. Its black base is 3 mm thick and its white details add 0.6 mm. The two mounting holes have a nominal diameter of 5 mm and center spacing of 182.432 mm. The preview is rendered from the distributed geometry. No successful physical print is claimed.

The mesh files, preview and model documentation have the separate [personal printing terms](../fan-art/TERMS.md), covering only rights in our contributions. No third-party character or artwork rights are granted.

## Metallica fan-art wall sign

The logo geometry was traced from an SVG on Metallica's official website. The logo and underlying artwork are third-party material, not an original design by Levi / Cyberlevi. Our contribution is the 3D adaptation and print preparation, including the layered sign and mounting arrangement. The source being publicly accessible does not itself grant reuse permission.

The distributed sign measures 200 × 75.446 × 4 mm. Its black base is 3 mm thick and its white details add 1 mm. The two mounting holes have a nominal diameter of 4 mm and center spacing of 60 mm. The preview is rendered from the distributed geometry. No successful physical print is claimed.

The mesh files, preview and model documentation have the separate [personal printing terms](../fan-art/TERMS.md), covering only rights in our contributions. This project has no official affiliation with or endorsement from Metallica or the relevant rights holders.

## Original BACKSTAGE lightning pick sign

The pick outline, lightning shape, dimensions and mounting arrangement are defined in the model's Python source. Lettering is generated using **DejaVu Sans Bold Oblique**, not a band logo. The font is supplied by the user's Matplotlib installation and is not bundled here. [DejaVu license](https://dejavu-fonts.github.io/License.html). Python dependencies retain their upstream licenses.

The preview is rendered from the actual meshes. An earlier local slicing run was completed, but the print was cancelled before model layers were produced. No successful physical print is claimed.

## Original long-neck dinosaur keyring

The figure is constructed procedurally from implicit shapes and mesh operations, with an integrated loop. It is an original generic dinosaur design, not a trace of a third-party character. The preview is a CAD render; its metal split ring is illustrative and is not included in the model files.

No successful physical print or durability test has been verified. The neck, loop and small face details need real print testing. See the model page for the currently distributed variants.

## What the checks establish

The published STL files are reloaded from disk and checked for finite coordinates, closed surfaces, consistent winding and positive volume. Bounds and connected components are recorded in each model's `validation.json`. 3MF packages are created from those parts, then their packaged meshes are checked separately. Their contents are geometry and display colours, not printer presets or ready-to-run G-code.

These checks do not establish material strength, minimum printable features, support removal quality, colour fidelity or suitability for children. Those need physical tests. Mesh components may be disconnected within a colour part, because separate letters, pupils or details are intentional.
