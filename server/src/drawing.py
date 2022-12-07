from typing import Iterable
from PIL import Image, ImageDraw
from io import BytesIO
import config


BACKGROUND_COLOR = (211, 211, 211)  # Gray
WHITE_COLOR = (255, 255, 255)
LINE_SIZE = 2  # Fixed or dynamic?
MAX_WORKLOAD = 10


def get_road_color(road: dict):
    workload = road.get("workload", None)
    if workload is None:
        return WHITE_COLOR
    c = workload / MAX_WORKLOAD
    return (int(c * 255), int((1 - c) * 255), 0)


def create_map_image(roads: Iterable, size: tuple[int, int], min_x: float, min_y: float,
                     x_coeff: float, y_coeff:float, colored=False) -> bytes:
    img = Image.new("RGB", (size[0] + 2 * config.MAP_IMAGE_MARGIN, size[1] + 2 *config.MAP_IMAGE_MARGIN), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    for road in roads:
        start, end = road["location"][0], road["location"][1]
        color = get_road_color(road) if colored else WHITE_COLOR
        new_start = (
            int((start[0] - min_x) * x_coeff + config.MAP_IMAGE_MARGIN),
            int(size[1] - (start[1] - min_y) * y_coeff + config.MAP_IMAGE_MARGIN)
        )
        new_end = (
            int((end[0] - min_x) * x_coeff + config.MAP_IMAGE_MARGIN),
            int(size[1] - (end[1] - min_y) * y_coeff + config.MAP_IMAGE_MARGIN)
        )
        draw.line((new_start, new_end), fill=color, width=LINE_SIZE)
    bs = BytesIO()
    img.save(bs, format="png", bitmap_format="png")
    return bs.getvalue()
