file_path = "GIS_DATA/Exploration_area.txt"
xll, yll = 432000, 3939700 # Geographic coordinate offset

# exploration_area_dict is used to store the horizontal grid coordinates of the exploreable area, with forbiden zones excluded
exploration_area_dict = set()

# The resolution of the DEM is 30 meters
with open(file_path, 'r') as file:
    for line in file:
        data = line.strip().split(',')
        key = (int((float(data[0])-15-xll)/30), int((float(data[1])-15-yll)/30))
        exploration_area_dict |= {key}

print('Exploration_area Table Done!!')