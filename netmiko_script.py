# Automation for sending the interface configs to the routers
from netmiko import ConnectHandler
import json
from getpass import getpass

def render_interface(interface_data):
    """Generate a list of commands for the given interface configuration."""
    commands = []
    
    # Add tunnel-specific commands if applicable
    if interface_data['interface'].startswith("Tunnel"):
        commands.extend([
            # GRE Tunnel configuration
            f"interface {interface_data['interface']}",
            f"ip address {interface_data['ip_address']} {interface_data['subnet_mask']}",
            f"bandwidth {interface_data.get('bandwidth', 1000)}",  # Default bandwidth if not provided
            f"description {interface_data['description']}",
            f"ip mtu {interface_data.get('mtu', 1400)}",  # Default MTU if not provided
            f"tunnel source {interface_data['tunnel_src']}",
            f"tunnel destination {interface_data['tunnel_dst']}",
        ])
    else:
        # General interface configuration
        commands.extend([
            f"no cdp run",
            f"interface {interface_data['interface']}",
            f"ip address {interface_data['ip_address']} {interface_data['subnet_mask']}",
            f"description {interface_data['description']}",
        ])

        # Add optional configurations if available
        if 'duplex' in interface_data:
            commands.append(f"duplex {interface_data['duplex']}")
        if 'speed' in interface_data:
            commands.append(f"speed {interface_data['speed']}")
    
    # Finalize with `no shutdown`
    commands.append("no shutdown")
    
    return commands


def render_routing(router_data):
    """Generate routing commands based on router configuration."""
    return [
        f"ip route 0.0.0.0 0.0.0.0 {router_data['ip_route']}",
        "router ospf 1",
        f"router-id {router_data['router-id']}",
        f"network {router_data['network_1']}",
        f"network {router_data['network_2']}",
    ]


def push_config(device_config, commands):
    print(f"Configuring device: {device_config['host']}")
    
    with ConnectHandler(**device_config) as net_connect:
        net_connect.enable()
        output = net_connect.send_config_set(commands)

        # Save the configuration
        net_connect.save_config()
        print(output)
        print(f"Configurations successfully pushed to {device_config['host']}!")
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
    # Dict of devices
    routers = {"R1": "192.168.15.150", 
               "R2": "192.168.15.151", 
               "ISP1": "192.168.15.152",
               "ISP2": "192.168.15.153"
               }
    # Get user credentials
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    secret = password

     # Load interface data from JSON
    data = open_json_file()

    for router, ip_address in routers.items():
        if router in data: # Check if the router exists in the JSON file
            # Define the device configuration
            cisco_device = {
                "device_type": "cisco_ios",
                "host": ip_address,
                "username": username,
                "password": password,
                "secret": secret,
            }

             # Generate all commands for the current router
            all_commands = []
            for interface in data[router]:
                if 'interface' in interface: # Interface-specific commands
                    all_commands.extend(render_interface(interface))
                elif 'router-id' in interface: # Routing commands
                    all_commands.extend(render_routing(interface))

            # Push configuration to the device
            push_config(cisco_device, all_commands)

            print("All DEVICES ARE SUCCESSFULLY CONFIGURED AND GRE TUNNEL IS CREATED!")
        else:
            print(f"Warning: No configuration found in JSON for {router}")

if __name__ == "__main__":
    main()