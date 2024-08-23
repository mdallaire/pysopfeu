import urllib.parse

from pysopfeu import construct_wms_url, fetch_wms_data, generate_bbox, parse_wms_response


def test_generate_bbox():
    lat = 45.5
    lon = -73.6
    buffer = 0.0000000000001
    expected_bbox = (-73.6000000000001, 45.4999999999999, -73.5999999999999, 45.5000000000001)
    bbox = generate_bbox(lat, lon, buffer)
    assert bbox == expected_bbox, f"Expected {expected_bbox}, got {bbox}"


def test_construct_wms_url():
    lat = 45.5
    lon = -73.6
    width = 10
    height = 10
    url = construct_wms_url(lat, lon, width, height)

    # Expected BBOX value, URL-encoded
    expected_bbox = "45.4999999999999,-73.6000000000001,45.5000000000001,-73.5999999999999"
    encoded_bbox = urllib.parse.quote(expected_bbox)

    assert "SERVICE=WMS" in url, "WMS service parameter missing"
    assert f"BBOX={encoded_bbox}" in url, f"BBOX parameters incorrect, expected {encoded_bbox}"
    assert "I=5" in url, "I value incorrect"
    assert "J=5" in url, "J value incorrect"


def test_fetch_wms_data(monkeypatch):
    # Mock response
    mock_response = "<test>data</test>"

    def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            @property
            def text(self):
                return mock_response

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)

    url = "https://fake-url.com"
    response = fetch_wms_data(url)
    assert response == mock_response, f"Expected {mock_response}, got {response}"


def test_parse_wms_response():
    # Test with valid XML
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<msGMLOutput>
	<danger_incendie_layer>
		<danger_incendie_feature>
			<nom>Laurentides</nom>
			<numero>16</numero>
			<indice>1</indice>
			<indice_demain>2</indice_demain>
			<indice_apres_demain>1</indice_apres_demain>
		</danger_incendie_feature>
	</danger_incendie_layer>
</msGMLOutput>"""

    expected_data = {
        "nom": "Laurentides",
        "numero": "16",
        "indice": "1",
        "indice_demain": "2",
        "indice_apres_demain": "1",
    }

    parsed_data = parse_wms_response(xml_data)
    assert parsed_data == expected_data, f"Expected {expected_data}, got {parsed_data}"

    # Test with invalid XML
    xml_data_invalid = "<invalid>data</invalid>"
    parsed_data_invalid = parse_wms_response(xml_data_invalid)
    assert parsed_data_invalid == {}, "Expected empty dictionary for invalid XML"


# TODO Fix this test
# def test_wms_to_json(monkeypatch):
#     lat = 45.5
#     lon = -73.6
#     width = 10
#     height = 10
#
#     # Mock the WMS data fetch function
#     mock_response = """<?xml version="1.0" encoding="UTF-8"?>
# <msGMLOutput>
# 	<danger_incendie_layer>
# 		<danger_incendie_feature>
# 			<nom>Laurentides</nom>
# 			<numero>16</numero>
# 			<indice>1</indice>
# 			<indice_demain>2</indice_demain>
# 			<indice_apres_demain>1</indice_apres_demain>
# 		</danger_incendie_feature>
# 	</danger_incendie_layer>
# </msGMLOutput>"""
#
#     def mock_fetch_wms_data(url):
#         return mock_response
#     url = "https://fake-url.com"
#
#     monkeypatch.setattr("pysopfeu.fetch_wms_data", mock_fetch_wms_data)
#
#
#     expected_json = json.dumps({
#         "nom": "Laurentides",
#         "numero": "16",
#         "indice": "1",
#         "indice_demain": "2",
#         "indice_apres_demain": "1"
#     }, ensure_ascii=False, indent=2)
#
#     json_data = wms_to_json(lat, lon, width, height)
#
#     assert json_data == expected_json, f"Expected {expected_json}, got {json_data}"
