# Import necessary libraries
import folium
from Triangle import Triangle
from map_leds import leds
import math
import json
import datetime
import os

# Get user requirements
latitude = 51.7   #float(input("Enter the latitude of the center point: "))
longitude = -1.9  #float(input("Enter the longitude of the center point: "))
side_length = 3.4 #float(input("Enter the side length of the triangle in miles: "))
depth = 5 #int(input("Enter the depth of the hexagons: "))
hex_type = "flat_sides" #input("Enter the type of hexagon. (flat_top or flat_sides): ").strip().lower()
miles_per_degree_longitude = 45 #float(input("Enter the miles per degree longitude: "))


# Function to calculate the flat top hexagon
def generate_flat_top(latitude, longitude, side_length_miles, depth, miles_per_degree_longitude):
    """
    Generates a list of Triangle objects based on a starting point, side length, and depth.

    Args:
        latitude (float): Latitude of the starting point.
        longitude (float): Longitude of the starting point.
        side_length_miles (float): Side length of the equilateral triangles in miles.
        depth (int): Number of layers of triangles to generate.

    Returns:
        list: A list of Triangle objects.
    """

    target_depth = depth  # Store the target depth
    current_depth = 0  # Initialize the current depth
    triangles = []  # List to store Triangle objects
    triangle_name = 1  # Initialize triangle name
    leds = 0  # Initialize LED counter
    current_points = [[latitude, longitude]]  # Starting point
    next_points = []  # List to store points for the next layer

    #miles_per_degree_longitude = 45.0
    miles_per_degree_latitude = 69.0

    longitude_diff = side_length_miles / miles_per_degree_longitude
    height_miles = (side_length_miles * math.sqrt(3)) / 2
    latitude_diff = height_miles / miles_per_degree_latitude

    def calculate_triangle_center(coords):
        """Calculates the center (centroid) of a triangle."""
        lat_sum = sum(coord[0] for coord in coords)
        long_sum = sum(coord[1] for coord in coords)
        return [lat_sum / 3, long_sum / 3]

    def generate_single_triangle(lat, long, direction):
        """Generates coordinates for a single triangle based on direction."""
        if direction == "nw":
            bottom_left_lat = lat
            bottom_left_long = long - longitude_diff
            top_lat = lat + latitude_diff
            top_long = long - (longitude_diff / 2)
            return [[bottom_left_lat, bottom_left_long], [lat, long], [top_lat, top_long]]
        elif direction == "n":
            top_left_lat = lat + latitude_diff
            top_left_long = long - (longitude_diff / 2)
            top_right_lat = lat + latitude_diff
            top_right_long = long + (longitude_diff / 2)
            return [[top_left_lat, top_left_long], [top_right_lat, top_right_long], [lat, long]]
        elif direction == "ne":
            bottom_right_lat = lat
            bottom_right_long = long + longitude_diff
            top_lat = lat + latitude_diff
            top_long = long + (longitude_diff / 2)
            return [[lat, long], [bottom_right_lat, bottom_right_long], [top_lat, top_long]]
        elif direction == "se":
            top_right_lat = lat
            top_right_long = long + longitude_diff
            bottom_lat = lat - latitude_diff
            bottom_long = long + (longitude_diff / 2)
            return [[lat, long], [top_right_lat, top_right_long], [bottom_lat, bottom_long]]
        elif direction == "s":
            bottom_left_lat = lat - latitude_diff
            bottom_left_long = long - (longitude_diff / 2)
            bottom_right_lat = lat - latitude_diff
            bottom_right_long = long + (longitude_diff / 2)
            return [[bottom_left_lat, bottom_left_long], [bottom_right_lat, bottom_right_long], [lat, long]]
        elif direction == "sw":
            top_left_lat = lat
            top_left_long = long - longitude_diff
            bottom_lat = lat - latitude_diff
            bottom_long = long - (longitude_diff / 2)
            return [[top_left_lat, top_left_long], [lat, long], [bottom_lat, bottom_long]]
        else:
            return None

    def create_triangle_if_unique(coords, center):
        """Creates a Triangle object if its center is unique (rounded comparison)."""
        center_exists = False
        rounded_center = [round(center[0], 6), round(center[1], 6)]

        for existing_triangle in triangles:
            existing_rounded_center = [round(existing_triangle.get_centre()[0], 6), round(existing_triangle.get_centre()[1], 6)]
            if existing_rounded_center == rounded_center:
                center_exists = True
                break

        if not center_exists:
            nonlocal triangle_name, leds
            triangle = Triangle(triangle_name, [leds + 1, leds + 2], coords, center)
            triangles.append(triangle)
            triangle_name += 1
            leds += 2

    while current_depth < target_depth:
        temp_points = [] #collect next points to avoid changing next_points during iteration.
        for current_point in current_points:
            lat, long = current_point

            # Generate and process each of the six triangles
            for direction in ["nw", "n", "ne", "se", "s", "sw"]:
                coords = generate_single_triangle(lat, long, direction)
                if coords:
                    center = calculate_triangle_center(coords)
                    create_triangle_if_unique(coords, center)
                    for coord in coords: #append all points from the triangle to the next point list.
                        if coord not in temp_points:
                            temp_points.append(coord)

        current_depth += 1
        current_points = temp_points
        next_points = [] #reset next points.

    return triangles

