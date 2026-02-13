"""Generate styled KML output from classified features.

All output is branded as ATOC.  Any references to Overpass Turbo, Overpass API,
osmtogeojson, or similar tooling in source names/descriptions are stripped.

Uses lxml directly for full control over the KML structure.
"""

from __future__ import annotations

import re
from collections import defaultdict

from lxml import etree

from .classifier import Classification, classify
from .parser import Feature, KML_NS
from .styles import FeatureStyle, get_style, style_id

# ---------------------------------------------------------------------------
# Branding / sanitisation
# ---------------------------------------------------------------------------

_OVERPASS_PATTERNS = re.compile(
    r"(?i)"
    r"exported?\s+from\s+overpass[\s\-_]*(?:turbo|api)?|"
    r"generated?\s+by\s+overpass[\s\-_]*(?:turbo|api)?|"
    r"overpass[\s\-_]*turbo|"
    r"overpass[\s\-_]*api|"
    r"overpass|"
    r"osmtogeojson|"
    r"openstreetmap\s*export|"
    r"osm\s*export|"
    r"tokml"
)

ATOC_DESCRIPTION = "Processed by ATOC"


def _sanitise_text(text: str) -> str:
    """Remove Overpass/OSM tool references from a string."""
    return _OVERPASS_PATTERNS.sub("", text).strip()


def _build_description(feature: Feature) -> str:
    """Create a clean HTML description balloon from OSM tags."""
    skip_prefixes = ("@", "id", "source")
    rows: list[str] = []
    for k, v in sorted(feature.tags.items()):
        if any(k.startswith(p) for p in skip_prefixes):
            continue
        rows.append(f"<tr><td><b>{k}</b></td><td>{v}</td></tr>")
    if not rows:
        return ""
    return "<table>" + "".join(rows) + "</table>"


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


def _coords_text(geom_el: etree._Element) -> str:
    """Get raw coordinate text from a geometry element."""
    for child in geom_el.iter():
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "coordinates" and child.text:
            return child.text.strip()
    return ""


# ---------------------------------------------------------------------------
# lxml KML builder helpers
# ---------------------------------------------------------------------------


def _kml_el(tag: str, text: str | None = None, **attribs: str) -> etree._Element:
    """Create a KML-namespaced element."""
    el = etree.SubElement(etree.Element("dummy"), f"{{{KML_NS}}}{tag}", **attribs)
    # detach from dummy parent
    el = etree.Element(f"{{{KML_NS}}}{tag}", **attribs)
    if text is not None:
        el.text = text
    return el


def _sub(parent: etree._Element, tag: str, text: str | None = None, **attribs: str) -> etree._Element:
    """Append a KML-namespaced child element."""
    el = etree.SubElement(parent, f"{{{KML_NS}}}{tag}", **attribs)
    if text is not None:
        el.text = text
    return el


def _build_style_element(sid: str, fstyle: FeatureStyle, geom_type: str) -> etree._Element:
    """Build a <Style id="..."> element."""
    style = etree.Element(f"{{{KML_NS}}}Style", id=sid)

    # IconStyle (for points)
    if geom_type == "Point" and fstyle.icon_href:
        icon_style = _sub(style, "IconStyle")
        _sub(icon_style, "scale", str(fstyle.icon_scale))
        _sub(icon_style, "color", fstyle.line_color)
        icon = _sub(icon_style, "Icon")
        _sub(icon, "href", fstyle.icon_href)

    # LabelStyle
    label_style = _sub(style, "LabelStyle")
    _sub(label_style, "color", fstyle.label_color)
    _sub(label_style, "scale", str(fstyle.label_scale))

    # LineStyle
    line_style = _sub(style, "LineStyle")
    _sub(line_style, "color", fstyle.line_color)
    _sub(line_style, "width", str(fstyle.line_width))

    # PolyStyle (for polygons)
    if geom_type == "Polygon" and fstyle.poly_color:
        poly_style = _sub(style, "PolyStyle")
        _sub(poly_style, "color", fstyle.poly_color)
        _sub(poly_style, "fill", "1" if fstyle.poly_fill else "0")
        _sub(poly_style, "outline", "1" if fstyle.poly_outline else "0")

    return style


