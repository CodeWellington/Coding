#!/usr/bin/python3
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

# -----------------------------
# CONFIGURATION
# -----------------------------
IPS = [
    "x.x.x.x",
    "y.y.y.y",
    "z.z.z.z"
]

PING_INTERVAL = 1
PING_TIMEOUT = 1
RUN_DURATION_HOURS = 4
SUMMARY_INTERVAL = 1000
LATENCY_THRESHOLD_MS = 100

# Traceroute behavior
RUN_TRACEROUTE_ON_THRESHOLD = True
RUN_TRACEROUTE_ON_FAILURE = True
TRACEROUTE_COOLDOWN_SEC = 10
TRACEROUTE_MAX_HOPS = 30
TRACEROUTE_WAIT_PER_HOP_SEC = 2
TRACEROUTE_QUERIES_PER_HOP = 1
TRACEROUTE_TIMEOUT_SEC = 60
USE_ICMP_TRACEROUTE = False

# -----------------------------
# INTERNALS
# -----------------------------
def log(msg, logfile):
    with logfile.open("a") as f:
        f.write(msg + "\n")

def ping(ip):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(PING_TIMEOUT), ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception:
        return (False, None)

    if result.returncode != 0:
        return (False, None)

    for line in result.stdout.split("\n"):
        if "time=" in line:
            try:
                part = line.split("time=")[1]
                latency = float(part.split(" ")[0])
                return (True, latency)
            except:
                return (True, None)

    return (True, None)

def run_traceroute(ip):
    cmd = ["traceroute", "-n",
           "-m", str(TRACEROUTE_MAX_HOPS),
           "-w", str(TRACEROUTE_WAIT_PER_HOP_SEC),
           "-q", str(TRACEROUTE_QUERIES_PER_HOP)]

    if USE_ICMP_TRACEROUTE:
        cmd.append("-I")

    cmd.append(ip)

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=TRACEROUTE_TIMEOUT_SEC
        )
        return result.stdout
    except FileNotFoundError:
        return "traceroute not found on system."
    except subprocess.TimeoutExpired:
        return f"traceroute timed out after {TRACEROUTE_TIMEOUT_SEC}s."
    except Exception as e:
        return f"traceroute failed: {e}"

def write_summary(ip, stats, logfile):
    sent = stats["sent"]
    ok = stats["ok"]
    fail = stats["fail"]
    loss_pct = (fail / sent * 100) if sent else 0

    if stats["latencies"]:
        avg_lat = sum(stats["latencies"]) / len(stats["latencies"])
        min_lat = min(stats["latencies"])
        max_lat = max(stats["latencies"])
    else:
        avg_lat = min_lat = max_lat = 0

    high_count = stats.get("high_latency", 0)
    if stats.get("high_latency_values"):
        high_avg = sum(stats["high_latency_values"]) / len(stats["high_latency_values"])
        high_max = max(stats["high_latency_values"])
    else:
        high_avg = 0
        high_max = 0

    summary = (
        f"--- SUMMARY {ip} ---\n"
        f"timestamp={datetime.now().isoformat()}\n"
        f"sent={sent} ok={ok} fail={fail} loss={loss_pct:.2f}%\n"
        f"avg_latency={avg_lat:.2f} ms  "
        f"min_latency={min_lat:.2f} ms  "
        f"max_latency={max_lat:.2f} ms\n"
        f"high_latency_events>{LATENCY_THRESHOLD_MS}ms: {high_count}  "
        f"(avg_high={high_avg:.2f} ms, max_high={high_max:.2f} ms)\n"
        f"----------------------"
    )
    log(summary, logfile)

def try_traceroute(ip, logfile, last_traceroute, reason):
    now = time.time()
    if (now - last_traceroute.get(ip, 0)) >= TRACEROUTE_COOLDOWN_SEC:
        last_traceroute[ip] = now
        tr_output = run_traceroute(ip)

        log(f"{datetime.now().isoformat()} | {ip} | TRACEROUTE ({reason}) BEGIN", logfile)
        for line in tr_output.splitlines():
            log(f"{datetime.now().isoformat()} | {ip} | TRACEROUTE | {line}", logfile)
        log(f"{datetime.now().isoformat()} | {ip} | TRACEROUTE ({reason}) END", logfile)

def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    logfile = Path(f"icmp-error_{date_str}.log")

    if not logfile.exists():
        log("# ICMP error log", logfile)
        log(f"# created_at={datetime.now().isoformat()}", logfile)
        log("# Format: timestamp | IP | event", logfile)
        log("", logfile)

    stats = {
        ip: {
            "sent": 0,
            "ok": 0,
            "fail": 0,
            "latencies": [],
            "high_latency": 0,
            "high_latency_values": []
        }
        for ip in IPS
    }

    last_traceroute = {ip: 0.0 for ip in IPS}

    start = datetime.now()
    end_time = start + timedelta(hours=RUN_DURATION_HOURS)

    log(f"{datetime.now().isoformat()} | INFO | Monitor started", logfile)

    try:
        while datetime.now() < end_time:
            loop_start = time.time()

            for ip in IPS:
                stats[ip]["sent"] += 1
                success, latency = ping(ip)

                if success:
                    stats[ip]["ok"] += 1

                    if latency is not None:
                        stats[ip]["latencies"].append(latency)

                        if latency > LATENCY_THRESHOLD_MS:
                            stats[ip]["high_latency"] += 1
                            stats[ip]["high_latency_values"].append(latency)

                            log(
                                f"{datetime.now().isoformat()} | {ip} | HIGH LATENCY {latency:.2f} ms "
                                f"(threshold={LATENCY_THRESHOLD_MS} ms)",
                                logfile
                            )

                            if RUN_TRACEROUTE_ON_THRESHOLD:
                                try_traceroute(ip, logfile, last_traceroute, "HIGH LATENCY")
                else:
                    stats[ip]["fail"] += 1
                    log(f"{datetime.now().isoformat()} | {ip} | ICMP FAILED", logfile)

                    if RUN_TRACEROUTE_ON_FAILURE:
                        try_traceroute(ip, logfile, last_traceroute, "PING FAIL")

                if stats[ip]["sent"] % SUMMARY_INTERVAL == 0:
                    write_summary(ip, stats[ip], logfile)

            elapsed = time.time() - loop_start
            time.sleep(max(0, PING_INTERVAL - elapsed))

    except KeyboardInterrupt:
        log(f"{datetime.now().isoformat()} | INFO | Interrupted", logfile)

    log("\n=== FINAL SUMMARY ===", logfile)
    for ip, s in stats.items():
        write_summary(ip, s, logfile)
    log("=== END SUMMARY ===\n", logfile)

    print("Monitoring complete. Results written to:", logfile)

if __name__ == "__main__":
    main()

"""
Send the scrip to device
Change the file to executable:
chmod +x ping-test.py

Run the script to keep the session: NO Hang UP
nohup python3 ping-test.py

Check the PID:
ps -ef | grep ping-test.py

Kill the session:
kill <PID>
"""
