#!/usr/bin/python3
import tkinter as tk
from tkinter import ttk
from tkinter import *
import sys , random, time, requests, json
import PIL
from PIL import Image, ImageTk
from time import sleep
from request_functions import *
from backend_functions import *
import threading


import tkinter as tk



LARGE_FONT= ("Verdana", 9)
MEDIUM_FONT= ("Verdana", 8)

status_one = []
status_two = []
switch_one_name = []
switch_two_name = []
ip_address = []
mac_address = []
id_name = []
device_status = []
imgStatusOne = 0
imgStatusTwo = 0
server_memory_switch_one = []
server_memory_switch_two = []
device_memory_switch_one = []
device_memory_switch_two = []
connected_to_server = True
debug = True
scan_button =''
remove_button =''

spoof_ssid = "dajwdsad"
spoof_psk = "sdawdas"
spoof_server_ip = "dadwaawdadwd"


ssid= getWifiCredentials('ssid')
psk = getWifiCredentials('pass')
server_id = getWifiCredentials('serverip')
timeout_delay = getWifiCredentials('timeout')
ssid= ssid[:-1]
psk = psk[:-1]
server_id = server_id[:-1]
timeout_delay = float(timeout_delay[:-1])
print("Wifi-SSID:", ssid)
print("Wifi-password:", psk)
print("server ip_address:", server_id)
print("timeout delay:", timeout_delay)

controller_ip_address = knowAddress();
print('controller ip address:', controller_ip_address)

#send ip to server
controller_name = "server_controller"
send_controller_ip(controller_name,server_id,timeout_delay)


request_query_server = 'http://' + server_id + '/devicestatus'

def get_server_data():
    global id_name
    global switch_one_name
    global switch_two_name
    global status_one
    global status_two
    global ip_address
    global device_status
    global connected_to_server
    request_query = 'http://' + server_id + '/getdevices'
    try:
        req = requests.post(request_query, timeout=timeout_delay)
        data_dict = json.loads(req.text)
        connected_to_server = True
    except Exception as e:
        print("errorG: yeha", e)
        print("proceed to get previous settings")
        connected_to_server = False
        with open('Config/lastconfiguration.ini') as json_file:
            data_dict = json.load(json_file)
        print('done getting previous setting')

    if connected_to_server:
        with open('Config/lastconfiguration.ini', 'w') as outfile:
            json.dump(data_dict, outfile)
    for y in range(0,len(data_dict)):
        id_name.append(data_dict[y]['device_name'])
        switch_one_name.append(data_dict[y]['switch_one_name'])
        switch_two_name.append(data_dict[y]['switch_two_name'])
        status_one.append(data_dict[y]['status_one'])
        status_two.append(data_dict[y]['status_two'])
        ip_address.append(data_dict[y]['ip_address'])
        #device_status.append(data_dict[y]['device_status'])


#call function above
get_server_data()

#get update on every ip and know thier statuses, upodate the server statuses

def update_server():
    global id_name
    global device_status
    for y in range(0, len(id_name)):
        request_query_device = "http://" + ip_address[y] + "/"
        request_query_server = 'http://' + server_id + '/devicestatus'
        try:
            req = requests.get(request_query_device, timeout=timeout_delay)
        except Exception as e:
            print('error getting info:', e)
            req = "unavailable"

        if req != "unavailable":
            req_json = req.json()
            if req_json['Switch1'] == "ON":
                swt_one_status = 0
            elif req_json['Switch1'] == "OFF":
                swt_one_status = 1
            if req_json['Switch2'] == "ON":
                swt_two_status = 0
            elif req_json['Switch2'] == "OFF":
                swt_two_status = 1
            try:
                postServer(id_name[y],1, swt_one_status,server_id,timeout_delay)
                postServer(id_name[y],2, swt_two_status,server_id,timeout_delay)
            except Exception as e:
                print('cannot connect')
            try:
                device_status.append(1)
                payload = {'device_name': id_name[y], 'device_status': 1}
                req = requests.post(request_query_server, json=payload, timeout=timeout_delay)
                print("success")
            except:
                print("no connection to server")

        else:
            print("device unavailable")
            try:
                payload = {'device_name': id_name[y], 'device_status': 0}
                req = requests.post(request_query_server, json=payload, timeout=timeout_delay)
            except Exception as e:
                print("no connection to server:", e)

            device_status.append(0)


