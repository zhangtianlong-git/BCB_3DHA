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


"""--------------------------------Input manual alignment and program-optimized alignment----------------------------------"""
manual_alignment = load_dict('Manual/Manual_alignment.json')

als_1 = load_dict('Optimized_alignment-objective-1.json')
als_2 = load_dict('Optimized_alignment-objective-2.json')

code_alignments = {}

als_dics = [als_1, als_2]
indexs = range(len(als_dics))
for als_set, id in zip(als_dics, indexs):
    for key in als_set:
        code_alignments[int(key)+id*100] = als_set[key]
m_a_info = manual_alignment['0']

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
fig_aligns= plt.figure(figsize=(10, 6))
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
    plot_alignments([t_xs, t_ys], fig_aligns, colors=np.random.rand(3,))

plt.show()

plot_an_alignment(alignments_updated[1])
plot_an_alignment(alignments_updated[101])