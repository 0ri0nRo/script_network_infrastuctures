# Network Configuration and Graph Tools

## Disclaimer

Note that this script is intended solely for quickly creating folders and template files. All generated files and configurations require manual review and adjustments to ensure correctness.

## Installation Requirements

Before using the scripts, make sure to install the required libraries:

```bash
pip install networkx matplotlib
pip install --upgrade networkx matplotlib
```

---

## Script 1: `plot_grafo.py`

### Description

This script generates a graph based on the lab configuration contained in a `.conf` file. It is used to quickly visualize the network setup and produces an output file that can be used with other tools.

### Input

- **`.conf`**\*\* File\*\*: The file describing the lab connections (example provided below).

### Usage

1. Open the terminal.
2. Navigate to the folder containing the script:
   ```bash
   cd <path_to_script>
   ```
3. Run the script with the path to the `.conf` file:
   ```bash
   python plot_grafo.py my_first_lab/lab.conf
   ```

### Output

1. An image representing the lab's graph.
2. A `general_configuration.txt` file in CSV format containing the general configuration. This file may require manual corrections.

### Note

The main purpose is to verify the configuration of the `.conf` file. The generated `general_configuration.txt` file might not be correctly formatted and may need manual editing.

#### Example of `.conf` file

```conf
pc1[0]=A
r1[0]=A

r1[1]=B
pc2[0]=B
```

---

## Script 2: `create_startup.py`

### Description

This script generates the `.startup` files needed to configure the network devices based on the `general_configuration.txt` file.

### Usage

1. Complete the `general_configuration.txt` file by manually adding the necessary information.
2. Open the terminal.
3. Navigate to the folder containing the script:
   ```bash
   cd <path_to_script>
   ```
4. Run the script providing the path to the `general_configuration.txt` file:
   ```bash
   python create_startup.py my_first_lab/general_configuration.txt
   ```

### Output

1. `.startup` files with the specified instructions.
2. A summary `.txt` file containing the content of all generated `.startup` files.
3. Folders for each device containing etc/quagga or etc/network directories, depending on the configuration. These directories will include the following initialized files:
   - `etc/network/interfaces`: Configuration for network interfaces.
   - `etc/quagga/daemons.conf`: Configuration file for Quagga daemons.
   - `etc/quagga/zebra.conf`: Configuration for the Zebra daemon.
   - `etc/quagga/ospfd.conf`: Configuration for the OSPF daemon.
   - `etc/dhcp/dhcpd.conf`: Configuration file for DHCP.

---

## Script 3: `create_summary_startup.py`

### Description

This script creates a summary file containing the content of all `.startup` files for quick instruction verification.

### Usage

1. Open the terminal.
2. Navigate to the folder containing the script:
   ```bash
   cd <path_to_script>
   ```
3. Run the script providing the path to the lab directory:
   ```bash
   python create_summary_startup.py my_first_lab
   ```

### Output

- A text file containing the content of all `.startup` files in the specified directory.

### Usage

Useful for quickly checking the instructions contained in the `.startup` files without opening them individually.

---

## Final Notes

- Note that this script is intended solely for quickly creating folders and template files. All generated files and configurations require manual review and adjustments to ensure correctness.

- Ensure you verify the output files to correct any errors.

- Comment or modify the functions to adapt the script to the specific needs of your lab.



