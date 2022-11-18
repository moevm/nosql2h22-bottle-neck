import matplotlib.pyplot as plt
from io import BytesIO


BACKGROUND_COLOR = (211 / 256, 211 / 256, 211 / 256)
LINE_SIZE = 2.0  # Fixed or dynamic?
PX = 1 / plt.rcParams['figure.dpi']


def get_road_color(road: dict):
    c = max(min(road.get("car_count", 0) / road.get("capacity", 1), 1.0), 0.0)
    return (c, 1 - c, 0)


def create_map_image(roads: list, size: tuple[int, int], colored=False) -> bytes:
    fig = plt.figure(figsize=(size[0] * PX, size[1] * PX), facecolor=BACKGROUND_COLOR)
    ax = fig.gca()
    ax.set_facecolor(BACKGROUND_COLOR)
    lines = []
    colors = []
    for road in roads:
        lines.append((road["start"][0], road["end"][0]))
        lines.append((road["start"][1], road["end"][1]))
        if colored:
            colors.append(get_road_color(road))
    if colored:
        ax.set_prop_cycle(color=colors)
    else:
        ax.set_prop_cycle(color=["white"])
    ax.plot(*lines, linewidth=LINE_SIZE)
    bs = BytesIO()
    fig.savefig(bs, format="png")
    return bs.getvalue()
