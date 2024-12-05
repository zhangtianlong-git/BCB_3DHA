import time
import json
import heapq
import matplotlib.pyplot as plt
import numpy as np
from get_explore_cost_and_carbon import OTHER_COST_CARBON, get_cost_and_tunnel_info
from GIS_DATA.House_table import house_info_dict
from GIS_DATA.Exploration_area import exploration_area_dict
from Input_paramters import x_s_int, y_s_int, x_g_int, y_g_int, z_s, z_g, terrain, max_bridge_height, max_tunnel_deepth, MAX_GRADIENT, MAX_NEAR_GRADIENT, res, second_res, zres_in_astar

z_res = zres_in_astar
[house_unit_cost, house_unit_carbon] = OTHER_COST_CARBON["house_cost_carbon"]

z_itervals = int(MAX_GRADIENT * second_res // z_res)
delta_z_list = list(np.array(range(-z_itervals, z_itervals+1))*z_res)
max_near_delta_z = int(MAX_NEAR_GRADIENT * second_res)

min_seq_len = 600 / res  # Minimum continuous straight line length; values with excessively large radii are treated the same as continuous slope lengths
min_seq_slope = 600 / res  # Minimum continuous slope length

motion = [
        [1, 0, 1],
        [0, 1, 1],
        [-1, 0, 1],
        [0, -1, 1],
        [-1, -1, 1.414],
        [-1, 1, 1.414],
        [1, -1, 1.414],
        [1, 1, 1.414],
    ]


class Node:
    def __init__(self, x, y, cost, pind, z=0, is_start=False, line_type=None, seq_len=0,
        seq_slope=0, delta_z=None, total_len=0, seq_tunnul=0, seq_bri=0, carbon=0, high_bridge=0,
        structure_type=None, earthwork=0, water=0, house_set=set(), total_house=0):
        self.x = x
        self.y = y
        self.cost = cost
        self.pind = pind
        self.z = z
        self.is_start = is_start
        self.line_type = line_type  # Exploration types, such as [1, 0, 1], [1, 1, 1.414], etc
        self.seq_len = seq_len
        self.seq_slope = seq_slope
        self.delta_z = delta_z
        self.total_len = total_len
        self.seq_tunnul = seq_tunnul
        self.carbon = carbon
        self.structure_type = structure_type  # # "T" for tunnel, "S" for subgrade, and "B" for bridge.
        self.earthwork = earthwork
        self.water = water
        self.house_set = house_set
        self.total_house = total_house
        self.high_bridge = high_bridge
        self.seq_bri = seq_bri
        self.pe = self.get_pe()
    
    def get_pe(self):
        lt, dz = self.line_type, self.delta_z
        pe = []
        if self.is_start:
            for i in motion:
                for j in delta_z_list:
                    pe.append([i, j])
            return pe
        if self.seq_len < min_seq_len and self.seq_slope < min_seq_slope:
            pe.append([lt, dz])
        elif self.seq_len >= min_seq_len and self.seq_slope < min_seq_slope:
            for i in motion:
                # if i[0] == -lt[0] and i[1] == -lt[1]:  # Backward exploration is not allowed
                if abs(i[0] + lt[0]) + abs(i[1] + lt[1]) < 2:  # Backward exploration is not allowed
                    continue
                pe.append([i, dz])
        elif self.seq_len < min_seq_len and self.seq_slope >= min_seq_slope:
            for j in delta_z_list:
                if abs(j-dz)>max_near_delta_z:  # Maximum adjacent slope difference
                    continue
                pe.append([lt, j])
        elif self.seq_len >= min_seq_len and self.seq_slope >= min_seq_slope:
            for i in motion:
                # if i[0] == -lt[0] and i[1] == -lt[1]:  # Backward exploration is not allowed
                if abs(i[0] + lt[0]) + abs(i[1] + lt[1]) < 2:  # Backward exploration is not allowed
                    continue
                for j in delta_z_list:
                    if abs(j-dz)>max_near_delta_z:  # Maximum adjacent slope difference
                        continue
                    pe.append([i, j])
        return pe


def get_neighbors(current):
    pe = current.pe
    if pe:
        x_old, y_old, z_old, lt, dz = current.x, current.y, current.z, current.line_type, current.delta_z
        seq_tun_old, struc_t_old, house_set_old = current.seq_tunnul, current.structure_type, current.house_set
        high_bridge_old, seq_bri_old = current.high_bridge, current.seq_bri
        
        tmp_node, nu_back, xy_set = current.pind, 20, []  # Prevent the occurrence of spiral-shaped lines
        nu_back = 2 if (y_old > y_s_int - 50) else 20
        for nu in range(nu_back):
            if tmp_node is None:
                break
            xy_set += [(tmp_node.x, tmp_node.y, current.total_len-tmp_node.total_len)]
            tmp_node = tmp_node.pind
        """-------The above refers to the preprocessing work---------"""
        for i in pe:
            x_list, y_list, z_list, z_minus_t, house_list = [], [], [], [], []
            x_d, y_d, l_d, d_z = i[0][0], i[0][1], i[0][2], i[1]  # The structure of i is , e.g., [[1, 1, 1.414], 6].
            arc_len = l_d * second_res
            # Out-of-bounds check, must be within the exploration area
            x_bound, y_bound = x_old + x_d * second_res, y_old + y_d * second_res
            if (x_bound, y_bound) not in exploration_area_dict:
                continue
            
            is_back = False  # Prevent the occurrence of spiral-shaped lines
            for xyd in xy_set:
                ds = abs(x_bound-xyd[0])+abs(y_bound-xyd[1])
                if ds <= xyd[2]/2+second_res:
                    is_back = True
                    break
            if is_back:
                continue
            height_forbiden = False  # Maximum bridge height and tunnel depth
            for iter in range(1, second_res+1):
                tmp_x, tmp_y, tmp_z = x_old + iter * x_d, y_old + iter * y_d, z_old + iter / second_res * d_z
                tmp_z_m_t = tmp_z - terrain[tmp_x][tmp_y]
                if tmp_z_m_t > -15:  # Houses are only counted for non-tunnel sections
                    house_list += house_info_dict.get((tmp_x*6, tmp_y*6), [])
                height_forbiden = height_forbiden if (max_bridge_height > tmp_z_m_t > max_tunnel_deepth) else True
                x_list.append(tmp_x), y_list.append(tmp_y), z_list.append(tmp_z)
                z_minus_t.append(tmp_z_m_t)
            if height_forbiden:
                continue
            house_set = set(house_list) - house_set_old
            house_area = sum(house_set)
            house_cost, house_carbon = house_unit_cost*house_area, house_unit_carbon*house_area
            # Maximum gradient constraint
            if abs((z_s-z_list[-1])/((x_s_int-x_list[-1])**2+(y_s_int-y_list[-1])**2)**0.5) > 3*MAX_GRADIENT:
                continue
            # This is where the cost and carbon emissions are calculated
            out = get_cost_and_tunnel_info(z_minus_t, struc_t_old, seq_tun_old, seq_bri_old, high_bridge_old, XY_RES_2=l_d)
            if out is None:  # The maximum tunnel length or super-elevated bridge length does not meet the requirements
                continue
            [add_cost, add_carbon, struc_t_new, seq_tun_new, seq_bri_new, high_bri_new, earthwork_v, water_v] = out
            seqLen, seqSlope = arc_len, arc_len
            # Update the length of the continuous straight line
            if lt:  # At the starting point, lt is None, so it is checked first
                if lt[0] == x_d and lt[1] == y_d:
                    seqLen = current.seq_len + arc_len
            # Update the length of the continuous slope.
            if dz == d_z:  # At the starting point, lt is None, so it is checked first
                seqSlope = current.seq_slope + arc_len
            # Update cost or carbon
            new_cost = current.cost + add_carbon + house_carbon
            new_carbon = current.carbon + add_cost + house_cost

            node = Node(x_list[-1], y_list[-1], new_cost, current, z=z_list[-1], structure_type=struc_t_new, house_set=house_set,
            line_type=i[0], seq_len=seqLen, seq_slope=seqSlope, delta_z=d_z, seq_tunnul=seq_tun_new, high_bridge=high_bri_new, carbon=new_carbon,
            seq_bri=seq_bri_new,
            total_len=current.total_len + arc_len,
            earthwork=current.earthwork + earthwork_v,
            water=current.water + water_v,
            total_house=current.total_house + house_area)

            yield node


def calc_final_path(ngoal):
    # generate final alignment
    n = ngoal
    rx, ry, rz, tz, lc = [n.x], [n.y], [n.z], [terrain[n.x][n.y]], [0]
    print("total cost is {}".format(ngoal.cost))
    print("total carbon is {}".format(ngoal.carbon))
    print("total earthwork is {}".format(ngoal.earthwork))
    print("total water is {}".format(ngoal.water))
    print("total house is {}".format(ngoal.total_house))
    print("total len is {}".format(ngoal.total_len*res))
    print('house set is below:')
    print(ngoal.house_set)
    while n.pind is not None:
        x_old, y_old, z_old, x_d, y_d, l_d, d_z = rx[-1], ry[-1], rz[-1], -n.line_type[0], -n.line_type[1], n.line_type[2], -n.delta_z
        for iter in range(1,second_res+1):
            tmp_x, tmp_y, tmp_z = x_old + iter * x_d, y_old + iter * y_d, z_old + iter / second_res * d_z
            tmp_lc = lc[-1] + l_d
            tmp_t = terrain[tmp_x][tmp_y]
            rx.append(tmp_x), ry.append(tmp_y), rz.append(tmp_z), tz.append(tmp_t), lc.append(tmp_lc)
        n = n.pind

    return rx, ry, rz, tz, lc


def dp_planning( gx, gy):
    start_time_1 = time.time()

    # Note that the structure_type needs to be determined in advance
    ngoal = Node(round(gx), round(gy), 0.0, None, z=z_g, is_start=True, structure_type='S')

    openset, closedset, outputset = dict(), dict(), dict()
    openset[(ngoal.x, ngoal.y, int(ngoal.z // z_res))] = ngoal
    pq = []
    pq.append((0, (ngoal.x, ngoal.y, int(ngoal.z // z_res))))

    while 1:
        if not pq:
            break
        _, c_id = heapq.heappop(pq)
        if c_id in openset:
            current = openset[c_id]
            closedset[c_id] = current
            outputset[str(c_id)] = current.cost
            openset.pop(c_id)
        else:
            continue
        ## show graph
        if len(closedset.keys()) % 500 == 0:
            plt.plot(current.x, current.y, "xc")
        if current.high_bridge == 390:
            plt.plot(current.x, current.y, "xg")
        if len(closedset.keys()) % 1000 == 0:
            plt.pause(0.001)

        # expand search grid based on motion model
        for neighbor in get_neighbors(current):
            neighbor_index = (neighbor.x, neighbor.y, int(neighbor.z // z_res))
            if neighbor_index in closedset:
                continue
            if neighbor_index not in openset or openset[neighbor_index].cost > neighbor.cost:
                heapq.heappush(pq, (neighbor.cost, neighbor_index))
                openset[neighbor_index] = neighbor

    print(len(closedset.keys()))
    end_time_1 = time.time()
    print('final time comsuption is {}'.format(end_time_1-start_time_1))
    tmp_xind, tmp_yind = (x_s_int-x_g_int)//second_res*second_res+x_g_int, (y_s_int-y_g_int)//second_res*second_res+y_g_int
    t_node = Node(tmp_xind, tmp_yind, 0.0, None, z=z_s)
    if (t_node.x, t_node.y, int(t_node.z // z_res)) in closedset:
        tmp_nstart = closedset[(t_node.x, t_node.y, int(t_node.z // z_res))]
    else:
        raise
    rx, ry, rz, tz, lc = calc_final_path(tmp_nstart)
    
    plt.plot(rx, ry, ".-r")
    plt.figure()
    plt.plot(lc, rz, "--r")
    plt.plot(lc, tz, "-k")
    plt.show()
    save_dict(outputset, 'h_carbon.json')


    return rx, ry, closedset, rz, tz


def save_dict(dictionary, file_path):
    with open(file_path, 'w') as file:
        json.dump(dictionary, file)


def main():
    print(__file__ + " start!!")

    sx = x_s_int  # [100m]
    sy = y_s_int  # [100m]
    gx = x_g_int  # [100m]
    gy = y_g_int  # [100m]

    ox, oy = [], []
    (xw, yw) = terrain.shape
    for i in range(xw + 1):
        ox.append(i), oy.append(0), ox.append(i), oy.append(yw)
    for i in range(yw + 1):
        ox.append(0), oy.append(i), ox.append(xw), oy.append(i)

    plt.plot(ox, oy, ".k")
    plt.plot(sx, sy, "xr")
    plt.plot(gx, gy, "xb")
    plt.grid(True)
    plt.axis("equal")

    dp_planning(gx, gy)


if __name__ == "__main__":
    main()
