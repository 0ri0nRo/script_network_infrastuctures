import sys
import os
import networkx as nx
import matplotlib.pyplot as plt

# You have to install libraries from plot ( matplotlib ) and for graph ( networkx )
# pip install networkx matplotlib
# pip install --upgrade networkx matplotlib

# KEYBOARD INPUT: 
# 1.   open terminal
# 2.   navigate in a folser ( e.g. >> Desktop )
# 3.   run the program:     ( e.g. >> python network-graph.py my_first_lab/lab.conf )
# 3.1  the program that a path to the files.

# OUTPUT
# 1. An image of the lab.conf
# 2. A file "general_configuration.txt" which contain a 
#    csv format of .conf used for "create_startup.py"

# NOTE: to aim of this script is to check the configuration of lab.conf
#       general_configuration.txt can be not correcly formatted, so it
#       need to edit manually.

# example of .conf file;
# pc1[0]=A
# r1[0]=A

# r1[1]=B
# pc2[0]=B


# ----------- Check for the input file path argument ----------- #
if len(sys.argv) != 2:
    print("Usage: python network-graph.py <path_to_lab.conf> \ne.g. >> python network-graph.py my_first_lab/lab.conf")
    sys.exit(1)

# You can place here manually to path to the file
# commenting the lines above.
FILE_NAME = sys.argv[1]     # global/relative path to the file e.g. my_first_lab/lab.conf
FILE_CONFIGURATION = "general_configuration.txt" # name of generated file
FILE_STARTUP_NAME = os.path.join( os.path.dirname(os.path.join(os.getcwd(), FILE_NAME)), FILE_CONFIGURATION )


# keys:     collision domain
# values:   array of dictionary [{'device': device1, 'eth': eth1}, {'device': device2, 'eth': eth2}]
network_structure = {} 

# ----------- READING FILE .conf ----------- #
devices_interfaces = {} # used to build-up next file
n_interfaces_max = 0

with open(FILE_NAME, 'r') as file:

    for line in file:

        # ----------- clearing the lines ----------- #
        line = line.strip().replace(" ", "")

        # skip line if are trash
        if not line or line[0] == "#" :
            continue

        # from pc1[0]=C to ['pc1', '0', 'C']
        device_eth_domain = line.replace("[", " ").replace("]=", " ").split(" ")
        
        device  = device_eth_domain[0]
        eth    = device_eth_domain[1]
        domain    = device_eth_domain[2] 

        # ----------- Put into dictionary to create graph ----------- #
        if domain not in network_structure.keys():
            network_structure[domain] = []
        
        network_structure[domain].append( {'device': device, 'eth': eth} )

        # ----------- CODE FOR THE GENERATION OF NEW FILES FOR create_startup.py ----------- #
        if device not in devices_interfaces.keys():
            devices_interfaces[device] = []

        devices_interfaces[device].append(eth)
        n_interfaces_max = max( n_interfaces_max, len(devices_interfaces[device]) ) # used to calculate length of the header

    with open(FILE_STARTUP_NAME, 'w') as file_startup_name:
        
        # ----------- creating header ----------- #
        # creating header dynamically: device, interface_1, ip_1, interface_2, ip_2, interface_3, ip_3
        header_string = "device"
        for i in range(n_interfaces_max):
            header_string += f", interface_{i}, ip_{i}"
        file_startup_name.write(f"{header_string}\n")

        # -----------  writing into new file ----------- #
        
        print(f"device, <current_n_commas> / <target_n_commas>")
        for device in devices_interfaces.keys():

            # converting array [eth1, eth2, eth3] to a string "eth1, <ip>, eth2, <ip>, eth3, <ip>"
            interfaces_list = ",\t<ip>, ".join( devices_interfaces[device]) 

            file_startup_string = f"{device},\t {interfaces_list},\t<ip>"
            
            missing_commas = header_string.count(",") - file_startup_string.count(",") 

            commas_string = ", " * missing_commas
            file_startup_added_commas = file_startup_string + commas_string + "\n"

            print(f"{device}: {file_startup_added_commas.count(',') }/{header_string.count(',')} -> {missing_commas} commas were missing in and have been added")  
            file_startup_name.write( file_startup_added_commas )
        
        print(f"File {FILE_STARTUP_NAME} created")


# ----------- CREATING GRAPH ----------- #
G = nx.Graph()

# ----------- adding nodes to the graph ----------- #
node_labels = {}

# loop to find all devices
for domain in network_structure.keys():         
    for element in network_structure[domain]:
        
        device = element['device']
        G.add_node(device)

        node_labels[device] = f"{device}"

# ----------- adding edges  ----------- #
edge_labels = {}
for domain in network_structure.keys():        # loop over collision zone

    for element1 in network_structure[domain]:      # find start-edge
        for element2 in network_structure[domain]:  # find end-edge

            device1 = element1['device']
            eth1    = element1['eth']

            device2 = element2['device']
            eth2    = element2['eth']

            # avoid loop edge
            if device1 == device2:
                continue
            
            
            if not ( G.has_edge(device1, device2) or G.has_edge(device2, device1)) :
                G.add_edge(device1, device2)

            edge_labels[(device1, device2)] = f"{device1}: eth{eth1}, {device2}: eth{eth2}"


#  ----------- plot and save the graph  ----------- #
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=False, node_size=500, node_color='lightgreen', font_size=10, font_weight='bold', edge_color='blue')
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_color='black')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

plt.title("Network Graph with Node and Edge Labels")
plt.savefig(os.path.join(os.path.dirname(os.path.join(os.getcwd(), FILE_NAME)), "current_lab_topology.png" ))
plt.show()