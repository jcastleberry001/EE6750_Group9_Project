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

# -----------------------------
# Parameters
# -----------------------------
AP_POS = '50,50,0'
STA1_START_POS = '50,20,0' # Start within range so STA can associate
STA2_START_POS = '50,80,0'
#STA_END_POS = '50,50,0'
TRIAL_DURATION = 30
TCP_PORT = 5201
UDP_PORT = 5001
MOVE_INTERVAL = 0.2
AP_RANGE = 60 # Coverage range
timesleep_speed = 0.01

print("Cleaning mn and iperf")
os.system("sudo pkill -f iperf3")
os.system("sudo mn -c")

# -----------------------------
# Helper: RSSI logging
# -----------------------------
#def log_rssi(sta, logfile, duration):
# with open(logfile, 'w') as f:
# for t in range(duration):
# rssi = sta.cmd(f"iw dev {sta.name}-wlan0 link | grep signal | awk '{{print
#$2}}'").strip()
# f.write(f"{t},{rssi}\n")
# sleep(1)


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

#for ap in net.aps:
#	ap.cmd('ovs-vsctl set-fail-mode {} standalone'.format(ap.name))

#ap1.cmd('ifconfig ap1 10.0.0.1/24 up')
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

sta2_x, sta2_y = sta2.position[0], sta2.position[2]
sta2_dot, = ax.plot(sta2_x, sta2_y, 'yo', markersize=8, label='STA2')

first_legend = ax.legend(handles=[sta1_dot, sta2_dot, ap_dot], loc='upper right')
ax.add_artist(first_legend)

plt.show()

# -----------------------------
# Start long-running servers
# -----------------------------
tcp_server = sta1.popen(f'iperf3 -s -p {TCP_PORT} --logfile tcp_server.txt')

# -----------------------------
# TCP trial with live movement
# -----------------------------
print("*** TCP trial with STA moving")
#rssi_thread = Thread(target=log_rssi, args=(sta1, "tcp_rssi.txt",TRIAL_DURATION))
#rssi_thread.start()

#tcp_client = sta2.popen(f'iperf3 -c 10.0.0.1 -p {TCP_PORT} -t {TRIAL_DURATION} -i 1')

for t in range(201):
	x = 50
	y1 = 20 + (100 * t / 1000)
	y2 = 80 - (100 * t / 1000)
	
	#Update station coordinates in network logic
	sta1.setPosition(f"{x},{y1},0")
	sta2.setPosition(f"{x},{y2},0")
	
	#Update RSSI	
	rssi_1 = sta1.wintfs[0].rssi
	rssi_2 = sta2.wintfs[0].rssi
	#print(rssi_1)
	#print(rssi_2)
	item1 = f"rssi1 {rssi_1} dB"
	item2 = f"rssi2 {rssi_2} dB"
	receiver_one = mpatches.Patch(color='purple', label=item1)
	receiver_two = mpatches.Patch(color='green', label=item2)
	second_legend = ax.legend(handles=[receiver_one, receiver_two], loc='lower right')
	ax.add_artist(second_legend)

	#Update Matplotlib plot only
	sta1_dot.set_data(x, y1)
	sta2_dot.set_data(x, y2)
	fig.canvas.draw()
	fig.canvas.flush_events()

	#rssi_thread.join()
	tcp_client = sta2.popen(f'iperf3 -c 10.0.0.1 -p {TCP_PORT}')
	time.sleep(timesleep_speed)

print("*** TCP trial complete\n")
info("*** Running CLI\n")
CLI(net)

# -----------------------------
# Stop network
# -----------------------------
#tcp_server.terminate()
#tcp_server.wait()
#net.stop()
