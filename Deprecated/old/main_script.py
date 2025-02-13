import os
import glob
import shutil
import re
import pandas as pd
import csv
EMPTY_FIELD = ""
USER_ID = "pc"
ROUTER_ID = "r"
SERVER_ID = "s"
DHCP_ID = "dhcp"
FILE_NAME = "network_config.csv"
STARTUP_SUMMARY_NAME = "summary_startup.txt"

def create_daemons_file(file_name):
    file_name = os.path.join(os.path.dirname(file_name), os.path.basename(file_name).split(".")[0])
    path_to_daemons_file = os.path.join(file_name, "etc", "quagga", "daemons.conf")
    os.makedirs(os.path.dirname(path_to_daemons_file), exist_ok=True)
    
    with open(path_to_daemons_file, 'w') as output_file:
        output_file.write("zebra=yes\n")
        output_file.write("bgpd=no\n")
        output_file.write("ospfd=yes\n")
        output_file.write("ospf6d=no\n")
        output_file.write("ripd=no\n")
        output_file.write("ripngd=no\n")
        output_file.write("isisd=no\n")
        output_file.write("ldpd=no\n")

def create_dhcp_file(file_name):
    file_name = os.path.join(os.path.dirname(file_name), os.path.basename(file_name).split(".")[0])
    path_to_dhcp_file = os.path.join(file_name, "etc", "dhcp", "dhcpd.conf")
    os.makedirs(os.path.dirname(path_to_dhcp_file), exist_ok=True)
    
    with open(path_to_dhcp_file, 'w') as output_file:
        output_file.write("default-lease-time 3600\n")
        output_file.write("option domain-name-server 8.8.8.8;\n\n")
        output_file.write("subnet <ip_subnet> netmask <ip_netmask> {\n")
        output_file.write("\trange <ip_from> <ip_to>;\n")
        output_file.write("\toption routers <ip_default_gateway>;\n}")

def cidr_to_dec(ip_and_netmask):
    bits = int(ip_and_netmask.split('/')[-1])
    binary_str = '1' * bits + '0' * (32 - bits)
    octets = [str(int(binary_str[i:i+8], 2)) for i in range(0, 32, 8)]
    return '.'.join(octets)

def create_interfaces_file(file_name, info):
    eth_list = [info[key] for key in info.keys() if key.startswith('interface_') and info[key] != EMPTY_FIELD]
    ip_list = [info[key] for key in info.keys() if key.startswith('ip_') and info[key] != EMPTY_FIELD]
    
    file_name = os.path.join(os.path.dirname(file_name), os.path.basename(file_name).split(".")[0])
    path_to_interface_file = os.path.join(file_name, "etc", "network", "interfaces")
    os.makedirs(os.path.dirname(path_to_interface_file), exist_ok=True)
    
    with open(path_to_interface_file, 'w') as output_file:
        for current_eth, current_ip in zip(eth_list, ip_list):
            output_file.write(f"auto eth{current_eth}\n")
            output_file.write(f"iface eth{current_eth} inet static\n")
            output_file.write(f"\taddress {current_ip.split('/')[0]}\n")
            output_file.write(f"\tnetmask {cidr_to_dec(current_ip)}\n")
            output_file.write(f"\tgateway 192.168.1.1\n\n")

def create_startup_file(file_name, info):
    """Crea un file di startup con le informazioni fornite."""
    with open(file_name, 'w') as output_file:
        output_file.write(f"# Startup file per {info['device']}\n")
        output_file.write("/etc/init.d/networking restart\n\n")

        # Configura le interfacce
        for i in range(2):  # ip_0 e ip_1
            interface = info.get(f"interface_{i}")
            ip = info.get(f"ip_{i}")
            if interface and ip:
                output_file.write(f"ip addr add {ip} dev eth{interface}\n")

        # Configura la route di default se presente
        if info.get("default_route_add") and info.get("default_route_to"):
            output_file.write(f"ip route add {info['default_route_add']} via {info['default_route_to']}\n")

    print(f"Creato {file_name}")
def delete_startup_files():
    startup_files = glob.glob("*.startup")
    for file_path in startup_files:
        os.remove(file_path)

def delete_folder():
    device_dirs = [d for d in glob.glob("*") if os.path.isdir(d) and re.match(r'(pc|r|s)\d+', d)]
    for path in device_dirs:
        shutil.rmtree(path)

def process_input_file():
    # Legge il file CSV e lo processa correttamente
    with open(FILE_NAME, 'r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            info = {key: row[key] if row[key] else EMPTY_FIELD for key in row}

            # Controllo che il campo 'device' esista
            if 'device' not in info:
                print(f"Errore: 'device' non trovato in {row}")
                continue

            file_name = f"{info['device']}.startup"
            print(f"Generando file di startup per {info['device']}...")
            
            # Qui puoi chiamare create_startup_file() o altre funzioni necessarie
            create_startup_file(file_name, info)


def check_input_file():
    corrupted_rows = {}
    with open(FILE_NAME, 'r') as file:
        expected_commas = next(file).count(',')
        for i, line in enumerate(file, start=2):
            if line.count(',') != expected_commas:
                corrupted_rows[i] = line.strip()
    if corrupted_rows:
        print("-- Corrupted rows detected:")
        for row, content in corrupted_rows.items():
            print(f"Row {row}: {content}")
    else:
        print("-- No errors found in input file.")

def summary_startup():
    with open(STARTUP_SUMMARY_NAME, 'w') as summary:
        for filename in glob.glob("*.startup"):
            with open(filename, 'r') as file:
                summary.write(f"\n\t{filename}\n")
                summary.write(file.read())
    print(f"{STARTUP_SUMMARY_NAME} generated.")

# Eseguire il controllo e la generazione dei file
check_input_file()
delete_startup_files()
delete_folder()
process_input_file()
summary_startup()
