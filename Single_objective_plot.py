from general_tool_functions import load_dict
import matplotlib.pyplot as plt
from GIS_DATA.House_table import house_info_dict
import numpy as np
from get_explore_cost_and_carbon import get_cost_and_tunnel_info, OTHER_COST_CARBON
[house_unit_cost, house_unit_carbon] = OTHER_COST_CARBON["house_cost_carbon"] 


def plot_an_alignment(alignment_info):
    [xs, ys, zs, ts, ss, bpd_ss, bpd_zs, pix, piy, pir] = alignment_info
    plt.figure(figsize=(7, 7)), plt.axis('equal'), plt.plot(xs, ys, '-r')
    if pix is not None:
        plt.plot(pix, piy, '--y'), plt.plot(pix, piy, 'xb')
    plt.figure(figsize=(20, 4)), plt.plot(ss, ts, '-k'), plt.plot(ss, zs, '--r'), plt.plot(bpd_ss, bpd_zs, '^g')
    plt.show()

def plot_alignments(alignment_info, fig_aligns, colors):
    [xs, ys] = alignment_info
    plt.figure(fig_aligns.number)
    plt.axis('equal'), plt.plot(xs, ys, color=colors, linestyle='-')

def get_final_alignment_info(alignment_info):
    print("--------------The recalculated results for important parameters such as route cost are as follows-------------------")
    [xs, ys, zs, ts, ss] = alignment_info
    h_diffs = np.array(zs) - np.array(ts)
    """Recalculation of tunnel and bridge lengths"""
    types = np.array(len(h_diffs)*['S'])
    types[h_diffs > 8] = 'B'
    types[h_diffs < -15] = 'T'
    counts, last_type = {'S':[], 'B':[], 'T':[]}, None
    for t in types:
        if last_type == t:
            counts[t][-1] += 1
        else:
            counts[t] += [1]
        last_type = t
    tunnuls, bridges = np.array(counts['T']), np.array(counts['B'])
    # Note that only counts greater than 1 are output here, but all counts are considered in the cost calculation.
    tunnuls_valid, bridges_valid = tunnuls[tunnuls>1], bridges[bridges>1]  
    tunnul_num, tunnul_len = len(tunnuls_valid), sum(tunnuls_valid)*30
    bri_num, bri_len = len(bridges_valid), sum(bridges_valid)*30
    print('Tunnel number:{}，Length:{}, Bridge number:{}，Length:{}'.format(tunnul_num, tunnul_len, bri_num, bri_len))
    """Recalculation of land area"""
    h_diffs_Sub_and_Bri = h_diffs[h_diffs>=-15]
    h_diffs_Sub = h_diffs_Sub_and_Bri[h_diffs_Sub_and_Bri<=8]
    right_of_way_area = (sum(abs(h_diffs_Sub)*1.75*2)+len(h_diffs_Sub_and_Bri)*(24+10))*30
    print('Land area：', right_of_way_area)
    """Recalculation of alignment cost (excluding house demolition)"""
    output = get_cost_and_tunnel_info(h_diffs[:-30*2], 'S', 0, 0, 0)
    [t_cost, t_carbon, _, _, _, _, t_earthwork, t_water] = output
    print('Alignment length:{}，cost:{}，carbon:{}，earthwork:{}，water:{}'.format(ss[-1], t_cost, t_carbon, t_earthwork, t_water))
    """Recalculation of route cost (including house demolition)"""
    iter, house_list, old_house_set, t_house = 0, [], set(), 0
    for tx, ty, hd in zip(xs, ys, h_diffs):
        if iter % 20 == 0:  # Groups of twenty points, approximately corresponding to the process in the exploration phase, do not affect the final calculation results
            old_house_set = set(house_list) - old_house_set
            t_house += sum(old_house_set)
            house_list = []
        if hd > -15:
            house_list += house_info_dict.get((int(tx*6), int(ty*6)), [])
        iter += 1
    old_house_set = set(house_list) - old_house_set
    t_house += sum(old_house_set)
    print("Demolition area (considering tunnels) is", t_house)
    iter, house_list, old_house_set, _t_house = 0, [], set(), 0
    for tx, ty, hd in zip(xs, ys, h_diffs):
        if iter % 20 == 0:  # Groups of twenty points, approximately corresponding to the process in the exploration phase, do not affect the final calculation results
            old_house_set = set(house_list) - old_house_set
            _t_house += sum(old_house_set)
            house_list = []
        house_list += house_info_dict.get((int(tx*6), int(ty*6)), [])
        iter += 1
    old_house_set = set(house_list) - old_house_set
    _t_house += sum(old_house_set)
    print("Demolition area (excluding tunnels) is", _t_house)
    house_cost, house_carbon = house_unit_cost*t_house, house_unit_carbon*t_house
    t_cost, t_carbon = t_cost + house_cost, t_carbon + house_carbon
    print('The final total cost considering the houses:{}，total carbon:{}'.format(t_cost, t_carbon))
    return t_cost, t_carbon


