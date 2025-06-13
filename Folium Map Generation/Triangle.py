class Triangle:
    def __init__(self, name, leds, coordinates, centre):
        """
        Initialises a Triangle object.

        Args:
            name (int): The name of the triangle.
            leds (list): A list of LED identifiers associated with the triangle.
            coordinates (list): A nested list of three coordinate pairs (latitude, longitude).
            centre (list): A pair of coordinates (latitude, longitude) for the triangle's center.
        """
        self.name = name
        self.leds = leds
        self.coordinates = coordinates
        self.centre = centre

    def get_name(self):
        """Returns the name of the triangle."""
        return self.name

    def get_leds(self):
        """Returns the list of LEDs associated with the triangle."""
        return self.leds

    def get_coordinates(self):
        """Returns the nested list of coordinates for the triangle."""
        return self.coordinates

    def get_centre(self):
        """Returns the center coordinates of the triangle."""
        return self.centre
    
    def set_leds(self, leds):
        """Sets the LEDs associated with the triangle."""
        self.leds = leds