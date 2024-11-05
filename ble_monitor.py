import csv
import time
import curses
from bluepy import btle

def read_devices_csv():
    devices = []
    try:
        with open('devices.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 3:
                    mac_address = row[0].lower()
                    uuid = row[1]
                    name = row[2]
                    devices.append({
                        'mac_address': mac_address,
                        'uuid': uuid,
                        'name': name,
                        'rssi': None,
                        'online': False,
                        'last_seen': None  # Initialize last_seen
                    })
            return devices
    except FileNotFoundError:
        print("Error: 'devices.csv' file not found.")
        exit(1)

def main(stdscr):
    # Clear screen and hide cursor
    curses.curs_set(0)
    stdscr.nodelay(True)  # Don't block on getch()
    stdscr.clear()

    devices = read_devices_csv()
    scanner = btle.Scanner()
    row_start = 3  # Starting row for device display
    devices_per_column = 20
    max_columns = 3  # Adjust as needed
    offline_threshold = 10  # Seconds after which device is considered offline

    try:
        while True:
            scan_time = 5.0  # Scan duration in seconds
            scan_start_time = time.time()
            devices_found = scanner.scan(scan_time)

            # Update device status based on scan results
            for dev in devices_found:
                addr = dev.addr.lower()
                rssi = dev.rssi
                # Check if the found device is in our list
                for device in devices:
                    if addr == device['mac_address']:
                        device['rssi'] = rssi
                        device['last_seen'] = time.time()
                        break  # No need to check other devices

            # Update the display
            stdscr.clear()
            stdscr.addstr(0, 0, "BLE Device Monitor")
            stdscr.addstr(1, 0, "Press 'q' to quit.")
            stdscr.addstr(2, 0, "-" * 70)

            # Calculate column positions
            column_width = 30  # Adjust as needed
            total_columns = min((len(devices) - 1) // devices_per_column + 1, max_columns)

            for idx, device in enumerate(devices):
                col = idx // devices_per_column
                row = idx % devices_per_column + row_start
                if col >= max_columns:
                    break  # Limit to max_columns

                x = col * column_width
                name = device['name']

                # Determine online status based on last_seen
                if device['last_seen'] is None:
                    online = 'Offline'
                    seconds_since_seen = '--'
                else:
                    time_since_seen = time.time() - device['last_seen']
                    if time_since_seen > offline_threshold:
                        online = 'Offline'
                    else:
                        online = 'Online'
                    seconds_since_seen = f"{int(time_since_seen)}s"

                rssi = f"{device['rssi']}" if device['rssi'] is not None else '--'
                display_str = f"{name:<10} {online:<7} RSSI: {rssi:<5} Last Seen: {seconds_since_seen}"
                stdscr.addstr(row, x, display_str)

            stdscr.refresh()

            # Handle user input
            key = stdscr.getch()
            if key == ord('q'):
                break

            time.sleep(1)
    except Exception as e:
        stdscr.addstr(curses.LINES - 1, 0, f"An error occurred: {e}")
        stdscr.refresh()
        time.sleep(3)

if __name__ == '__main__':
    curses.wrapper(main)
