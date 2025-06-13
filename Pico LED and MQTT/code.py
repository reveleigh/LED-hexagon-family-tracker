import board
import neopixel
import time
import json
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import supervisor
import traceback

from secrets import secrets # WIFI and MQTT connection details

# Configuration Constants
NEOPIXEL_PIN = board.GP22
NUM_LEDS = 300
MQTT_TOPIC = "pico/leds/command"

# Color Constants
COLOR_DAD = [255, 0, 0] 
COLOR_MUM = [0, 255, 0]
COLOR_SON = [0, 0, 255]
COLOR_OFF = [0, 0, 0]
DAD_LOCATION = None
MUM_LOCATION = None
SON_LOCATION = None
MODE = "tracker"


# NeoPixel Setup
print("Initializing NeoPixels...")
pixels = neopixel.NeoPixel(NEOPIXEL_PIN, NUM_LEDS, auto_write=False, brightness=1.0)
pixels.fill((0, 0, 0))
pixels.show()
print("NeoPixels Initialized.")

def fade_leds(rgb_start: tuple, rgb_end: tuple, led_list: list):
    """
    Gracefully fades the specified LEDs from a starting RGB color to an ending RGB color over 1 second.

    Args:
        rgb_start (tuple): A tuple (R, G, B) representing the starting color.
        rgb_end (tuple): A tuple (R, G, B) representing the ending color.
        led_list (list): A list of LED indices to apply the fade to.
    """
    duration = 1.0  # seconds
    steps = 50      # Number of steps for the fade, higher means smoother but more CPU usage
    delay_per_step = duration / steps

    r_start, g_start, b_start = rgb_start
    r_end, g_end, b_end = rgb_end

    for step in range(steps + 1):
        # Calculate the interpolation factor (0.0 to 1.0)
        t = step / steps

        # Interpolate each color component
        current_r = int(r_start + (r_end - r_start) * t)
        current_g = int(g_start + (g_end - g_start) * t)
        current_b = int(b_start + (b_end - b_start) * t)

        current_color = (current_r, current_g, current_b)

        # Apply the current color to all specified LEDs
        for led_index in led_list:
            if 0 <= led_index < NUM_LEDS: # Ensure the index is within bounds
                pixels[led_index] = current_color
            else:
                print(f"Warning: LED index {led_index} is out of bounds (0-{NUM_LEDS-1}).")

        pixels.show()
        time.sleep(delay_per_step)


# Basic Hardware Test (Temporary)
print("Performing basic LED test...")
try:
    pixels[149] = (255, 0, 0)
    pixels.show()
    print("Basic LED test: Set pixel 0 to red and called show().")
    time.sleep(2)
    pixels.fill((0, 0, 0))
    pixels.show()
    print("Basic LED test: Cleared pixels.")
except Exception as e:
    print(f"Basic LED test failed: {e}")
    traceback.print_exception(e)

# Wi-Fi Connection
print(f"Connecting to Wi-Fi: {secrets['ssid']}...")
wifi_connected = False
try:
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print(f"Connected to Wi-Fi!")
    print(f"My IP address: {wifi.radio.ipv4_address}")
    wifi_connected = True
except ConnectionError as e:
    print(f"Failed to connect to Wi-Fi: {e}")
    print("Please check secrets.py settings or Wi-Fi signal.")

