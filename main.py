from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
import topology
import data_analysis
import os
import traffic_generation
import csv
import random
import numpy as np
import sys
import argparse
import time

DATA_MINING = 2 
WEB_SEARCH  = 1
PCAP_PATH = "/tmp/traffic.pcap"


def run_test(net, traffic_type:int, traffic_intensity:int, traffic_generation_time:int, seed:int, source_name: str, sink_name:str):
    rng = np.random.default_rng(seed)

    source = net.getNodeByName(source_name)
    sink   = net.getNodeByName(sink_name)

    net.ping([source, sink])
    
    result = traffic_generation.genDCTraffic(
        traffic_source=source,
        traffic_sink=sink,
        traffic_type=traffic_type,
        traffic_intensity=traffic_intensity,
        traffic_generation_time=traffic_generation_time,
        rng=rng,
        pcap_path=PCAP_PATH
    )
    return result

def evaluate_test(traffic_type:int, traffic_intensity_min:int, traffic_intensity_max:int, iterations:int, csv_filename:str, summary_filename:str, node_bw:int):
    if traffic_intensity_max <= 0 or traffic_intensity_min <=0:
        print("[Error] invalid traffic generation size!")
        return
        
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Traffic_Intensity", "Run_Number", "Source", "Sink", "Stream_ID", "FCT", "Total_Bytes"])

    print(f"\n[Log] Building and starting mininet (bandwidth: {node_bw} Mbps)...")
    setLogLevel('error')
    MyTopology = topology.MyTopo(node_bw)
    net = Mininet(MyTopology,link=TCLink)
    net.staticArp()
    net.start()

    try:
        for i in range(traffic_intensity_min, traffic_intensity_max+1):
            source_sink_num = random.sample(range(1, 17), 2)
            source_name = f"h_{source_sink_num[0]}"
            sink_name   = f"h_{source_sink_num[1]}"
            for j in range(1, iterations+1):
                success = False
            
                while not success:
                    try:
                        seed = random.randint(0, 100000) 

                        run_test(net, traffic_type, i, 10, seed, source_name, sink_name)

                        run_data = data_analysis.tshark_get_data_from_pcap(PCAP_PATH)

                        with open(csv_filename, mode='a', newline='') as f:
                            writer = csv.writer(f)
                            
                            for stream_id, data in run_data.items():
                                fct = data["fct"]
                                #for timeouts
                                if fct >= 4.9:
                                    fct = 5.0
                                total_bytes = data["total_bytes"]
                                
                                writer.writerow([i, j, source_name, sink_name, stream_id, fct, total_bytes])
                                
                        print(f"[Log] Intensity {i} done, iteration {j}. Data saved.")
                        success = True
                        
                        time.sleep(1)

                    except Exception as e:
                        print(f"[Warning] iteration {j}, intensity {i} failed. Retrying.....  Error:{e}")
                        source = net.getNodeByName(source_name)
                        sink = net.getNodeByName(sink_name)
                        source.cmd('pkill -9 iperf'); sink.cmd('pkill -9 iperf'); source.cmd('pkill -9 tshark')
    finally:
        print("[Log] Tests done. Closing mininet...")
        net.stop()
        
    print(f"Evaluation completed. Results written to {csv_filename}")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Mininet simulation for Flow Completion Time (FCT).")
    
    parser.add_argument(
        "--type", 
        choices=["web", "data", "both"], 
        default="both", 
        help="Which traffic type to run (web, data, or both)."
    ) 
    parser.add_argument(
        "--min_intensity", 
        type=int, 
        default=1, 
        help="Minimum traffic intensity (default: 1)."
    )

    parser.add_argument(
        "--max_intensity", 
        type=int, 
        default=10, 
        help="Maximum traffic intensity (default: 10)."
    )
    parser.add_argument(
        "--iterations", 
        type=int, 
        default=10, 
        help="Number of iterations per intensity level (default: 10)."
    )
    
    parser.add_argument(
        "--bandwidth", 
        type=int, 
        default=20, 
        help="Node bandwidth (in Mbps, default 20)"
    )
    args = parser.parse_args()

    print(f"Starting test: Type={args.type}, Min intensity={args.min_intensity}, Max Intensity={args.max_intensity}, Iterations={args.iterations} Node bandwidth={args.bandwidth} Mbps")
    
    #generate data

    if args.type in ["data", "both"]:
        print("\n--- Running Data Mining ---")
        evaluate_test(
            traffic_type=DATA_MINING, 
            traffic_intensity_min=args.min_intensity,
            traffic_intensity_max=args.max_intensity, 
            iterations=args.iterations, 
            csv_filename="fct_data_mining.csv", 
            summary_filename="summary_data_mining.txt",
            node_bw=args.bandwidth
        )

    if args.type in ["web", "both"]:
        print("\n--- Running Web Search ---")
        evaluate_test(
            traffic_type=WEB_SEARCH, 
            traffic_intensity_min=args.min_intensity,
            traffic_intensity_max=args.max_intensity, 
            iterations=args.iterations, 
            csv_filename="fct_web_search.csv", 
            summary_filename="summary_web_search.txt",
            node_bw=args.bandwidth
        )



