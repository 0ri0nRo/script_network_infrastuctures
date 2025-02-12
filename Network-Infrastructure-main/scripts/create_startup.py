import sys
import os
import glob
import shutil
import re

# KEYBOARD INPUT: 
# 1.   open terminal
# 2.   navigate in a folder ( e.g. >> Desktop )
# 3    remeber to complete target file ( open general_configuration.txt and add what is necessary)
# 4.   run the program:     ( e.g. >> python create_startup.py my_first_lab/general_configuration.txt )
# 4.1  the program that a path to the files.

# OUTPUT:
# 1. startup files with instruction specified in 'create_startup_file'
# 2. a txt file with all .startup file to check faster their instructions

# USAGE: 
# EDIT ->   process_input_file(): at the end of this function there are a bunch
#           of call to functions to create files and folder, 
#           comment and uncomment what is necessary to create things in a faster way
# EDIT ->   create_<target>_file(file_name, info): you decide what to write on the
#           target file modifing what is inside the 
#           'with open(path_to_interface_file, 'w') as output_file:' 
#           adding, deleting, modifying with output.write 
# EDIT IMPORTANT -> whenever you add column to the general_configuration.txt,
#                   ensure that the header row ( first row ) 
#                   match in part of fully the header name

# example of general_configuration.txt
# device,	interface_0,	 ip_0,         interface_1,     ip_1
# pc1,	    0,	        10.0.0.100/24,                 ,
# r1,	    0,	        10.0.0.1/24,        1,	            10.0.1.1/24
# pc2,	    0,	        10.0.1.100/24,                  ,



# ----------- Check for the input file path argument ----------- #
if len(sys.argv) != 2:
    print("Usage: python create_files.py <input_file.txt> \ne.g >>  python create_startup.py my_first_lab/general_configuration.txt")
    sys.exit(1)

# You can place here manually the to path to 
# the file commenting the lines above.
FILE_NAME   = sys.argv[1]   # global/relative path to the file e.g. lab_0/general_configuration.txt
EMPTY_FIELD = ''            # flag to charaterize a non-used filed
STARTUP_SUMMARY_NAME = 'startup_summary.txt'    # name of the generate file containes all startup instructions

# ----------- to create file based od their type ----------- #
USER_ID     = 'pc'
ROUTER_ID   = 'r'
SERVER_ID   = 's'
DHCP_ID     = '_dhcp'

# Used to create <device>/etc/quagga/ospfd.conf
def create_ospfd_file(file_name, info):
    eth_list = [info[key] for key in info.keys() if key.startswith('interface_') and info[key] != EMPTY_FIELD]
    net_area_list = [info[key] for key in info.keys() if key.startswith('net_area') and info[key] != EMPTY_FIELD]
    device_name = info['device']

    file_name = os.path.join( os.path.dirname(file_name), os.path.basename(file_name).split(".")[0])
    path_to_ospfd_file = os.path.join(file_name, "etc", "quagga", "ospfd.conf")

    with open(path_to_ospfd_file, 'w') as output_file:
        output_file.write(f"hostname {device_name}\n")
        output_file.write("password zebra\n\n")

        for eth in eth_list:
            output_file.write(f"interface eth{eth}\n")
            output_file.write("ospf hello-interval 2\n\n")

        output_file.write("router ospf\n")
        for entry in net_area_list:
            ip, area = entry.split("-")
            output_file.write(f"network {ip} area {area}\n")

# Used to create <device>/etc/quagga/zebra.conf
def create_zebra_file(file_name, info):

    eth_list = [info[key] for key in info.keys() if key.startswith('interface_') and info[key] != EMPTY_FIELD]
    ip_list = [info[key] for key in info.keys() if key.startswith('ip_') and info[key] != EMPTY_FIELD]
    device_name = info['device']

    file_name = os.path.join( os.path.dirname(file_name), os.path.basename(file_name).split(".")[0])
    path_to_zebra_file = os.path.join(file_name, "etc", "quagga", "zebra.conf")

    with open(path_to_zebra_file, 'w') as output_file:
        output_file.write(f"hostname {device_name}\n")
        output_file.write("password zebra\n")
        output_file.write("enable password zebra\n\n")

        for i, (eth, ip) in enumerate(zip(eth_list, ip_list)):
            output_file.write(f"interface eth{eth}\n")
            output_file.write(f"ip address {ip}\n")
            output_file.write("link-detect\n\n")

