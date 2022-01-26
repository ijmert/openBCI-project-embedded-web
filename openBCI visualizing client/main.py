import requests
import tkinter as tk
import json

import scipy.signal
from dateutil import parser
from datetime import timedelta
import plotly.graph_objects as go
import numpy as np
from scipy.fft import fft, ifft, fftfreq

def getHelmets():
    helmet_names = requests.get('http://localhost:3000/brains/getAllHelmets')
    helmet_names = helmet_names.text[1:-1]
    print(helmet_names)
    helmet_names = helmet_names.split(',')
    for i in range(0, len(helmet_names)):
        helmet_names[i] = helmet_names[i][1:-1]
    print(helmet_names)
    return helmet_names


def ParseJsonToPackage(jsonString):
    jsonPackages = json.loads(jsonString)
    if type(jsonPackages) != dict:
        for p in jsonPackages:
            p['TimeStamp'] = parser.parse(p['TimeStamp'])
    else:
        jsonPackages['TimeStamp'] = parser.parse(jsonPackages['TimeStamp'])
    return jsonPackages


def receive_json_packages_by_helmet(helmet):
    packages = []
    json_received = requests.get('http://localhost:3000/brains/getFirstPackageByName/%s' % helmet).content
    # json_received = json_received.decode('utf-8')
    json_packages = ParseJsonToPackage(json_received)
    packages.append(json_packages)
    while json_received != b'[]':
        json_received = requests.get(
            'http://localhost:3000/brains/getNext5PackagesByName/%s/%s' % (helmet, packages[-1]['TimeStamp'])).content
        # json_received = json_received.decode('utf-8')
        json_packages = ParseJsonToPackage(json_received)
        packages.extend(json_packages)
    return packages


def load_package_data_for_helm(*args):
    print('load_data called')
    print(args)
    helmet = helmet_option_var.get()
    packages = receive_json_packages_by_helmet(helmet)
    set_global_sessions(packages)

class Session:
    packages = []
    Until = None
    From = None
    def __init__(self):
        self.packages = []
        self.Until = None
        self.From = None


def set_global_sessions(packages):
    global sessions
    global sessions_strings
    global SessionDropdown
    sessionsBuilder = []
    delta = timedelta(seconds=1)
    current_session = Session()
    for idx, p in enumerate(packages):
        if len(current_session.packages) == 0:
            current_session.packages.append(p)
            current_session.From = p['TimeStamp']
        else:
            if current_session.packages[-1]['TimeStamp'] != p['TimeStamp'] - delta:
                current_session.Until = current_session.packages[-1]['TimeStamp']
                sessionsBuilder.append(current_session)
                current_session = Session()
                current_session.packages.append(p)
                current_session.From = p['TimeStamp']
            elif idx == len(packages) - 1:
                current_session.packages.append(p)
                current_session.Until = p['TimeStamp']
                sessionsBuilder.append(current_session)
            else:
                current_session.packages.append(p)
    sessions = sessionsBuilder
    sessions_strings = []
    for s in sessions:
        sessions_strings.append(converttomenuitemstring(s))
    SessionDropdown['menu'].delete(0, 'end')
    SessionDropdown.options = sessions_strings
    for string in SessionDropdown.options:
        SessionDropdown['menu'].add_command(label=string, command=lambda value=string: session_option_var.set(value))
    session_option_var.set(sessions_strings[0])


def placeholder(*args):
    print("you selected a new session.")
    print(args)
    print("%s; this was the session clicked on" %session_option_var.get())


def placeholder_channel(*args):
    print("you selected a new channel.")
    print(args)
    print("%s; this was the channel clicked on" %channel_option_var.get())


def converttomenuitemstring(session):
    stringlist = [session.From.strftime("%m/%d/%Y, %H:%M:%S"), session.Until.strftime("%m/%d/%Y, %H:%M:%S"), "session", str(sessions.index(session))]
    menuitemstring = " ".join(stringlist)
    return menuitemstring

def convertfrommenuitemstring(menuitemstring):
    menuitemlist = menuitemstring.split(" ")
    sessionIndex = int(menuitemlist[-1])
    return sessions[sessionIndex]


sessions = None
sessions_strings = ['placeholder']
helmets = getHelmets()
root = tk.Tk()
root.geometry('500x500')
# frame = tk.Frame(root)



#this creates session option menu, any change will be written to session option var (the entry in sessions strings, sessions strings is string representation of the sessions)
session_option_var = tk.StringVar(root)
session_option_var.trace('w', callback=placeholder)
SessionDropdown = tk.OptionMenu(root, session_option_var, *sessions_strings)
SessionDropdown.grid(columnspan=4, ipadx=5, ipady=5, padx=15, pady=15)


#this creates helmet option meny, any change will be written to helmet option var (the entry in helmets), helmets contains all helmet names in the database.
helmet_option_var = tk.StringVar(root)
helmet_option_var.trace('w', callback=load_package_data_for_helm)
helmet_option_var.set(helmets[0])
session_option_var.set(converttomenuitemstring(sessions[0]))

helmetDropdown = tk.OptionMenu(root, helmet_option_var, *helmets)
helmetDropdown.grid(column=4, row=0, ipadx=5, ipady=5, padx=15, pady=15)

channel_option_var = tk.StringVar(root)
channel_option_var.trace('w', callback=placeholder_channel)
channel_arr = ['1', '2', '3', '4', '5', '6', '7', '8']
channelDropdown = tk.OptionMenu(root, channel_option_var, *channel_arr)
channel_option_var.set('1')
channelDropdown.grid(column=4, ipadx=5, ipady=5, padx=15, pady=15, row=1)

label = tk.Label(root, text="Channel:")
label.grid(column=3, row=1)




def show_graph():
    channel = channel_option_var.get()
    session_string = session_option_var.get()
    session = convertfrommenuitemstring(session_string)
    delta = timedelta(seconds=1)
    delta = delta/250
    all_dates = []
    all_samples = []
    for package in session.packages:
        all_dates.append(package['TimeStamp'])
        for i in range(0, 250):
            all_dates.append(package['TimeStamp'] + delta*i)
        all_samples.extend(package['Channels'][int(channel)])
    b, a = scipy.signal.butter(4, [0.384, 0.416], 'bandstop', output='ba') #48-52
    all_samples = scipy.signal.filtfilt(b, a, all_samples)
    b, a = scipy.signal.butter(4, [0.04, 0.36], 'bandpass', output='ba') #5-45
    all_samples = scipy.signal.filtfilt(b, a, all_samples)
    fourier = fft(all_samples)
    freq = fftfreq(len(all_samples), 1/250)
    fig = go.FigureWidget([go.Scatter(x=all_dates, y=all_samples)])
    fig.show()
    fig = go.FigureWidget([go.Scatter(x=freq[:int(len(freq)/2)], y=np.abs(fourier[:int(len(fourier)/2)]))])
    fig.show()



btn = tk.Button(root, text="Show session graph", command=show_graph)
btn.grid(row=1, column=1)

root.mainloop()





root.mainloop()
