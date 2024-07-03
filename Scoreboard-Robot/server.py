import asyncio
import websockets
import json
import tkinter as tk
from tkinter import ttk
import threading

# Global variables for scores and connections
score_data = {
    'plant1': 0,
    'harvest1': 0,
    'store1': 0,
    'plant2': 0,
    'harvest2': 0,
    'store2': 0,
    'silos': [[], [], [], [], []]
}

silos_temp = [[], [], [], [], []]

controller_connections = 0
display_connected = False

# Function to update the GUI with connection counts
def update_connections():
    controller_label.config(text=f"Controller Connections: {controller_connections}")
    if display_connected:
        display_label.config(text="Display Connected: Yes")
    else:
        display_label.config(text="Display Connected: No")
    root.after(100, update_connections)

# Function to handle controller websocket connections
async def handle_controller(websocket, path):
    global controller_connections
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
                        score_data['plant1'] -= 1
                    elif more == 1:
                        score_data['plant1'] += 1
                elif area == 2:
                    if more == 0:
                        score_data['harvest1'] -= 1
                    elif more == 1:
                        score_data['harvest1'] += 1
                elif area == 3:
                    score_data['store1'] += 1
                    score_data['silos'][more].append(1)
                    print(score_data['silos'][0])

            elif team == 2:
                if area == 1:
                    if more == 0:
                        score_data['plant2'] -= 1
                    elif more == 1:
                        score_data['plant2'] += 1
                elif area == 2:
                    if more == 0:
                        score_data['harvest2'] -= 1
                    elif more == 1:
                        score_data['harvest2'] += 1
                elif area == 3:
                    score_data['store2'] += 1
                    score_data['silos'][more].append(2)

            score_data_json = json.dumps(score_data)
            await broadcast_to_displays(score_data_json)

    finally:
        controller_connections -= 1
        update_connections()

# Function to handle display websocket connections
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

# Function to broadcast data to all connected displays
async def broadcast_to_displays(message):
    global display_connected
    if display_connected:
        try:
            await display_ws.send(message)
        except websockets.exceptions.ConnectionClosed:
            display_connected = False
            update_connections()

# Function to start the controller server
async def start_controller():
    async with websockets.serve(handle_controller, "192.168.22.38", 8834):
        print("Controller listening on port 8834")
        await asyncio.Future()

# Function to start the display server
async def start_display():
    global display_ws
    async with websockets.serve(handle_display, "localhost", 8991):
        print("Display server listening on port 8991")
        await asyncio.Future()

def reset():
    global score_data
    print("hii")
    score_data = {
        'plant1': 0,
        'harvest1': 0,
        'store1': 0,
        'plant2': 0,
        'harvest2': 0,
        'store2': 0,
        'silos': [[], [], [], [], []]
    }
    broadcast_to_displays(score_data)


# Create the GUI thread
def run_gui():
    global root, controller_label, display_label

    root = tk.Tk()
    root.title("WebSocket Server")

    # Create labels for connection counts
    controller_label = ttk.Label(root, text="Controller Connections: 0")
    controller_label.pack()

    display_label = ttk.Label(root, text="Display Connected: No")
    display_label.pack()

    
    btt = ttk.Button(root, text="reset", command=reset)
    btt.pack()

    # Start updating connection counts in the GUI
    update_connections()

    root.mainloop()

# Create a function to run the servers in a separate thread
def run_servers():
    # Create a new event loop for the server thread
    server_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(server_loop)

    try:
        # Run the servers in the separate event loop
        server_loop.run_until_complete(asyncio.gather(start_controller(), start_display()))
    finally:
        # Close the separate event loop
        server_loop.close()

# Create and start the threads
gui_thread = threading.Thread(target=run_gui)
server_thread = threading.Thread(target=run_servers)

gui_thread.start()
server_thread.start()

# Wait for the threads to finish (optional, but good practice)
gui_thread.join()
server_thread.join()