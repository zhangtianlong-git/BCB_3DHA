file_path = "GIS_DATA/House_table.txt"  
xll, yll = 432000, 3939700  # Geographic coordinate offset

house_info_dict = {}

# The resolution of the building table is 5 meters
with open(file_path, 'r') as file:
    for line in file:
        data = line.strip().split(',')
        key = (int((float(data[0])-2.5-xll)/5), int((float(data[1])-2.5-yll)/5))
        value = [round(float(data[2]), 1)] 
        if key in house_info_dict:
            house_info_dict[key] += value
        else:
            house_info_dict[key] = value

print('House Table Done!!')