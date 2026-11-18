from backend.services.ollama_client import generate
import logging

logger = logging.getLogger("remediation")

TEMPLATES = {
    "PORT_SCAN": {
        "immediate": [
            "iptables -A INPUT -s {attacker_ip} -j DROP",
            "nmap --open -p- localhost",
            "ss -tulpn | grep LISTEN"
        ],
        "hardening": [
            "Close unused ports in /etc/ufw/ufw.conf",
            "Enable port knocking with knockd",
            "Set up fail2ban for repeated scan attempts"
        ]
    },
    "BRUTE_FORCE": {
        "immediate": [
            "fail2ban-client status sshd",
            "passwd -l {username}",
            "who -a | grep {attacker_ip}"
        ],
        "hardening": [
            "Disable password auth: PasswordAuthentication no in /etc/ssh/sshd_config",
            "Enable 2FA: apt install libpam-google-authenticator",
            "Restrict SSH to specific IPs in ufw"
        ]
    },
    "DDOS": {
        "immediate": [
            "iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute -j ACCEPT",
            "ip route add blackhole {attacker_ip}",
            "netstat -an | grep SYN_RECV | wc -l"
        ],
        "hardening": [
            "Enable SYN cookies: sysctl -w net.ipv4.tcp_syncookies=1",
            "Rate limit connections per IP in iptables",
            "Contact ISP for upstream null routing"
        ]
    },
    "LATERAL_MOVE": {
        "immediate": [
            "iptables -I INPUT -s {attacker_ip} -j DROP",
            "netstat -an | grep ESTABLISHED",
            "crontab -l && ls /etc/cron.d/"
        ],
        "hardening": [
            "Segment network into VLANs",
            "Enable host-based firewall on all internal machines",
            "Audit shared credentials across machines"
        ]
    },
    "C2_BEACON": {
        "immediate": [
            "iptables -A OUTPUT -d {attacker_ip} -j DROP",
            "clamscan -r / --remove --quiet",
            "netstat -tulpn | grep {attacker_ip}"
        ],
        "hardening": [
            "Block outbound on non-standard ports",
            "Enable DNS filtering",
            "Deploy EDR on all endpoints"
        ]
    },
    "MITM": {
        "immediate": [
            "arp -n | grep {attacker_ip}",
            "arp -s {gateway_ip} {real_gateway_mac}",
            "openssl s_client -connect {target_host}:443 -verify 5"
        ],
        "hardening": [
            "Enable Dynamic ARP Inspection on managed switches",
            "Use static ARP entries for critical hosts",
            "Deploy certificate pinning on all services"
        ]
    },
    "SQLI_XSS": {
        "immediate": [
            "grep '{attacker_ip}' /var/log/apache2/access.log | tail -50",
            "fail2ban-client set apache-auth banip {attacker_ip}",
            "grep -i 'union\\|select\\|script' /var/log/apache2/access.log"
        ],
        "hardening": [
            "Deploy ModSecurity WAF",
            "Use parameterized queries everywhere",
            "Enable CSP headers to block XSS"
        ]
    },
    "RANSOMWARE": {
        "immediate": [
            "ifconfig {interface} down",
            "vssadmin list shadows",
            "ps aux | grep -i crypt"
        ],
        "hardening": [
            "Restore from offline backup",
            "Report to CERT-In: https://www.cert-in.org.in",
            "Full forensic image before any cleanup"
        ]
    },
    "PRIV_ESC": {
        "immediate": [
            "last | grep {attacker_username}",
            "find / -perm -4000 2>/dev/null",
            "chage -l {attacker_username}"
        ],
        "hardening": [
            "Remove SUID bits from non-essential binaries",
            "Audit /etc/sudoers with visudo",
            "Enable auditd: auditctl -e 1"
        ]
    }
}

async def generate_report(attack_type: str, attacker_ip: str,
                           shap_values: dict, risk_score: float) -> dict:
    template = TEMPLATES.get(attack_type, TEMPLATES["PORT_SCAN"])
    
    # Pre-fill real payload parameters directly into the bash scripts for the Analyst
    commands = [cmd.format(attacker_ip=attacker_ip,
                            username="root", interface="eth0",
                            gateway_ip="192.168.1.1",
                            real_gateway_mac="xx:xx:xx:xx:xx:xx",
                            target_host="localhost",
                            attacker_username="unknown",
                            port="4444")
                for cmd in template["immediate"]]

    # Structure top 3 contributing agents from Explainable AI
    top_agents = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
    shap_text  = ", ".join([f"{k}={v:+.2f}" for k, v in top_agents])

    # Dynamic contextual prompt tailored for Llama 3.1
    prompt = f"""A '{attack_type}' attack was detected from IP address '{attacker_ip}'.
The severity risk score is {risk_score:.2f}. Mathematical SHAP analysis shows these agents were the strongest indicators: {shap_text}.
In 3 short sentences: explain what the attacker was likely doing, why it is dangerous to the network, and confidently verify that the immediate remediation actions provided below are correct for this scenario."""

    logger.info(f"[*] Calling Ollama (llama3) for {attack_type} remediation report...")
    explanation = await generate(prompt, model="llama3",
        system="You are a senior cybersecurity analyst. Be highly specific, factual, and strictly do not hallucinate attack techniques. Keep it concise, maximum 4 sentences.")

    return {
        "attack_type":   attack_type,
        "attacker_ip":   attacker_ip,
        "risk_score":    risk_score,
        "explanation":   explanation,
        "immediate":     commands,
        "hardening":     template["hardening"],
        "shap_summary":  shap_text
    }
