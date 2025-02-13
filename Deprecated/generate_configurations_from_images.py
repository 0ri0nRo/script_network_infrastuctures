import cv2
import pytesseract
import re
import os

def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

def parse_network_configuration(text):
    devices = {
        "r4": [("image", "<ip>"), ("0", "<ip>"), ("1", "<ip>"), ("2", "<ip>"), ("3", "<ip>")],
        "r5": [("image", "<ip>"), ("0", "<ip>"), ("1", "<ip>"), ("2", "<ip>"), ("3", "<ip>")],
        "pc1": [("0", "<ip>")],
        "r1": [("0", "<ip>"), ("1", "<ip>"), ("2", "<ip>"), ("3", "<ip>")],
        "r2": [("0", "<ip>"), ("1", "<ip>")],
        "r3": [("0", "<ip>"), ("1", "<ip>")],
        "r8": [("0", "<ip>"), ("1", "<ip>"), ("2", "<ip>")],
        "r7": [("0", "<ip>"), ("2", "<ip>"), ("1", "<ip>"), ("3", "<ip>")],
        "r6": [("0", "<ip>"), ("1", "<ip>"), ("2", "<ip>"), ("3", "<ip>")],
        "s1": [("0", "<ip>")],
        "r9": [("0", "<ip>"), ("1", "<ip>")],
        "s2": [("0", "<ip>")],
        "pc2": [("0", "<ip>")]
    }
    return devices

def generate_configuration_file(devices, output_file):
    max_interfaces = max(len(interfaces) for interfaces in devices.values())
    
    header = "device" + ", " + ", ".join([f"interface_{i}, ip_{i}" for i in range(max_interfaces)])
    with open(output_file, 'w') as f:
        f.write(header + "\n")
        for device, interfaces in devices.items():
            interfaces_str = ", ".join([f"{iface}, {ip}" for iface, ip in interfaces])
            missing_commas = header.count(",") - interfaces_str.count(",")
            f.write(f"{device}, {interfaces_str}{',' * missing_commas}\n")

def main(image_path):
    text = extract_text_from_image(image_path)
    devices = parse_network_configuration(text)
    output_file = os.path.join(os.path.dirname(image_path), "general_configuration.txt")
    generate_configuration_file(devices, output_file)
    print(f"Configuration file saved: {output_file}")

if __name__ == "__main__":
    image_path = "path/to/image.png"  # Modifica con il percorso corretto
    main(image_path)
