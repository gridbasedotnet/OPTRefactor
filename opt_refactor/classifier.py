"""Classify OSM features into visual categories based on their tags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .parser import Feature

# ---------------------------------------------------------------------------
# Category and sub-category definitions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Classification:
    """Result of classifying a single feature."""

    category: str       # e.g. "road", "building", "water"
    subcategory: str    # e.g. "motorway", "residential", "river"


# Rules are checked top-to-bottom; first match wins.
# Each rule: (osm_key, set_of_values | None, category, subcategory)
#   - If values is None, any value for that key matches.
#   - If values is a set, the tag value must be in the set.

_RULES: list[tuple[str, set[str] | None, str, str]] = [
    # --- Roads (ordered by hierarchy) ---
    ("highway", {"motorway", "motorway_link"}, "road", "motorway"),
    ("highway", {"trunk", "trunk_link"}, "road", "trunk"),
    ("highway", {"primary", "primary_link"}, "road", "primary"),
    ("highway", {"secondary", "secondary_link"}, "road", "secondary"),
    ("highway", {"tertiary", "tertiary_link"}, "road", "tertiary"),
    ("highway", {"residential", "living_street"}, "road", "residential"),
    ("highway", {"service"}, "road", "service"),
    ("highway", {"unclassified"}, "road", "unclassified"),
    ("highway", {"footway", "pedestrian", "path", "steps"}, "road", "footway"),
    ("highway", {"cycleway"}, "road", "cycleway"),
    ("highway", {"track"}, "road", "track"),
    ("highway", None, "road", "other"),

    # --- Railways ---
    ("railway", {"rail", "light_rail", "narrow_gauge"}, "railway", "rail"),
    ("railway", {"subway"}, "railway", "subway"),
    ("railway", {"tram"}, "railway", "tram"),
    ("railway", {"station", "halt"}, "railway", "station"),
    ("railway", None, "railway", "other"),

    # --- Water ---
    ("waterway", {"river", "canal"}, "water", "river"),
    ("waterway", {"stream", "drain", "ditch"}, "water", "stream"),
    ("waterway", None, "water", "waterway"),
    ("natural", {"water"}, "water", "lake"),
    ("water", None, "water", "lake"),

    # --- Buildings ---
    ("building", {"church", "cathedral", "chapel", "mosque", "temple", "synagogue"}, "building", "worship"),
    ("building", {"school", "university", "college", "kindergarten"}, "building", "education"),
    ("building", {"hospital"}, "building", "hospital"),
    ("building", {"commercial", "retail", "office"}, "building", "commercial"),
    ("building", {"industrial", "warehouse"}, "building", "industrial"),
    ("building", None, "building", "general"),

    # --- Parks and green spaces ---
    ("leisure", {"park", "garden"}, "green", "park"),
    ("leisure", {"nature_reserve"}, "green", "nature_reserve"),
    ("leisure", {"playground"}, "green", "playground"),
    ("leisure", {"pitch", "sports_centre", "stadium"}, "sport", "facility"),
    ("boundary", {"national_park", "protected_area"}, "green", "protected"),
    ("landuse", {"forest"}, "green", "forest"),
    ("landuse", {"grass", "meadow", "village_green"}, "green", "grass"),
    ("landuse", {"orchard", "vineyard", "allotments"}, "green", "agriculture"),
    ("natural", {"wood"}, "green", "forest"),
    ("natural", {"scrub", "heath", "grassland"}, "green", "scrub"),

    # --- Land use ---
    ("landuse", {"residential"}, "landuse", "residential"),
    ("landuse", {"commercial", "retail"}, "landuse", "commercial"),
    ("landuse", {"industrial"}, "landuse", "industrial"),
    ("landuse", {"farmland", "farmyard"}, "landuse", "farmland"),
    ("landuse", {"cemetery"}, "landuse", "cemetery"),
    ("landuse", {"military"}, "landuse", "military"),
    ("landuse", None, "landuse", "other"),

    # --- Amenities ---
    ("amenity", {"restaurant", "cafe", "fast_food", "bar", "pub", "food_court"}, "amenity", "food"),
    ("amenity", {"school", "university", "college", "kindergarten", "library"}, "amenity", "education"),
    ("amenity", {"hospital", "clinic", "doctors", "dentist", "pharmacy"}, "amenity", "health"),
    ("amenity", {"parking", "fuel", "charging_station"}, "amenity", "transport"),
    ("amenity", {"police", "fire_station"}, "amenity", "emergency"),
    ("amenity", {"place_of_worship"}, "amenity", "worship"),
    ("amenity", {"bank", "atm"}, "amenity", "finance"),
    ("amenity", None, "amenity", "other"),

    # --- Tourism ---
    ("tourism", {"hotel", "motel", "hostel", "guest_house"}, "tourism", "accommodation"),
    ("tourism", {"museum", "gallery", "artwork"}, "tourism", "culture"),
    ("tourism", {"viewpoint"}, "tourism", "viewpoint"),
    ("tourism", {"camp_site", "caravan_site"}, "tourism", "camping"),
    ("tourism", None, "tourism", "other"),

    # --- Shops ---
    ("shop", {"supermarket", "convenience"}, "shop", "grocery"),
    ("shop", None, "shop", "other"),

    # --- Power / Utilities ---
    ("power", {"line", "minor_line"}, "utility", "power_line"),
    ("power", {"tower", "pole"}, "utility", "power_tower"),
    ("power", {"plant", "generator", "substation"}, "utility", "power_facility"),
    ("power", None, "utility", "power"),
    ("man_made", {"pipeline"}, "utility", "pipeline"),
    ("man_made", {"water_tower", "tower", "mast"}, "utility", "tower"),

    # --- Barriers ---
    ("barrier", {"fence", "wall"}, "barrier", "linear"),
    ("barrier", {"gate", "bollard", "lift_gate"}, "barrier", "access"),
    ("barrier", None, "barrier", "other"),

    # --- Aeroway ---
    ("aeroway", {"runway", "taxiway"}, "aeroway", "runway"),
    ("aeroway", {"terminal", "gate"}, "aeroway", "terminal"),
    ("aeroway", None, "aeroway", "other"),

    # --- Natural features (catch-all after water/green) ---
    ("natural", {"peak", "volcano"}, "natural", "peak"),
    ("natural", {"cliff"}, "natural", "cliff"),
    ("natural", {"beach"}, "natural", "beach"),
    ("natural", {"tree"}, "natural", "tree"),
    ("natural", None, "natural", "other"),

    # --- Administrative boundaries ---
    ("boundary", {"administrative"}, "boundary", "administrative"),
    ("boundary", None, "boundary", "other"),

    # --- Public transport ---
    ("public_transport", {"station", "stop_position", "platform"}, "transport", "stop"),
    ("public_transport", None, "transport", "other"),
]

# Default for features that match no rule
_DEFAULT = Classification("other", "unknown")


def classify(feature: Feature) -> Classification:
    """Classify a feature based on its OSM tags.

    Returns the first matching Classification, or a default 'other/unknown'.
    """
    tags = feature.tags
    for key, values, category, subcategory in _RULES:
        tag_val = tags.get(key)
        if tag_val is None:
            continue
        if values is None or tag_val in values:
            return Classification(category, subcategory)
    return _DEFAULT
