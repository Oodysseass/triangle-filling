import numpy as np  
import math
from edge import Edge

def get_data(filename):
    data = np.load(filename, allow_pickle=True).item()
    return data

def interpolate_vectors(p1, p2, V1, V2, xy, dim):
    ## find line connecting p1-p2
    # parallel to xx
    if p1[1] == p2[1]:
        # obviously dim == 1
        p = np.array([xy, p1[1]])

    # vertical line
    elif p1[0] == p2[0]:
        # obviously dim == 2
        p = np.array([p1[0], xy])

    # normal line
    else:
        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b = p1[1] - m * p1[0]
        if dim == 1:
            p = np.array([xy, m * xy + b])
        elif dim == 2:
            p = np.array([(xy - b) / m, xy])

    ## find p-p1 and p1-p2 distance
    # p-p1
    d1 = np.linalg.norm(p - p1)
    
    # p1-p2
    d2 = np.linalg.norm(p1 - p2)

    ## interpolation
    # coefficient
    if d2 == 0:
        l = 1
    else:
        l = d1 / d2

    # interpolate
    V = abs((1 - l) * V1 + l * V2)

    return V

def flats(canvas, vertices, vcolors):
    updatedcanvas = canvas

    # flat color that's going to be used for all vertices
    flat_color = np.mean(vcolors, axis = 0)


    ## save edges
    edges = [Edge() for _ in range(3)]
    for i in range(3):
        if i == 2:
            edges[i] = Edge(i, np.array([vertices[(i + 1) % 3, :], \
                                         vertices[i, :]]))
        else:
            edges[i] = Edge(i, np.array([vertices[i, :], \
                                         vertices[(i + 1) % 3, :]]))

    ## find overall min and max
    y_min = min([edge.y_min[1] for edge in edges])
    y_max = max([edge.y_max[1] for edge in edges])


    active_edges = []
    horizontal = False

    ## find active edges for y == ymin
    for edge in edges:
        # found edge
        if edge.y_min[1] == y_min:
            # active edge is horizontal
            if edge.m == 0:
                horizontal = True
            else:
                edge.active = True
                active_edges.append(edge)

    # paint starting point
    if not horizontal:
        updatedcanvas[y_min, active_edges[0].y_min[0]] = flat_color


    ## find border points
    # a border point is: xk, mk, on which edge
    border_points = [[active_edges[0].y_min[0], active_edges[0].m, \
                      active_edges[0].ordinal], \
                     [active_edges[1].y_min[0], active_edges[1].m, \
                      active_edges[1].ordinal]]


    ### scanlines
    for y in range(y_min, y_max + 1):
        border_points = sorted(border_points, key=lambda x: x[0])

        ## scan x between border points
        for x in range(math.floor(border_points[0][0] + 0.5), \
                       math.floor(border_points[1][0] + 0.5) + 1):
            # draw pixel
            # reverse due to how it is rendered by imshow later
            updatedcanvas[y, x] = flat_color


        ## skip last active edges and border points
        if y == y_max:
            break

        ## refresh active edges
        # add any new ones
        for edge in edges:
            if edge.y_min[1] == y + 1:
                edge.active = True
                active_edges.append(edge)

        # remove any old ones
        temp = []
        for i, active_edge in enumerate(active_edges):
            active_edge.active = False
            if active_edge.y_max[1] != y:
                active_edge.active = True
                temp.append(active_edge)
        active_edges = temp


        ## refresh border points
        # remove old points
        temp = []
        for point in border_points:
            if edges[point[2]].active:
                temp.append(point)
        border_points = temp

        # add 1 / m to previous points
        for point in border_points:
            point[0] = point[0] + 1 / point[1]

        # add points of new edge with ykmin == y + 1
        if active_edges[-1].y_min[1] == y + 1:
            border_points.append([active_edges[-1].y_min[0], \
                                  active_edges[-1].m, active_edges[-1].ordinal])


        # there is an edge case when we have 3 active edges
        # and we get three border points, 2 with the same xk
        if len(border_points) == 3:
            if math.floor(border_points[0][0] + 0.5) == \
                math.floor(border_points[2][0] + 0.5):
                for i, edge in enumerate(active_edges):
                    if edge.ordinal == border_points[0][2]:
                        del active_edges[i]
                        break
                del border_points[0]
            elif math.floor(border_points[1][0] + 0.5) == \
                math.floor(border_points[2][0] + 0.5):
                for i, edge in enumerate(active_edges):
                    if edge.ordinal == border_points[1][2]:
                        del active_edges[i]
                        break
                del border_points[1]


        ## last edge horizontal, fix border points and active edges
        temp = []
        flag = False
        for edge in active_edges:
            if edge.m == 0:
                border_points = [[edge.y_min[0], 0, edge.ordinal],\
                                 [edge.y_max[0], 0, edge.ordinal]]
                if not flag:
                    for edge in active_edges:
                        if edge.y_min[1] == y + 1:
                            temp.append(edge)
                            flag = True
        if flag:
            active_edges = temp


    return updatedcanvas

