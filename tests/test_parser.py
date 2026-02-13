"""Tests for the KML parser."""

from pathlib import Path

from opt_refactor.parser import parse_kml, parse_kml_file

SAMPLE_DIR = Path(__file__).parent / "sample_data"


def test_parse_sample_kml_file():
    features = parse_kml_file(str(SAMPLE_DIR / "overpass_sample.kml"))
    assert len(features) == 10


def test_feature_geometry_types():
    features = parse_kml_file(str(SAMPLE_DIR / "overpass_sample.kml"))
    types = {f.name: f.geometry_type for f in features}
    assert types["Main Street"] == "LineString"
    assert types["City Library"] == "Polygon"
    assert types["Joe's Pizza"] == "Point"
    assert types["Riverside Park"] == "Polygon"


def test_feature_tags_extracted():
    features = parse_kml_file(str(SAMPLE_DIR / "overpass_sample.kml"))
    pizza = next(f for f in features if f.name == "Joe's Pizza")
    assert pizza.tags["amenity"] == "restaurant"
    assert pizza.tags["cuisine"] == "pizza"


def test_osm_id_extracted():
    features = parse_kml_file(str(SAMPLE_DIR / "overpass_sample.kml"))
    main_st = next(f for f in features if f.name == "Main Street")
    assert main_st.osm_id == "way/12345"


def test_parse_inline_kml():
    kml = """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Document>
        <Placemark>
          <name>Test Point</name>
          <ExtendedData>
            <Data name="amenity"><value>bench</value></Data>
          </ExtendedData>
          <Point><coordinates>1.0,2.0,0</coordinates></Point>
        </Placemark>
      </Document>
    </kml>"""
    features = parse_kml(kml)
    assert len(features) == 1
    assert features[0].geometry_type == "Point"
    assert features[0].tags["amenity"] == "bench"


def test_placemark_without_geometry_skipped():
    kml = """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Document>
        <Placemark>
          <name>No geometry</name>
        </Placemark>
      </Document>
    </kml>"""
    features = parse_kml(kml)
    assert len(features) == 0
