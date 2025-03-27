
# Websocket: ws://raspberrypi.local:4616

import json
import socket
import time
import traceback
import uuid
import os
import asyncio
import struct
import requests
import queue
import threading
import tornado
import tornado.ioloop
import tornado.web
import tornado.websocket
import hashlib

from typing import Dict

import sys

bool_is_in_terminal_mode= sys.stdout.isatty()
if bool_is_in_terminal_mode:
    print("Running in a terminal.")
    stop_service_script ="""
    sudo systemctl stop apint_trusted_lobby_iid.service
    sudo systemctl stop apint_trusted_lobby_iid.timer
    """
    # run code to stop current service
    os.system(stop_service_script)
    
    # WHEN YOU NEED TO RESTART IT.
    """
    sudo systemctl restart apint_trusted_lobby_iid.service
    sudo systemctl restart apint_trusted_lobby_iid.timer
    """



int_max_byte_size = 16

# 4615 IS RESERVED FOR PUSH IID GATE WITH CRYPTO HANDSHAKE
server_websocket_port = 4615
# 4625 IS RESERVED FOR PUSH IID GATE WITH TRUSTED
server_websocket_port = 4625
server_websocket_mask= "0.0.0.0"

 
# If you want to relay the IID to a secure gate with cryto handshake
broadcast_ip_gate="127.0.0.1"
broadcast_port_gates= [3615,4625]




class UserHandshake:
    def __init__(self):
        self.address:str = ""
        self.remote_address:str = None          
        self.websocket= None       
        self.exit_handler=False
    
    def is_connection_lost(self):
        return self.user.exit_handler or self.user.websocket is None
        
        
                
guid_handshake_to_valide_user = {}
index_handshake_to_valide_user_list = {}

bool_use_debug_print = True
def debug_print(text):
    if bool_use_debug_print:
        print(text)
        
## If true bytes can only by of 16 bytes
bool_use_iid_max_size_kick_bytes=True 
## If true, the server accept text message
bool_allow_text_broadcasting= False
 

queue_broadcast_text_message = queue.Queue()
queue_boardcast_byte_iid_message = queue.Queue()
queue_boardcast_byte_message = queue.Queue()
 
 
async def relay_iid_message_as_local_udp_thread(byte):
    print(f"Relay UDP {byte}")
    for port in broadcast_port_gates:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(byte, (broadcast_ip_gate, port))
        sock.close()
        

async def push_byte_or_close( user: UserHandshake,  b: bytes):
    if user is None or user.is_connection_lost():
        return
    try:
        await user.websocket.write_message(b, binary=True)
    except tornado.websocket.WebSocketClosedError:
        print(f"WebSocketClosedError: Connection closed for user {user.index}")
        user.websocket.close()
        remove_user_from_connected(user)
        
async def push_text_or_close( user: UserHandshake,  b: str):
    if user is None or user.is_connection_lost():
        return
    try:
        await user.websocket.write_message(b)
    except tornado.websocket.WebSocketClosedError:
        print(f"WebSocketClosedError: Connection closed for user {user.index}")
        user.websocket.close()
        remove_user_from_connected(user) 



 
bool_need_push_debug_text_bytes = False
bool_need_push_debug_iid = False
def push_waiting_text_message():
    while not queue_broadcast_text_message.empty():
        message = queue_broadcast_text_message.get()
        for user in list_of_user_connected:
            push_text_or_close(user, message)
    
    if bool_need_push_debug_text_bytes and is_terminal_mode():
        termnial_print(f"Pushing Text: {queue_boardcast_byte_iid_message}")
                
def push_waiting_byte_message():
    while not queue_boardcast_byte_message.empty():
        message = queue_boardcast_byte_message.get()
        for user in list_of_user_connected:
            push_byte_or_close(user, message)
            
    if bool_need_push_debug_text_bytes and is_terminal_mode():
        termnial_print(f"Pushing Bytes: {len(queue_boardcast_byte_iid_message)}")
    
def push_waiting_byte_iid_message():
    
    while not queue_boardcast_byte_iid_message.empty():
        message = queue_boardcast_byte_iid_message.get()
        relay_iid_message_as_local_udp_thread(message)
        for user in list_of_user_connected:
            push_byte_or_close(user, message)
                
    if bool_need_push_debug_iid and is_terminal_mode():
        termnial_print(f"Pushing IID: {queue_boardcast_byte_iid_message}")
                
