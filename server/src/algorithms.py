import networkx as nx


MAX_PREDECESSORS_COUNT = 1
MAX_SPEED = 60 * 1000 / 60
MIN_SPEED = 10 * 1000 / 60


def convert_roads_to_graph(roads: dict) -> nx.DiGraph:
    g = nx.DiGraph()
    for road in roads.values():
        road_id = str(road["_id"])
        g.add_node(road_id)
        g.add_edges_from([(road_id, str(way)) for way in road["ways"]])
    return g


def find_paths(g: nx.DiGraph, source: str, target: str) -> list:
    paths = []
    bridges_set = set()

    removed_edges = []
    last_edge = None
    while True:
        try:
            path = nx.dijkstra_path(g, source, target)
            if last_edge is not None:
                bridges_set.add(last_edge)
            last_edge = None
            if len(paths) == 0 or path != paths[-1]:
                paths.append(path)
            count = 0
            for i, node_id in enumerate(path[1:-1]):
                predecessors_count = 0
                for _ in g.predecessors(node_id):
                    predecessors_count += 1
                    if predecessors_count > MAX_PREDECESSORS_COUNT:
                        break
                edge = (path[i], node_id)
                if predecessors_count > MAX_PREDECESSORS_COUNT and edge not in bridges_set:
                    g.remove_edge(*edge)
                    removed_edges.append(edge)
                    count += 1
            if count == 0:
                break
        except nx.NetworkXNoPath:
            if len(removed_edges) == 0:
                break
            last_edge = removed_edges.pop()
            g.add_edge(*last_edge)
    return paths


def pass_flow_on_routes(routes: list[dict], cars_count: int, roads: dict):
    while True:
        for route in routes:
            new_cars_count = __pass_flow_on_one_route(route, cars_count, roads)
            if new_cars_count == cars_count or new_cars_count <= 0:
                return
            cars_count = new_cars_count


def __pass_flow_on_one_route(route: dict, cars_count: int, roads: dict) -> int:
    passed_count = 0
    for road_id in route["roads_ids"]:
        road = roads[road_id]
        if road["car_count"] >= road["capacity"]:
            continue
        road["car_count"] += 1
        passed_count += 1
        if passed_count >= cars_count:
            break
    return cars_count - passed_count


def calculate_route_time(route: dict) -> float:
    time = 0.0
    for workload, road_len in zip(route["workloads"], route["roads_lengths"]):
        speed = max((1 - workload / 10) * MAX_SPEED, MIN_SPEED)
        time += road_len / speed
    return time
