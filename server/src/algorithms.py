import networkx as nx


MAX_PREDECESSORS_COUNT = 2


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
            if len(path) == 0 or path != paths[-1]:
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