def _copy_geometry(geom_el: etree._Element) -> etree._Element:
    """Deep-copy a geometry element, preserving its structure."""
    from copy import deepcopy
    return deepcopy(geom_el)


def _build_placemark(
    feature: Feature,
    cls: Classification,
    fstyle: FeatureStyle,
    sid: str,
) -> etree._Element:
    """Build a styled <Placemark> element."""
    pm = etree.Element(f"{{{KML_NS}}}Placemark")

    name = _sanitise_text(feature.name) or cls.subcategory.replace("_", " ").title()
    _sub(pm, "name", name)

    desc = _build_description(feature)
    if desc:
        _sub(pm, "description", desc)

    _sub(pm, "styleUrl", f"#{sid}")

    # Copy original geometry
    geom_copy = _copy_geometry(feature.geometry_element)
    pm.append(geom_copy)

    return pm


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_styled_kml(
    features: list[Feature],
    *,
    use_folders: bool = True,
    document_name: str = "ATOC Export",
) -> str:
    """Transform parsed features into a fully styled KML document.

    Args:
        features: Parsed Feature objects from the parser module.
        use_folders: Group features into folders by category.
        document_name: Name for the KML Document element.

    Returns:
        KML content as a UTF-8 string.
    """
    nsmap = {None: KML_NS}
    kml_root = etree.Element(f"{{{KML_NS}}}kml", nsmap=nsmap)
    doc = _sub(kml_root, "Document")
    _sub(doc, "name", _sanitise_text(document_name) or "ATOC Export")
    _sub(doc, "description", ATOC_DESCRIPTION)

    # Classify all features and collect unique styles needed
    classified: list[tuple[Feature, Classification]] = []
    styles_needed: dict[str, tuple[FeatureStyle, str]] = {}  # sid -> (style, geom_type)

    for feat in features:
        cls = classify(feat)
        classified.append((feat, cls))
        sid = style_id(cls.category, cls.subcategory)
        if sid not in styles_needed:
            fstyle = get_style(cls.category, cls.subcategory)
            styles_needed[sid] = (fstyle, feat.geometry_type)

    # Emit shared styles at document level
    for sid, (fstyle, geom_type) in sorted(styles_needed.items()):
        style_el = _build_style_element(sid, fstyle, geom_type)
        doc.append(style_el)

    # Also emit styles for geometry types we haven't seen yet but might need
    # (e.g., a style defined for Points but first seen as LineString)
    # We handle this by emitting one style per sid; the first geometry type wins.

    # Group features by category
    grouped: dict[str, list[tuple[Feature, Classification]]] = defaultdict(list)
    for feat, cls in classified:
        grouped[cls.category].append((feat, cls))

    folder_labels = {
        "road": "Roads", "railway": "Railways", "water": "Water",
        "building": "Buildings", "green": "Green Spaces", "sport": "Sports",
        "landuse": "Land Use", "amenity": "Amenities", "tourism": "Tourism",
        "shop": "Shops", "utility": "Utilities", "barrier": "Barriers",
        "aeroway": "Aeroways", "natural": "Natural Features",
        "boundary": "Boundaries", "transport": "Public Transport",
        "other": "Other",
    }

    for category, items in sorted(grouped.items()):
        if use_folders:
            folder = _sub(doc, "Folder")
            _sub(folder, "name", folder_labels.get(category, category.title()))
            parent = folder
        else:
            parent = doc

        for feat, cls in items:
            sid = style_id(cls.category, cls.subcategory)
            fstyle = get_style(cls.category, cls.subcategory)
            pm = _build_placemark(feat, cls, fstyle, sid)
            parent.append(pm)

    tree = etree.ElementTree(kml_root)
    return etree.tostring(
        tree,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    ).decode("utf-8")


def generate_styled_kml_file(
    features: list[Feature],
    output_path: str,
    **kwargs,
) -> None:
    """Generate styled KML and write to a file."""
    content = generate_styled_kml(features, **kwargs)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
