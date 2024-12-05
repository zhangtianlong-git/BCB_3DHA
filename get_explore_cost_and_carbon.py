import json
import numpy as np
from general_tool_functions import  load_dict


COST_AND_CARBON_TMP, COST_AND_CARBON = load_dict("COST_AND_CARBON.json"), {}
for i in COST_AND_CARBON_TMP:
    COST_AND_CARBON[int(i)] = COST_AND_CARBON_TMP[i]
TYPE_CHANGE_COST = load_dict("TYPE_CHANGE_COST.json")
OTHER_COST_CARBON = load_dict("OTHER_COST_CARBON.json")
tunnel_unit_length_add_cost_10000 = 30000
bridge_unit_length_add_cost_500 = 16000
COST_ADD_10000 = tunnel_unit_length_add_cost_10000 * 10000
COST_ADD_500 = bridge_unit_length_add_cost_500 * 500


def get_cost_and_tunnel_info(h_diffs, last_type, sequential_tunnel, sequential_bri, high_bridge_len, XY_RES_1=30, XY_RES_2=1):
    """——————Initialization——————"""
    step_len = XY_RES_1 * XY_RES_2
    tmp_type = last_type
    tunnel_length_new = sequential_tunnel
    type_change_count = {"T": 0, "S": 0, "B": 0}
    total_cost, total_carbon = 0, 0
    total_earthwork, total_water = 0, 0
    length_add_cost = 0  # Cost increase due to length
    high_bridge_length = high_bridge_len
    bri_length_new = sequential_bri
    for h_dif in h_diffs:
        """——————Cost and carbon emissions-related calculations——————"""
        h_index = int(h_dif)
        t, base_cost, base_carbon, earthwork, water = COST_AND_CARBON[h_index].values()
        total_earthwork, total_water = total_earthwork+earthwork, total_water + water
        total_cost += base_cost
        total_carbon += base_carbon
        """——————Additional length-related calculations——————"""
        if tunnel_length_new > 15000:  # Tunnel length exceeds the limit
            return None
        if bri_length_new > 1500:  # Bridge length exceeds the limit
            return None
        if tunnel_length_new >= 10000:
            if sequential_tunnel < 10000 and (tunnel_length_new-step_len) < 10000:
                length_add_cost += COST_ADD_10000
            total_cost += tunnel_unit_length_add_cost_10000
        if bri_length_new >= 500:
            if sequential_bri < 500 and (bri_length_new-step_len) < 500:
                length_add_cost += COST_ADD_500
            total_cost += bridge_unit_length_add_cost_500

        tunnel_length_new = (tunnel_length_new + step_len) if t == "T" else 0
        bri_length_new = (bri_length_new + step_len) if t == "B" else 0

        # Continuous super-elevated bridge length
        if h_dif > 100:
            high_bridge_length += step_len
        else:
            high_bridge_length = 0
        if high_bridge_length > 400:  # Super-elevated bridge length exceeds the limit
            return None
        """——————Update the alignment change status——————"""
        if tmp_type != t:  # Record the points where the alignment changes; both the line types before and after the change need to be counted
            type_change_count[tmp_type] += 1
            type_change_count[t] += 1
            tmp_type = t

    """——————Cost increment caused by alignment changes——————"""
    type_change_add_cost = (
        TYPE_CHANGE_COST["T"] * type_change_count["T"]
        + TYPE_CHANGE_COST["B"] * type_change_count["B"]
    )

    total_cost = total_cost * step_len + type_change_add_cost + length_add_cost
    total_carbon = total_carbon * step_len
    out = [total_cost, total_carbon, t, tunnel_length_new, bri_length_new, high_bridge_length, total_earthwork*step_len, total_water*step_len]
    return out


if __name__ == "__main__":
    """——————Input——————"""
    last_type, sequential_tunnel = "T", 2970
    h_diffs = np.array([-105.45, -55.2, -45.5, -15.4, -5.3, 5.5, 5.1, 25.7, 35.1, -35])
    print(get_cost_and_tunnel_info(h_diffs, last_type, sequential_tunnel, 0, 0))