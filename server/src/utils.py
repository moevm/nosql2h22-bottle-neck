from pyproj import Transformer
from pymongo.cursor import Cursor
from random import randint, choice
import math
import config


transformer = Transformer.from_crs(config.FROM_EPSG, config.TO_EPSG, always_xy=True)


def transform_roads(roads: Cursor) -> list[dict]:
    projected_roads = []
    xs = []
    ys = []
    for road in roads:
        projected_start = transformer.transform(*road["location"][0])
        projected_end = transformer.transform(*road["location"][1])
        road["location"][0] = list(projected_start)
        road["location"][1] = list(projected_end)
        projected_roads.append(road)
        xs.append(projected_start[0])
        xs.append(projected_end[0])
        ys.append(projected_start[1])
        ys.append(projected_end[1])
    min_x, min_y = min(xs), min(ys)
    max_x, max_y = max(xs), max(ys)
    x_diff = max_x - min_x
    y_diff = max_y - min_y
    return projected_roads, min_x, min_y, x_diff, y_diff


def distance(point1: tuple, point2: tuple):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def rotate_point(point: tuple[float, float], cos_value: float, sin_value: float, center: tuple[float, float] = (0.0, 0.0)):
    shifted_point = (
        point[0] - center[0],
        point[1] - center[1],
    )
    rotated_point = (
        shifted_point[0] * cos_value - shifted_point[1] * sin_value,
        shifted_point[0] * sin_value + shifted_point[1] * cos_value
    )
    return (
        rotated_point[0] + center[0],
        rotated_point[1] + center[1],
    )


def approximate_ellipse(p1: tuple[float, float], p2: tuple[float, float],
                        radius: tuple[float, float], n: int) -> list[tuple[float, float]]:
    quadrant1 = []
    quadrant2 = []
    quadrant3 = []
    quadrant4 = []
    center = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    angle = math.atan(abs(p1[1] - p2[1]) / max(abs(p1[0] - p2[0]), 0.000001))
    cos_value = math.cos(angle)
    sin_value = math.sin(angle)
    x_len = distance(p1, p2) / 2
    y_len = radius[0]
    quadrant1.append((
            center[0] + x_len,
            center[1] + y_len
    ))
    quadrant2.append((
            center[0] - x_len,
            center[1] + y_len
    ))
    quadrant3.append((
            center[0] - x_len,
            center[1] - y_len
    ))
    quadrant4.append((
            center[0] + x_len,
            center[1] - y_len
    ))
    return [rotate_point(point, cos_value, sin_value, center)
            for point in quadrant1 + quadrant2 + quadrant3 + quadrant4]


def simulate(roads: Cursor, car_count: int) -> tuple[list[dict], list[dict]]:
    new_roads = {}
    for road in roads:
        cars = randint(0, road["capacity"])
        road["car_count"] = cars
        road["workload"] = round(cars / road["capacity"] * 10)
        new_roads[(road["_id"])] = road
    ways = []
    roads_values = list(new_roads.values())
    for _ in range(randint(0, 20)):
        way = {
            "time": 0.0,
            "length": 0.0,
            "points": []
        }
        cur_road = roads_values[randint(0, len(new_roads) - 1)]
        way["points"].append(cur_road["location"][0])
        for _ in range(len(new_roads) // 10):
            way["points"].append(cur_road["location"][1])  # end
            way["length"] += distance(cur_road["location"][0], cur_road["location"][0])
            way["time"] += randint(10, 100) / 100
            if len(cur_road["ways"]) == 0:
                break
            cur_road = new_roads.get(choice(cur_road["ways"]), cur_road)
        ways.append(way)
    return new_roads.values(), ways


def scale_ways_points(points: list, min_x: float, min_y: float, x_coeff: float, y_coeff:float) -> list:
    return [((p[0] - min_x) * x_coeff, (p[1] - min_y) * y_coeff) for p in points]