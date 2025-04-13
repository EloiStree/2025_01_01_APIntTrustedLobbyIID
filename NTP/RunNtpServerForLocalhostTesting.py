import socket
import struct
import time

def system_time_to_ntp_time(timestamp):
    """Convert system time to NTP time."""
    return timestamp + 2208988800  # NTP epoch starts in 1900

def run_ntp_server(host='0.0.0.0', port=123):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"NTP server started on {host}:{port}")

    while True:
        data, addr = sock.recvfrom(1024)
        if data:
            print(f"Received NTP request from {addr}")

            transmit_time = system_time_to_ntp_time(time.time())
            packet = b'\x1c' + 47 * b'\0'
            # Insert the transmit timestamp (last 8 bytes of the 48-byte NTP packet)
            packet = packet[:40] + struct.pack('!I', int(transmit_time)) + struct.pack('!I', 0)
            
            sock.sendto(packet, addr)

if __name__ == '__main__':
    run_ntp_server()
