#!/usr/bin/env python3

import os # for going directories
import subprocess # for running commands, in particular fuser
import sys # for exiting
import signal # for killing processes


white_listed_programs_file = 'config/white_listed_programs.txt'
auto_kill_programs_file = 'config/auto_kill_programs.txt'
kbd_names_file = 'config/kbd_names.txt'
auto_kill_option = False
verbose_option = False
safe_option = False
kbd_names = ['kbd']

# Check if the user is in sudo mode
def check_sudo():
    if os.geteuid() != 0:
        print("[-] Please rerun as root")
        sys.exit(1)

# Check if the user has the required packages installed
def check_packages():
    packages = ['fuser']
    missing_packages = []
    for package in packages:
        try:
            subprocess.check_call(['which', package])
        except subprocess.CalledProcessError:
            missing_packages.append(package)
    if len(missing_packages) > 0:
        print("[-] Please install the following packages:", str(missing_packages))
        sys.exit(1)

       
    

# Follow symlinks to find real path
def get_real_path(path):
    if os.path.islink(path):
        return os.path.realpath(path)
    else:
        return path

# get keyboard device files
def get_keyboard_device_files():
    keyboard_device_files = []
    for root, dirs, files in os.walk('/dev/input/by-path'):
        for file in files:
            if any(kbd_name in file for kbd_name in kbd_names):
                keyboard_device_files.append(get_real_path(os.path.join(root, file)))
    return keyboard_device_files

# print a list to a file separated by newlines
def print_list_to_file(list, file):
    with open(file, 'w') as f:
        for item in list:
            f.write("%s\n" % item)

# find pids using file using fuser
def get_pids(file):
    try:
        pids = subprocess.check_output(['fuser', file]).decode('utf-8').split()
    except subprocess.CalledProcessError:
        if verbose_option:
            print("[-] Error: fuser failed to run on", file)
        return []
    #pids = [int(pid) for pid in pids]
    return pids

# clear a file
def clear_file(file):
    open(file, 'w').close()


# find programm name using pid
def get_program_name(pid):
    status_file = '/proc/' + str(pid) + '/status'
    with open(status_file, 'r') as f:
        # See cat /proc/[pid]/status | grep Name
        for line in f:
            if line.startswith('Name:'):
                program_name = line.split(":")[1].strip()
                return program_name

# proces input arguments and set options
def set_input_arguments():
    global auto_kill_option
    global verbose_option
    if len(sys.argv) > 1:
        if '-a' in sys.argv:
            auto_kill_option = True
        if '-v' in sys.argv:
            verbose_option = True
        if '-s' in sys.argv:
            safe_option = True

# initialize kbd_names based on input file
def initialize_kbd_names():
    global kbd_names
    try:
        with open(kbd_names_file, 'r') as f:
            for line in f:
                kbd_names.append(line.strip())
    except:
        pass # default is kbd_names=['kbd'] as set at the top
                             
# ask user to confirm a list of programs to kill
def confirm_kill_programs(programs, times=0):
    print("Confirm to kill the following programs:")
    for program in programs:
        print(program)
    print("y/n?")
    answer = input()
    if answer == 'y':
        return True
    elif answer == 'n':
        return False
    else:
        if times > 5:
            print("[-] Too many tries. Exiting")
            sys.exit(1)
        print("[-] Please answer y or n")
        return confirm_kill_programs(programs, times+1)

# kill list of processes
def kill_processes(pids):
    for pid in pids:
        os.kill(pid, signal.SIGKILL)
        if verbose_option:
            print("[-] Killed process with pid", pid)

# the main program starts here
def detect_keyloggers():
    ###############################
    # Step 0: Check minimal requirements/ Set up
    ###############################
    check_sudo()
    check_packages()
    set_input_arguments()
    ###############################
    # Step 1: Get keyboard device files
    ###############################
    keyboard_device_files = get_keyboard_device_files()
    clear_file('keyboard_device_files.txt')
    print_list_to_file(keyboard_device_files, 'keyboard_device_files.txt')

    ###############################
    # Step 2: Get pids using keyboard device files
    ###############################
    pids = []
    for file in keyboard_device_files:
        pids += get_pids(file)
    pids = sorted(list(set(pids)))
    clear_file('pids.txt')
    print_list_to_file(pids, 'pids.txt')

    ###############################
    # Step 3: Get program names using pids
    ###############################
    program_names = []
    program_pid_dict = {}
    auto_kill_programs = []
    white_listed_programs = []

    # Get white listed programs
    try:
        with open(white_listed_programs_file, 'r') as f:
            for line in f:
                white_listed_programs.append(line.strip())
    except:
            pass    
        
    # Get auto kill programs
    try:
        with open(auto_kill_programs_file, 'r') as f:
            for line in f:
                auto_kill_programs.append(line.strip())
    except:
            pass

    # Get program names
    for pid in pids:
        program_name = get_program_name(pid)
        program_pid_dict[program_name] = pid
        if auto_kill_option and program_name in auto_kill_programs:
            os.kill(pid, signal.SIGKILL)
            if verbose_option:
                print("[-] Auto-Killed process", program_name, "with pid", pid)
        else:
            program_names.append(program_name)
    program_names = sorted(list(set(program_names)))

    # Identify suspicious programs
    suspicious_programs = []
    for program_name in program_names:
        if program_name not in white_listed_programs:
            suspicious_programs.append(program_name)





    if verbose_option:
        ###############################=
        # Intermezzo: Print results
        ###############################
        print("Keyboard device files:")
        for file in keyboard_device_files:
            print(file)
        print("")
        print("Pids:")
        for pid in pids:
            print(pid)
        print("")
        print("Program names:")
        for program_name in program_names:
            print(program_name)
        print("")

    if len(suspicious_programs) == 0:
        print("[+] No suspicious programs found")
        sys.exit(0)
    
    ###############################
    # Step 4: Ask user to kill any suspicious programs
    ###############################
    print("Suspicious programs:")
    for program_name in suspicious_programs:
        print(program_name)
    user_input = input("Please enter any program/ that should be kept from running. Use the whitespace(spacebar) to separate values.") 
    if user_input == '':
        print("[-] No programs to kill")
        sys.exit(0)
    
    programs_to_kill = user_input.split()
    programs_to_kill = [program_name for program_name in programs_to_kill if program_name in suspicious_programs] # Filter out programs that are not suspicious
    pids_to_kill = []
    for program_name in programs_to_kill:
        pids_to_kill.append(program_pid_dict[program_name])
    
    if safe_option:
        if confirm_kill_programs(programs_to_kill):
            kill_processes(pids_to_kill)
    else:
        kill_processes(pids_to_kill)

if __name__ == "__main__":
    detect_keyloggers()

