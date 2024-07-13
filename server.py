import asyncio
import websockets
import json
import tkinter as tk
from tkinter import ttk
import threading
import socket
import time
import pygame

pygame.init()
 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('10.255.255.255', 1))
IPAddr = s.getsockname()[0]
s.close()

ltime = 0
timer_running = False
state = "preparing"
startTime = time.monotonic()
PrepareTime = 60
readyTime = 10

startingsoundPlayed = False
startingsound = pygame.mixer.Sound("public/starting.mp3")
winningsound = pygame.mixer.Sound("public/winning-sound.mp3")

score_data = {
    'plant1': 0,
    'harvest1': 0,
    'store1': 0,
    'plant2': 0,
    'harvest2': 0,
    'store2': 0,
    'silos': [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
    'team1': "",
    'team2': "",
    "time": "",
    "bg_hidden": False,
    "cheyyo": 0,
    "cheyyoPlayed": 0
}


controller_connections = 0
display_connected = False

def updateFile(data, file_path):
  with open(file_path, 'w') as f:
    f.write(data)

def appending_silo(silo: list, ball: int):
    for i in range(3):
        if silo[i] == 0:
            silo[i] = ball
            break
        else: 
            continue

    return silo

def popping_silo(index):
    tem = [2, 1, 0]
    ball = 0
    for i in tem:
        if score_data['silos'][index][i] == 0:
            continue
        elif score_data['silos'][index][i] == 1:
            score_data['silos'][index][i] = 0 
            ball = 1
            break
        elif score_data['silos'][index][i] == 2:
            score_data['silos'][index][i] = 0
            ball = 2
            break

    return ball

def update_connections():
    controller_label.config(text=f"Controller Connections: {controller_connections}")
    if display_connected:
        display_label.config(text="Display Connected: Yes")
    else:
        display_label.config(text="Display Connected: No")
    root.after(100, update_connections)

def findCHeyYo():
    global score_data
    r = 0
    b = 0
    for silo in score_data['silos']:
        cheyyo = findSuccessful(silo)
        if cheyyo == 1:
            r += 1
        elif cheyyo == 2:
            b += 1
    if r >= 3:
        score_data['cheyyo'] = 1
    elif b >= 3:
        score_data['cheyyo'] = 2
    else:
        score_data['cheyyo'] = 0


def findSuccessful(silo: list):
    if (silo == [1, 2, 1] or silo == [2, 1, 1] or silo == [1, 1, 1]):
        return 1
    elif (silo == [2, 1, 2] or silo == [1, 2, 2] or silo == [2, 2, 2]):
        return 2
    else:
        return 0


async def handle_controller(websocket, path):
    global controller_connections, ltime
    controller_connections += 1
    update_connections()

    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Controller received: {data}")
            team = data["team"]
            area = data["area"]
            more = data["index"]

            if team == 1:
                if area == 1:
                    if more == 0:
                        if score_data['plant1'] > 0:
                            score_data['plant1'] -= 1
                    elif more == 1:
                        if score_data['plant1'] < 12:
                            score_data['plant1'] += 1
                elif area == 2:
                    if more == 0:
                        if score_data['harvest1'] > 0:
                            score_data['harvest1'] -= 1
                    elif more == 1:
                        if score_data['harvest1'] < 12:
                            score_data['harvest1'] += 1
                elif area == 3:
                    if 0 in score_data['silos'][more]:
                        score_data['store1'] += 1
                        score_data['silos'][more] = appending_silo(score_data['silos'][more], 1)
                        findCHeyYo()

            elif team == 2:
                if area == 1:
                    if more == 0:
                        if score_data['plant2'] > 0:
                            score_data['plant2'] -= 1
                    elif more == 1:
                        if score_data['plant2'] < 12:
                            score_data['plant2'] += 1
                elif area == 2:
                    if more == 0:
                        if score_data['harvest2'] > 0:
                            score_data['harvest2'] -= 1
                    elif more == 1:
                        if score_data['harvest2'] < 12:
                            score_data['harvest2'] += 1
                elif area == 3:
                    if 0 in score_data['silos'][more]:
                        score_data['store2'] += 1
                        score_data['silos'][more] = appending_silo(score_data['silos'][more], 2)
                        findCHeyYo()

            elif team == 0:
                popped =popping_silo(more)
                if popped != 0:
                    score_data[f'store{popped}'] -=  1
                    findCHeyYo()

            updateFile(f"{score_data['plant1']*10+score_data['harvest1']*10+score_data['store1']*30}", "VData/score1.txt")
            updateFile(f"{score_data['plant2']*10+score_data['harvest2']*10+score_data['store2']*30}", "VData/score2.txt")

            if(score_data['cheyyo']!=0):
                print(f"cheyyo: {score_data['cheyyo']}")

            score_data_json = json.dumps(score_data)
            await broadcast_to_displays(score_data_json)

            if(score_data['cheyyo']!=0 and score_data['cheyyoPlayed']==0):
                winningsound.play()
                print(f"{ltime//60}:{ltime%60}")
                score_data['cheyyoPlayed'] = 1
            
            if(score_data['cheyyo'] == 0 and score_data['cheyyoPlayed']==1):
                score_data['cheyyoPlayed'] = 0

    finally:
        controller_connections -= 1
        update_connections()

async def handle_display(websocket, path):
    global display_connected, display_ws
    display_connected = True
    display_ws = websocket
    update_connections()

    try:
        async for message in websocket:
            print(f"Display received: {message}")
    finally:
        display_connected = False
        update_connections()

async def broadcast_to_displays(message):
    global display_connected
    if display_connected:
        try:
            await display_ws.send(message)
        except websockets.exceptions.ConnectionClosed:
            display_connected = False
            update_connections()

async def start_controller():
    async with websockets.serve(handle_controller, IPAddr, 8834):
        print("Controller listening on port 8834")
        await asyncio.Future()

async def start_display():
    global display_ws
    async with websockets.serve(handle_display, "localhost", 8991):
        print("Display server listening on port 8991")
        await asyncio.Future()

def reset(t1:ttk.Entry, t2:ttk.Entry):
    global score_data, state, timer_running, startingsoundPlayed
    team1:str = t1.get()
    team2:str = t2.get()
    team1 = team1.split()
    team1[1] = f"{team1[0]} {team1[1]}"

    team2 = team2.split()
    team2[1] = f"{team2[0]} {team2[1]}"

    score_data = {
        'plant1': 0,
        'harvest1': 0,
        'store1': 0,
        'plant2': 0,
        'harvest2': 0,
        'store2': 0,
        'silos': [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
        'team1': team1,
        "team2": team2,
        "time": "0:00",
        "bg_hidden": 0,
        "cheyyo": 0,
        "cheyyoPlayed": 0
    }

    startingsoundPlayed = False
    state = "preparing"
    timer_running = False
    updateFile("0:00", "VData/timer.txt")
    updateFile(f"{score_data['plant1']*10+score_data['harvest1']*10+score_data['store1']*30}", "VData/score1.txt")
    updateFile(f"{score_data['plant2']*10+score_data['harvest2']*10+score_data['store2']*30}", "VData/score2.txt")
    updateFile(f"{team1[1]}", "VData/team1.txt")
    updateFile(f"{team2[1]}", "VData/team2.txt")
    

    asyncio.run_coroutine_threadsafe(broadcast_to_displays(json.dumps(score_data)), server_loop)

def timer():
    global timer_running, ltime, startTime, state, startingsoundPlayed
    while True:
        if timer_running:
            dTime = time.monotonic() - startTime
            if state == "preparing":
                if PrepareTime > dTime:
                    ltime = PrepareTime - dTime
                else:
                    state = "ready"
                    timer_running = False
                    score_data["bg_hidden"] = False
                    updatestate()

            elif state == "ready":
                if readyTime > dTime:
                    ltime = readyTime - dTime
                else:
                    state = "play"
                    updatestate()
                    startTime = time.monotonic()
                    score_data["bg_hidden"] = False
                if ltime <= 4:
                    if not startingsoundPlayed:
                        startingsound.play()
                        startingsoundPlayed = True

            elif state == "play":
                ltime = dTime
                score_data["bg_hidden"] = False
                if ltime >= 180:
                    ltime = 180
            if state == "preparing" or state == "ready":
                if ltime <= 1 and state=="ready":
                    score_data["time"] = "Goo!!"
                else:
                    score_data["time"] = f"{int(ltime)}"
                updateFile(f"{int(ltime)}", "VData/timer.txt")
            else:
                score_data["time"] = f"{int(ltime//60)}:{int(ltime%60):02}"
                updateFile(f"{int(ltime//60)}:{int(ltime%60):02}", "VData/timer.txt")
            
            asyncio.run_coroutine_threadsafe(broadcast_to_displays(json.dumps(score_data)), server_loop)
            time.sleep(0.1)

def startTImer():
    global timer_running, ltime, startTime, state, score_data
    if state == "preparing" or "ready":
        startTime = time.monotonic()
        timer_running = True
        score_data['bg_hidden'] = True
    
def startTImer1():
    global timer_running, ltime, startTime, state, score_data
    state = "ready"
    startTime = time.monotonic()
    timer_running = True
    score_data['bg_hidden'] = True

def updatestate():
    stateLabel.config(text=f"state: {state}")
    
def run_gui():
    global root, controller_label, display_label, stateLabel

    root = tk.Tk()
    root.title("WebSocket Server")

    ip = ttk.Label(root, text=f"site: {IPAddr}:8821", font=30)
    ip.pack()

    controller_label = ttk.Label(root, text="Controller Connections: 0", font=30)
    controller_label.pack()

    display_label = ttk.Label(root, text="Display Connected: No", font=30)
    display_label.pack()

    stateLabel = ttk.Label(root, text=f"state: {state}", font=30)
    stateLabel.pack()

    frame1 = ttk.Frame(root)

    ent1 = ttk.Entry(frame1)
    ent1.pack(side="left")

    ent2 = ttk.Entry(frame1)
    ent2.pack(side="right")

    frame1.pack()

    btt = ttk.Button(root, text="reset", command=lambda: reset(ent1, ent2))
    btt.pack()

    t_btt = ttk.Button(root, text="Start Timer", command=startTImer)
    t_btt.pack()

    t_ready = ttk.Button(root, text="Start Ready", command=startTImer1)
    t_ready.pack()

    update_connections()

    root.mainloop()

def run_servers():
    global server_loop
    server_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(server_loop)

    try:
        server_loop.run_until_complete(asyncio.gather(start_controller(), start_display()))
    finally:
        server_loop.close()

gui_thread = threading.Thread(target=run_gui)
server_thread = threading.Thread(target=run_servers)
timer_thread = threading.Thread(target=timer)

gui_thread.start()
server_thread.start()
timer_thread.start()

gui_thread.join()
server_thread.join()
timer_thread.join()
