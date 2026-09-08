import time
import numpy as np
from numpy.random import Generator
from mininet.net import Node 
import random
from mininet.util import pmonitor
import threading

WEB_SEARCH_CDF = np.array([
    (0, 0.0), (10000, 0.18), (20000, 0.3), (30000, 0.6), 
    (50000, 0.9), (80000, 0.95), (100000, 1.0)
])

DATA_MINING_CDF = np.array([
    (180, 0.1), (300, 0.2), (460, 0.3), (570, 0.4), (590, 0.5), 
    (600, 0.6), (650, 0.7), (710, 0.8), (810, 0.9), (910, 1.0) ])


WEB_SEARCH = 1
DATA_MINING = 2

def monitor_flow(flow_id, process, start_time, flow_size, results):
    process.wait()

    stop_time = time.monotonic()
    duration = stop_time - start_time

    results[flow_id] = {
        "size": flow_size,
        "duration": duration
    }

def gen_size(traffic_type:int, size:int, rng:Generator):
    p = rng.random(size)
    if traffic_type == WEB_SEARCH:
        flow_size = np.interp(p, WEB_SEARCH_CDF[:, 1], WEB_SEARCH_CDF[:, 0])
    elif traffic_type == DATA_MINING:
        flow_size = np.interp(p, DATA_MINING_CDF[:, 1], DATA_MINING_CDF[:,0])
    else:
        raise ValueError("Unknown traffic type")


    return np.round(flow_size)


def genDCTraffic(
    traffic_source: Node,
    traffic_sink: Node,
    traffic_type: int,
    traffic_intensity: int,
    traffic_generation_time: int,
    rng: Generator
):
    total_traffic = int(traffic_intensity * traffic_generation_time)

    if total_traffic <= 0:
        return {}

    time_interval = traffic_generation_time / total_traffic
    interp_traffic = gen_size(traffic_type, total_traffic, rng)

    sink_ip = traffic_sink.IP()
    port = rng.integers(10000, 60001)

    server_process = traffic_sink.popen(f"iperf -s -p {port}")
    time.sleep(0.5)
    active_processes = []
    measurement_threads = []

    results = {}
    for i in range(total_traffic):
        flow_size = int(interp_traffic[i])

        client_cmd = f"iperf -c {sink_ip} -p {port} -n {flow_size}"

        start_time = time.monotonic()
        process = traffic_source.popen(client_cmd)
        thread = threading.Thread(target=monitor_flow,
                                             args=(i,
                                             process,
                                             start_time,
                                             flow_size,
                                             results))

        thread.start()
        measurement_threads.append(thread)
        active_processes.append(process)
        time.sleep(time_interval)


    for thread in measurement_threads:
        thread.join()

    server_process.terminate()
    return results
