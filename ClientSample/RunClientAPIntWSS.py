'''
Bad code but show that it run.
'''

# import asyncio
# import struct
# import ssl
# import functools
# import tornado.websocket

# # Configuration
# STRING_DDNS_SERVER = "apint.ddns.net"
# STRING_DDNS_PORT = 4725

# # Asynchronous input helper
# async def async_input(prompt):
#     return await asyncio.get_event_loop().run_in_executor(None, functools.partial(input, prompt))

# # Shared state with lock protection
# class State:
#     def __init__(self):
#         self._lock = asyncio.Lock()
#         self._int_index = 0
#         self._long_date_time = 0

#     async def get_state(self):
#         async with self._lock:
#             return self._int_index, self._long_date_time

#     async def set_state(self, int_index=None, long_date_time=None):
#         async with self._lock:
#             if int_index is not None:
#                 self._int_index = int_index
#             if long_date_time is not None:
#                 self._long_date_time = long_date_time

#     async def increment_index(self):
#         async with self._lock:
#             self._int_index += 1
#             return self._int_index

# class WebSocketClient:
#     def __init__(self, server, port):
#         self.server = server
#         self.port = port
#         self.ws = None

#     async def connect(self):
#         url = f"wss://{self.server}:{self.port}"
#         try:
#             self.ws = await tornado.websocket.websocket_connect(url)
#             print(f"[Connected] to {url}")
#             return True
#         except Exception as e:
#             print(f"[Connection Failed] {e}")
#             return False

#     async def send_message(self, message):
#         if self.ws:
#             await self.ws.write_message(message)
#             print(f"[Sent] {message}")

#     async def receive_message(self):
#         if self.ws:
#             try:
#                 message = await self.ws.read_message()
#                 if isinstance(message, str):
#                     message = message.encode('utf-8')

#                 if message:
#                     print(f"[Received Raw Bytes] {message}")
#                     try:
#                         if len(message) == 4:
#                             value = struct.unpack('<i', message)[0]
#                             print(f"[Parsed] 4-byte integer: {value}")
#                         elif len(message) == 16:
#                             index, integer, date_time = struct.unpack('<iid', message)
#                             print(f"[Parsed] Index: {index}, Integer: {integer}, DateTime: {date_time}")
#                         else:
#                             print("[Info] Received unexpected byte length.")
#                     except struct.error:
#                         print("[Error] Failed to unpack message.")
#                 return message
#             except Exception as e:
#                 print(f"[Receive Error] {e}")

# async def main():
#     state = State()
#     client = WebSocketClient(STRING_DDNS_SERVER, STRING_DDNS_PORT)

#     if not await client.connect():
#         return

#     async def receive_loop():
#         while True:
#             await client.receive_message()
#             await asyncio.sleep(0.1)  # Yield control

#     async def send_loop():
#         while True:
#             user_input = await async_input("Enter an integer to send to the server: ")
#             user_input = user_input.strip().replace(" ", "").replace(",", "")

#             if not user_input.isdigit():
#                 print("[Input Error] Please enter a valid integer.")
#                 continue

#             try:
#                 user_integer = int(user_input)
#                 int_index = await state.increment_index()
#                 _, long_date_time = await state.get_state()
#                 packed_data:bytes = struct.pack('<iid', int_index, user_integer, long_date_time)
#                 print(f"[Packing] Index: {int_index}, Integer: {user_integer}, DateTime: {long_date_time}")
#                 print(f"[Packed Data {len(packed_data)}] {packed_data}")
#                 await client.send_message(packed_data)
#             except struct.error as e:
#                 print(f"[Pack Error] {e}")
#                 # displqy stqck
#                 import traceback
#                 traceback.print_exc()

#     await asyncio.gather(receive_loop(), send_loop())

# if __name__ == "__main__":
#     while True:
#         try:
#             ssl_context = ssl.create_default_context()
#             ssl_context.check_hostname = False
#             ssl_context.verify_mode = ssl.CERT_NONE

#             asyncio.run(main())
#         except KeyboardInterrupt:
#             print("[Exiting] Client terminated by user.")
#             break
#         except Exception as e:
#             print(f"[Error] {e}")
#             print("[Retrying] Reconnecting...")
