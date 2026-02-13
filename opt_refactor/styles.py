"""KML style definitions mapped to feature classifications.

KML colors use the format ``aabbggrr`` (alpha-blue-green-red).
Helper utilities convert from standard hex RGB for readability.
"""

from __future__ import annotations

from dataclasses import dataclass


def rgb_to_kml(hex_rgb: str, alpha: str = "ff") -> str:
    """Convert ``#RRGGBB`` or ``RRGGBB`` to KML ``aabbggrr``."""
    h = hex_rgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"{alpha}{b}{g}{r}"


# ---------------------------------------------------------------------------
# Style definition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FeatureStyle:
    """Visual style to apply to a KML feature."""

    # Line / polygon outline
    line_color: str       # KML aabbggrr
    line_width: float = 2.0

    # Polygon fill (only used for Polygon geometries)
    poly_color: str = ""  # KML aabbggrr; empty = no fill
    poly_fill: bool = True
    poly_outline: bool = True

    # Point icon
    icon_href: str = ""   # URL; empty = default pushpin
    icon_scale: float = 1.0

    # Label
    label_color: str = "ffffffff"
    label_scale: float = 0.8


# ---------------------------------------------------------------------------
# Google Earth built-in icon base URL
# ---------------------------------------------------------------------------

_GICON = "http://maps.google.com/mapfiles/kml"

# Shortcuts to commonly used Google Earth palette icons
ICON_CIRCLE = f"{_GICON}/shapes/placemark_circle.png"
ICON_SQUARE = f"{_GICON}/shapes/placemark_square.png"
ICON_STAR = f"{_GICON}/shapes/star.png"
ICON_TRIANGLE = f"{_GICON}/shapes/triangle.png"
ICON_DINING = f"{_GICON}/shapes/dining.png"
ICON_SCHOOLS = f"{_GICON}/paddle/grn-blank.png"
ICON_HOSPITAL = f"{_GICON}/paddle/red-circle.png"
ICON_PARKING = f"{_GICON}/paddle/blu-blank.png"
ICON_POLICE = f"{_GICON}/paddle/blu-circle.png"
ICON_WORSHIP = f"{_GICON}/paddle/purple-blank.png"
ICON_HOTEL = f"{_GICON}/paddle/ylw-blank.png"
ICON_MUSEUM = f"{_GICON}/paddle/pink-blank.png"
ICON_VIEWPOINT = f"{_GICON}/shapes/camera.png"
ICON_CAMPING = f"{_GICON}/paddle/grn-circle.png"
ICON_SHOP = f"{_GICON}/paddle/wht-blank.png"
ICON_TREE = f"{_GICON}/shapes/parks.png"
ICON_PEAK = f"{_GICON}/shapes/mountains.png"
ICON_RAIL_STATION = f"{_GICON}/shapes/rail.png"
ICON_BUS = f"{_GICON}/shapes/bus.png"
ICON_DEFAULT = f"{_GICON}/paddle/wht-circle.png"

# ---------------------------------------------------------------------------
# Style palette — keyed by (category, subcategory)
#
# Falls back: (category, subcategory) -> (category, "*") -> ("other", "*")
# ---------------------------------------------------------------------------