# MQTT Callback Function Definitions
def connected(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with code: {rc}")
    if rc == 0:
        print(f"Subscribing to topic: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Connection failed with code {rc}")


def message_handler(client, topic, message):
    global MODE

    print(f"Received message on topic {topic}: {message}")

    try:
        command = json.loads(message)
        print("Parsed command:", command)
        
        option = command.get("mode")
        #MODE = option
        print("Mode set to:", MODE)
        if MODE == "tracker":
            global DAD_LOCATION
            global MUM_LOCATION
            global SON_LOCATION
            prev_dad_location = DAD_LOCATION
            prev_mum_location = MUM_LOCATION
            prev_SON_LOCATION = SON_LOCATION

            person_id = command.get("person_id")
            new_leds = command.get("leds") # The LEDs for this person's NEW location
            if person_id == "mum":
                prev_mum_location = MUM_LOCATION
                MUM_LOCATION = new_leds
                print("Mum's location updated to:", MUM_LOCATION)
                if prev_mum_location == prev_dad_location == prev_SON_LOCATION:
                    before = (255,255,255)
                    after = (255,0,255)
                elif prev_mum_location == prev_dad_location:
                    before = (255,255,0)
                    after = (255,0,0)
                elif prev_mum_location == prev_SON_LOCATION:
                    before = (0,255,255)
                    after = (0,0,255)
                else:
                    before = (0,255,0)
                    after = (0,0,0)
                prev_state_change = {"leds": prev_mum_location, "before": before, "after": after}
                if prev_state_change["leds"] is not None:
                    # Fade out the previous location
                    fade_leds(before, after, prev_state_change["leds"])

                print("BEFORE Animation state change:", prev_state_change)
                if MUM_LOCATION == DAD_LOCATION == SON_LOCATION:
                    before = (255,0,255)
                    after = (255,255,255)
                elif MUM_LOCATION == DAD_LOCATION:
                    before = (255,0,0)
                    after = (255,255,0)
                elif MUM_LOCATION == SON_LOCATION:
                    before = (0,0,255)
                    after = (0,255,255)
                else:
                    before = (0,0,0)
                    after = (0,255,0)
                post_state_change = {"leds": MUM_LOCATION, "before": before, "after": after}
                fade_leds(before, after, post_state_change["leds"])
                print("AFTER Animation state change:", post_state_change)
                
            elif person_id == "dad":
                prev_dad_location = DAD_LOCATION
                DAD_LOCATION = new_leds
                print("Dad's location updated to:", DAD_LOCATION) 
                if prev_dad_location == prev_mum_location == prev_SON_LOCATION:
                    before = (255,255,255)
                    after = (0,255,255)
                elif prev_dad_location == prev_mum_location:
                    before = (255,255,0)
                    after = (0,255,0)
                elif prev_dad_location == prev_SON_LOCATION:
                    before = (255,0,255)
                    after = (0,0,255)
                else:
                    before = (255,0,0)
                    after = (0,0,0)
                prev_state_change = {"leds": prev_dad_location, "before": before, "after": after}
                if prev_state_change["leds"] is not None:
                    # Fade out the previous location
                    fade_leds(before, after, prev_state_change["leds"])
                print("BEFORE Animation state change:", prev_state_change)
                if DAD_LOCATION == MUM_LOCATION == SON_LOCATION:
                    before = (0,255,255)
                    after = (255,255,255)
                elif DAD_LOCATION == MUM_LOCATION:
                    before = (0,255,0)
                    after = (255,255,0)
                elif DAD_LOCATION == SON_LOCATION:
                    before = (0,0,255)
                    after = (255,0,255)
                else:
                    before = (0,0,0)
                    after = (255,0,0)
                post_state_change = {"leds": DAD_LOCATION, "before": before, "after": after}
                fade_leds(before, after, post_state_change["leds"])
                print("AFTER Animation state change:", post_state_change)
            elif person_id == "son":
                prev_SON_LOCATION = SON_LOCATION
                SON_LOCATION = new_leds
                print("son's location updated to:", SON_LOCATION)
                if prev_SON_LOCATION == prev_dad_location == prev_mum_location:
                    before = (255,255,255)
                    after = (255,255,0)
                elif prev_SON_LOCATION == prev_dad_location:
                    before = (255,0,255)
                    after = (255,0,0)
                elif prev_SON_LOCATION == prev_mum_location:
                    before = (0,255,255)
                    after = (0,255,0)
                else:
                    before = (0,0,255)
                    after = (0,0,0)
                prev_state_change = {"leds": prev_SON_LOCATION, "before": before, "after": after}
                if prev_state_change["leds"] is not None:
                    # Fade out the previous location
                    fade_leds(before, after, prev_state_change["leds"])
                print("BEFORE Animation state change:", prev_state_change)
                if SON_LOCATION == DAD_LOCATION == MUM_LOCATION:
                    before = (255,255,0)
                    after = (255,255,255)
                elif SON_LOCATION == DAD_LOCATION:
                    before = (255,0,0)
                    after = (255,0,255)
                elif SON_LOCATION == MUM_LOCATION:
                    before = (0,255,0)
                    after = (255,0,255)
                else:
                    before = (0,0,0)
                    after = (0,0,255)
                post_state_change = {"leds": SON_LOCATION, "before": before, "after": after}
                fade_leds(before, after, post_state_change["leds"])
                print("AFTER Animation state change:", post_state_change)
                
                
            else:
                print("Unknown person_id:", person_id)
                return

            


    except json.JSONDecodeError:
        print("Failed to decode JSON message. Is the payload valid JSON? Message:", message)
        # Log JSON error
    except Exception as e:
        print(f"An unexpected error occurred in message handler: {e}")
        import traceback
        traceback.print_exception(e) # Print full traceback for debugging



# MQTT Setup
# Initialize mqtt_client variable BEFORE the if block
mqtt_client = None
print("Attempting MQTT setup...")
if wifi_connected:
    try:
        print("Creating socket pool...")
        pool = socketpool.SocketPool(wifi.radio)
        print("Socket pool created.")

        print("Setting up MQTT Client...")
        client_id_str = "HexPico"
        try:
            client_id_str = f"pico-{supervisor.get_board_id()}"
        except AttributeError:
            print("supervisor.get_board_id() not available, using default client ID.")
        except Exception as e:
            print(f"Error getting board ID: {e}, using default client ID.")

        mqtt_client = MQTT.MQTT(
            broker=secrets['mqtt_broker'],
            port=secrets['mqtt_port'],
            username=secrets.get('mqtt_username', None),
            password=secrets.get('mqtt_password', None),
            socket_pool=pool,
            client_id=client_id_str
        )
        print(f"MQTT client instance created with ID: {mqtt_client.client_id}")

        print("Assigning MQTT callbacks...")
        mqtt_client.on_connect = connected
        mqtt_client.on_message = message_handler
        print("MQTT callbacks assigned.")

        print(f"Attempting to connect to MQTT broker: {secrets['mqtt_broker']}:{secrets['mqtt_port']}...")
        mqtt_client.connect()
        print("MQTT connect() called. Check serial for connection status.")

    except Exception as e:
        print(f"An error occurred during MQTT setup: {e}")
        traceback.print_exception(e)
        mqtt_client = None # Ensure mqtt_client is None if setup fails

else:
    print("Skipping MQTT setup due to Wi-Fi connection failure.")

# Main Loop
print("Entering main loop...")

reconnect_delay = 1.0
max_reconnect_delay = 60.0
last_reconnect_attempt = 0

print(f"Initial state before loop: wifi_connected={wifi_connected}, mqtt_client is None={mqtt_client is None}")

while True:
    current_time = time.monotonic()

    if mqtt_client is not None:
        try:
            if not mqtt_client.is_connected():
                print(f"MQTT disconnected. Attempting to reconnect in {reconnect_delay:.1f}s...")
                if current_time - last_reconnect_attempt >= reconnect_delay:
                    try:
                        mqtt_client.reconnect()
                        print("MQTT reconnect successful!")
                        reconnect_delay = 1.0
                    except Exception as e:
                        print(f"MQTT reconnect failed: {e}")
                        reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
                        last_reconnect_attempt = current_time

            if mqtt_client.is_connected():
                 mqtt_client.loop()

        except Exception as e:
            print(f"Error during MQTT loop processing: {e}")


    pixels.show()

    time.sleep(0.001)



