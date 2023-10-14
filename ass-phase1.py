
# OS: MACOS
import subprocess, re
import csv
import sys
import os
from tabulate import tabulate
from datetime import datetime

# checker: /Users/ashnadesai/Documents/UNI/COMP4336/test.csv

from re import findall
from subprocess import Popen, PIPE

# airport commands to get AP info
scanned_wifi = subprocess.check_output(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/A/Resources/airport","-s"])
if len(scanned_wifi.splitlines()) < 2:
    quit()

SSID = scanned_wifi.decode()
filename = 'test.csv'
table = []
columns = []
# columns to be included in CSV file
# columns = ['time', 'os', 'network interface', 'gps latitude', 'gps longitude', 'gps accuracy (meters)', 'ssid', 'bssid', 'wi-fi standard', 'frequency', 'network channel', 'channel width (in mhz)', 'rssi (in dbm)', 'noise level (in dbm)', 'public ip address', 'network delay (in ms)']
# table.append(columns)

# 'time', 'os', 'network interface', 'gps latitude', 'gps longitude', 'gps accuracy (meters)', 
# 'ssid', 'bssid', 'wi-fi standard', 'frequency', 'network channel', 'channel width (in mhz)', 
# 'rssi (in dbm)', 'noise level (in dbm)', 'public ip address', 'network delay (in ms)'
# write columns to csv
# with open(filename, 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(columns)

# info gathered from Netspot to get info on channel width (not accessible from terminal)
with open('all_networks.csv','r') as networks:
    wifisbyline = networks.readlines()

print(SSID)
# TODO: set value
gps_latitude = [-33.918711]
gps_longitude = [151.228814]
ip = '101.188.67.134'
network_interface = ['en0']

# unchanged vals
time = [int(datetime.now().timestamp())]
my_os = ['MACOS']
gps_accuracy = ['20']
wifi_standard = '802.11'
# write to phase1 csv file
reached_bssi = 0
with open(filename, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    all_aps = SSID.splitlines()[1:]
    for lines in all_aps:
        all_values = []
        values = lines.split()
        if len(values) == 0:
            reached_bssi = 2
            continue
        if reached_bssi > 0:
            reached_bssi -= 1
            continue
        for index,l in enumerate(values):
            if values[index + 2].lstrip('-').isdigit():
                break
        name = ''
        for i, a in enumerate(values):
            if i == index:
                if index > 0:
                    name = name + " " + values[i]
                else:
                    name = name + values[i]
                break
            name = name + values[i]
        list_values = ([name] + values[index+1:])
        all_values = time + my_os + network_interface + gps_latitude + gps_longitude + gps_accuracy + [name] + [list_values[1]]
        
        found = False
        bssid = list_values[1]
        ssid = list_values[0]
        for netspot in wifisbyline:
            netspot_info = netspot.split(',')
            if ssid in netspot_info[0] and bssid in netspot_info[1].lower():
                # append wifi standard
                all_values.append(wifi_standard + netspot_info[3].replace('"', '').replace(" ", ''))
                # append frequency
                #print(int(list_values[3].split(',')[0]))
                all_values.append(netspot_info[4].replace('"', ''))
                channel = list_values[3].split(',')[0]
                all_values.append(int(channel))
                all_values.append(netspot_info[2].replace('"', ''))
                all_values.append(list_values[2])
                all_values.append(netspot_info[5].replace('"', ''))
                found = True
                break
        if not found:
            all_values.append('')
        if name == 'uniwide':
            all_values.append(ip)
        else:
            all_values.append('')

        delay = os.system("ping -c 1 -w2 " + 'unsw.edu.au' + " > /dev/null 2>&1")
        all_values.append(delay)
        if found:
            writer.writerow(all_values)
            table.append(all_values)

print(tabulate(table))

