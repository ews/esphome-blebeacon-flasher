import uuid
import subprocess
import sys
import argparse
import time
import serial  # Import PySerial
import re

def number_to_words(n):
    if n < 0 or n > 60:
        return "Number out of range (0-60 only)"

    ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen",
             "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty"]

    if n == 0:
        return "ZERO"
    elif 1 <= n < 10:
        return ones[n]
    elif 10 <= n < 20:
        return teens[n - 10]
    elif 20 <= n <= 60:
        if n % 10 == 0:
            return tens[n // 10]
        else:
            return tens[n // 10] + "-" + ones[n % 10]

def get_mac_address(port):
    try:
        # Run esptool.py to read the MAC address
        output = subprocess.check_output(
            ['esptool.py', '--port', port, 'read_mac'],
            stderr=subprocess.STDOUT
        )
        output = output.decode('utf-8')
        for line in output.splitlines():
            if 'MAC:' in line:
                mac_address = line.split('MAC:')[1].strip()
                return mac_address
        print("Could not find MAC address in esptool.py output.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("Error reading MAC address with esptool.py:")
        print(e.output.decode('utf-8'))
        sys.exit(1)

def get_existing_uuid(port):
    try:
        # Open serial connection
        ser = serial.Serial(port, 115200, timeout=5)
        time.sleep(2)  # Wait for the serial connection to initialize

        # Read lines from the serial output
        output = ""
        start_time = time.time()
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                output += line + "\n"
                # Check if the line contains the UUID
                match = re.search(r'UUID: ([a-fA-F0-9\-]+)', line)
                if match:
                    existing_uuid = match.group(1)
                    ser.close()
                    return existing_uuid
            if time.time() - start_time > 5:
                # Timeout after 5 seconds
                break
        ser.close()
        return None  # UUID not found
    except serial.SerialException as e:
        print(f"Error reading from serial port {port}: {e}")
        return None

def load_devices_csv():
    devices = {}
    try:
        with open('devices.csv', 'r') as csvfile:
            for line in csvfile:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        mac_address = parts[0]
                        uuid_ = parts[1]
                        name_ = parts[2]
                        devices[mac_address] = (uuid_, name_)
                    elif len(parts) >= 2:
                        mac_address = parts[0]
                        uuid_ = parts[1]
                        name_ = ""
                        devices[mac_address] = (uuid_, name_)
        return devices
    except FileNotFoundError:
        # If devices.csv doesn't exist, return empty dict
        return {}

def main():
    parser = argparse.ArgumentParser(description='Create ESPHome template and update devices.csv')
    parser.add_argument('--port', default='/dev/ttyACM0', help='Serial port of the ESP32 device')
    parser.add_argument('--test', action='store_true', help='Run in test mode without updating number.txt or devices.csv')
    args = parser.parse_args()

    port = args.port

    # Get the MAC address of the ESP32 device
    mac_address = get_mac_address(port)

    # Load devices.csv into devices dict
    devices = load_devices_csv()

    if mac_address in devices:
        # Device is already registered
        existing_uuid, name = devices[mac_address]
        print(f"Device with MAC address {mac_address} is already registered.")
        print(f"Using existing UUID: {existing_uuid} and Name: {name}")
        my_uuid = existing_uuid

        # Do not update number.txt or devices.csv

    else:
        # Device is not registered
        # Try to get existing_uuid from the device
        existing_uuid = get_existing_uuid(port)

        if existing_uuid:
            my_uuid = existing_uuid
            print(f"Existing UUID found on device: {existing_uuid}")
        else:
            my_uuid = str(uuid.uuid4())
            print("No existing UUID found on device. Generating a new UUID.")

        # Read the number from 'number.txt' and convert it to an integer
        with open('number.txt', 'r') as numberin:
            number = int(numberin.read().strip())

        name = number_to_words(number)

        if not args.test:
            # Write the incremented number back to 'number.txt' if a new UUID was generated
            if not existing_uuid:
                with open('number.txt', 'w') as numberout:
                    numberout.write(str(number + 1))

            # Write mac_address, my_uuid, and name to 'devices.csv'
            with open('devices.csv', 'a') as devicesout:
                devicesout.write(f"{mac_address},{my_uuid},{name}\n")

            print(f"\nDevice information saved to devices.csv:")
            print(f"MAC Address: {mac_address}")
            print(f"UUID: {my_uuid}")
            print(f"Name: {name}")
        else:
            print("\nTest mode: number.txt and devices.csv were not updated.")
            print(f"MAC Address: {mac_address}")
            print(f"UUID: {my_uuid}")
            print(f"Name: {name}")

    # Read the template file as plain text
    with open('beacon_config_template.yaml', 'r') as template_file:
        template_text = template_file.read()

    # Replace placeholders manually
    template_text = template_text.replace("{{ NAME }}", name)
    template_text = template_text.replace("{{ UUID }}", my_uuid)

    # Write the result to the output file
    with open('template.yaml', 'w') as fout:
        fout.write(template_text)

if __name__ == '__main__':
    main()