def Gourauds(canvas, vertices, vcolors):
    updatedcanvas = canvas

    ## save edges
    edges = [Edge() for _ in range(3)]
    for i in range(3):
        if i == 2:
            edges[i] = Edge(i, np.array([vertices[(i + 1) % 3, :], \
                                         vertices[i, :]]))
        else:
            edges[i] = Edge(i, np.array([vertices[i, :], \
                                         vertices[(i + 1) % 3, :]]))

    ## find overall min and max
    y_min = min([edge.y_min[1] for edge in edges])
    y_max = max([edge.y_max[1] for edge in edges])


    active_edges = []
    horizontal = False

    ## find active edges for y == ymin
    for edge in edges:
        # found edge
        if edge.y_min[1] == y_min:
            # active edge is horizontal
            if edge.m == 0:
                horizontal = True
            else:
                edge.active = True
                active_edges.append(edge)

    # paint starting point
    if not horizontal:
        for i in range(len(vertices)):
            if vertices[i, 1] == y_min:
                updatedcanvas[y_min, active_edges[0].y_min[0]] = vcolors[i, :]


    ## find border points
    # a border point is: xk, mk, on which edge
    border_points = [[active_edges[0].y_min[0], active_edges[0].m, \
                      active_edges[0].ordinal], \
                     [active_edges[1].y_min[0], active_edges[1].m, \
                      active_edges[1].ordinal]]


    ### scanlines
    for y in range(y_min, y_max + 1):
        border_points = sorted(border_points, key=lambda x: x[0])

        ## first color interpolation
        #  find color on each active edge
        for i, edge in enumerate(active_edges):
            if edge.ordinal == border_points[0][2]:
                edge_A = i
            elif edge.ordinal == border_points[1][2]:
                edge_B = i

        color_A = interpolate_vectors(active_edges[edge_A].vertices[0, :], \
                                      active_edges[edge_A].vertices[1, :], \
                                      vcolors[active_edges[edge_A].ordinal], \
                                      vcolors[(active_edges[edge_A].ordinal + 1) % 3], \
                                      y, 2)
        color_B = interpolate_vectors(active_edges[edge_B].vertices[0, :], \
                                      active_edges[edge_B].vertices[1, :], \
                                      vcolors[active_edges[edge_B].ordinal], \
                                      vcolors[(active_edges[edge_B].ordinal + 1) % 3], \
                                      y, 2)

        ## scan x between border points
        for x in range(math.floor(border_points[0][0] + 0.5), \
                       math.floor(border_points[1][0] + 0.5) + 1):
            # draw pixel
            # reverse due to how it is rendered by imshow later
            updatedcanvas[y, x] = interpolate_vectors(np.array([border_points[0][0], y]), \
                                                      np.array([border_points[1][0], y]), \
                                                      color_A, color_B, x, 1)


        ## skip last active edges and border points
        if y == y_max:
            break

        ## refresh active edges
        # add any new ones
        for edge in edges:
            if edge.y_min[1] == y + 1:
                edge.active = True
                active_edges.append(edge)

        # remove any old ones
        temp = []
        for i, active_edge in enumerate(active_edges):
            active_edge.active = False
            if active_edge.y_max[1] != y:
                active_edge.active = True
                temp.append(active_edge)
        active_edges = temp


        ## refresh border points
        # remove old points
        temp = []
        for point in border_points:
            if edges[point[2]].active:
                temp.append(point)
        border_points = temp

        # add 1 / m to previous points
        for point in border_points:
            point[0] = point[0] + 1 / point[1]

        # add points of new edge with ykmin == y + 1
        if active_edges[-1].y_min[1] == y + 1:
            border_points.append([active_edges[-1].y_min[0], \
                                  active_edges[-1].m, active_edges[-1].ordinal])

        # there is an edge case when we have 3 active edges
        # and we get three border points, 2 with the same xk
        if len(border_points) == 3:
            if math.floor(border_points[0][0] + 0.5) == \
                math.floor(border_points[2][0] + 0.5):
                for i, edge in enumerate(active_edges):
                    if edge.ordinal == border_points[0][2]:
                        del active_edges[i]
                        break
                del border_points[0]
            elif math.floor(border_points[1][0] + 0.5) == \
                math.floor(border_points[2][0] + 0.5):
                for i, edge in enumerate(active_edges):
                    if edge.ordinal == border_points[1][2]:
                        del active_edges[i]
                        break
                del border_points[1]


        ## last edge horizontal, fix border points and active edges
        temp = []
        flag = False
        for edge in active_edges:
            if edge.m == 0:
                border_points = [[edge.y_min[0], 0, edge.ordinal],\
                                 [edge.y_max[0], 0, edge.ordinal]]
                if not flag:
                    for edge in active_edges:
                        if edge.y_min[1] == y + 1:
                            temp.append(edge)
                            flag = True
        if flag:
            active_edges = temp


    return updatedcanvas