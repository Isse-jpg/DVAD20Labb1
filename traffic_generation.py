import numpy as np
import random
import time
WEB_SEARCH_CDF = np.array([
    (0, 0.0), (10000, 0.18), (20000, 0.3), (30000, 0.6), 
    (50000, 0.9), (80000, 0.95), (100000, 1.0)
])

DATA_MINING_CDF = np.array([
    (180, 0.1), (300, 0.2), (460, 0.3), (570, 0.4), (590, 0.5), 
    (600, 0.6), (650, 0.7), (710, 0.8), (810, 0.9), (910, 1.0) ])


WEB_SEARCH = 1
DATA_MINING = 0


def gen_size(traffic_type=int, size=int):
    
    flow_size = -1
    #generate ammount 
    p = np.linspace(0,1,num=size)
    if traffic_type == WEB_SEARCH:
        flow_size = np.interp(p, WEB_SEARCH_CDF[:, 1], WEB_SEARCH_CDF[:, 0])
    elif traffic_type == DATA_MINING:
        flow_size = np.interp(p, DATA_MINING_CDF[:, 1], DATA_MINING_CDF[:,0])


    return np.round(flow_size).astype(int)




def genDCTraffic(traffic_source=str, traffic_sink=str, traffic_type=int, traffic_intensity=int, traffic_generation_time=int):

    total_traffic = int(traffic_intensity * traffic_generation_time)
    time_interval = traffic_generation_time / total_traffic 
    interp_traffic = gen_size(traffic_type, total_traffic)

    sink_ip = traffic_sink.IP()
    port = random.randint(10000, 60000)
    server_process = traffic_sink.popen(f"iperf -s -p {port}")
    time.sleep(0.5) 
    active_processes = []


    for i in range(total_traffic):
        
        client_cmd = f"iperf -c {sink_ip} -p {port} -n {interp_traffic[i]}"
        p = traffic_source.popen(client_cmd)
        active_processes.append(p)

        time.sleep(time_interval)

    
    for p in active_processes:
        p.wait()

    server_process.terminate()


