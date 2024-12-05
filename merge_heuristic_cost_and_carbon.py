from Input_paramters import x_g_int, y_g_int, second_res
from general_tool_functions import load_dict

heuristic_cost = load_dict('h_cost.json')
heuristic_carbon = load_dict('h_carbon.json')
h_cost_carbon = {}
print(len(heuristic_cost), len(heuristic_carbon))
for i in heuristic_carbon:
    if i not in heuristic_cost:
        continue
    h_cost_carbon[eval(i)] = [heuristic_cost[i], heuristic_carbon[i]]
print(len(h_cost_carbon))
H_COST_CARBON = {}
X_NEW_ORIGIN, Y_NEW_ORIGIN = x_g_int % second_res, y_g_int % second_res
for i in h_cost_carbon:
    (x, y, z) = i
    sll, sul, slu = (x, y, z), (x+second_res, y, z), (x, y+second_res, z)
    heuristic_sll, heuristic_sul, heuristic_slu = h_cost_carbon.get(sll), h_cost_carbon.get(sul), h_cost_carbon.get(slu)
    if None in (heuristic_sll, heuristic_sul, heuristic_slu):
        continue
    new_index = (int((x-X_NEW_ORIGIN)/second_res), int((y-Y_NEW_ORIGIN)/second_res), z)
    H_COST_CARBON[new_index] = heuristic_sll + heuristic_sul + heuristic_slu
print(len(H_COST_CARBON))