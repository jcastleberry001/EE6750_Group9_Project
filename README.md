# EE6750_Group9_Project

Please perform the following steps to use this code:
1) Download VirtualBox from: https://www.virtualbox.org/wiki/Downloads
2) Download VirtualBox Extension Pack from: https://www.virtualbox.org/wiki/Downloads
3) Download Mininet-Wifi VM Image from: https://mininet-wifi.github.io/get-started/
4) Open VirtualBox, then click File > Import Appliance
5) Search for mn-wifi-vm.ova and import.
  <img width="147" height="171" alt="1) Import Appliance" src="https://github.com/user-attachments/assets/dea0b051-400e-40f4-80eb-e0a18bee4cfd" />
 <img width="235" height="183" alt="2) Import ova" src="https://github.com/user-attachments/assets/eb1b2178-3e2d-4c84-9d0f-db4b8c8e3a72" />
 
6) From the Virtual Box screen click "Start" to boot the VM.
   <img width="1276" height="1397" alt="3) VM start" src="https://github.com/user-attachments/assets/e068b91c-e020-4943-9c74-c1240c6b290f" />
   
7) After booting, CNTRL + ALT + T to open a bash shell.
   <img width="1028" height="1058" alt="image" src="https://github.com/user-attachments/assets/7cfbc3be-1c63-4c0c-9184-0d233be1d165" />
   
8) Copy and paste "v2_tcp.py" and "v2_udp.py" to the VM, and make sure it has the ".py" extension.
9) In the shell, move directory to v1.py.
    <img width="879" height="196" alt="4) cd" src="https://github.com/user-attachments/assets/4a165576-e815-402b-867c-e2b93c20ea8c" />
    
10) In the shell, write "sudo python v2_tcp.py" (for TCP traffic mobility)
    <img width="1005" height="175" alt="TCP file" src="https://github.com/user-attachments/assets/09f2023f-6e8d-4176-bb7d-ffec8317e1e2" />
    or "sudo python v2_udp.py" (for UDP traffic mobility) to execute the script.
    <img width="995" height="178" alt="UDP file" src="https://github.com/user-attachments/assets/b9c27d6d-4aa4-46c8-9ee2-f00681ba4e75" />

    
12) If the script executed correctly, two figures should open like shown below.
    <img width="1221" height="1123" alt="6) Figures" src="https://github.com/user-attachments/assets/0a6313f8-9e2f-4570-8e68-5cc425121bc3" />
