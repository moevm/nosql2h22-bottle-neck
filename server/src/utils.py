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


def rotate_point(point: tuple[float, float], cos_value: float, sin_value: float,
                 center: tuple[float, float] = (0.0, 0.0)):
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
    x_points_diff = max(abs(p2[0] - p1[0]), 0.000001)
    if p2[0] - p1[0] < 0:
        x_points_diff *= -1
    angle = math.atan((p2[1] - p1[1]) / x_points_diff)
    cos_value = math.cos(angle)
    sin_value = math.sin(angle)
    a = distance(p1, p2) / 2
    b = distance((0, 0),
                 (radius[0] * math.cos(angle + math.pi / 2),
                  radius[1] * math.sin(angle + math.pi / 2)))
    if a < b:
        a, b = b, a
        cos_value, sin_value = -sin_value, -cos_value
    for i in range(n):
        angle = math.pi / 2 - math.atan(math.tan(math.pi / 2 * i / n) * a / b) if i != n - 1 else 0
        x = a * math.cos(angle)
        y = b * math.sin(angle)
        quadrant1.insert(0, (
            center[0] + x,
            center[1] + y
        ))
        quadrant2.append((
            center[0] - x,
            center[1] + y
        ))
        quadrant3.insert(0, (
            center[0] - x,
            center[1] - y
        ))
        quadrant4.append((
            center[0] + x,
            center[1] - y
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
    routes = []
    roads_values = list(new_roads.values())
    for _ in range(randint(0, 20)):
        route = {
            "time": 0.0,
            "length": 0.0,
            "points": [],
            "workloads": []
        }
        cur_road = roads_values[randint(0, len(new_roads) - 1)]
        route["points"].append(cur_road["location"][0])
        for _ in range(len(new_roads) // 10):
            route["points"].append(cur_road["location"][1])  # end
            route["workloads"].append(cur_road["workload"])
            route["length"] += distance(cur_road["location"][0], cur_road["location"][1])
            route["time"] += randint(10, 100) / 100
            if len(cur_road["ways"]) == 0:
                break
            cur_road = new_roads.get(choice(cur_road["ways"]), cur_road)
        routes.append(route)
    return new_roads.values(), routes


def convert_image_coordinates_to_real(point: tuple[int, int], min_x: float, min_y: float,
                                      x_coeff: float, y_coeff: float, margin: float=config.MAP_IMAGE_MARGIN) -> tuple[float, float]:
    return (
        (point[0] - margin) / x_coeff + min_x,
        (config.MAP_IMAGE_SIZE[1] - (point[1] - margin)) / y_coeff + min_y
    )


def convert_real_coordinates_to_image(point: tuple[int, int], min_x: float, min_y: float,
                                      x_coeff: float, y_coeff: float, margin: float=config.MAP_IMAGE_MARGIN) -> tuple[float, float]:
    return (
        round((point[0] - min_x) * x_coeff) + margin,
        config.MAP_IMAGE_SIZE[1] - round((point[1] - min_y) * y_coeff) + margin
    )


def convert_radius_scale_to_real(radius: float, x_coeff: float, y_coeff: float) -> tuple[float, float]:
    radius = min(1.0, max(0.0, radius))
    return (
        config.MAP_IMAGE_SIZE[0] * radius / x_coeff,
        config.MAP_IMAGE_SIZE[1] * radius / y_coeff,
    )


def scale_roads(roads: list, min_x: float, min_y: float, x_coeff: float,
                y_coeff: float, margin: float=config.MAP_IMAGE_MARGIN) -> list:
    for road in roads:
        road["location"][0] = convert_real_coordinates_to_image(road["location"][0], min_x, min_y, x_coeff, y_coeff, margin)
        road["location"][1] = convert_real_coordinates_to_image(road["location"][1], min_x, min_y, x_coeff, y_coeff, margin)


def scale_routes(routes: list, min_x: float, min_y: float, x_coeff: float,
                 y_coeff: float, margin: float=config.MAP_IMAGE_MARGIN) -> list:
    for route in routes:
        route['points'] = scale_routes_points(route['points'], min_x, min_y, x_coeff, y_coeff, margin)


def scale_routes_points(points: list, min_x: float, min_y: float, x_coeff: float,
                        y_coeff: float, margin: float=config.MAP_IMAGE_MARGIN) -> list:
    return [convert_real_coordinates_to_image(p, min_x, min_y, x_coeff, y_coeff, margin) for p in points]
