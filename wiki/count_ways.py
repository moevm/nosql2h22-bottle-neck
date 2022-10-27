nodes_ways = {
    1: [2],
    2: [1, 3, 6],
    3: [2, 4, 7],
    4: [3, 5, 8],
    5: [4, 9],
    6: [2, 7, 13],
    7: [3, 6, 8],
    8: [4, 7, 12],
    9: [5, 10, 11],
    10: [9, 11, 25],
    11: [9, 10, 12],
    12: [8, 11, 14, 24],
    13: [6, 15, 16],
    14: [12, 15, 18, 17],
    15: [13, 14, 16],
    16: [13, 15, 20],
    17: [14],
    18: [14, 19],
    19: [18, 21, 23],
    20: [16, 21, 23],
    21: [19, 20, 22],
    22: [21, 24, 26],
    23: [19, 20, 27],
    24: [12, 22, 25, 26],
    25: [10, 24, 28],
    26: [22, 24, 27],
    27: [23, 26, 28],
    28: [25, 27]
}

start_node = 1
end_node = 28
count = 0

cur_way = []


def count_ways(next_node):
    global count
    if next_node == end_node:
        count += 1
        return
    if next_node in cur_way:
        return
    if any([node in cur_way for node in nodes_ways[next_node] if len(cur_way) == 0 or cur_way[-1] != node]):
        return
    cur_way.append(next_node)
    for node in nodes_ways[next_node]:
        count_ways(node)
    cur_way.pop()


if __name__ == "__main__":
    count_ways(start_node)
    print("Количество путей:", count)
