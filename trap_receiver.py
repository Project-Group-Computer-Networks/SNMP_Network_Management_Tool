import subprocess
import os

# Command to run
command = ['sudo', 'tcpdump', '-i', 'any', 'port', '162']

# Define the working directory (Desktop)
working_directory = os.path.expanduser('~/Desktop')

# Define output log files
output_log_file = 'outputlog.txt'
error_log_file = 'errorlog.txt'

try:
    # Open output and error log files
    with open(os.path.join(working_directory, output_log_file), 'a') as log_file, \
         open(os.path.join(working_directory, error_log_file), 'a') as error_file:

        # Execute the command
        print("Starting tcpdump... (Press Ctrl+C to stop)")
        while True:
            # Run the command
            process = subprocess.run(command, stdout=log_file, stderr=error_file, cwd=working_directory)
                   

except KeyboardInterrupt:
    print("Stopped capturing SNMP traps.")
except Exception as e:
    print(f"An error occurred: {e}")






