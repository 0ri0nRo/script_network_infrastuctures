import os
import re

def build_ip_mapping(filename):
    ip_mapping = {}
    with open(filename, 'r') as f:
        for line in f:
            match = re.match(r'([A-Za-z]+)\s*=\s*([\d\.]+)', line.strip())
            if match:
                label, ip = match.groups()
                ip_mapping[label] = ip
    return ip_mapping

# Build the IP mapping from the lab.conf file
ip_mapping = build_ip_mapping('lab.conf')

# Netmask and default gateway (adjustable)
netmask = '255.255.255.0'
gateway = '192.168.1.1'

# Read lab.conf and parse it into a usable format
def parse_lab_conf(filename):
    devices = {}
    with open(filename, 'r') as f:
        for line in f:
            # Regex to extract the device name and interface-label mappings
            match = re.match(r'([a-zA-Z0-9]+)\[(\d+)\]=([A-Za-z]+)', line.strip())
            if match:
                device, interface, label = match.groups()
                if device not in devices:
                    devices[device] = {}
                devices[device][int(interface)] = label
    return devices

# Function to create the /etc/network/interfaces configuration file for static IP assignment
def create_network_config(device_name, interface, ip_address, netmask, gateway=None):
    interfaces_config = f"""
# Static IP configuration for {device_name} eth{interface}
auto eth{interface}
iface eth{interface} inet static
    address {ip_address}
    netmask {netmask}
"""
    if gateway:
        interfaces_config += f"    gateway {gateway}\n"
    return interfaces_config

# Function to create folders for devices
def create_device_folders(devices):
    for device in devices:
        if not os.path.exists(device):
            os.makedirs(device)
            print(f"Folder for {device} created.")
        else:
            print(f"Folder for {device} already exists.")

# Function to write the /etc/network/interfaces file for a device
def write_network_config(device, interface, label):
    ip_address = ip_mapping.get(label)
    if ip_address:
        # The path now is relative to the working directory, not system-level
        interfaces_path = f"./{device}/etc/network/interfaces"
        # Ensure the directories are created
        os.makedirs(os.path.dirname(interfaces_path), exist_ok=True)
        config_content = create_network_config(device, interface, ip_address, netmask, gateway)
        with open(interfaces_path, "w") as file:
            file.write(config_content)
            print(f"Static IP config written for {device} interface eth{interface} at {interfaces_path}")

# Main function
def main():
    # Parse the lab.conf to get the devices and their interface mappings
    devices = parse_lab_conf('lab.conf')

    # Create folders for devices
    create_device_folders(devices)

    # Assign IPs and write the network configuration files
    for device, interfaces in devices.items():
        for interface, label in interfaces.items():
            write_network_config(device, interface, label)

    print("All devices configured.")

# Run the script
if __name__ == "__main__":
    main()
