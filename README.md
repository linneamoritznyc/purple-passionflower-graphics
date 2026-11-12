# purple-passionflower-graphics

Code-generated graphics from the passion flower corona: banded purple and white filaments, cream anthers, ikat smears.

- `generate.py` renders every design (`pip install pillow numpy && python generate.py`)
- `files/` print files, 1200x2400
- `mockups/` phone case previews
- `sheet.png` all designs side by side

## Halftone (pixel micrograph style)

`halftone.py` turns plates into a honeycomb dot texture and clips it into one huge shape on a flat colour. Output in `halftone/` (1800x3680), preview in `halftone_sheet.png`.
Put real passion flower photos in `plates/` (white = flower) and they replace the generated plates.
