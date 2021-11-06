import socket
import os
import time
import tkinter as tk
import requests

def reboot_device():
	try:
		os.system("sudo reboot")
	except Exception as a:
		print("this will reboot")

def scanDevices():
	deviceList = []
	device_id = []
	no_data = ['no Data']
	try:
		getWlan = os.system("sudo iwlist wlan0 scan | grep ESSID | sed -e 's/^\s*//' -e '/^$/d' | tr -d '\"' > files/mySSID.txt")
		readWlan = open('files/mySSID.txt', 'r').readlines()
		print(readWlan)
		for Wlan in readWlan:
			if Wlan.startswith('ESSID:CTL'):
				Wlan = Wlan[6:]
				deviceList.append(Wlan)
		for x in deviceList:
			if x.endswith('\n'):
				x = x[:-1]
			device_id.append(x)
		readWlan.clear()
		return device_id, True
	except Exception as e:
		print('error:', e)
		return no_data, False


def knowAddress():
	try:
		myAddress = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())
								[2] if not ip.startswith("127.")][:1],
								 [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
								   [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
		return myAddress
	except:
		return '0.0.0.0'

def registerDevice(ssid,psk,server_id,targetIP,ip_len):
	query = 'http://' + targetIP + '/setting'
	print(query)
	myIP = knowAddress()
	payload = {'ssid':ssid,'pass':psk,'queip':server_id, 'ip_len':str(ip_len)}
	req = requests.post(query,data=payload, timeout=1)
	print("status code",req)
	return True


def verifyCheck():
	targetIP = 'http://192.168.4.1/'
	req = requests.get(targetIP)
	r = req.json()
	return r

def postServer(device_name, switch_position, value, server_ip, timeout_delay):
	if value == 1: #
		newValue = "ON"
	elif value == 0:
		newValue = "OFF"
	request_query = 'http://' + server_ip + '/postupdate'
	payload = {'device_name': device_name, 'switch_position':switch_position, 'status': newValue}
	req = requests.post(request_query,payload,timeout=timeout_delay)

def postSwitch(ip_address, switch_position, value, server_ip, timeout_delay):
	if value == 1: #
		newValue = "true"
	elif value == 0:
		newValue = "false"
	if switch_position == 1:
		switch_type = "Switch1"
	elif switch_position == 2:
		switch_type = "Switch2"
	try:
		request_query = "http://" + ip_address + "/query?" + switch_type + "=" + newValue
		print(request_query)
		req = requests.post(request_query, timeout=timeout_delay)
	except Exception as e:
		print('errorT:', e)

def send_controller_ip(controller_name, server_ip_address, timeout_delay):
	ip_address = knowAddress()
	payload = {'controller_name': controller_name, 'ip_address' : ip_address}
	request_query = 'http://' + server_ip_address + '/sendipcontroller'
	try:
		req = requests.post(request_query, json=payload, timeout=timeout_delay)
		print('send ip to server:', ip_address)
	except:
		print("error sending ip to server")


def post_change(device_name, switch_position,recent_change, server_ip, timeout_delay):
	request_query = 'http://' + server_ip + '/recentchange'
	payload = {'device_name': device_name, 'switch_position':switch_position, 'recent_change': recent_change}
	req = requests.post(request_query,json=payload,timeout=timeout_delay)