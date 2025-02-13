import sys
import os

# KEYBOARD INPUT: 
# 1.   open terminal
# 2.   navigate in a folder ( e.g. >> Desktop )
# 4.   run the program:     ( e.g. >> python crreate_summary_startup.py my_first_lab )

# OUTPUT:
# 1. a txt file with all .startup file to check faster their instructions

# USAGE: 
# It can be used to generate a txt with the content of all startup files
# to check more fast data and instruction into them.


# ----------- Check for the input file path argument ----------- #
if len(sys.argv) != 2:
    print("Usage: python create_summary_startup.py <path_to_folder_containing_startups> \ne.g >>  python create_summary_startup.py Desktop/my_first_lab")
    sys.exit(1)

# You can place here manually the to path to 
# the file commenting the lines above.
FILE_PATH   = sys.argv[1]   # path to folder which contain .startup files
STARTUP_SUMMARY_NAME = 'startup_summary.txt'    # name of the generate file containes all startup instructions

# Generare a txt file with all .startup files 
def summary_startup():

    target_path = os.path.join( os.getcwd(), FILE_PATH )
    
    summary_file = os.path.join(target_path, STARTUP_SUMMARY_NAME)
    
    with open(summary_file, 'w') as summary:

        # ----------- Iterate in directory and select .startup files ----------- #
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

    summary_startup()       # generate a file which contain all startup

main()

