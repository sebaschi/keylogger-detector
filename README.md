# KLDetect
KLDetect is a keylogger detector for the Linux Desktop.
It can detect processes reading from ```/dev/input/event*``` devices and kernel modules registered to listen to keyboard events.

# Dependencies
* [Python](https://www.python.org/downloads/)
* [SystemTap](https://sourceware.org/systemtap/wiki)
* [```fuser```](https://www.man7.org/linux/man-pages/man1/fuser.1.html)
* Utilities that come with [Fedora](https://fedoraproject.org/) like ```which```.

# Setup
Download or clone this repository:
```
git clone https://github.com/sebaschi/keylogger-detector.git
```
Navigate into the src directory:
```
cd keylogger-detector/src
```
Run a keylogger. KLDetect has been tested and shown to work on the following keylogger.

User progams:
* [simple-key-logger](https://github.com/gsingh93/simple-key-logger/tree/master)
* [logkeys](https://github.com/kernc/logkeys)
* [keylog](https://github.com/SCOTPAUL/keylog)


Kernel Module:
* [spy](https://github.com/jarun/spy)

# Usage 
KLDetect **must** be run as root (sudo). 
If KLDetect is not run as root the user is reminded to try again with root permissions.

Running without options just runs userspace detection:
```
./kldetect.py
```
To get a list of command line options:
```
./kldetect.py -h
```
To run with kernel module detection:
```
./kldetect.py -k
```
To run just kernel module detection
```
./kernel_detector.py
```

# Warning
Running any part if this program in a lightheaded manner may break your system.
Killing processes and unloading modules should be done with caution. We suggest testing it an a VM.
If one runs the KLDetect with the kernel module keylogger detection option set, make sure to update the [whitelist.txt](https://github.com/sebaschi/keylogger-detector/blob/main/src/whitelist.txt) with the safe kernel modules that you know you have on your system. In particular we highly suggest running ```lsmod > <path-to-kldetect>/whitelist.txt```, before inserting a kernel keylogger. This writes the modules currently inserted in the kernel to the whitelist. This way 'normal' modules that you already have installed on the 'clean' kernel will not accidentally be unloaded. Altough KLDetect should not unload any kernel modules currently used, better safe than sorry.

# Developers
Copyright © 2023[Michel Romancuk](https://github.com/SoulKindred), [Sebastian Lenzlinger](https://github.com/sebaschi)





This project is Part of a Univeristy project at the [Operating Systems](https://dmi.unibas.ch/de/studium/computer-science-informatik/lehrangebot-fs23/vorlesung-operating-systems-1/) lecture at the University of Basel, Switzerland.
 A project journal can be found [here](https://github.com/sebaschi/keylogger-detector/blob/main/doc/dev_journal.md).
