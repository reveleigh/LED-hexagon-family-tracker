import board
import neopixel  # Library to control NeoPixel LEDs
import time  # Library for time-related functions (like delays)
from hex_leds import leds  # Import LED indices from the hex_leds.py file

from adafruit_led_animation.helper import PixelMap  # Helper class to group LEDs
from adafruit_led_animation.animation.comet import Comet  # Comet animation
from adafruit_led_animation.animation.chase import Chase  # Chase animation
from adafruit_led_animation.animation.solid import Solid  # Solid colour display
from adafruit_led_animation.animation.blink import Blink  # Blinking effect
from adafruit_led_animation.animation.colorcycle import ColorCycle  # Colour cycling
from adafruit_led_animation.animation.pulse import Pulse  # Pulsing effect
from adafruit_led_animation.animation.sparkle import Sparkle  # Sparkle effect
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle  # Rainbow sparkle effect

# --- Configuration ---
pixel_pin = board.GP22  # The GPIO pin connected to the NeoPixel data line
pixel_num = 300  # The total number of NeoPixels in your setup

# --- Initialise NeoPixels ---
pixels = neopixel.NeoPixel(pixel_pin, pixel_num, brightness=1.0, auto_write=False)
# Create a NeoPixel object. brightness controls overall brightness.
# auto_write=False means we need to call pixels.show() to update the LEDs.

# --- Extract pixels from each hexagon group ---
# These list comprehensions efficiently extract the LED indices for each hexagon
# from your 'leds' data structure.
hex1 = [index for pair in leds[0:6] for index in pair]  # Inner hexagon
hex2 = [index for pair in leds[6:24] for index in pair]  # Second hexagon
hex3 = [index for pair in leds[24:54] for index in pair]  # Third hexagon
hex4 = [index for pair in leds[54:96] for index in pair]  # Fourth hexagon
hex5 = [index for pair in leds[96:150] for index in pair]  # Fifth hexagon

# --- Create PixelMap groups ---
# These create PixelMap objects, which treat the specified LEDs as a single group.
# individual_pixels=True is important; see explanation below.
group1 = PixelMap(pixels, hex1, individual_pixels=True)
group2 = PixelMap(pixels, hex2, individual_pixels=True)
group3 = PixelMap(pixels, hex3, individual_pixels=True)
group4 = PixelMap(pixels, hex4, individual_pixels=True)
group5 = PixelMap(pixels, hex5, individual_pixels=True)

# Explanation of individual_pixels=True:
# This parameter is crucial for how animations behave on the PixelMap.
# When set to True, it tells the animation library to treat the PixelMap
# as if it were a single LED strip, even though it's a group of LEDs.
# This is what allows animations like Chase and Comet to run across the entire group
# as a single unit, rather than on each individual LED within the group.

groups = [group1, group2, group3, group4, group5]  # List of all the groups

# --- Colour definitions ---
colors = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
]

# --- Animation definitions ---
# Create a list of animation objects for each group.
# This makes it easy to apply the same animation type to all groups.
solid_animations = [Solid(group, color=(255, 255, 255)) for group in groups]  # Solid white
blink_animations = [Blink(group, color=(255, 255, 255), speed=2) for group in groups]  # Blinking white
colorcycle_animations = [ColorCycle(group, colors=colors, speed=2) for group in groups]  # Colour cycle
chase_animations = [Chase(group, speed=0.1, color=colors[i % len(colors)], size=2) for i, group in enumerate(groups)]
# Chase effect, using different colours for each group
comet_animations = [Comet(group, speed=0.5, color=(255, 255, 255), tail_length=30, bounce=False) for group in groups]  # Comet effect
pulse_animations = [Pulse(group, color=(255, 255, 255), speed=2, period=2) for group in groups]  # Pulse effect
sparkle_pulse_animations = [Sparkle(group, color=(255, 255, 255), speed=0.5, num_sparkles=20) for group in groups]  # Sparkle effect
rainbow_animations = [RainbowSparkle(group, speed=0.5, num_sparkles=10) for group in groups]  # Rainbow sparkle

all_animations = [  # List of lists, containing all animation types
    solid_animations,
    blink_animations,
    colorcycle_animations,
    chase_animations,
    comet_animations,
    pulse_animations,
    sparkle_pulse_animations,
    rainbow_animations
]

# --- Animation control variables ---
animation_index = 0  # Index of the current animation type
last_switch = time.monotonic()  # Time of the last animation switch
animation_delay = 2.0  # Delay between starting animations on each group

# --- Function to clear all pixels ---
def clear_pixels():
    pixels.fill((0, 0, 0))  # Set all pixels to black (off)
    pixels.show()  # Update the LEDs

# --- Main loop ---
while True:
    now = time.monotonic()  # Get the current time
    current_animation = all_animations[animation_index]  # Get the list of animations for the current type

    # Iterate through each group's animation
    for i, animation in enumerate(current_animation):
        # Start animations on each group with a slight delay
        if now - last_switch >= i * animation_delay:
            animation.animate()  # Run the animation

    pixels.show()  # Update the LEDs with the current animation state

    # Switch to the next animation every 30 seconds
    if now - last_switch > 30:
        clear_pixels()  # Turn off all LEDs before switching
        animation_index = (animation_index + 1) % len(all_animations)  # Move to the next animation type
        last_switch = time.monotonic()  # Update the last switch time

    time.sleep(1)  # Small delay to control the animation speed

    