# Automation for sending the interface configs to the routers
from netmiko import ConnectHandler
import json
from getpass import getpass

def render_interface(interface_data):
    # Generate a list of commands for the interface
    commands = [
        f"interface {interface_data['interface']}",
        f"ip address {interface_data['ip']} {interface_data['subnet_mask']}",
        f"description {interface_data['description']}",
        f"duplex {interface_data['duplex']}",
        f"speed {interface_data['speed']}",
        "no shutdown"
    ]
    return commands

def push_config(device_config, commands):
    print(f"Configuring device: {device_config['host']}")
    
    with ConnectHandler(**device_config) as net_connect:
        net_connect.enable()
        output = net_connect.send_config_set(commands)
        print(output)
        print("Configurations successfully pushed!")
        # Disconnect automatically handled by the context manager

def open_json_file(file_path='device.json'):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: File {file_path} contains invalid JSON.")
        exit(1)

def main():
    # Get user credentials and device details
    host = input("Enter the device IP address: ")
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    secret = getpass("Enter your enable secret: ")

    # Define the device configuration
    cisco_device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": password,
        "secret": secret,
    }

    # Load interface data from JSON
    data = open_json_file()
    all_commands = []
    for interface in data:
        all_commands.extend(render_interface(interface))

    # Push configuration to the device
    push_config(cisco_device, all_commands)

if __name__ == "__main__":
    main()