# Used to create <device>/etc/quagga/daemons.conf
def create_daemons_file(file_name):
    file_name = os.path.join( os.path.dirname(file_name), os.path.basename(file_name).split(".")[0])
    path_to_daemons_file = os.path.join(file_name, "etc", "quagga", "daemons.conf")

    with open(path_to_daemons_file, 'w') as output_file:
        output_file.write("zebra=yes\n")
        output_file.write("bgpd=no\n")
        output_file.write("ospfd=yes\n")
        output_file.write("ospf6d=no\n")
        output_file.write("ripd=no\n")
        output_file.write("ripngd=no\n")
        output_file.write("isisd=no\n")
        output_file.write("ldpd=no\n")

# Used to create <device>/etc/network/dhcp/dhcpd.conf
def create_dhcp_file(file_name):
    
    #eth_list    = [info[key] for key in info.keys() if key.startswith('interface_') and info[key] != EMPTY_FIELD] 

    file_name = os.path.join( os.path.dirname(file_name), os.path.basename(file_name).split(".")[0])
    path_to_interface_file = os.path.join(file_name, "etc", "dhcp", "dhcpd.conf")

    with open(path_to_interface_file, 'w') as output_file:

        output_file.write("default-lease-time 3600\n")    
        output_file.write("option domain-name-server <server ip e.g. 8.8.8.8, lab DHCP>\n\n")
        output_file.write(f"subnet <ip_subnet> netmask <ip_netmask> {{ \n")
        output_file.write(f"\trange <ip_from> <ip_to>;\n")
        output_file.write(f"\toption routers <ip_default_gateway>;\n}}")
        
# Convert netmask from integer to binary dot notation
def cidr_to_dec(ip_and_netmask):

    bits = int(ip_and_netmask.split('/')[1])
    
    # create binary strings 
    binary_str = '1' * bits + '0' * (32 - bits)

    # convert to decimals
    octets = [str(int(binary_str[i:i+8], 2)) for i in range(0, 32, 8)]
    
    return '.'.join(octets)

# Used to create <device>/etc/network/interfaces
def create_interfaces_file(file_name, info):

    eth_list    = [info[key] for key in info.keys() if key.startswith('interface_') and info[key] != EMPTY_FIELD] 
    ip_list     = [info[key] for key in info.keys() if key.startswith('ip_') and info[key] != EMPTY_FIELD]

    file_name = os.path.join( os.path.dirname(file_name), os.path.basename(file_name).split(".")[0])
    path_to_interface_file = os.path.join(file_name, "etc", "network", "interfaces")
    

    with open(path_to_interface_file, 'w') as output_file:
            
        for current_eth, current_ip in zip(eth_list, ip_list):
            
            # when dhcp is up
            #output_file.write(f"auto eth{current_eth}\n")
            #output_file.write(f"iface eth{current_eth} inet dhcp\n")

            output_file.write(f"auto eth{current_eth}\n")
            output_file.write(f"iface eth{current_eth} inet static\n")
            output_file.write(f"\taddress {current_ip}\n")
            #output_file.write(f"\taddress {current_ip.split('/')[0]}\n")
            #output_file.write(f"\tnetmask {cidr_to_dec(current_ip)}\n")
            output_file.write(f"\tgateway 192.168.1.1\n\n")

