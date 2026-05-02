#!/usr/bin/env python3
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.node import OVSKernelAP, Station, UserAP
from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI
from mininet.link import TCLink
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import time
from time import sleep
from threading import Thread
import os
from matplotlib.animation import FuncAnimation
import json
import re

# -----------------------------
# Parameters
# -----------------------------
AP_POS = '50,50,0'
TCP_PORT = 5201
UDP_PORT = 5001
MOVE_INTERVAL = 0.2
AP_RANGE = 60 # Coverage range
timesleep_speed = 0
STOP_POSITION = 80
STA1_START_POS = '50,20,0'
STA2_START_POS = '50,80,0'
curr_dir = os.getcwd()

print("Cleaning mn and iperf")
os.system("sudo pkill -f iperf3")
os.system("sudo mn -c")
os.system("sudo pkill -f ping")

# -----------------------------
# Create network
# -----------------------------
print("Creating controller")
net = Mininet_wifi(controller=Controller, link=wmediumd,
accessPoint=OVSKernelAP, autoSetMacs=True, autoStaticArp=True)

c0 = net.addController('c0')
print("Creating AP1")
ap1 = net.addAccessPoint('ap1', ssid='wifi-test', mode='g', channel='1',
position=AP_POS, range=AP_RANGE, wlans=2)

print("Creating sta1")
sta1 = net.addStation('sta1', ip='10.0.0.1/24', position=STA1_START_POS)

print("Creating sta2")
sta2 = net.addStation('sta2', ip='10.0.0.2/24', position=STA2_START_POS)

print("Setting up propogation model")
net.setPropagationModel(model="logDistance", exp=4)

net.configureWifiNodes()
net.plotGraph(max_x=100, max_y=100)

print("Starting network")
net.start()

sleep(1)

# -----------------------------
# Helper: move STA gradually + update plot
# -----------------------------
plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_title("Live Mininet-WiFi Simulation")

#Plot AP
ap_dot, = ax.plot(ap1.position[0], ap1.position[1], 'ro', markersize=12, label='AP1')

#Plot station/clients
sta1_x, sta1_y = sta1.position[0], sta1.position[1]
sta1_dot, = ax.plot(sta1_x, sta1_y, 'bo', markersize=8, label='STA1')

sta2_x, sta2_y = sta2.position[0], sta2.position[1]
sta2_dot, = ax.plot(sta2_x, sta2_y, 'yo', markersize=8, label='STA2')

first_legend = ax.legend(handles=[sta1_dot, sta2_dot, ap_dot], loc='upper right')
ax.add_artist(first_legend)

plt.show()
fig.canvas.draw()
background = fig.canvas.copy_from_bbox(ax.bbox)

#Iperf server
tcp_server = sta1.popen(f'iperf3 -s -p {TCP_PORT} --logfile tcp_server.txt')

#Iperf client
tcp_client = sta2.popen(f'iperf3 -c 10.0.0.1 -t {TCP_PORT} -b 0 -i 1 -t 0 > --logfile iperf.txt')

#Ping logging
pingsta1 = sta1.popen(f'stdbuf -oL ping 10.0.0.2 > {curr_dir}/ping_log.txt', shell=True)

iperf_file = open("iperf.txt", "w")

def get_latest_bitrate(filename="iperf.txt"):
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
        
        # Search from bottom to top for the last valid data line
        for line in reversed(lines):
            if "Gbits/sec" in line:
                parts = line.split()
                value = parts[-5]
                value1 = float(value)
                #print(f"Found throughput: {value1} Mbits/sec")
                value2 = value1*1000
                return float(value2)
            elif "Mbits/sec" in line:
            	parts = line.split()
            	value = parts[-5]
            	#print(f"Found throughput: {value} Mbits/sec")
            	return float(value)
                
    except (FileNotFoundError, ValueError, IndexError) as e:
        print(f"Error reading throughput: {e}")
        return 0
    
    return 0

def get_latest_ping(filename="ping_log.txt"):
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
        
        for line in reversed(lines):
            # Check for "time" (making it case-insensitive just in case)
            if "time" in line.lower():
                # Look for "time=" or "time<", then capture the digits/decimals right after it
                match = re.search(r'time[=<]([\d.]+)', line, re.IGNORECASE)
                
                if match:
                    value = match.group(1) # Extracts just the number (e.g., '14.2')
                    return float(value)
                    
    except (FileNotFoundError, ValueError, IndexError) as e:
        print(f"Error reading ping: {e}")
        return 0
        
    return 0