def push_waiting_message():
    push_waiting_byte_iid_message()
    push_waiting_byte_message()
    push_waiting_text_message()
 
 
def is_terminal_mode():
    return bool_is_in_terminal_mode

def termnial_print(text):
    if bool_is_in_terminal_mode:
        print(text)
 
async def handle_text_message(user: UserHandshake, message: str):
    if not bool_allow_text_broadcasting:
        return
    queue_broadcast_text_message.put(message)
    termnial_print(message)
    
    

def user_to_json(user):
                return json.dumps(user.__dict__, indent=4, default=str)  



list_of_user_connected: UserHandshake= []
def add_user_to_connected(user: UserHandshake):
    list_of_user_connected.append(user)
    print (f"USER COUNT, ADD: {len(list_of_user_connected)}")
    
def remove_user_from_connected(user: UserHandshake):
    list_of_user_connected.remove(user)
    print (f"USER COUNT, REMOVE: {len(list_of_user_connected)}")
    
def remove_of_list_close_websocket():
    for user in list_of_user_connected:
        if user.is_connection_lost():
            remove_user_from_connected(user)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
        async def open(self):
            print("WebSocket opened")
            self.user = UserHandshake()
            self.user.websocket = self
            self.user.exit_handler=False
            self.user.remote_address = self.request.remote_ip
            list_of_user_connected.append(self.user)
            
            print (f"New connection from {self.user.remote_address}")
            print(user_to_json(self.user))

            welcome = f"""
            WELCOME TO TRUSTED INTEGER IID SERVER
            DOCUMENTATION: https://github.com/EloiStree/2025_01_01_APIntTrustedLobbyIID
            WHAT IS AN IID: https://github.com/EloiStree/IID
            """
            
            if bool_use_iid_max_size_kick_bytes:
                welcome+="""
                RULE, ONLY IID BYTES SERVER: MAX 16 BYTES OR YOUR ARE KICKED 
                """
            if bool_allow_text_broadcasting:
                welcome+="""
                RULE, TEXT BROADCASTING IS ALLOWED (DONT ABUSE OF IT)
                """
            else:
                welcome+="""
                RULE, TEXT BROADCASTING IS DISABLED: YOUR TEXT MESSAGE ARE NOT BROADCASTED
                """
            await self.user.websocket.write_message(welcome)
            

            
        def is_connection_lost(self):
            return self.user.exit_handler or self.user.websocket is None
            

        async def on_message(self, message):
            if isinstance(message, str):                    
                queue_broadcast_text_message.put(message)
            else:
                lenght_message = len(message)
                if lenght_message== 4 or lenght_message== 8 or lenght_message== 12 or lenght_message== 16:
                    queue_boardcast_byte_iid_message.put(message)
                else:
                    queue_boardcast_byte_message.put(message)

        def on_close(self):
            print("WebSocket closed")
            self.user.exit_handler=True
            remove_user_from_connected(self.user)

        def check_origin(self, origin):
            return True
        
def make_app():
    return tornado.web.Application([
        (r"/", WebSocketHandler),  # WebSocket endpoint
    ])    


async def udp_async_server():
    while True:        
        await push_waiting_message()
        await asyncio.sleep(0.0001)


        
def loop_udp_server():
    while True:
        try :
            asyncio.run(udp_async_server())
        except Exception as e:
            termnial_print (f"RELAYER CRASHED: {e}")
            if is_terminal_mode():
                traceback.print_exc()
        time.sleep(2)

def print_local_ip():
    
    print("IPv4")
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Hostname: {hostname}")
    print(f"Local IP: {local_ip}")
    

if __name__ == "__main__":

    print_local_ip()    
    
    server_thread = threading.Thread(target=loop_udp_server)
    server_thread.daemon = True 
    server_thread.start()
    

    while True:
        try:
            app = make_app()
            app.listen(server_websocket_port)  
            print(f"Server started on ws://{server_websocket_mask}:{server_websocket_port}/")
            tornado.ioloop.IOLoop.current().start()
        except Exception as e:
            print (f"SERVER TORANDO CRASHED: {e}")
            traceback.print_exc()
        time.sleep(2)
        
    
    


