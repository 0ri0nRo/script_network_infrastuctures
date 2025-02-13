import os
import networkx as nx
import matplotlib.pyplot as plt

def generate_network_graph(file_path):
    FILE_CONFIGURATION = "general_configuration.txt"
    FILE_STARTUP_NAME = os.path.join(os.path.dirname(os.path.abspath(file_path)), FILE_CONFIGURATION)

    network_structure = {}
    devices_interfaces = {}
    n_interfaces_max = 0

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip().replace(" ", "")
            if not line or line.startswith("#"):
                continue

            device, eth, domain = line.replace("[", " ").replace("]=", " ").split(" ")
            
            if domain not in network_structure:
                network_structure[domain] = []
            
            network_structure[domain].append({'device': device, 'eth': eth})
            
            if device not in devices_interfaces:
                devices_interfaces[device] = []
            
            devices_interfaces[device].append(eth)
            n_interfaces_max = max(n_interfaces_max, len(devices_interfaces[device]))

    with open(FILE_STARTUP_NAME, 'w') as file_startup:
        header_string = "device" + ", " + ", ".join([f"interface_{i}, ip_{i}" for i in range(n_interfaces_max)])
        file_startup.write(f"{header_string}\n")

        for device, interfaces in devices_interfaces.items():
            interfaces_list = ", ".join([f"{eth}, <ip>" for eth in interfaces])
            file_startup_string = f"{device}, {interfaces_list}"
            missing_commas = header_string.count(",") - file_startup_string.count(",")
            file_startup.write(file_startup_string + "," * missing_commas + "\n")
    
    G = nx.Graph()
    node_labels = {}
    for domain, elements in network_structure.items():
        for element in elements:
            device = element['device']
            G.add_node(device)
            node_labels[device] = device
    
    edge_labels = {}
    for domain, elements in network_structure.items():
        for element1 in elements:
            for element2 in elements:
                if element1['device'] != element2['device']:
                    device1, eth1 = element1['device'], element1['eth']
                    device2, eth2 = element2['device'], element2['eth']
                    if not G.has_edge(device1, device2):
                        G.add_edge(device1, device2)
                        edge_labels[(device1, device2)] = f"{device1}: eth{eth1}, {device2}: eth{eth2}"

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=False, node_size=500, node_color='lightgreen', font_size=10, edge_color='blue')
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_color='black')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    output_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), "current_lab_topology.png")
    plt.title("Network Graph with Node and Edge Labels")
    plt.savefig(output_path)
    plt.show()
    
    print(f"Graph saved at: {output_path}")
    print(f"Configuration file created at: {FILE_STARTUP_NAME}")
