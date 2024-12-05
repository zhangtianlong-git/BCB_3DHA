from math import cos, sin, pi
import numpy as np
from Input_paramters import LEN_SPIRAL, EXPLORE_RES, RADIUS
# Coordinate calculation cache to avoid redundant calculations
distances_zy, distances_tr = np.array(range(1, EXPLORE_RES + 1)), np.array(range(1, LEN_SPIRAL + 1))
buffer_zy, buffer_tr_1, buffer_tr_2 = {}, {}, {}
for r in RADIUS:
    """Cache for calculating parameters of straight lines and circular curves"""
    theta = (distances_zy / r + pi) % (2 * pi) - pi
    tmp_x = r * np.sin(theta)
    tmp_y = r - r * np.cos(theta)
    new_r = np.sqrt(np.square(tmp_x) + np.square(tmp_y))
    new_arctan = np.arctan(tmp_y / tmp_x)
    buffer_zy[r] = (theta, new_r, new_arctan)
    """Cache for calculating transition curve parameters"""
    """----Straight-to-circular transition curve----"""
    ls, l = LEN_SPIRAL, distances_tr
    c = l * (1 - (l**4) / (90 * r**2 * ls**2) + (l**8) / (22680 * r**4 * ls**4))  # Chord length
    theta = ((l**2)/ (r * ls)* (1 / 6- (l**4) / (2835 * r**2 * ls**2)- (l**8) / (467775 * r**4 * ls**4)))  # Chord tangent angle
    beta = (l**2) / (2 * r * ls)  # 切线角
    buffer_tr_1[r] = (c, theta, beta)
    """----Circular-to-straight transition curve----"""
    c_f, theta_f, beta_f = c[-1], theta[-1], beta[-1]
    ls, l = LEN_SPIRAL, LEN_SPIRAL - distances_tr
    c = l * (1 - (l**4) / (90 * r**2 * ls**2) + (l**8) / (22680 * r**4 * ls**4))  # Chord length
    theta = ((l**2)/ (r * ls)* (1 / 6- (l**4) / (2835 * r**2 * ls**2)- (l**8) / (467775 * r**4 * ls**4)))  # Chord tangent angle
    buffer_tr_2[r] = (c_f, theta_f, beta_f, c, theta)


def pi_2_pi(angle):
    """Convert the angle to the range between -π and π"""
    return (angle + pi) % (2 * pi) - pi


def z_y_move_list(x, y, z, theta_xy, gradient_z, radi):
    if radi is not None:
        (theta, new_r, new_arctan) = buffer_zy[radi]
        theta0 = theta_xy + new_arctan
        x += new_r * np.cos(theta0)
        y += new_r * np.sin(theta0)
        z += distances_zy * gradient_z
        theta_xy = (theta_xy + theta[-1] + pi) % (2 * pi) - pi
    else:
        x += distances_zy * cos(theta_xy)
        y += distances_zy * sin(theta_xy)
        z += distances_zy * gradient_z
        theta_xy = (theta_xy + pi) % (2 * pi) - pi
    return x, y, z, theta_xy, gradient_z


def spr_move1_list(x, y, z, theta_xy, gradient_z, radi):
    (c, theta, beta) = buffer_tr_1[radi]
    theta0 = theta_xy + theta
    x += c * np.cos(theta0)
    y += c * np.sin(theta0)
    z += distances_tr * gradient_z
    theta_xy = (theta_xy + beta[-1] + pi) % (2 * pi) - pi
    return x, y, z, theta_xy, gradient_z


def spr_move2_list(x, y, z, theta_xy, gradient_z, radi):
    (c_f, theta_f, beta_f, c, theta) = buffer_tr_2[radi]
    theta0 = theta_xy + (beta_f - theta_f)
    x_final = x + c_f * cos(theta0)
    y_final = y + c_f * sin(theta0)
    theta_xy_final = (theta_xy + beta_f + pi) % (2 * pi) - pi

    theta0 = theta_xy_final + pi - theta
    x = x_final + c * np.cos(theta0)
    y = y_final + c * np.sin(theta0)
    z = z + distances_tr * gradient_z

    return x, y, z, theta_xy_final, gradient_z


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    r_index = -1
    ox, oy, oz, ot, og = spr_move1_list(0, 0, 0, 0, 0.5, RADIUS[r_index])
    ax.scatter(ox, oy, oz, c="g", marker="o")
    ox, oy, oz, ot, og = z_y_move_list(ox[-1], oy[-1], oz[-1], ot, og, RADIUS[r_index])
    ax.scatter(ox, oy, oz, c="r", marker="o")
    ox, oy, oz, ot, og = spr_move2_list(ox[-1], oy[-1], oz[-1], ot, og, RADIUS[r_index])
    ax.scatter(ox, oy, oz, c="b", marker="o")
    plt.axis('equal')
    plt.show()