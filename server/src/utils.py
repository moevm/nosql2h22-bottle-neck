from pyproj import Transformer
from pymongo.cursor import Cursor
import config


transformer = Transformer.from_crs(config.FROM_EPSG, config.TO_EPSG, always_xy=True)


def transform_roads(roads: Cursor) -> list[dict]:
    projected_roads = []
    for road in roads:
        projected_start = transformer.transform(*road["start"])
        projected_end = transformer.transform(*road["end"])
        road["start"] = list(projected_start)
        road["end"] = list(projected_end)
        projected_roads.append(road)
    return projected_roads
