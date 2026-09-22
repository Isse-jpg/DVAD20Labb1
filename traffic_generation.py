import time
import subprocess
import numpy as np
from numpy.random import Generator
from mininet.net import Node
import signal
WEB_SEARCH_CDF = np.array([

    (0, 0.0), (10000, 0.18), (20000, 0.3), (30000, 0.6),
    (50000, 0.9), (80000, 0.95), (100000, 1.0)
])

DATA_MINING_CDF = np.array([
    (180, 0.1), (300, 0.2), (460, 0.3), (570, 0.4), (590, 0.5),
    (600, 0.6), (650, 0.7), (710, 0.8), (810, 0.9), (910, 1.0)])


WEB_SEARCH = 1
DATA_MINING = 2
PCAP_PATH = "/tmp/traffic.pcap"

def gen_size(traffic_type: int, size: int, rng: Generator):
    p = rng.random(size)
    if traffic_type == WEB_SEARCH:
        flow_size = np.interp(p, WEB_SEARCH_CDF[:, 1], WEB_SEARCH_CDF[:, 0])
    elif traffic_type == DATA_MINING:
        flow_size = np.interp(p, DATA_MINING_CDF[:, 1], DATA_MINING_CDF[:, 0])
    else:
        raise ValueError("Unknown traffic type")

    return np.round(flow_size)


def genDCTraffic(
    traffic_source: Node,
    traffic_sink: Node,
    traffic_type: int,
    traffic_intensity: int,
    traffic_generation_time: int,
    rng: Generator,
    pcap_path: str = PCAP_PATH
):
    total_traffic = int(traffic_intensity * traffic_generation_time)
    if total_traffic <= 0:
        return {}
    time_interval = traffic_generation_time / total_traffic
    flow_sizes = gen_size(traffic_type, total_traffic, rng)
    sink_ip = traffic_sink.IP()
    port = int(rng.integers(10000, 60001))

    intf = f"{traffic_source.name}-eth0"
    server_process = traffic_sink.popen(f"iperf -s -p {port}")

    tshark_process = traffic_source.popen(
        f"tshark -l -i {intf} -w {pcap_path} tcp port {port}",
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )    #allow tshark to start
    time.sleep(2)
    if tshark_process.poll() is not None:
        _, stderr = tshark_process.communicate()
        server_process.terminate()
        raise RuntimeError(f"tshark crasched! Error: {stderr.decode('utf-8', errors='ignore')}")
    client_processes = []

    try:
        for flow_id in range(total_traffic):
            flow_size = int(flow_sizes[flow_id])
            client_cmd = f"iperf -c {sink_ip} -p {port} -n {flow_size} -N"

            p = traffic_source.popen(client_cmd)
            client_processes.append(p)

            time.sleep(time_interval)

        for p in client_processes:
            p.wait()

    finally:
        server_process.terminate()
        server_process.wait()

        #for graceful shutdown
        tshark_process.send_signal(signal.SIGINT)
        tshark_process.wait()
        time.sleep(0.5)
