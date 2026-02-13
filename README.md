# ATOC — KML Processing Tool

Transform raw KML exports into visually styled, color-coded KML files with clear markers, categorized folders, and geospatial boundaries.

## Features

- **Auto-classification** — Detects roads, buildings, water, parks, amenities, railways, and 15+ other feature categories from OSM tags
- **Color-coded styling** — Each category and subcategory gets distinct line colors, polygon fills, and point icons
- **Road hierarchy** — Motorways, primary roads, residential streets, footways each styled with appropriate widths and colors
- **Organized output** — Features grouped into labeled folders by category
- **ATOC branding** — All output branded as ATOC; source tool references are stripped
- **Rich descriptions** — OSM tags rendered as clean HTML tables in info balloons

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Basic usage — produces input_styled.kml
opt-refactor input.kml

# Specify output path
opt-refactor input.kml -o output.kml

# Custom document name
opt-refactor input.kml --name "My Project Map"

# Flat output (no category folders)
opt-refactor input.kml --no-folders
```

## Supported Feature Categories

| Category | Examples | Style |
|----------|----------|-------|
| Roads | motorway, primary, residential, footway, cycleway | Color-coded by hierarchy, varying widths |
| Railways | rail, subway, tram, stations | Dark tones with rail icons |
| Water | rivers, streams, lakes | Blue lines and semi-transparent fills |
| Buildings | general, commercial, worship, hospital | Brown/themed outlines with fills |
| Green Spaces | parks, forests, nature reserves | Green tones |
| Amenities | restaurants, schools, hospitals, parking | Category-specific icons |
| Tourism | hotels, museums, viewpoints | Themed icons |
| Boundaries | administrative, protected areas | Purple dashed lines |
| + more | shops, utilities, barriers, aeroways, natural features | ... |

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Architecture

```
opt_refactor/
  parser.py        # KML parsing, tag extraction from ExtendedData
  classifier.py    # OSM tag -> category/subcategory rule engine
  styles.py        # Visual style definitions per classification
  generator.py     # Styled KML output with lxml
  cli.py           # Command-line interface
```
