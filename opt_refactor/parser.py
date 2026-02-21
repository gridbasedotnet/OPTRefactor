"""Parse Overpass Turbo KML exports and extract features with their OSM tags."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from typing import Literal
from lxml import etree

# KML namespace
KML_NS = "http://www.opengis.net/kml/2.2"
NS = {"kml": KML_NS}

GeometryType = Literal["Point", "LineString", "Polygon", "MultiGeometry"]

GEOMETRY_TAGS = {"Point", "LineString", "Polygon", "MultiGeometry"}


@dataclass
class Feature:
    """A single parsed KML placemark with its OSM metadata."""

    name: str
    geometry_type: GeometryType
    geometry_element: etree._Element
    tags: dict[str, str] = field(default_factory=dict)
    osm_id: str = ""

    def tag(self, key: str, default: str = "") -> str:
        return self.tags.get(key, default)


def _extract_tags(placemark: etree._Element) -> dict[str, str]:
    """Pull OSM tags from <ExtendedData><Data name="..."><value>...</value>."""
    tags: dict[str, str] = {}
    for data_el in placemark.findall(".//kml:ExtendedData/kml:Data", NS):
        key = data_el.get("name", "")
        value_el = data_el.find("kml:value", NS)
        if key and value_el is not None and value_el.text:
            tags[key] = value_el.text
    return tags


def _detect_geometry(placemark: etree._Element) -> tuple[GeometryType, etree._Element] | None:
    """Find the first geometry element inside a placemark."""
    for tag in GEOMETRY_TAGS:
        el = placemark.find(f"kml:{tag}", NS)
        if el is not None:
            return tag, el  # type: ignore[return-value]
    return None


def parse_kml(source: str | bytes) -> list[Feature]:
    """Parse a KML string/bytes and return a list of Features.

    Args:
        source: Raw KML content as a string or bytes.

    Returns:
        List of Feature objects extracted from the document.
    """
    if isinstance(source, str):
        source = source.encode("utf-8")

    tree = etree.fromstring(source)
    features: list[Feature] = []

    for pm in tree.iter(f"{{{KML_NS}}}Placemark"):
        geom = _detect_geometry(pm)
        if geom is None:
            continue

        geom_type, geom_el = geom
        tags = _extract_tags(pm)

        name_el = pm.find("kml:name", NS)
        name = name_el.text.strip() if name_el is not None and name_el.text else ""

        osm_id = tags.get("@id", tags.get("id", ""))

        features.append(Feature(
            name=name,
            geometry_type=geom_type,
            geometry_element=geom_el,
            tags=tags,
            osm_id=osm_id,
        ))

    return features


def _read_kmz(path: str) -> bytes:
    """Extract the KML content from a KMZ (ZIP) archive."""
    with zipfile.ZipFile(path, "r") as zf:
        # KMZ spec: the first .kml file found (usually doc.kml)
        for name in zf.namelist():
            if name.lower().endswith(".kml"):
                return zf.read(name)
        raise ValueError(f"No .kml file found inside {path}")


def parse_kml_file(path: str) -> list[Feature]:
    """Read a KML or KMZ file from disk and parse it."""
    if path.lower().endswith(".kmz"):
        return parse_kml(_read_kmz(path))
    with open(path, "rb") as f:
        return parse_kml(f.read())
