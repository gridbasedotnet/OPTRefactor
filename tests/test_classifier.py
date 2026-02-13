"""Tests for the feature classifier."""

from opt_refactor.classifier import classify, Classification
from opt_refactor.parser import Feature
from lxml import etree


def _make_feature(tags: dict[str, str], geom_type: str = "Point") -> Feature:
    """Helper to create a minimal Feature with given tags."""
    geom = etree.Element("Point")
    return Feature(
        name="test",
        geometry_type=geom_type,
        geometry_element=geom,
        tags=tags,
    )


def test_classify_motorway():
    f = _make_feature({"highway": "motorway"}, "LineString")
    c = classify(f)
    assert c.category == "road"
    assert c.subcategory == "motorway"


def test_classify_residential_road():
    f = _make_feature({"highway": "residential"}, "LineString")
    c = classify(f)
    assert c.category == "road"
    assert c.subcategory == "residential"


def test_classify_footway():
    f = _make_feature({"highway": "footway"}, "LineString")
    c = classify(f)
    assert c.category == "road"
    assert c.subcategory == "footway"


def test_classify_building():
    f = _make_feature({"building": "yes"}, "Polygon")
    c = classify(f)
    assert c.category == "building"
    assert c.subcategory == "general"


def test_classify_building_hospital():
    f = _make_feature({"building": "hospital"}, "Polygon")
    c = classify(f)
    assert c.category == "building"
    assert c.subcategory == "hospital"


def test_classify_park():
    f = _make_feature({"leisure": "park"}, "Polygon")
    c = classify(f)
    assert c.category == "green"
    assert c.subcategory == "park"


def test_classify_river():
    f = _make_feature({"waterway": "river"}, "LineString")
    c = classify(f)
    assert c.category == "water"
    assert c.subcategory == "river"


def test_classify_lake():
    f = _make_feature({"natural": "water"}, "Polygon")
    c = classify(f)
    assert c.category == "water"
    assert c.subcategory == "lake"


def test_classify_restaurant():
    f = _make_feature({"amenity": "restaurant"}, "Point")
    c = classify(f)
    assert c.category == "amenity"
    assert c.subcategory == "food"


def test_classify_hospital_amenity():
    f = _make_feature({"amenity": "hospital"}, "Point")
    c = classify(f)
    assert c.category == "amenity"
    assert c.subcategory == "health"


def test_classify_subway():
    f = _make_feature({"railway": "subway"}, "LineString")
    c = classify(f)
    assert c.category == "railway"
    assert c.subcategory == "subway"


def test_classify_unknown_defaults_to_other():
    f = _make_feature({"some_random_tag": "value"})
    c = classify(f)
    assert c.category == "other"
    assert c.subcategory == "unknown"


def test_classify_empty_tags_defaults_to_other():
    f = _make_feature({})
    c = classify(f)
    assert c == Classification("other", "unknown")


def test_first_match_wins():
    # A feature with both highway and building tags — highway should win
    # because road rules come first
    f = _make_feature({"highway": "primary", "building": "yes"}, "LineString")
    c = classify(f)
    assert c.category == "road"


def test_classify_boundary():
    f = _make_feature({"boundary": "administrative"})
    c = classify(f)
    assert c.category == "boundary"
    assert c.subcategory == "administrative"