# Function to create flat sides hexagon
def generate_flat_sides(latitude, longitude, side_length_miles, depth, miles_per_degree_longitude):
    target_depth = depth  # Store the target depth
    current_depth = 0  # Initialize the current depth
    triangles = []  # List to store Triangle objects
    triangle_name = 1  # Initialize triangle name
    leds = 0  # Initialize LED counter
    current_points = [[latitude, longitude]]  # Starting point
    next_points = []  # List to store points for the next layer

    def get_triangle_center(coords):
        """Calculates the center (centroid) of a triangle."""
        lat_sum = sum(coord[0] for coord in coords)
        long_sum = sum(coord[1] for coord in coords)
        return [lat_sum / 3, long_sum / 3]


    def calculate_new_latitude(original_latitude, distance_miles, direction="north"):
        delta_latitude = distance_miles / 69
        if direction.lower() == "north":
            return original_latitude + delta_latitude
        elif direction.lower() == "south":
            return original_latitude - delta_latitude
        else:
            return None

    def calculate_new_longitude(original_longitude, distance_miles, direction="east"):
        #miles_per_degree_longitude = 45.0
        delta_longitude = distance_miles / miles_per_degree_longitude
        if direction.lower() == "east":
            return original_longitude + delta_longitude
        elif direction.lower() == "west":
            return original_longitude - delta_longitude
        else:
            return None
    

    def caculate_hexagon(center_lat, center_lon, side):
        points = []
        #push passed in lat and lon to the list
        points.append([center_lat, center_lon])

        # calculate the 6 points of the hexagon
        #top point
        lat = calculate_new_latitude(center_lat, side, "north")
        lon = center_lon
        points.append([lat, lon])

        #top right point
        lat = calculate_new_latitude(center_lat, side * 0.5, "north")
        lon = calculate_new_longitude(center_lon, side * 0.866025, "east")
        points.append([lat, lon])

        #bottom right point
        lat = calculate_new_latitude(center_lat, side * 0.5, "south")
        lon = calculate_new_longitude(center_lon, side * 0.866025, "east")
        points.append([lat, lon])

        #bottom point
        lat = calculate_new_latitude(center_lat, side, "south")
        lon = center_lon
        points.append([lat, lon])

        #bottom left point
        lat = calculate_new_latitude(center_lat, side * 0.5, "south")
        lon = calculate_new_longitude(center_lon, side * 0.866025, "west")
        points.append([lat, lon])

        #top left point
        lat = calculate_new_latitude(center_lat, side * 0.5, "north")
        lon = calculate_new_longitude(center_lon, side * 0.866025, "west")
        points.append([lat, lon])

        #close the hexagon by adding the first point again
        points.append([center_lat, center_lon])
        return points

    def calculate_triangles(points):
        triangles = []
        # Triangle 1
        triangle = [ points[0], points[1], points[2] ]
        triangles.append(triangle)

        # Triangle 2
        triangle = [ points[0], points[2], points[3] ]
        triangles.append(triangle)

        # Triangle 3
        triangle = [ points[0], points[3], points[4] ]
        triangles.append(triangle)

        # Triangle 4
        triangle = [ points[0], points[4], points[5] ]
        triangles.append(triangle)

        # Triangle 5
        triangle = [ points[0], points[5], points[6] ]
        triangles.append(triangle)

        # Triangle 6
        triangle = [ points[0], points[6], points[1] ]
        triangles.append(triangle)
        return triangles
    
    while current_depth < target_depth:
        #Get loop through the current points and calculate the hexagon for each point
        for current_point in current_points:
            lat, long = current_point
            #Calculate the hexagon for each point and add it to the temp points list
            hexagon = caculate_hexagon(lat, long, side_length_miles)
            #Calculate the triangles for each hexagon and add it to the temp triangles list
            t = calculate_triangles(hexagon)
            # Calculate the center of each triangle and add it to the temp triangles list
            for triangle in t:
                #get center of the triangle
                center = get_triangle_center(triangle)
                #loop through triangles and check if the center is unique
                center_exists = False
                rounded_center = [round(center[0], 6), round(center[1], 6)]
                for i in triangles:
                    existing_rounded_center = [round(i.get_centre()[0], 6), round(i.get_centre()[1], 6)]
                    if existing_rounded_center == rounded_center:
                        center_exists = True
                        break
                if not center_exists:
                    #create a new triangle object and add it to the triangles list
                    triangle = Triangle(triangle_name, [leds + 1, leds + 2], triangle, center)
                    triangles.append(triangle)
                    triangle_name += 1
                    leds += 2
            # put the coors of the hexagon into the next points list
            for i in range (1,7):
                next_points.append(hexagon[i])
        current_depth += 1
        current_points = next_points
        next_points = []
    return triangles

