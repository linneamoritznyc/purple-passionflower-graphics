# purple-passionflower-graphics

Code-generated graphics from the passion flower corona: banded purple and white filaments, cream anthers, ikat smears.

- `generate.py` renders every design (`pip install pillow numpy && python generate.py`)
- `files/` print files, 1200x2400
- `mockups/` phone case previews
- `sheet.png` all designs side by side

## Dot cases from a photo

`dots.py` turns the passion flower photo in `plates/passiflora.png` into honeycomb dots, maps its colours to the brand palette and writes 4 cases to `dots/` (1800x3680). Preview: `dots_sheet.png`.
The photo is a screenshot crop. Swap in a larger photo you own before selling.

## Seed generator
`gen.py` turns a seed number into a phone case (14 pattern types, palette and settings from the seed).
- `python gen.py 1 24` renders a preview sheet of seeds 1 to 24.
- `python gen.py 14 1 full` renders seed 14 at 1800x3680 into `seeds/`.

Kept seeds (in `seeds/`): 2, 9, 14, 18, 23, 24.

Kept SFW ikat cases with no logo or text (in `sfw-nologo/`): 16 dark green branches, 17 purple band, 19 green leaf with ring, 20 blue roots. Source: sfw-merch-print-files `files/phone-cases/cases4.py`.

## Ikat generator
`ikatgen.py` makes two-colour ikat cases in the SFW style from a seed (roots, tendril, corona, leaf, flower, ripples, blobs, weave, banded stripe, nematode). `python ikatgen.py 1 24`.
Kept ikat seeds (in `keep/ikat/`): 5, 17, 18, 29.
`keep/sfw-four-cases-strip.png`: the four SFW no-logo cases side by side.

## Style generator
`stylegen.py` renders a seed in one of 13 print and textile styles: linocut, riso, stitch, torn paper, cyanotype, batik, shibori, marbling, spray stencil, knit, topo, moire, woodgrain; from seed 27 also collage, jacquard, halftone, rug. `python stylegen.py 1 26` for previews, add `full` for 1800x3680.
Kept style seeds (in `keep/styles/`): 3 torn at zoom 0.7, 9 knit, 11 moire, 16 torn.

## Wild generator
`wild.py`: 22 unrelated concepts, one per seed (pixel sort, RGB split, aurora, Swiss grid, reaction-diffusion, flow field, stained glass, truchet, slit-scan, kaleidoscope, thermal, xerox, Albers squares, dot fade, circle packing, interference, L-system, mosaic, stacked arcs, string art, posterized bands, attractor).
`collection.png`: every kept design on one sheet.

## Leaf x torn band
`combine.py`: 12 ways to cross the fringed leaf (ikat 50) with the torn striped band (torn 105). `python combine.py 0 24`.