#Open log file
log_file = open("experiment_log.txt", "w")
log_file.write("time,sta1_y,y_diff,rssi1,throughput,rtt,estimated latency\n")


#Initial starting positions
y1 = 20
y2 = 80
# -----------------------------
# TCP trial with live movement
# -----------------------------
print("*** TCP trial with STA moving")

rssi_1 = sta1.wintfs[0].rssi
rssi_2 = sta2.wintfs[0].rssi
item1 = f"rssi1 {rssi_1} dB"
item2 = f"rssi2 {rssi_2} dB"

receiver_one = mpatches.Patch(color='purple', label=item1)
receiver_two = mpatches.Patch(color='green', label=item2)
second_legend = ax.legend(handles=[receiver_one, receiver_two], loc='lower right')

time.sleep(10)
distance_moved = 0
step_size = 0.07
start_time = time.time()

while y1 <= STOP_POSITION:
	x = 50
	#y1 = y1 + .07
	#y2 = y2 - .07
	y1 = y1 + step_size
	y2 = y2 - step_size
	
	y_diff = abs(y1-y2)
	distance_moved += step_size
	
	def update_and_log():
		global rssi_1, rssi_2, second_legend
		iperf_bitrate = get_latest_bitrate()
		rtt = get_latest_ping()
		est_latency = rtt/2
		
		#Update RSSI	
		rssi_1 = sta1.wintfs[0].rssi
		rssi_2 = sta2.wintfs[0].rssi
		
		current_time = time.time() - start_time
		log_file.write(f"{current_time},{y1},{y_diff},{rssi_1},{iperf_bitrate},{rtt},{est_latency}\n")
		log_file.flush()
	

		sta1_dot.set_data(x, y1)
		sta2_dot.set_data(x, y2)
		receiver_one.set_label(f"rssi1 {rssi_1} dB")
		receiver_two.set_label(f"rssi2 {rssi_2} dB")
		second_legend.get_texts()[0].set_text(f"rssi1 {rssi_1} dB")
		second_legend.get_texts()[1].set_text(f"rssi2 {rssi_2} dB")

		ax.draw_artist(sta1_dot)
		ax.draw_artist(sta2_dot)
		ax.draw_artist(second_legend)

		#second_legend = ax.legend(handles=[receiver_one, receiver_two], loc='lower right')
		fig.canvas.blit(ax.bbox)
		fig.canvas.flush_events()
		
	#Update station coordinates in network logic
	sta1.setPosition(f"{x},{y1},0")
	sta2.setPosition(f"{x},{y2},0")
	update_and_log()
	
	if distance_moved >= 5.0:
		print(f"*** Traveled 5m. Pauing for 5 seconds at y1={y1:.2f}")
		pause_start = time.time()
		while(time.time() - pause_start) < 5.0:
			update_and_log()
			
			if timesleep_speed > 0:
				time.sleep(timesleep_speed)
		distance_moved = 0
	else:
		if timesleep_speed > 0:
			time.sleep(timesleep_speed)

	
log_file.close()
iperf_file.close()
pingsta1.terminate()
os.system("sudo pkill -f iperf3")
os.system("sudo pkill -f ping")

time, y_diff, rssi, throughput, rtt, latency = [], [], [], [], [], []
with open('experiment_log.txt', 'r') as f:
    next(f)  # Skip the first line
    for line in f:
        values = line.split(',')
        time.append(values[0])
        y_diff.append(values[2])
        rssi.append(values[3])
        throughput.append(values[4])
        rtt.append(values[5])
        latency.append(values[6])

#fig = plt.figure()
#ax = plt.subplot(2,2,1)
#fig.suptitle("TCP Metrics")
#ax.plot(y_diff,throughput)
#ax.set_title('y_diff vs throughput, TCP')
#ax.set_xlabel("Distance from STAs, (m)")
#ax.set_ylabel("Throughput, (MBits/sec)")
#ax = plt.subplot(2,2,2)
#ax.plot(time,rssi)
#ax.set_title('rssi over time, TCP')
#ax.set_xlabel("time, (s)")
#ax.set_ylabel("rssi, (dBm)")
#ax = plt.subplot(2,2,3)
#ax.plot(time,latency)
#ax.set_title('latency over time, TCP')
#ax.set_xlabel("time, (s)")
#ax.set_ylabel("latency, (s)")
#ax = plt.subplot(2,2,4)
#ax.plot(time,rtt)
#ax.set_title('Rtt, TCP')
#ax.set_xlabel("time, (s)")
#ax.set_ylabel("Rtt, (s)")
#plt.show()

print("*** TCP trial complete\n")
info("*** Running CLI\n")
#CLI(net)
