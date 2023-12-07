
from pymavlink import mavutil
import time
import threading

# Function to set mode
def set_mode(master, mode):
    mode_id = master.mode_mapping()[mode]
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )

# Function to send a waypoint
def send_waypoint(master, lat, lon, alt):
    waypoint = mavutil.mavlink.MAVLink_mission_item_message(
        master.target_system,
        master.target_component,
        0, # sequence number
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # frame
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, # command
        0, 0, # current, autocontinue
        0, # param1 (hold time)
        0, # param2 (acceptance radius)
        0, # param3 (pass radius)
        0, # param4 (yaw angle)
        lat, lon, alt # coordinates
    )
    master.mav.send(waypoint)
    time.sleep(1)

# Function to monitor and react to anomalies
def monitor_and_react(master):
    while True:
        # Define the conditions for hovering or RTH here
        # Placeholder condition: if True, switch to LOITER; if False, switch to RTL
        condition_for_hover = False
        condition_for_RTH = False

        if condition_for_hover:
            print("Condition for hover met, switching to LOITER mode")
            set_mode(master, 'LOITER')
            break
        elif condition_for_RTH:
            print("Condition for Return-To-Home met, switching to RTL mode")
            set_mode(master, 'RTL')
            break
        time.sleep(1)

def check_drone_status(master):
    """
    Check the current location and state of the drone.

    :param master: MAVLink connection object
    :return: None
    """
    try:
        # Fetch the global position
        global_position = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
        if global_position:
            latitude = global_position.lat / 1e7
            longitude = global_position.lon / 1e7
            altitude = global_position.alt / 1000.0
            print(f"Current Location - Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude} meters")

        # Fetch the current state
        state = master.recv_match(type='HEARTBEAT', blocking=True, timeout=3)
        if state:
            mode = mavutil.mode_string_v10(state)
            is_armed = 'Armed' if state.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED else 'Disarmed'
            print(f"Current State - Mode: {mode}, Armed: {is_armed}")

    except Exception as e:
        print(f"Error in check_drone_status: {e}")

def relinquish_control(master):
    """
    Relinquish control back to the original controller (Manual mode).

    :param master: MAVLink connection object
    :return: None
    """
    try:
        # Set the flight mode to MANUAL
        set_mode(master, 'MANUAL')
        print("Control relinquished to Manual mode")

    except Exception as e:
        print(f"Error in relinquish_control: {e}")

def transfer_and_transmit_image(raspberry_pi_image_path, flight_controller_image_path):
    try:
        # Connect to the flight controller (adjust the connection settings)
        master = mavutil.mavlink_connection('/dev/ttyAMA0', baud=57600)

        # Read the image file from Raspberry Pi
        with open(raspberry_pi_image_path, 'rb') as image_file:
            image_data = image_file.read()

        # Define the remote file path on the flight controller
        remote_image_path_on_fc = flight_controller_image_path

        # Upload the image from Raspberry Pi to the flight controller using MAVLink FTP
        master.mav.file_transfer_protocol_send(
            mavutil.mavlink.MAVLINK_MSG_ID_FILE_TRANSFER_START,
            mavutil.mavlink.MAV_COMP_ID_SYSTEM_CONTROL,
            0,
            1,
            remote_image_path_on_fc.encode(),
            len(image_data),
            mavutil.mavlink.MAVLINK_FT_IMAGE,  # Use MAVLINK_FT_IMAGE for image files
            image_data,
        )

        # Wait for acknowledgement
        ack_msg = master.recv_match(type='FILE_TRANSFER_PROTOCOL', blocking=True)
        if ack_msg.payload.result == mavutil.mavlink.MAVLINK_FT_RESULT_ACCEPTED:
            print("Image transfer accepted")
        else:
            print("Image transfer failed")
            master.close()
            return

        print("Image transfer complete")

        # Close the MAVLink connection
        master.close()

    except Exception as e:
        print(f"Error: {e}")

# Main control function
def main():
    master = mavutil.mavlink_connection('/dev/ttyAMA0', baud=57600)

    print("waiting for heartbeat...")
    master.wait_heartbeat()
    print("heartbeat found")

    # Arm the drone
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0
    )
    time.sleep(2)

    # Set to AUTO mode
    set_mode(master, 'AUTO')
    time.sleep(2)

    # Start the monitoring thread
    monitoring_thread = threading.Thread(target=monitor_and_react, args=(master,))
    monitoring_thread.start()

    # Send a waypoint
    latitude = 47.397748
    longitude = 8.545596
    altitude = 10.0
    send_waypoint(master, latitude, longitude, altitude)

    # Wait for the monitoring thread to complete
    monitoring_thread.join()

if __name__ == "__main__":
    main()
