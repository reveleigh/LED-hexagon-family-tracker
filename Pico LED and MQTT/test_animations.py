import board
import neopixel  # Library to control NeoPixel LEDs
import time  # Library for time-related functions (like delays)
from hex_leds import leds  # Import LED indices from the hex_leds.py file

hex1 = [index for pair in leds[0:6] for index in pair]  # Inner hexagon
hex2 = [index for pair in leds[6:24] for index in pair]  # Second hexagon
hex3 = [index for pair in leds[24:54] for index in pair]  # Third hexagon
hex4 = [index for pair in leds[54:96] for index in pair]  # Fourth hexagon
hex5 = [index for pair in leds[96:150] for index in pair]  # Fifth hexagon
import random  # Library for generating random numbers (though not currently used)


# --- Configuration ---
pixel_pin = board.GP22  # The GPIO pin connected to the NeoPixel data line
pixel_num = 300  # The total number of NeoPixels in your setup

# --- Initialise NeoPixels ---
pixels = neopixel.NeoPixel(pixel_pin, pixel_num, brightness=1.0, auto_write=False)

# --- Colour definitions ---
colors = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
]

# --- Function to perform a color fade ---
def color_fade(group_indices, start_color, end_color, steps=50, delay=0.02):
    """Fades a group of LEDs from a start color to an end color."""
    r1, g1, b1 = start_color
    r2, g2, b2 = end_color

    for i in range(steps + 1):
        ratio = i / steps
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        fade_color = (r, g, b)
        for index in group_indices:
            pixels[index] = fade_color
        pixels.show()
        time.sleep(delay)

while True:

# Choose 10 random LED *pairs* from the list of LEDs (without random.sample)
    num_to_select = 10
    selected_pairs = []
    available_indices = list(range(len(leds)))  # Create a list of indices

    if len(available_indices) >= num_to_select:
        for _ in range(num_to_select):
            random_index = random.choice(available_indices)
            selected_pairs.append(leds[random_index])
            available_indices.remove(random_index)  # Ensure no duplicates

        # Loop through the selected pairs and fade them in and out to white
        for pair in selected_pairs:
            # Fade in
            for i in range(0, 256, 5):
                for index in pair:
                    pixels[index] = (i, i, i)  # Set both LEDs in the pair to white
                pixels.show()
                time.sleep(0.05)

            time.sleep(2)

            # Fade out
            for i in range(255, -1, -5):
                for index in pair:
                    pixels[index] = (i, i, i)  # Fade both LEDs in the pair to black
                pixels.show()
                time.sleep(0.05)
    time.sleep(1)
    
    # Fade in all to white
    for i in range(0, 256, 5):
        pixels.fill((i, i, i))  # Set all pixels to white with increasing brightness
        pixels.show()  # Update the LEDs
        time.sleep(0.05)  # Small delay for smooth transition   

    #Time delay to see the effect
    time.sleep(5)

    # Fade out
    for i in range(255, -1, -5):
        pixels.fill((i, i, i))  # Set all pixels to white with decreasing brightness
        pixels.show()  # Update the LEDs
        time.sleep(0.05)  # Small delay for smooth transition

    # Sleep for a moment
    time.sleep(1)

    #fade in hex1 to red
    for i in range(0, 256, 5):
        for index in hex1:
            pixels[index] = (i, 0, 0)  # Set hex1 to red with increasing brightness
        pixels.show()  # Update the LEDs
        time.sleep(0.05)  # Small delay for smooth transition
    # fade in hex2 to red
    for i in range(0, 256, 5):
        for index in hex2:
            pixels[index] = (i, 0, 0)  # Set hex2 to red with increasing brightness
        pixels.show()  # Update the LEDs
        time.sleep(0.05)  # Small delay for smooth transition

    # fade in hex3 to red
    for i in range(0, 256, 5):
        for index in hex3:
            pixels[index] = (i, 0, 0)  # Set hex3 to red with increasing brightness
        pixels.show()  # Update the LEDs
        time.sleep(0.05)  # Small delay for smooth transition

    # fade in hex4 to red
    for i in range(0, 256, 5):
        for index in hex4:
            pixels[index] = (i, 0, 0)  # Set hex4 to red with increasing brightness
        pixels.show()  # Update the LEDs
        time.sleep(0.05)  # Small delay for smooth transition

    # fade in hex5 to red
    for i in range(0, 256, 5):
        for index in hex5:
            pixels[index] = (i, 0, 0)  # Set hex5 to red with increasing brightness
        pixels.show()  # Update the LEDs
        time.sleep(0.05)  # Small delay for smooth transition

    # Sleep for a moment
    time.sleep(1)

    # Fade out all to black
    for i in range(255, -1, -5):
        pixels.fill((i, 0, 0))  # Set all pixels to black (off)
        pixels.show()  # Update the LEDs
        time.sleep(0.05)  # Small delay for smooth transition

    # fade in one leds to yellow
    # Fade in all pairs of LEDs to yellow simultaneously
    for pair in leds:
        for index in pair:
            pixels[index] = (255, 255, 0)  # Set to yellow
        pixels.show()
        time.sleep(0.05)
    time.sleep(5)

    # Fade out all pairs of LEDs to black simultaneously
    for pair in leds:
        for index in pair:
            pixels[index] = (0, 0, 0)  # Set to black
        pixels.show()
        time.sleep(0.05)
    time.sleep(1)

    num_hex_groups = 5
    for i in range(len(colors)):
        start_color = colors[i]
        end_color = colors[(i + 1) % len(colors)]  # Cycle through colors

        # Fade each hexagon group sequentially
        color_fade(hex1, start_color, end_color)
        color_fade(hex2, start_color, end_color)
        color_fade(hex3, start_color, end_color)
        color_fade(hex4, start_color, end_color)
        color_fade(hex5, start_color, end_color)

        time.sleep(1) # Small pause between full color transitions


