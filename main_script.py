import os
import pandas as pd

def create_device_directories(csv_file):
    # Leggi il file CSV
    df = pd.read_csv(csv_file)
    
    # Estrai le righe uniche per ciascun dispositivo
    devices = df.dropna(subset=['Device'])  # Rimuovi le righe senza 'Device'
    
    # Crea le cartelle per ogni dispositivo
    for device, device_data in devices.groupby('Device'):
        # Crea il percorso per il dispositivo
        device_path = os.path.join(device.strip(), "etc", "network")
        os.makedirs(device_path, exist_ok=True)

        # Crea il file 'interfaces' per ogni dispositivo
        with open(os.path.join(device_path, "interfaces"), 'w') as f:
            f.write(f"# Network configuration for {device}\n")
            
            # Aggiungi la configurazione delle interfacce di rete
            for _, row in device_data.iterrows():
                # Gestisci i PC
                if row['isPC'] == 't':
                    device_type = "PC"
                    gateway = row['gateway'] if pd.notna(row['gateway']) else ""
                    netmask = row['Netmask'] if pd.notna(row['Netmask']) else "255.255.255.0"
                    
                    # Configurazione per i PC
                    f.write(f"\n# {device_type} - Interface eth0\n")
                    f.write(f"auto eth0\n")
                    f.write(f"iface eth0 inet static\n")
                    f.write(f"    address {row['address']}\n")
                    f.write(f"    netmask {netmask}\n")
                    if gateway:
                        f.write(f"    gateway {gateway}\n")
                # Gestisci i Router
                else:
                    device_type = "Router"
                    netmask = row['Netmask'] if pd.notna(row['Netmask']) else "255.255.255.0"
                    
                    # Scrivi la configurazione per il router
                    f.write(f"\n# {device_type} - Interface {row['ethX']}\n")
                    f.write(f"iface eth{row['ethX']} inet static\n")
                    f.write(f"    address {row['address']}\n")
                    f.write(f"    netmask {netmask}\n")
                    # Se il gateway è presente, aggiungilo
                    gateway = row['gateway'] if pd.notna(row['gateway']) else ""
                    if gateway:
                        f.write(f"    gateway {gateway}\n")
        
        # Crea il file vuoto 'lab.conf' alla radice dell'albero delle directory
        with open("lab.conf", 'w') as f:
            pass  # Crea un file vuoto
        
        # Crea un file 'device.startup' per ogni dispositivo alla radice
        startup_file_path = f"{device}.startup"
        with open(startup_file_path, 'w') as f:
            pass  # Crea un file vuoto
    
    print("Device directories, interfaces files, lab.conf, and device.startup files created successfully!")

# Esegui lo script con il file CSV
create_device_directories("devices.csv")