update_server()
    #this will have memory object for every id_name
for status in status_one:
    server_memory_switch_one.append(status)
    device_memory_switch_one.append(status)
for status in status_two:
    server_memory_switch_two.append(status)
    device_memory_switch_two.append(status)




class controlSystem(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)
        self.frames = {}

        for F in (StartPage,ScanPage,SettingPage,RemovePage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self,container):
        frame = self.frames[container]
        frame.tkraise()
        self.winfo_toplevel().title("TUPC-WBHCS")

class StartPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        StartPage.guiLabels(self)
        StartPage.guiScanButton(self,controller)
        StartPage.guiSettingButton(self, controller)
        StartPage.guiDeviceName(self)
        StartPage.guiSwitchName(self)
        StartPage.guiStatusOne(self)
        StartPage.guiStatusTwo(self)
        StartPage.guiOnButton(self)
        StartPage.guiOffButton(self)
        StartPage.guiRemoveDevice(self,controller)
        self.after(10, StartPage.update_status(self))




    def update_status(self):
        global status_one
        global status_two
        global imgStatusTwo
        global imgStatusOne
        global ip_address
        global server_memory_switch_one
        global server_memory_switch_two
        global connected_to_server
        global device_status
        global scan_button
        global remove_button
        ########### Server Scan Mode START
        try :
            request_query = 'http://'+ server_id + '/datadump'
            req_server = requests.get(request_query, timeout=timeout_delay)
            server_data = json.loads(req_server.text)
            device_position = 0
            for data in server_data:
                ip_address[device_position] = data['ip_address']
                if data['status_one'] == 0 and data['status_one'] != server_memory_switch_one[device_position]:
                     status_one[device_position] = 0
                     server_memory_switch_one[device_position] = 0
                     device_memory_switch_one[device_position] = 0
                     imgStatusOne.after(10, StartPage.guiStatusOne(self))
                     try:
                        postSwitch(ip_address[device_position], 1, 0,server_id,timeout_delay)
                     except:
                         print('cannot send to switch')
                if data['status_one'] == 1 and data['status_one'] != server_memory_switch_one[device_position]:
                    status_one[device_position] = 1
                    server_memory_switch_one[device_position] = 1
                    device_memory_switch_one[device_position] = 1
                    imgStatusOne.after(10, StartPage.guiStatusOne(self))
                    try:
                        postSwitch(ip_address[device_position], 1, 1,server_id,timeout_delay)
                    except:
                        print('cannot send to switch')
                if data['status_two'] == 0 and data['status_two'] != server_memory_switch_two[device_position]:
                    status_two[device_position] = 0
                    server_memory_switch_two[device_position] = 0
                    device_memory_switch_two[device_position] = 0
                    imgStatusTwo.after(10, StartPage.guiStatusTwo(self))
                    try:
                        postSwitch(ip_address[device_position], 2, 0,server_id,timeout_delay)
                    except:
                        'cannot connect to switch'
                if data['status_two'] == 1 and data['status_two'] != server_memory_switch_two[device_position]:
                    status_two[device_position] = 1
                    server_memory_switch_two[device_position] = 1
                    device_memory_switch_two[device_position] = 1
                    imgStatusTwo.after(10, StartPage.guiStatusTwo(self))
                    try:
                        postSwitch(ip_address[device_position], 2, 1,server_id,timeout_delay)
                    except:
                        print('cannot send to switch')
                device_position += 1
            connected_to_server = True
        except Exception as e:
            print("no data:", e)
            connected_to_server = False
        # guiScanButton guiRemoveDevice
        self.after(10, StartPage.guiLabels(self))
        #self.after(10, StartPage.guiScanButton(self,controller))

        #if connected_to_server == False:
            #scan_button.config(state=DISABLED)
            #remove_button.config(state=DISABLED)
        #else:
            #scan_button.config(state="normal")
           # remove_button.config(state="normal")
        #self.after(10, StartPage.guiRemoveDevice(self,controller))
        ########### Server Scan Mode END

        ########## Device Scan Mode Start
        try:
            device_position = 0
            for device_ip in ip_address:
                request_query_device = "http://" + device_ip + "/"
                try:
                    req_device = requests.get(request_query_device, timeout=timeout_delay)
                    device_status_value = 1
                    device_status[device_position] = device_status_value

                    payload = {'device_name': id_name[device_position], 'device_status': device_status_value}
                    req = requests.post(request_query_server, json=payload, timeout=timeout_delay)
                except Exception as a:

                    req_device = "unavailable"
                    device_status_value = 0
                    device_status[device_position] =device_status_value


                    payload = {'device_name': id_name[device_position], 'device_status': device_status_value}
                    req = requests.post(request_query_server, json=payload, timeout=timeout_delay)
                    ################################
                    #print(a)
                if req_device != "unavailable":
                    req_json = req_device.json()
                    if req_json['Switch1'] == "ON":
                        swt_one_status = 0
                    elif req_json['Switch1'] == "OFF":
                        swt_one_status = 1
                    if req_json['Switch2'] == "ON":
                        swt_two_status = 0
                    elif req_json['Switch2'] == "OFF":
                        swt_two_status = 1
                # kapag OFF(1) at ON(1)
                    if swt_one_status == 1 and swt_one_status == device_memory_switch_one[device_position]:
                        status_one[device_position] = 0
                        server_memory_switch_one[device_position] = 0
                        device_memory_switch_one[device_position] = 0
                        imgStatusOne.after(10, StartPage.guiStatusOne(self))
                        try:
                            postServer(id_name[device_position],1,1,server_id,timeout_delay)
                            post_change(id_name[device_position],1,"Switch",server_id,timeout_delay)
                        except:
                            print('cannot send to server')
                        print("OFF THE SERVER - SWITCH1")
                    if swt_one_status == 0 and swt_one_status == device_memory_switch_one[device_position]:
                        status_one[device_position] = 1
                        server_memory_switch_one[device_position] = 1
                        device_memory_switch_one[device_position] = 1
                        imgStatusOne.after(10, StartPage.guiStatusOne(self))
                        try:
                            postServer(id_name[device_position], 1, 0,server_id,timeout_delay)
                            post_change(id_name[device_position], 1, "Switch", server_id, timeout_delay)
                        except:
                            print('cannot send to server')
                        print("ON THE SERVER - SWITCH1")
                    if swt_two_status == 1 and swt_two_status == device_memory_switch_two[device_position]:
                        status_two[device_position] = 0
                        server_memory_switch_two[device_position] = 0
                        device_memory_switch_two[device_position] = 0
                        imgStatusTwo.after(10, StartPage.guiStatusTwo(self))
                        try:
                            postServer(id_name[device_position], 2, 1,server_id,timeout_delay)
                            post_change(id_name[device_position], 2, "Switch", server_id, timeout_delay)
                        except:
                            print('cannot send to server')
                        print("OFF THE SERVER - SWITCH2")
                    if swt_two_status == 0 and swt_two_status == device_memory_switch_two[device_position]:
                        status_two[device_position] = 1
                        server_memory_switch_two[device_position] = 1
                        device_memory_switch_two[device_position] = 1
                        imgStatusTwo.after(10, StartPage.guiStatusTwo(self))
                        try:
                            postServer(id_name[device_position], 2, 0,server_id,timeout_delay)
                            post_change(id_name[device_position], 2, "Switch", server_id, timeout_delay)
                        except:
                            print('cannot send to server')
                        print("ON THE SERVER - SWITCH2")
                device_position += 1
        except Exception as e:
            print('error yada:',e)
        self.after(10, StartPage.guiOnButton(self))
        self.after(10, StartPage.guiOffButton(self))
        ########## Device Scan Mode END

        self.after(4000, self.update_status)

    def guiSettingButton(self,controller):
        setting_button = ttk.Button(self, text='Settings', command=lambda : controller.show_frame(SettingPage))
        setting_button.grid(row=0, column= 4, pady=(10, 0))


    def guiRemoveDevice(self,controller):
        global id_name
        global remove_button
        remove_button = ttk.Button(self, text="Remove Device",command=lambda : controller.show_frame(RemovePage))
        if id_name != []:
            remove_button.grid(row=2, column=4, pady=(5, 0))
        else:
           remove_button.grid(row=2, column=4, pady=(5, 0))


    def guiScanButton(thisWindow,controller):
        global id_name
        global scan_button
        scan_button = ttk.Button(thisWindow, text="Register Device",
                                command=lambda : controller.show_frame(ScanPage))
        scan_button.grid(row=2, column=3, pady=(5, 0))


    def guiLabels(thisWindow):
        global id_name
        labelServer = tk.Label(thisWindow, anchor="center", relief="sunken")
        orig_color =labelServer.cget('bg')
        #connected_to_server = False
        if connected_to_server == True:
            labelServer.grid_forget()
            labelServer.config(text="    connected to server    ", bg=orig_color)
        else:
            labelServer.grid_forget()
            labelServer.config(text="not connected to server", bg = 'red')
        labelServer.grid(row=0, column=0, columnspan=2, sticky='S', ipady = 2, ipadx = 20,pady=(5, 0))
        ip_address_label_name = "IP Address: " + controller_ip_address
        labelIP = tk.Label(thisWindow, text=ip_address_label_name, anchor="center", relief="sunken")
        labelIP.grid(row=0, column=2, columnspan=2, sticky='S', ipady = 2, ipadx = 2)
        if id_name != []:
            labelDevice = ttk.Label(thisWindow, text="Device Name", relief='ridge', anchor="center")
            labelDevice.grid(row=2, column=0, ipadx=7, padx=(5, 0), pady=(10,0))
            labelSwitch2 = ttk.Label(thisWindow, text="Switch Name", relief='ridge', anchor="center")
            labelSwitch2.grid(row=2, column=1, ipadx=7, pady=(10,0))
            labelStatus3 = ttk.Label(thisWindow, text="Status", relief='ridge', anchor="center")
            labelStatus3.grid(row=2, column=2, ipadx=7, pady=(10,0))

    def guiDeviceName(thisWindow):
        global id_name
        if id_name != []:
            x = 4
            for nameLabel in id_name:
                ct = [random.randrange(256) for x in range(3)]
                brightness = int(round(0.299 * ct[0] + 0.587 * ct[1] + 0.114 * ct[2]))
                ct_hex = "%02x%02x%02x" % tuple(ct)
                bg_colour = '#' + "".join(ct_hex)
                nameLabel = tk.Label(thisWindow, text=nameLabel, fg='White' if brightness < 120 else 'Black',
                                     bg=bg_colour, font=LARGE_FONT)
                nameLabel.grid(row=x, column=0, ipady=10, ipadx=10, pady=3, rowspan=2)
                x = x + 2
        else:
            noDeviceLabel = tk.Label(thisWindow, text="No Devices", font=("Verdana", 13))
            noDeviceLabel.grid(row=3, column=0, ipady=10, ipadx=10, pady=3, rowspan=2)



    def guiSwitchName(thisWindow):
        global switch_one_name
        global switch_two_name
        x = 4
        for switchLabel in switch_one_name:
            switchLabel = tk.Label(thisWindow, text=switchLabel)
            switchLabel.grid(row=x, column=1)
            x = x + 2
        x = 5
        for switchLabel in switch_two_name:
            switchLabel = tk.Label(thisWindow, text=switchLabel)
            switchLabel.grid(row=x, column=1)
            x = x + 2

    def guiStatusOne(thisWindow):
        global status_one
        global imgStatusOne
        x = 4
        pos = 1
        for imageLabel in status_one:
            if imageLabel == 1:
                image = Image.open('Config/ON.png')
            elif imageLabel == 0:
                image = Image.open('Config/OFF.png')
            render = ImageTk.PhotoImage(image)
            imgStatusOne = tk.Label(thisWindow, image=render)  # ,
            # command= lambda imageLabel=imageLabel,pos=pos: tryFunction(imageLabel,switchNumber,pos))
            imgStatusOne.image = render
            imgStatusOne.grid(row=x, column=2)
            x = x + 2
            pos = pos + 1

    def guiStatusTwo(thisWindow):
        global imgStatusTwo
        global status_two
        pos = 1
        x = 5
        for imageLabel in status_two:
            imageON = Image.open('Config/ON.png')
            imageOFF = Image.open('Config/OFF.png')
            renderON = ImageTk.PhotoImage(imageON)
            renderOFF = ImageTk.PhotoImage(imageOFF)
            if imageLabel == 1:
                image = imageON
                render = renderON
            elif imageLabel == 0:
                image = imageOFF
                render = renderOFF
            imgStatusTwo = tk.Label(thisWindow, image=render)  # ,
            imgStatusTwo.image = render
            imgStatusTwo.grid(row=x, column=2)
            x = x + 2
            pos = pos + 1

    def guiOnButton(thisWindow):
        global id_name
        global device_status
        list_lenght = len(id_name) * 2
        x = 4
        for pos in range(0, list_lenght):
            onButton = ttk.Button(thisWindow, text="ON",
                                  command=lambda pos=pos: StartPage.onDecision(pos, thisWindow))
            onButton.grid(row=x, column=3, ipadx=4, padx=3)
            if device_status[pos // 2] == 0:
                onButton.config(state=DISABLED)
            elif device_status[pos // 2] == 1:
                onButton.config(state="normal")
            x += 1

    def guiOffButton(thisWindow):
        global id_name
        global device_status
        list_lenght = len(id_name) * 2
        x = 4
        device_pos = 0
        for pos in range(0, list_lenght):
            offButton = ttk.Button(thisWindow, text="OFF",
                                   command=lambda pos=pos: StartPage.offDecision(pos, thisWindow))
            offButton.grid(row=x, column=4, ipadx=4)
            if device_status[pos//2] == 0:
                offButton.config(state=DISABLED)
            elif device_status[pos//2] == 1:
                offButton.config(state="normal")
            x += 1

    def onDecision(position, thisWindow):
        global status_one
        global status_two
        global imgStatusOne
        global imgStatusTwo
        #global ip_address
        checkSwitchPosition = (position % 2) + 1
        devicePosition = (position // 2)
        print("device name is: ", id_name[devicePosition])
        print("Switch Position:", checkSwitchPosition)
        if checkSwitchPosition == 1:
            try:
                postServer(id_name[devicePosition],checkSwitchPosition,0,server_id,timeout_delay)
                #post_change(id_name[device_position], 1, "Switch", server_id, timeout_delay)
                post_change(id_name[devicePosition],checkSwitchPosition,"Controller",server_id,timeout_delay)
                print('postserver on')
            except:
                print('cannot send to server')
            try:
                postSwitch(ip_address[devicePosition], checkSwitchPosition, 1, server_id, timeout_delay)
                print('postswitch on')
            except:
                print('cannot send to switch')
            postSwitch(ip_address[devicePosition],checkSwitchPosition,1,server_id,timeout_delay)
            status_one[devicePosition] = 1
            imgStatusOne.after(10, StartPage.guiStatusOne(thisWindow))
            print(status_one)
        elif checkSwitchPosition == 2:
            try:
                postServer(id_name[devicePosition], checkSwitchPosition, 0,server_id,timeout_delay)
                post_change(id_name[devicePosition], checkSwitchPosition, "Controller", server_id, timeout_delay)
            except:
                print('cannot send to server')
            try:
                postSwitch(ip_address[devicePosition], checkSwitchPosition, 1, server_id, timeout_delay)
            except:
                postSwitch('cannot send to switch')
            status_two[devicePosition] = 1
            imgStatusTwo.after(10, StartPage.guiStatusTwo(thisWindow))
            print(status_two)



    def offDecision(position, thisWindow):
        global status_one
        global status_two
        global imgStatusOne
        global imgStatusTwo
        checkSwitchPosition = (position % 2) + 1
        devicePosition = (position // 2)
        print("device name is: ", id_name[devicePosition])
        print("Switch Position:", checkSwitchPosition)
        if checkSwitchPosition == 1:
            try:
                postServer(id_name[devicePosition], checkSwitchPosition, 1,server_id,timeout_delay)
                post_change(id_name[devicePosition], checkSwitchPosition, "Controller", server_id, timeout_delay)
            except:
                print('errorA: cannot send to server')
            try:
                postSwitch(ip_address[devicePosition], checkSwitchPosition, 0, server_id, timeout_delay)
            except:
                print('errorB: cannot send to switch')
            status_one[devicePosition] = 0
            imgStatusOne.after(10, StartPage.guiStatusOne(thisWindow))
            print(status_one)
        elif checkSwitchPosition == 2:
            try:
                postServer(id_name[devicePosition], checkSwitchPosition, 1,server_id,timeout_delay)
                post_change(id_name[devicePosition], checkSwitchPosition, "Controller", server_id, timeout_delay)
            except:
                print('error cannot send to server')
            try:
                postSwitch(ip_address[devicePosition], checkSwitchPosition, 0, server_id, timeout_delay)
            except:
                print('error, cannot send to switch')
            status_two[devicePosition] = 0
            imgStatusTwo.after(10, StartPage.guiStatusTwo(thisWindow))
            print(status_two)



msgLabel =0

class ScanPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        global msgLabel
        label = ttk.Label(self, text="Scan Page",font=LARGE_FONT)
        label.grid(row=0, column=0,pady=10, padx=10)
        button1 = ttk.Button(self,text="Main Window",
                            command=lambda: controller.show_frame(StartPage))
        button1.grid(row=0 ,column=1, padx=10, pady=(5,0))
        button_scan = ttk.Button(self, text="Scan Network", command= lambda: self.after(10, ScanPage.update_scan(self)))
        button_scan.grid(row=0 ,column=2, padx=10, pady=(5,0))

    def update_scan(self):
        deviceList, deviceBool = scanDevices()

        x = 1
        for deviceName in deviceList:
            deviceLabel = ttk.Label(self, text=deviceName, font=LARGE_FONT)
            deviceLabel.grid(row=x, column=0, padx=(5, 0))
            x += 1
        x = 1
        if deviceBool == True:  ## please change to true, for debuging purposes only if false
            for pos in range(0, len(deviceList)):
                deviceButton = ttk.Button(self, text="Full Registration",
                                          command=lambda pos=pos: popupmsg(deviceList[pos],pos))
                deviceButton.grid(row=x, column=1, padx=5)
                if deviceList[pos] in id_name:
                    device_register_status = True
                    device_wifi_status = False
                else:
                    device_register_status = False
                    device_wifi_status = True
                if connected_to_server == False or device_register_status == True:
                    deviceButton.config(state=DISABLED)
                    print('a')
                else:
                    deviceButton.config(state="normal")
                    print('b')
                wlan_register_button = ttk.Button(self, text="Wi-Fi Registration Only",
                                          command=lambda pos=pos: ScanPage.wifi_register(self))
                wlan_register_button.grid(row=x, column=2, padx=5)
                if device_wifi_status == True:
                    wlan_register_button.config(state=DISABLED)
                    print('c')
                else:
                    wlan_register_button.config(state="normal")
                    print('d')
                x += 1


    def wifi_register(self):
        popup = tk.Tk()
        popup.wm_title("Register device from wifi")

        def leavemini():
            try:
                default_ip = "192.168.4.1"
                status_code = registerDevice(ssid, psk, server_id, default_ip, len(server_id))
            except Exception as e:
                status_code = False
                registerLabel1.config(text="error! are you sure you're in device AP?", bg='red')
            if status_code == True:
                popup.destroy()
                success_msg()

        registerLabel1 = tk.Label(popup, text="Please connect to the device Wi-Fi,")
        registerLabel1.grid(row=0, column=0, padx=10, pady=10)
        registerLabel2 = tk.Label(popup, text='press register(NOTE: This system needs to reboot)')
        registerLabel2.grid(row=1, column=0, padx=10, pady=10)
        registerButton = tk.Button(popup, text="Register", command=lambda: leavemini())
        registerButton.grid(row=2, column=0)
        popup.mainloop()



    def guiErrorLabel(thisWindow,bool=True,pos=0):
        global msgLabel
        if bool == False:
            msgLabel = ttk.Label(thisWindow, text="Please Try Again", font=LARGE_FONT)
            msgLabel.grid(row=pos, column=2)
        else:
            msgLabel = ttk.Label(thisWindow, text="Registered", font=LARGE_FONT)
            msgLabel.grid(row=pos, column=2)

    def guiRegisterDevice(self,pos):
        global errorLabel

class SettingPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        SettingPage.gui_label(self)
        SettingPage.gui_entry(self,controller)

    def gui_entry(self,controller):
        self.server_string = StringVar()
        self.ssid_string = StringVar()
        self.psk_string = StringVar()
        self.timeout_string =StringVar()
        server_entry = ttk.Entry(self, textvariable=self.server_string)
        server_entry.grid(row=1, column=1, pady=(10, 0))
        server_entry.delete(0, END)
        server_entry.insert(0, server_id)

        ssid_entry = ttk.Entry(self, textvariable=self.ssid_string)
        ssid_entry.grid(row=2, column=1, pady=(10, 0))
        ssid_entry.delete(0, END)
        ssid_entry.insert(0, ssid)

        psk_entry = ttk.Entry(self,show="*", textvariable=self.psk_string)
        psk_entry.grid(row=3, column=1, pady=(10, 0))
        psk_entry.delete(0, END)
        psk_entry.insert(0, psk)

        timeout_entry = ttk.Entry(self, textvariable=self.timeout_string)
        timeout_entry.grid(row=4, column=1, pady=(10, 0))
        timeout_entry.delete(0, END)
        timeout_entry.insert(0, timeout_delay)

        save_button = ttk.Button(self, text="Save and Reboot", command=lambda: SettingPage.save_setting(self))
        save_button.grid(row=5, column=0, pady=(10, 0))
        cancel_button = ttk.Button(self, text="Cancel", command=lambda: controller.show_frame(StartPage))
        cancel_button.grid(row=5, column=1, pady=(10, 0))

    def save_setting(self):
        data= []
        data.append(self.server_string.get())
        data.append(self.ssid_string.get())
        data.append(self.psk_string.get())
        data.append(self.timeout_string.get())
        write_string ="serverip,"+ self.server_string.get() \
                      + "\n" + "ssid," + self.ssid_string.get() + "\n" \
                      + "pass," + self.psk_string.get() + "\n" + "timeout," \
                      + self.timeout_string.get() + "\n"
        fh=open('Config/config.ini', 'w')
        fh.write(write_string)
        fh.close()
        reboot_device()
    def gui_label(self):
        setting_label = ttk.Label(self, text="Settings", font=LARGE_FONT)
        setting_label.grid(row=0, column=0, pady=(10, 0), padx=(5, 5))
        server_label = ttk.Label(self, text='Server Domain:', font=MEDIUM_FONT ,justify=RIGHT)
        server_label.grid(row=1, column=0, pady=(10, 0), padx=(5, 5))
        ssid_label = ttk.Label(self, text='SSID:', font=MEDIUM_FONT ,justify=RIGHT)
        psk_label = ttk.Label(self, text='PSK:', font=MEDIUM_FONT ,justify=RIGHT)
        timeout_label = ttk.Label(self, text='Request Timeout:', font=MEDIUM_FONT ,justify=RIGHT)
        ssid_label.grid(row=2, column=0, pady=(10, 0), padx=(5, 5))
        psk_label.grid(row=3, column=0, pady=(10, 0), padx=(5, 5))
        timeout_label.grid(row=4, column=0, pady=(10, 0), padx=(5, 5))

class RemovePage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        home_button = ttk.Button(self, text="Main Window", command=lambda: controller.show_frame(StartPage))
        home_button.grid(row=0, column=0, pady=(10, 5), padx=10)
        update_button = ttk.Button(self, text="Update", command=lambda: self.after(10, RemovePage.devices_update(self)))
        update_button.grid(row=0, column=1, pady=(10, 5), padx=10)
        RemovePage.devices_update(self)

    def devices_update(self):
        id_len = len(id_name)
        for y in range(0, id_len):
            device_label = ttk.Label(self, text=id_name[y], font=LARGE_FONT)
            device_label.grid(row=(y + 1), column=0, padx=7, pady=7)
            device_button = ttk.Button(self, text='Remove Completely',
                                       command=lambda pos=y: RemovePage.popupmsg_remove(self, id_name[pos], pos))
            remove_wifi_button = ttk.Button(self, text='Remove From Wi-Fi Only',
                                            command=lambda pos=y: RemovePage.popupmsg_remove_wifi(self, id_name[pos], pos))

            try:
                request_query_device = "http://" + ip_address[y] + "/"
                requests.get(request_query_device, timeout=timeout_delay)
                device_button.config(state="normal")
                remove_wifi_button.config(state="normal")
            except Exception as e:
                print("error")
                device_button.config(state=DISABLED)
                remove_wifi_button.config(state=DISABLED)
            device_button.grid(row=(y + 1), column=1, padx=7, pady=7)
            remove_wifi_button.grid(row=(y + 1), column=2, padx=7, pady=7)

    def popupmsg_remove_wifi(self,device,pos):
        popup = tk.Tk()
        popup.wm_title("Remove device from wifi")

        def leavemini():
            try:
                request_query_device = ip_address[pos]
                registerDevice(spoof_ssid, spoof_psk, spoof_server_ip,request_query_device,len(spoof_server_ip))
                status_code = True
            except Exception as e:
                status_code = False
            if status_code == True:
                reboot_device()
                popup.destroy()

        registerLabel1 = tk.Label(popup, text="Are You Sure to remove device from wifi?")
        registerLabel1.grid(row=0, column=0, padx=10, pady=10)
        registerButton = tk.Button(popup, text="Remove and Reboot", command=lambda: leavemini())
        registerButton.grid(row=1, column=0)
        cancel_button = ttk.Button(popup, text="Cancel", command= lambda: popup.destroy())
        popup.mainloop()


    def popupmsg_remove(self,device,pos):
        popup = tk.Tk()
        popup.wm_title("Remove device")

        def leavemini():
            try:
                request_query_remove = 'http://' + server_id + '/removedevice'
                request_query_device = ip_address[pos]
                payload = {'device_name': device}
                registerDevice(spoof_ssid, spoof_psk, spoof_server_ip,request_query_device,len(spoof_server_ip))
                requests.post(request_query_remove, json=payload, timeout=timeout_delay)
                status_code = True
            except Exception as e:
                status_code = False
            if status_code == True:
                reboot_device()
                popup.destroy()

        registerLabel1 = tk.Label(popup, text="Are You Sure to remove device?")
        registerLabel1.grid(row=0, column=0, padx=10, pady=10)
        registerButton = tk.Button(popup, text="Remove and Reboot", command=lambda: leavemini())
        registerButton.grid(row=1, column=0)
        cancel_button = ttk.Button(popup, text="Cancel", command= lambda: popup.destroy())
        popup.mainloop()

def popupmsg(deviceName,pos):
    request_query_add = 'http://' + server_id + '/adddevice'
    payload = {'device_name': deviceName}
    requests.post(request_query_add, json=payload, timeout=timeout_delay)
    popup = tk.Tk()
    popup.wm_title("Register device")
    def leavemini():
        try:
            default_ip = "192.168.4.1"
            status_code = registerDevice(ssid, psk, server_id,default_ip,len(server_id))
        except Exception as e:
            status_code = False
            registerLabel1.config(text="error! are you sure you're in device AP?", bg='red')
        if status_code == True:
            popup.destroy()
            success_msg()


    registerLabel1 = tk.Label(popup, text="Please connect to the device Wi-Fi,")
    registerLabel1.grid(row=0, column =0, padx=10, pady=10)
    registerLabel2 = tk.Label(popup, text='press register(NOTE: This system needs to reboot)')
    registerLabel2.grid(row=1, column =0, padx=10, pady=10)
    registerButton = tk.Button(popup,text="Register", command= lambda : leavemini())
    registerButton.grid(row=2, column =0)
    popup.mainloop()

def success_msg():
    popup = tk.Tk()
    popup.wm_title("Success")

    def leavemini():
        try:
            status_code = True
        except Exception as e:
            status_code = False
        if status_code == True:
            reboot_device()
            popup.destroy()

    registerLabel1 = tk.Label(popup,
                              text="Please press Reboot button from the wireless switch")
    registerLabel1.grid(row=0, column=0, padx=10, pady=10)
    registerButton = tk.Button(popup, text="Reboot", command=lambda: leavemini())
    registerButton.grid(row=1, column=0)
    popup.mainloop()


app = controlSystem()
#app.after(5000, check_status)
app.geometry("480x320")
app.mainloop()

'''
to do list:


wag na mag reboot 
unclosable window 
7 secs 
user- server kung sino nag control
registration mode
charie:




'''