_STYLES: dict[tuple[str, str], FeatureStyle] = {
    # ---- Roads ----
    ("road", "motorway"):    FeatureStyle(line_color=rgb_to_kml("#E74C3C"), line_width=5.0),
    ("road", "trunk"):       FeatureStyle(line_color=rgb_to_kml("#E67E22"), line_width=4.5),
    ("road", "primary"):     FeatureStyle(line_color=rgb_to_kml("#F39C12"), line_width=4.0),
    ("road", "secondary"):   FeatureStyle(line_color=rgb_to_kml("#F1C40F"), line_width=3.5),
    ("road", "tertiary"):    FeatureStyle(line_color=rgb_to_kml("#FFFFFF"), line_width=3.0),
    ("road", "residential"): FeatureStyle(line_color=rgb_to_kml("#BDC3C7"), line_width=2.5),
    ("road", "service"):     FeatureStyle(line_color=rgb_to_kml("#95A5A6"), line_width=2.0),
    ("road", "unclassified"):FeatureStyle(line_color=rgb_to_kml("#BDC3C7"), line_width=2.0),
    ("road", "footway"):     FeatureStyle(line_color=rgb_to_kml("#E88DB4"), line_width=1.5),
    ("road", "cycleway"):    FeatureStyle(line_color=rgb_to_kml("#2980B9"), line_width=2.0),
    ("road", "track"):       FeatureStyle(line_color=rgb_to_kml("#8B6914"), line_width=1.5),
    ("road", "*"):           FeatureStyle(line_color=rgb_to_kml("#CCCCCC"), line_width=2.0),

    # ---- Railways ----
    ("railway", "rail"):     FeatureStyle(line_color=rgb_to_kml("#2C3E50"), line_width=3.0, icon_href=ICON_RAIL_STATION),
    ("railway", "subway"):   FeatureStyle(line_color=rgb_to_kml("#8E44AD"), line_width=3.0, icon_href=ICON_RAIL_STATION),
    ("railway", "tram"):     FeatureStyle(line_color=rgb_to_kml("#C0392B"), line_width=2.0, icon_href=ICON_RAIL_STATION),
    ("railway", "station"):  FeatureStyle(line_color=rgb_to_kml("#2C3E50"), line_width=2.0, icon_href=ICON_RAIL_STATION, icon_scale=1.2),
    ("railway", "*"):        FeatureStyle(line_color=rgb_to_kml("#2C3E50"), line_width=2.0, icon_href=ICON_RAIL_STATION),

    # ---- Water ----
    ("water", "river"):  FeatureStyle(line_color=rgb_to_kml("#2980B9"), line_width=3.5,
                                      poly_color=rgb_to_kml("#3498DB", "80")),
    ("water", "stream"): FeatureStyle(line_color=rgb_to_kml("#5DADE2"), line_width=2.0),
    ("water", "lake"):   FeatureStyle(line_color=rgb_to_kml("#2471A3"), line_width=2.0,
                                      poly_color=rgb_to_kml("#3498DB", "80")),
    ("water", "*"):      FeatureStyle(line_color=rgb_to_kml("#2980B9"), line_width=2.0,
                                      poly_color=rgb_to_kml("#3498DB", "80")),

    # ---- Buildings ----
    ("building", "worship"):    FeatureStyle(line_color=rgb_to_kml("#8E44AD"), line_width=1.5,
                                             poly_color=rgb_to_kml("#D2B4DE", "90"), icon_href=ICON_WORSHIP),
    ("building", "education"):  FeatureStyle(line_color=rgb_to_kml("#27AE60"), line_width=1.5,
                                             poly_color=rgb_to_kml("#A9DFBF", "90"), icon_href=ICON_SCHOOLS),
    ("building", "hospital"):   FeatureStyle(line_color=rgb_to_kml("#E74C3C"), line_width=1.5,
                                             poly_color=rgb_to_kml("#F5B7B1", "90"), icon_href=ICON_HOSPITAL),
    ("building", "commercial"):FeatureStyle(line_color=rgb_to_kml("#2980B9"), line_width=1.5,
                                             poly_color=rgb_to_kml("#AED6F1", "90")),
    ("building", "industrial"):FeatureStyle(line_color=rgb_to_kml("#7F8C8D"), line_width=1.5,
                                             poly_color=rgb_to_kml("#D5D8DC", "90")),
    ("building", "*"):         FeatureStyle(line_color=rgb_to_kml("#B0703C"), line_width=1.0,
                                             poly_color=rgb_to_kml("#E8C9A0", "90")),

    # ---- Green spaces ----
    ("green", "park"):           FeatureStyle(line_color=rgb_to_kml("#27AE60"), line_width=2.0,
                                              poly_color=rgb_to_kml("#2ECC71", "70"), icon_href=ICON_TREE),
    ("green", "forest"):         FeatureStyle(line_color=rgb_to_kml("#1E8449"), line_width=2.0,
                                              poly_color=rgb_to_kml("#196F3D", "70")),
    ("green", "nature_reserve"): FeatureStyle(line_color=rgb_to_kml("#1ABC9C"), line_width=2.5,
                                              poly_color=rgb_to_kml("#A3E4D7", "60")),
    ("green", "grass"):          FeatureStyle(line_color=rgb_to_kml("#82E0AA"), line_width=1.5,
                                              poly_color=rgb_to_kml("#ABEBC6", "70")),
    ("green", "protected"):      FeatureStyle(line_color=rgb_to_kml("#1ABC9C"), line_width=3.0,
                                              poly_color=rgb_to_kml("#A3E4D7", "50")),
    ("green", "*"):              FeatureStyle(line_color=rgb_to_kml("#27AE60"), line_width=1.5,
                                              poly_color=rgb_to_kml("#2ECC71", "60")),

    # ---- Sport ----
    ("sport", "*"): FeatureStyle(line_color=rgb_to_kml("#F39C12"), line_width=2.0,
                                 poly_color=rgb_to_kml("#F9E79F", "70")),

    # ---- Land use ----
    ("landuse", "residential"): FeatureStyle(line_color=rgb_to_kml("#D5D8DC"), line_width=1.0,
                                             poly_color=rgb_to_kml("#EAECEE", "50")),
    ("landuse", "commercial"):  FeatureStyle(line_color=rgb_to_kml("#AED6F1"), line_width=1.0,
                                             poly_color=rgb_to_kml("#D6EAF8", "50")),
    ("landuse", "industrial"):  FeatureStyle(line_color=rgb_to_kml("#ABB2B9"), line_width=1.0,
                                             poly_color=rgb_to_kml("#D5D8DC", "50")),
    ("landuse", "farmland"):    FeatureStyle(line_color=rgb_to_kml("#F5CBA7"), line_width=1.0,
                                             poly_color=rgb_to_kml("#FDEBD0", "50")),
    ("landuse", "cemetery"):    FeatureStyle(line_color=rgb_to_kml("#7D8B8A"), line_width=1.5,
                                             poly_color=rgb_to_kml("#ABB2B9", "60")),
    ("landuse", "military"):    FeatureStyle(line_color=rgb_to_kml("#E74C3C"), line_width=2.5,
                                             poly_color=rgb_to_kml("#F5B7B1", "40")),
    ("landuse", "*"):           FeatureStyle(line_color=rgb_to_kml("#D5D8DC"), line_width=1.0,
                                             poly_color=rgb_to_kml("#EAECEE", "40")),

    # ---- Amenities ----
    ("amenity", "food"):      FeatureStyle(line_color=rgb_to_kml("#E67E22"), line_width=1.5,
                                           icon_href=ICON_DINING, icon_scale=1.1),
    ("amenity", "education"): FeatureStyle(line_color=rgb_to_kml("#27AE60"), line_width=1.5,
                                           icon_href=ICON_SCHOOLS, icon_scale=1.1),
    ("amenity", "health"):    FeatureStyle(line_color=rgb_to_kml("#E74C3C"), line_width=1.5,
                                           icon_href=ICON_HOSPITAL, icon_scale=1.1),
    ("amenity", "transport"): FeatureStyle(line_color=rgb_to_kml("#3498DB"), line_width=1.5,
                                           icon_href=ICON_PARKING, icon_scale=1.0),
    ("amenity", "emergency"): FeatureStyle(line_color=rgb_to_kml("#2980B9"), line_width=1.5,
                                           icon_href=ICON_POLICE, icon_scale=1.1),
    ("amenity", "worship"):   FeatureStyle(line_color=rgb_to_kml("#8E44AD"), line_width=1.5,
                                           icon_href=ICON_WORSHIP, icon_scale=1.1),
    ("amenity", "finance"):   FeatureStyle(line_color=rgb_to_kml("#2C3E50"), line_width=1.5,
                                           icon_href=ICON_SQUARE, icon_scale=1.0),
    ("amenity", "*"):         FeatureStyle(line_color=rgb_to_kml("#E67E22"), line_width=1.5,
                                           icon_href=ICON_CIRCLE, icon_scale=0.9),

    # ---- Tourism ----
    ("tourism", "accommodation"): FeatureStyle(line_color=rgb_to_kml("#F1C40F"), line_width=1.5,
                                               icon_href=ICON_HOTEL, icon_scale=1.1),
    ("tourism", "culture"):       FeatureStyle(line_color=rgb_to_kml("#E91E8C"), line_width=1.5,
                                               icon_href=ICON_MUSEUM, icon_scale=1.1),
    ("tourism", "viewpoint"):     FeatureStyle(line_color=rgb_to_kml("#3498DB"), line_width=1.5,
                                               icon_href=ICON_VIEWPOINT, icon_scale=1.1),
    ("tourism", "camping"):       FeatureStyle(line_color=rgb_to_kml("#27AE60"), line_width=1.5,
                                               icon_href=ICON_CAMPING, icon_scale=1.1),
    ("tourism", "*"):             FeatureStyle(line_color=rgb_to_kml("#F1C40F"), line_width=1.5,
                                               icon_href=ICON_STAR, icon_scale=1.0),

    # ---- Shops ----
    ("shop", "*"): FeatureStyle(line_color=rgb_to_kml("#AF7AC5"), line_width=1.5,
                                icon_href=ICON_SHOP, icon_scale=1.0),

    # ---- Utilities ----
    ("utility", "power_line"):     FeatureStyle(line_color=rgb_to_kml("#7F8C8D"), line_width=1.5),
    ("utility", "power_tower"):    FeatureStyle(line_color=rgb_to_kml("#7F8C8D"), line_width=1.0,
                                                icon_href=ICON_TRIANGLE, icon_scale=0.8),
    ("utility", "power_facility"): FeatureStyle(line_color=rgb_to_kml("#F39C12"), line_width=2.0,
                                                poly_color=rgb_to_kml("#F9E79F", "60")),
    ("utility", "*"):              FeatureStyle(line_color=rgb_to_kml("#7F8C8D"), line_width=1.5),

    # ---- Barriers ----
    ("barrier", "linear"): FeatureStyle(line_color=rgb_to_kml("#616A6B"), line_width=1.5),
    ("barrier", "access"): FeatureStyle(line_color=rgb_to_kml("#E74C3C"), line_width=1.0,
                                        icon_href=ICON_SQUARE, icon_scale=0.7),
    ("barrier", "*"):      FeatureStyle(line_color=rgb_to_kml("#616A6B"), line_width=1.0),

    # ---- Aeroway ----
    ("aeroway", "runway"):   FeatureStyle(line_color=rgb_to_kml("#2C3E50"), line_width=5.0,
                                          poly_color=rgb_to_kml("#566573", "80")),
    ("aeroway", "terminal"): FeatureStyle(line_color=rgb_to_kml("#2C3E50"), line_width=2.0,
                                          poly_color=rgb_to_kml("#ABB2B9", "80")),
    ("aeroway", "*"):        FeatureStyle(line_color=rgb_to_kml("#566573"), line_width=2.0),

    # ---- Natural ----
    ("natural", "peak"):  FeatureStyle(line_color=rgb_to_kml("#784212"), line_width=1.0,
                                       icon_href=ICON_PEAK, icon_scale=1.2),
    ("natural", "cliff"): FeatureStyle(line_color=rgb_to_kml("#784212"), line_width=2.5),
    ("natural", "beach"): FeatureStyle(line_color=rgb_to_kml("#F9E79F"), line_width=1.5,
                                       poly_color=rgb_to_kml("#FCF3CF", "70")),
    ("natural", "tree"):  FeatureStyle(line_color=rgb_to_kml("#196F3D"), line_width=1.0,
                                       icon_href=ICON_TREE, icon_scale=0.8),
    ("natural", "*"):     FeatureStyle(line_color=rgb_to_kml("#7D6608"), line_width=1.5),

    # ---- Boundaries ----
    ("boundary", "administrative"): FeatureStyle(line_color=rgb_to_kml("#8E44AD"), line_width=3.0),
    ("boundary", "*"):              FeatureStyle(line_color=rgb_to_kml("#8E44AD"), line_width=2.0),

    # ---- Public transport ----
    ("transport", "stop"): FeatureStyle(line_color=rgb_to_kml("#2980B9"), line_width=1.5,
                                        icon_href=ICON_BUS, icon_scale=1.0),
    ("transport", "*"):    FeatureStyle(line_color=rgb_to_kml("#2980B9"), line_width=1.5,
                                        icon_href=ICON_BUS, icon_scale=0.9),

    # ---- Fallback ----
    ("other", "*"): FeatureStyle(line_color=rgb_to_kml("#BDC3C7"), line_width=1.5,
                                 icon_href=ICON_DEFAULT, icon_scale=0.8),
}


def get_style(category: str, subcategory: str) -> FeatureStyle:
    """Look up the visual style for a classification.

    Resolution order:
        1. Exact match  (category, subcategory)
        2. Wildcard      (category, "*")
        3. Default        ("other", "*")
    """
    style = _STYLES.get((category, subcategory))
    if style is not None:
        return style
    style = _STYLES.get((category, "*"))
    if style is not None:
        return style
    return _STYLES[("other", "*")]


def style_id(category: str, subcategory: str) -> str:
    """Return a stable style ID string suitable for a KML ``<Style id="...">``."""
    return f"style-{category}-{subcategory}"
