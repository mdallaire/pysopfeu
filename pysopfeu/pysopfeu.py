"""Main module."""

import json
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Tuple

import requests


def generate_bbox(lat: float, lon: float, buffer: float = 0.0001) -> Tuple[float, float, float, float]:
    """
    Generate a tight bounding box around the given latitude and longitude.

    :param lat: Latitude in EPSG:4326.
    :param lon: Longitude in EPSG:4326.
    :param buffer: Buffer distance to create the bounding box (default is 0.0001 degrees).
    :return: A tuple representing the bounding box (min_lon, min_lat, max_lon, max_lat).
    """
    min_lat = lat - buffer
    max_lat = lat + buffer
    min_lon = lon - buffer
    max_lon = lon + buffer

    return min_lon, min_lat, max_lon, max_lat


def construct_wms_url(lat: float, lon: float, width: int, height: int) -> str:
    bbox = generate_bbox(lat, lon)
    i = width // 2
    j = height // 2

    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetFeatureInfo",
        "BBOX": f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}",
        "CRS": "EPSG:4326",
        "WIDTH": str(width),
        "HEIGHT": str(height),
        "LAYERS": "danger_incendie",
        "STYLES": "",
        "FORMAT": "image/png",
        "QUERY_LAYERS": "danger_incendie",
        "INFO_FORMAT": "application/vnd.ogc.gml",
        "I": str(i),
        "J": str(j),
        "FEATURE_COUNT": "10",
    }

    base_url = "https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi"
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    return url


def fetch_wms_data(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text


def parse_wms_response(xml_data: str) -> dict:
    root = ET.fromstring(xml_data)
    feature = root.find('.//danger_incendie_feature')
    if feature is not None:
        data = {
            "nom": feature.findtext('.//nom'),
            "numero": feature.findtext('.//numero'),
            "indice": feature.findtext('.//indice'),
            "indice_demain": feature.findtext('.//indice_demain'),
            "indice_apres_demain": feature.findtext('.//indice_apres_demain'),
        }
        return data
    return {}


def wms_to_json(lat: float, lon: float, width: int, height: int) -> str:
    url = construct_wms_url(lat, lon, width, height)
    xml_data = fetch_wms_data(url)
    parsed_data = parse_wms_response(xml_data)
    return json.dumps(parsed_data, ensure_ascii=False, indent=2)
