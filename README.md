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