"""--------------------------------Input manual alignment and program-optimized alignment----------------------------------"""
mannual_alignment = load_dict('Mannual/Mannual_alignment.json')

als_1 = load_dict('Optimized_alignment-objective-1.json')
als_2 = load_dict('Optimized_alignment-objective-2.json')

code_alignments = {}

als_dics = [als_1, als_2]
indexs = range(len(als_dics))
for als_set, id in zip(als_dics, indexs):
    for key in als_set:
        code_alignments[int(key)+id*100] = als_set[key]
m_a_info = mannual_alignment['0']

"""------------------------Calculate the coordinates before station access based on the manual alignment---------------------------"""
ini_len, index = 3950 - 1520, int((3950 - 1520)/30)
m_xs, m_ys, m_zs, m_ts, m_ss, m_bpd_ss, m_bpd_zs, m_pi_x, m_pi_y, m_pi_r = m_a_info.values()
ini_xs, ini_ys, ini_zs, ini_ts, ini_ss = m_xs[:index], m_ys[:index], m_zs[:index], m_ts[:index], m_ss[:index]
ini_bpd_ss, ini_bpd_zs = [], []
for i in range(len(m_bpd_ss)):
    if m_bpd_ss[i] < index*30:
        ini_bpd_ss.append(m_bpd_ss[i]), ini_bpd_zs.append(m_bpd_zs[i])
    else:
        break


"""--------------------------------Program-optimized alignment calculations----------------------------------"""
fig_aligns, fig_para = plt.figure(figsize=(10, 6)), plt.figure()
plt.rcParams.update({'font.size': 15, 'font.family': 'Times New Roman'})
alignments_updated = {}
marks = ['^g', '^r', '^y', '^k', '^b']
for key in code_alignments:
    t_xs, t_ys, t_zs, t_ts, t_ss, t_bpd_ss, t_bpd_zs, t_pi_x, t_pi_y, t_pi_r = code_alignments[key].values()
    t_xs, t_ys, t_zs, t_ts = ini_xs + t_xs, ini_ys + t_ys, ini_zs + t_zs, ini_ts + t_ts
    t_ss = ini_ss + list(np.array(t_ss)+ini_len)
    t_bpd_ss = ini_bpd_ss + list(np.array(t_bpd_ss)+ini_len)
    t_bpd_zs = ini_bpd_zs + t_bpd_zs
    t_pi_x[0], t_pi_y[0] = ini_xs[0], ini_ys[0]
    alignments_updated[key] = [t_xs, t_ys, t_zs, t_ts, t_ss, t_bpd_ss, t_bpd_zs, t_pi_x, t_pi_y, t_pi_r]
    print('------------ID of the current alignment is {}--------------'.format(key))
    t_cost, t_carbon = get_final_alignment_info([t_xs, t_ys, t_zs, t_ts, t_ss])
    plot_alignments([t_xs, t_ys], fig_aligns, colors=np.random.rand(3,))
    plt.figure(fig_para.number), plt.plot(t_cost, t_carbon, marks[int(key/100)])

plt.show()

plot_an_alignment(alignments_updated[1])
plot_an_alignment(alignments_updated[101])