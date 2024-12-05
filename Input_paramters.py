import numpy as np
import math


"""输入约束和定义参数"""
res, ZRESO, second_res, zres_in_astar = 30, 2, 20, 2
xll, yll = 432000, 3939700
x_s, y_s = (465773.9176 - xll)/res, (3951729.3776 - yll)/res  # Initial starting point
x_g, y_g = (437870.8663 - xll)/res, (3943895.1365 - yll)/res  # Initial endpoint (also actual endpoint).
x_s, y_s = (465129.3399 - xll)/res, (3954072.3286 - yll)/res  # Actual starting point, considering the length of the station connection line

x_s_int, y_s_int = int(x_s), int(y_s)
x_g_int, y_g_int = int(x_g), int(y_g)
terrain = np.loadtxt("dem.txt")
x_width, y_width = terrain.shape[0]+2, terrain.shape[1]+2
z_s, z_g = 1389.027, 1123.940  # Initial elevation
z_s, z_g = 1401.077, 1123.940  # Actual elevation
start_angle = 105.382

max_bridge_height = 250
max_tunnel_deepth = -400  # This constraint is implemented in this case to align with the range in COST_AND_CARBON.json and is non-mandatory

MAX_GRADIENT = 0.013*res  # Maximum gradient value
MAX_NEAR_GRADIENT = 0.01*res
MIN_GRADIENT = 0.00*res  # Minimum gradient value
GRADIENT_Z_RESOLUTION = 0.002*res  # Gradient resolution
N_STEER = 30  # Maximum number of exploration directions
MIN_R = 1600  # Minimum curve radius, to be divided by the resolution (res) when calculating the radius later
MAX_R = 11000  # Maximum curve radius, to be divided by the resolution (res) when calculating the radius later.
LEN_SPIRAL = int(210/res)  # Transition curve length
EXPLORE_RES = int(300/res)  # Step length for exploring straight lines and circular curves
MIN_LEN_SLOPE = 1200/res  # Minimum slope length
MIN_LEN_CURV = 300/res  # Minimum curve length
MIN_LEN_TAN = 300/res  # Minimum straight line length
THETA_XY_RESOLUTION = np.deg2rad(10)  # Planar angle resolution
K_MIN = 15000/res/res  # Vertical curve radius
MAX_LEN_TAN = 10000/res  # Maximum straight line length
ZMAX = 800  # Maximum elevation difference
STOP_DIS_1 = MIN_R/res
STOP_DIS_2 = MIN_R/res/2

# Planar angle compensation value, to prevent negative values
THETA_XY_IND = round(math.pi / THETA_XY_RESOLUTION)
# Vertical slope compensation value, to prevent negative values
GRADIENT_Z_IND = round(MAX_GRADIENT / GRADIENT_Z_RESOLUTION)
# The number of line segments for the minimum curve length
MIN_SEG = MIN_LEN_CURV / EXPLORE_RES
# The number of line segments for the minimum straight length
MIN_SEG_T = MIN_LEN_TAN / EXPLORE_RES
# The number of line segments for slope
MIN_SEG_S = MIN_LEN_SLOPE / EXPLORE_RES
# Maximum turning angle, primarily used to determine the angle resolution
MAX_ANGLE_CHANGE = EXPLORE_RES / MIN_R
# All turning angles
ANGLES = list(np.linspace(-MAX_ANGLE_CHANGE, MAX_ANGLE_CHANGE, N_STEER))
# All exploration radii
RADIUS = EXPLORE_RES / np.linspace(-MAX_ANGLE_CHANGE, MAX_ANGLE_CHANGE, N_STEER)
RADIUS = RADIUS[abs(RADIUS) < MAX_R]
RADIUS = list(((RADIUS/100).round(0)) * 100 / res)
RADIUS = [800/res, -800/res] + RADIUS
# All gradients
GRADIENTS = np.linspace(
    -MAX_GRADIENT, MAX_GRADIENT, int(2 * MAX_GRADIENT / GRADIENT_Z_RESOLUTION + 1)
)

# Only used in Sinle_objective_BC_3DHA.py 
SINGLE_OBJECTIVE = 1  # '1' for single objective-1, and '1' for single objective-2