# which hexagon type to use
if hex_type == "flat_top":
    triangles = generate_flat_top(latitude, longitude, side_length, depth, miles_per_degree_longitude)
elif hex_type == "flat_sides":
    triangles = generate_flat_sides(latitude, longitude, side_length, depth, miles_per_degree_longitude)  

# Go through the the created triangles and update the LEDS with the leds from the hex_leds.py file.
for i in range(len(triangles)):
    triangle = triangles[i]
    triangle.set_leds(leds[i])
    triangles[i] = triangle

# Create a unique folder with today's date and time
# Make folder title
now = datetime.datetime.now()
folder_title = "HexMap - "+ now.strftime("%d-%m-%Y_%H-%M-%S")

# Create the folder
folder_path = os.path.join(os.getcwd(), folder_title)
os.makedirs(folder_path, exist_ok=True)

# Create a json file with the triangles and save it to the folder
with open(os.path.join(folder_path, "triangles.json"), "w") as f:
    json.dump([triangle.__dict__ for triangle in triangles], f, indent=4)

# Extract the coordinates from the triangles
triangle_coords = []
for triangle in triangles:
    triangle_coords.append(triangle.get_coordinates())

# Create a folium map centered on the starting point
m = folium.Map(location=(latitude, longitude), tiles="cartodb voyager", zoom_start=10)

# Add the triangles to the map
folium.Polygon(
    locations=triangle_coords,
    color="blue",
    weight=2,
    fill_color="red",
    fill_opacity=0.2,
    fill=True,
).add_to(m)

# Save map to HTML in folder created earlier
m.save(os.path.join(folder_title, "map.html"))





