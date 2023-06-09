# Project Journal
## Tuesday, 09.05.2023
### Sebastian Lenzlinger
Add some structure to the project directory. 

The following keyloggers seem promising: [keylogger](https://github.com/arunpn123/keylogger) by arunpn123, which is a keylogger for Linux systems written in C. At this point my understanding is that it is a kernel level keylogger. This is what it says in the Readme. [simple-key-logger](https://github.com/gsingh93/simple-key-logger/tree/master) by gsingh93 is a userspace keylogger. It is also written in C.

Suggested steps of our kernel module:
1. Search the /dev/input/ directory and figrue out which devices correspond to the keyboard.
2. Check who is reading from that file.
3. Somehow figure out what reading is malicious and which not (?!).

Possible flow if it is clearly a user program:
1. On Start, search Keyboard file as above.
2. Start monitoring who has it open.
3. Prompt user to type (randomly)  between 5 - 30 (arbitrary at this point, just to have it limited) characters on the keyboard.
4. Trace where the input is sent.
5. List the processes using it and the files that logged it.

For either path this cannot be the final functionality. It is unclear what is and isn't feasible at this point.
#### Open Questions:
1. What is the main difference between a user space keylogger (operating as root) and a keyloger which initself is a kernel module? What are the essential differences, and is ti really feasible to implement a kernel module that detects malicious kernel activity? Would't we loose usefull abstractions like /dev/ipnut/event* etc. which make it easier to track where I/O goes?
2. What datastructures would a kernel keylogger even use, if it is not storeing the info in user space  ( a log file say). Furthermore, how would it send the info via network? How would we be able to uncover such a datastructure and make it available to a system admin. 
3. How would a kernel keylogger send smth over the network, without any user space component being able to see that (aka not even an admin)?
4. What artifacts besides kernel logs does a kernel module produce. Are any visible in userspace?
5. Would it be possible to expose kernel datastructures to userface without comprimising security?
6. Maybe the app/module is only to be run once as a scan, then one removes the malicous software component, and then returns the OS to a safe state without leakage to user space...
7. Do this questions assume the right underlying model of the linux kernel?

...more ? certainly ...
#### TODOs:
1. Install both keyloggers in a VM and see how their functionality works, and how we would detect them  using system programs. This especially applies to the user space keylogger.
2. Really need to figure out where the effect of kernel module would be seen. If its just logging to a logfile then it's basically as good as a user space program and a system admin could find it. 
#### On what goes into the report
0. Abstract
1. Introduction
2. What is a keylogger
	1. The essential differences of malware in userspace vs embedded into the kernel
3. How do you detect keyloggers
	1. Fundamental difficulties
	2. addressing the difficulties
4. A possible, very constrained solution
5. Bibliography
6. Resources
#### Misc
What is the essential problem? We need to define what problem to solve more precisely and figure out what the essential complexities are. My current understanding is that detecting a keylogger embedded in the kernel is a fundamentally different task than detecting a keylogger that lives in user space (even with root priviledges). 

## Wednesday, 10.05.2023
### Sebastian 
Tested [simple-key-logger](https://github.com/gsingh93/simple-key-logger/tree/master). The following steps get me from getting device file name of keyboard to PID kapturing keystrokes and associated binary executable:
1. `ls -la /dev/ipnut/by-path | grep kbd` -> ../event2
2. `fuser /dev/input/event2` -> 1 880 1774 6327
3. `ls -l /proc/{1, 880, 1774, 63277}/exe` -> gnome-shell, systemd, systemd-logind AND /home/kldetect/simple-key-logger/skeylogger
So this keylogger can easily be found since only 3 other processes wherer reading from the kbd input file. Replicating on my host reveal that it would be similarly easy to snuff out their, as the only processes reading from my keyboard where gnome-shell, systemd and systemd-logind.

Attempting to install [keylogger](https://github.com/arunpn123/keylogger). It fails saying: 
```
make: PWD: No such file or directory
make -C /lib/modules/6.0.7-301.fc37.x86_64/build M= modules
make[1]: *** /lib/modules/6.0.7-301.fc37.x86_64/build: No such file or directory.  Stop.
make: *** [Makefile:4: all] Error 2
```
[This](https://github.com/jarun/spy) keylogger named 'spy' could be installed after installing dkms with `make -f Makefile.dkms`. Then `$ sudo insmod kisni.ko`.
Then `sudo cat /sys/kernel/debug/kisni/keys` will show keys that have been pressed.

After installing some updates and restarting the machine in the VM (Fedora 37) (it updated the kernel) [this](https://github.com/arunpn123/keylogger) was installable but some time after inserting it into kernel the VM freezes. Could replicate a second time. 
It seems after restart kernel modules must be reinserted (even though spy was inserted using dkms).
#### Next Steps:
1. Test some more user space keyloggers and see if it is truly basicallly always very easy to detect them.
2. Figrue out how to detect kernel module kerlogger w/o just scanning for suspiciously named logfiles.

## Thursday, 11.05.2023
### Michel
I was able to recreate all the steps Sebastian did on wednesday 10.05.2023. The only difference was, that on a ubuntu VM, the third step `ls -l /proc/{1, 880, 1774, 63277}/exe` has to be executed a little bit differently. I wasnt able to give out a list of all processes at once. I had to check each PID individually, to see which PID belongs to which process.

## Sunday, 14.05.23
### Sebastian
Talked to Dr. Eleliemy. Now have the following plan for the project:
Two parts: One User Space detector that can more or less aggressivly kill uknown processes reading from I/O files. Should be configurable how aggressive it treats found loggers. From Just informing the user to auto SIGINT KILL, for instance. The Second part of thew Software checks kernel modules and probably just notifies user. There should be some db where we have Kernel Modules known to use I/O, so kind of a list of "Trusted I/O Drivers/Modules". 
Here's an overview of the steps in the part of the programm that detects programm that have event files open which are not standard processes:
1. Use the `opendir()` function to open the directory `/dev/input/by-path/` and iterate over its contents using `readdir()`.
For each file in the directory, use the `strstr()` function to check if the file name contains "kbd" or "keyboard".
2. For each file that contain "kbd" or "keyboard", use readlink() to read the symbolic link, and get the device file that is mapped to it.
3. For each directory in `/proc/` check if the name is a numeric value and whenever it is, open `/proc/[PID]/fd/` and go over context with `readdir()`. If any of the filnames in there correspond to the ones found in step 2, it is a process that has a kbd device file open.
4. *TODO: FINNISH*

## Friday, 19.05.23
### Michel
`lsmod` shows most loaded kernel modules and who and how many use it at the moment.
I/O Module responsible for keyboard drivers is not fully listed with `lsmod`. With `ll /lib/modules/5.19.0-35-generic/kernel/drivers/input/keyboard`one can list all drivers connected in some way to the Keyboard.
I tried `hwinfo` to list all hardware on a device. To use it one needs to do `sudo apt install hwinfo`. With `hwinfo --short` one gets a short information list about devices and drivers / what they are. Further investigation is required.
TODO: Find a way to list all processes using those keyboard Kernel Modules

#### Next Step:
1. Learn how kernel modules read I/O and how it is detectable.
2. Start coding the user space detector part of the software.


## Saturday, 3. June 2023
### Sebastian
Instead of using c now used bash to make a script that
1. finds `/dev/input/event*` that correspond to keyboard files and writes them in a file.
2. checks which pids use those files and writes those into a file.
3. checks to which programms/executables the pids correspond to.
Still need to finnish it.

_TODO_: Add functionality that is asks user if the malicious process should be killed. I.e. add some configuration functionality. Finnish Step 3. in mentioned bash script.

## Monday, 5. June 2023
### Michel
Systemtap allowes one to write stap scripts and compile them as kernel modules. Linetimes.stp is usefull to filter functioncalls. With some slight modification (needs some more research) we could use it to filter all modules that perform the "register_keyboard_notifier" function inside of the kernel. Currently, it only lists events that happen durring probing. So the 'spy' keylogger has to be loaded as a kernel module for it to show up whilst monitoring. One could compile the systemtap script as a kernel module and load it very early on boot. That also would require some more research. Detecting the "register_keyboard_notifier" function call does not seem efficient.

### Sebastian
Ported the bash script for user space detection to python for easier string and list handling. Also finnished the main functionality: The script finds processes listening to the device input files and uses blacklists, autokill lists and whitelists to decide which ones to kill. It then asks the users which programs that it couldn't resolve by itself should be killed.

#### TODO:
Test in VM and finnishing touches to smooth things out.
## Tuesday, 6. June 2023
### Sebastian
Did a first test in a Fedora 37 VM. At first it didn't work. Then I tested it on my normal machine and it also stopped working. It turned out that it was just not getting the root priviledges right, even tho it passed the root check. Testing on the VM was then succesfull in that it found the pids. Killing the process wasn't succesfull and will need further testing and fixes.
#### TODO:
1. Fix the bug where the killing of the process doesn't work.
~~2. Build config files, maybe check if there is a better way to to do configs than with .txt files.~~ (finnished 6.06.23)
3. Keep testing. Goal is that if run as '''$ sudo ./kldetect.py -v''' one is prompted to kill the keylogger, and then rerunning the programm would give the output '''[+] No suspicious programms found'''
~~4. Note to self: Problem with killing is that not using pids-program dict to choose which program to kill.~~ 
#### Later that same say
Configuration is now done with json to keep it all central.
Test with json configuration works. 
Killing a process still doesn't work:
''' TypeError: 'str' object cannot be interpreted as integer '''
## Wednesday, 7. June 2023, night
### Sebastian
This is the latest output aftert a test run where actually 3 processes has keyloggers runnig.
```
[kldetect@fedora src]$ sudo ./keylogger_detector.py 
[sudo] password for kldetect: 
/usr/sbin/fuser
/usr/bin/which
[+] No suspicious processes found
[kldetect@fedora src]$ sudo ./keylogger_detector.py 
/usr/sbin/fuser
/usr/bin/which
[+] No suspicious processes found
[kldetect@fedora src]$ cat config.
cat: config.: No such file or directory
[kldetect@fedora src]$ cat config.json 
{"white_listed_programs": ["systemd", "gnome-shell"], "auto_kill_programs": ["skeylogger", "skeylogger", "skeylogger", "skeylogger", "skeylogger"], "kbd_names": ["kbd"]}[kldetect@fedora src]$ sudo ./keylogger_detector.py -v
[Verbose] Input options set
[Verbose] Root access checked
/usr/sbin/fuser
/usr/bin/which
[Verbose] Packages checked
[Verbose] Config file loaded
[Verbose] Config file parsed
[Verbose] Keyboard device files found: []
[Verbose] Process IDs using keyboard device files: []
[Verbose] Process names using keyboard device files: []
[Verbose] Suspicious processes found: []
[Verbose] Suspicious processes not killed: []
[Verbose] Suspicious processes killed: []
[+] No suspicious processes found
```
This is after extensivly refactoring because I was starting to loose oversight over the code. So I split it up into utils, config and keylogger_detector.
#### TODO:
1. Ivestigate and bug fix
## Wednesday, 7. June 2023, day
### Sebastian
VirtualBox stopped working so after much pain I decided to switch to Boxes. There the install of Fedora 37 went smoothly.
Then Started testing the userland detector on [simple-key-logger](https://github.com/gsingh93/simple-key-logger/tree/master), [logkeys](https://github.com/kernc/logkeys).
[pykeylogger](https://github.com/amoffat/pykeylogger) produced a segmentation fault, after I finaly got it to run. Trying to run [py-keylogger](https://github.com/hiamandeep/py-keylogger), turns out it only runs on X11 it seem (so we'd not catch it anyway).
[keylog](https://github.com/SCOTPAUL/keylog) was succesfully detected and removed.
All in all, the main functionality works as intended. Basically now would be the refinement phase to add more options or to have a way to configure the config.json file more easily.
#### TODO
1. Write report
2. Add functionality to userspace detector

## Wednesday, 7, June 2023
### Michel


I have written 1 systemtap scripts, that can detect, whenever a module registers at the Keyboard-notifier. The Script can currently detect whenever a module registers. My script cant detect which kernel module registered. Here comes Sebastians idea of writing a python script, that can unload all un-known modules and loads them back in, whilst the stap-script is running. Whenever a module is loaded in, and it triggers the stap-script, we know it is tracking key-strokes. Those modules will be shown to the user and the user then has to decide whether to unload and remove them, or keep them. My script is based on a redhat-script. The redhat-script is called funcall_tracer2.stp . The idea behind both scripts is the same. My script is simplyfied for the use with python. 

