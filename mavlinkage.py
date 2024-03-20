import socket
import sys
from pymavlink import mavutil

def open_mavlink_connection(udp_port="192.168.43.1:14550"):
    """
    Open a MAVLink connection on the specified UDP port.

    Args:
        udp_port (int): The UDP port to open the MAVLink connection.

    Returns:
        mavutil.mavlink_connection: A MAVLink connection object.
    """
    try:
        # Create a MAVLink message handler
        mavlink_msg = mavutil.mavlink_connection(
            'udpin:' + str(udp_port), dialect='common', notimestamps=True
        )
        return mavlink_msg
    except Exception as e:
        print(f"An error occurred while opening the MAVLink connection: {e}")
        return None

def read_latest_gps_info(mavlink_msg):
    """
    Read the most recent GPS location and coordinates information from a MAVLink connection.

    Args:
        mavlink_msg (mavutil.mavlink_connection): The MAVLink connection object.

    Returns:
        dict: A dictionary containing GPS information including latitude, longitude, and altitude.
    """
    gps_info = {
        "latitude": None,
        "longitude": None,
        "altitude": None
    }

    try:
        print("Waiting for GPS information...")
        msg = mavlink_msg.recv_msg()
        if msg and msg.get_type() == "GLOBAL_POSITION_INT":
            gps_info["latitude"] = msg.lat / 1e7
            gps_info["longitude"] = msg.lon / 1e7
            gps_info["altitude"] = msg.alt / 1e3  # Convert from mm to meters
            return gps_info
    except KeyboardInterrupt:
        print("Stopped waiting for GPS information.")
    except Exception as e:
        print(f"An error occurred while reading GPS information: {e}")
    return gps_info

# Example usage:
if __name__ == "__main__":

    
    udp_port = "192.168.43.1:14550" 
    print("Running test for mavlink data at port " + udp_port)

    # Open connection 
    mavlink_connection = open_mavlink_connection(udp_port)
    print("Connection: " +  str(mavlink_connection))

    if mavlink_connection:
        gps_data = read_latest_gps_info(mavlink_connection)

        print("GPS Information:")
        print(gps_data)

        # Close the MAVLink connection
        mavlink_connection.close()
    else:
        print("Error")
