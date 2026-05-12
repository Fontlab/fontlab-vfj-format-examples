# VFJ Format Examples — FontLab JSON Font Format Corpus

This repository contains a collection of `.vfj` (Variable Font JSON) files representing real-world
fonts from various vendors under different open source licenses. These files serve as examples
and test cases for FontLab's JSON-based font format.

## Corpus Overview

The corpus is organized by license type in the `corpus/` directory:

### CC0 (Creative Commons Zero — Public Domain)
- **Designer**: Sora Sagano — cosm, deco, medi, veni, vize, plum (variable & italic variants)
- **Designer**: Echo Heo — baar
- **Designer**: Dmitriy Sychiov — star
- **Designer**: Khalfani — pixa
- **Credits**: OCR fonts by Retorillo & Jonh Sauter — ocra

### Apache License 2.0
- **Designer**: Christian Robertson — boto (variable font)
- **Designer**: Astigmatic (AOETI) — cafe, fest, hint, zotoemoji
- **Designer**: Google Fonts (Monotype Design Team) — extensive Zotosans (writing systems across 60+ scripts)
- **Designer**: Google Fonts (Danh Hong) — Zotoserif Indic scripts (Lao, Khmer)

### SIL Open Font License (OFL)
- **Designer**: Eduardo Tunni — club (variable font)
- **Designer**: Philippe Cochy — ptit
- **Designer**: Carrois Corporate & Edenspiekermann AG — rafi (variable & italic)
- **Designer**: Thomas Phinney, Vassil Kateliev, Brandon Buerkle — scig (variable)
- **Designer**: Juan Pablo del Peral — stroke-chan
- **Designer**: Wei Huang — stroke-grot
- **Designer**: John Hudson, Ross Mills, Paul Hanslow — STIX (Tiro Typeworks), Castoro

### FontLab EULA (Educational/Tutorial)
- **Designer**: Dave Lawrence — cal-* series (learning/tutorial examples covering family setup,
  weight/width axes, kerning, hinting, path operations, style groups, and more)

## File Listing

For a complete list of all `.vfj` files, see `vfj-files.txt` in the repository root.

## Format Information

VFJ (Variable Font JSON) is FontLab's native JSON-based font format that serves as:
- A human-readable interchange format for fonts
- A structured representation of font data including glyphs, contours, components, axes,
  masters, instances, hints, and metadata
- A format intended for version control and collaborative development

## License Acknowledgments

All fonts in this corpus are used with the permission of their respective creators under the
terms of their specific licenses as listed above. Please refer to the individual font metadata
for detailed copyright and licensing information.

## Notes

- The corpus totals 130 VFJ files across 4 license categories
  - CC0: 13 files
  - Apache License 2.0: 81 files (including 72 Zotosans writing system variants)
  - SIL Open Font License: 11 files
  - FontLab EULA: 27 files (tutorial examples)
- Files range from simple single-master fonts to complex variable fonts with multiple axes
- Some files demonstrate advanced features: components, hints, variation axes, smart components
- See individual file metadata for specific feature demonstrations