# Function which create and edit startup files with "info" data
def create_startup_file(file_name, info):

    '''
    Args:
        file_name: path to the file
        info: dictionary with information like ip_adresses, eth
    '''

    # info: {'device': 'pc1', 'interface_0': '0', 'ip_0': '10.0.0.100/24', 'interface_1': '', 'ip_1': ''}

    # ----------- Clearing data ( dictionary ) ----------- #
    # create array with all feasible interfaces and ip_address: short for-loop with conditions
    # e.g 
    #       eth_list = ['0']    
    #       ip_list = ['10.0.0.100/24']
    # Empty field ( '' ) are not into dictionary
    eth_list    = [info[key] for key in info.keys() if key.startswith('interface_') and info[key] != EMPTY_FIELD] 
    ip_list     = [info[key] for key in info.keys() if key.startswith('ip_') and info[key] != EMPTY_FIELD]

    default_route_add_list = [info[key] for key in info.keys() if key.startswith('default_route_add') and info[key] != EMPTY_FIELD]
    default_route_to_list = [info[key] for key in info.keys() if key.startswith('default_route_to') and info[key] != EMPTY_FIELD]
    
    # ----------- Writing on file_name ----------- #
    with open(file_name, 'a') as output_file:
            
            # ----------- Device identification ----------- #
            # Extracting only the name of the file discarding the path
            # to identify the type of decive
            file_name_only = os.path.basename(file_name) 
            

            # ----------- File editing ----------- #
            output_file.write("/etc/init.d/networking restart\n\n")

            if USER_ID in file_name_only:

                # setting ip addresses to each interfaces
                for current_eth, current_ip in zip(eth_list, ip_list):
                    output_file.write(f"ip addr add {current_ip} dev eth{current_eth}\n")

                output_file.write("\n")  # to separate different instructions

                # setting default router per file_name device
                for current_default_route_add, current_default_route_to in zip(default_route_add_list, default_route_to_list):
                    output_file.write(f"ip route add {current_default_route_add} via {current_default_route_to}\n")
                    print("added")

                

            elif ROUTER_ID in file_name_only:

                output_file.write("/etc/init.d/quagga restart\n\n")

                # setting ip addresses to each interfaces
                for current_eth, current_ip in zip(eth_list, ip_list):
                    output_file.write(f"ip addr add {current_ip} dev eth{current_eth}\n")

                output_file.write("\n")  # to separate different instructions

                # setting default router per file_name device
                for current_default_route_add, current_default_route_to in zip(default_route_add_list, default_route_to_list):
                    output_file.write(f"ip route add {current_default_route_add} via {current_default_route_to}\n")

            elif SERVER_ID in file_name_only:

                # setting ip addresses to each interfaces
                for current_eth, current_ip in zip(eth_list, ip_list):
                    output_file.write(f"ip addr add {current_ip} dev eth{current_eth}\n")

                output_file.write("\n")  # to separate different instructions
                
                # setting default router per file_name device
                for current_default_route_add, current_default_route_to in zip(default_route_add_list, default_route_to_list):
                    output_file.write(f"ip route add {current_default_route_add} via {current_default_route_to}\n")

# Function to deleted existing startup files
def delete_startup_files():

    # Deleting all .startup files to avoid mistakes
    startup_files = glob.glob(os.path.join(os.path.dirname(os.path.join(os.getcwd(), FILE_NAME)), "*.startup"))

    # Loop through the list and remove each file
    for file_path in startup_files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

# Function to deleted folders of devices
def delete_folder():
    directory_files = glob.glob(os.path.join(os.path.dirname(os.path.join(os.getcwd(), FILE_NAME)), "*"))
    directory_filtered = [ directory_name for directory_name in directory_files if "." not in os.path.basename(directory_name) ]
    #directory_device = [ directory_name for directory_name in directory_filtered if "USER_ID" in os.path.basename(directory_name) or "ROUTER_ID" in os.path.basename(directory_name) or "SERVER_ID" in os.path.basename(directory_name) ]
    directory_device = [
        directory_name for directory_name in directory_filtered
        if re.search(f"{USER_ID}\\d+$", os.path.basename(directory_name))
        or re.search(f"{ROUTER_ID}\\d+$", os.path.basename(directory_name))
        or re.search(f"{SERVER_ID}\\d+$", os.path.basename(directory_name))
    ]
    
    for path in directory_device:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)  # Rimuove la directory e il suo contenuto
                print(f"Deleted directory: {path}")
        except Exception as e:
            print(f"Error deleting {path}: {e}")
    
