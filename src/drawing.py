from PIL import Image, ImageDraw
from io import BytesIO


BACKGROUND_COLOR = (211, 211, 211)  # Gray
WHITE_COLOR = (255, 255, 255)
LINE_SIZE = 7  # Fixed or dynamic?
MARGIN = 15


def get_road_color(road: dict):
    c = max(min(road.get("car_count", 0) / road.get("capacity", 1), 1.0), 0.0)
    return (c, 1 - c, 0)


def create_map_image(roads: list, size: tuple[int, int], colored=False) -> bytes:
    img = Image.new("RGB", (size[0] + 2 * MARGIN, size[1] + 2 *MARGIN), BACKGROUND_COLOR)
    lines = []
    xs = []
    ys = []
    colors = []
    for road in roads:
        lines.append((road["start"], road["end"]))
        xs.append(road["start"][0])
        xs.append(road["end"][0])
        ys.append(road["start"][1])
        ys.append(road["end"][1])
        if colored:
            colors.append(get_road_color(road["car_count"], road["capacity"]))
    min_x, min_y = min(xs), min(ys)
    max_x, max_y = max(xs), max(ys)
    x_len = max_x - min_x
    y_len = max_y - min_y
    lines_gen = zip(lines, colors) if colored else zip(lines)
    draw = ImageDraw.Draw(img)
    for item in lines_gen:
        start, end = item[0]
        color = item[1] if colored else WHITE_COLOR
        new_start = (
            (start[0] - min_x) / x_len * size[0] + MARGIN,
            size[1] - (start[1] - min_y) / y_len * size[1] + MARGIN
        )
        new_end = (
            (end[0] - min_x) / x_len * size[0] + MARGIN,
            size[1] - (end[1] - min_y) / y_len * size[1] + MARGIN
        )
        draw.line((new_start, new_end), fill=color, width=LINE_SIZE)
    bs = BytesIO()
    img.save(bs)
    return bs.getvalue()