# Preprocessing of input FILE_NAME It also call "create_startup_file"
def process_input_file():
    # Creating startup files
    with open(FILE_NAME, 'r') as file:

        parsed_first_line = False
        header_content = []   # saving header of th efiled
        for line in file:

            # -----------  Remove useless caracters ----------- #
            # Deleting spaces and tabulation in lines in a way to process data correctly ( csv formattation )
            # e.g.:  r1,0,10.0.0.1/24,1,10.0.1.1/24 ( from above example )
            line = line.strip().replace(" ", "").replace("\t", "")
            if line.strip() == "":
                break

            line = line.split(",")

            # ----------- first line is the header, saving it ----------- #
            if parsed_first_line == False:
                header_content = [key for key in line] # short for-loop
                parsed_first_line = True
                continue
            
            # ----------- Setting up for creation of startup file ----------- #
            # e.g. output -> {'device': 'pc1', 'interface_0': '0', 'ip_0': '10.0.0.100/24', 'interface_1': '', 'ip_1': ''}
            info = {key: EMPTY_FIELD for key in header_content} # dictionary initialization
            for i, current_info in enumerate( info.keys() ):
                
                # not enough information, can stop
                if i >= len(line):
                    break

                info[current_info] = line[i]

            # print(info)


            # ----------- Create startup file  ----------- #
            # Define the output file name (e.g., pc1.startup )
            # will be on the same directory of FILE_NAME.
            path_file_name = os.path.join( os.path.dirname(os.path.join(os.getcwd(), FILE_NAME)), f"{line[0].replace(DHCP_ID, '')}.startup")
            create_startup_file(path_file_name, info) # initialize startup files
            
            # ----------- Create interface file  ----------- #
            os.makedirs(os.path.join( os.path.dirname(path_file_name),  os.path.basename(path_file_name).split('.')[0], 'etc', 'network'), exist_ok=True)  
            create_interfaces_file(path_file_name, info)

            # ----------- Create dhcp file  ----------- #
            if DHCP_ID in line[0]:
                os.makedirs(os.path.join( os.path.dirname(path_file_name),  os.path.basename(path_file_name).split('.')[0], 'etc', 'dhcp'), exist_ok=True)
                create_dhcp_file(path_file_name)
      
            # ----------- Create daemons file  ----------- #
            if ROUTER_ID in line[0]:
                os.makedirs(os.path.join( os.path.dirname(path_file_name),  os.path.basename(path_file_name).split('.')[0], 'etc', 'quagga'), exist_ok=True)
                create_daemons_file(path_file_name)

            # ----------- Create zebra file  ----------- #
            if ROUTER_ID in line[0]:
                os.makedirs(os.path.join( os.path.dirname(path_file_name),  os.path.basename(path_file_name).split('.')[0], 'etc', 'quagga'), exist_ok=True)
                create_zebra_file(path_file_name, info)

            # ----------- Create ospfd file  ----------- #
            if ROUTER_ID in line[0]:
                os.makedirs(os.path.join( os.path.dirname(path_file_name),  os.path.basename(path_file_name).split('.')[0], 'etc', 'quagga'), exist_ok=True)
                create_ospfd_file(path_file_name, info)

# Checkif the input file is correctly formatted
def check_input_file():
    
    corrupted_rows = {}
    expected_commas = 0
    with open(FILE_NAME, 'r') as file:
        for i, line in enumerate(file):
            
            # ----------- counting commas on head ----------- #
            if i == 0:
                expected_commas = line.count(',')
                continue


            #  ----------- check in file is composed correclty  ----------- #
            comma_count = line.count(',')
            
            # Se il numero di virgole non corrisponde al numero atteso, salva la riga
            if comma_count != expected_commas:
                line.strip().replace("\t", " ")
                corrupted_rows[i] = {'current_commas': comma_count, 'line': line.strip()}
    
    if corrupted_rows != {}:
        print(f"\n-- Corrupted raw: check formattation of {os.path.basename(FILE_NAME)}. Startup file may be create wrongly")

        for row_index in corrupted_rows.keys():
            current_commas = corrupted_rows[row_index]['current_commas']
            current_line = corrupted_rows[row_index]['line']

            print(f"-- Row {row_index} -> commas: {current_commas}/{expected_commas}.\n-- Content: {current_line}\n")
    else:
        print(f"-- No know errors found in structure of {os.path.basename(FILE_NAME)}.")

# Generate a txt file with all .startup files 
def summary_startup():

    target_path = os.path.dirname(os.path.join(os.getcwd(), FILE_NAME))
    
    summary_file = os.path.join(target_path, STARTUP_SUMMARY_NAME)
    
    with open(summary_file, 'w') as summary:

        # ----------- Iterate in directory and select .startup files # ----------- #
        for filename in os.listdir(target_path):
            
            if filename.endswith('.startup'):

                # concatenate to obtain path to startup file
                file_path = os.path.join(target_path, filename)
                
                # Write a row to identify startup file
                summary.write(f"\n\t{filename}\n")
                
                # Copy the content of file
                with open(file_path, 'r') as file:
                    content = file.read()
                    summary.write(content)

    print(f"{STARTUP_SUMMARY_NAME} generated in {target_path}")

def main():

    check_input_file()      # check if file is created correcly 
    delete_startup_files()  # to avoid overlapping of instruction, I create them from scratch
    
    confirmation = input("Do you want to proceed with deleting the folder? (Y/N): ").strip().lower()
    if confirmation in ['Y', 'y']:
        delete_folder()
    else:
        print("-- Keeping folders")

    process_input_file()    # creating startup files and respective folder
    summary_startup()       # generate a file which contain all startup

main()

