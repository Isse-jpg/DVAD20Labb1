from mininet.net import Mininet
import topology
import data_analysis
import os
import traffic_generation
import csv
import random
import numpy as np
import sys
import argparse

DATA_MINING = 2 
WEB_SEARCH  = 1
PCAP_PATH = "/tmp/traffic.pcap"

def run_test(traffic_type:int, traffic_intensity:int, traffic_generation_time:int, seed:int, source_name: str, sink_name:str,node_bw:int):
    MyTopology = topology.MyTopo(node_bw)
    net = Mininet(MyTopology)
    net.start()
    net.pingAll()
    rng = np.random.default_rng(seed)

    source     = net.getNodeByName(source_name)
    sink       = net.getNodeByName(sink_name)
    result= traffic_generation.genDCTraffic(traffic_source=source,
                                             traffic_sink=sink,
                                             traffic_type=traffic_type,
                                             traffic_intensity=traffic_intensity,
                                             traffic_generation_time=traffic_generation_time,
                                             rng=rng,pcap_path=PCAP_PATH)
    net.stop()
    return result

def evaluate_test(traffic_type:int, traffic_intensity_max:int, iterations:int, csv_filename:str, summary_filename:str, node_bw:int):
    mean_result = []

    #create file if it doesnt exist
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Traffic_Intensity", "Run_Number", "Source", "Sink", "Stream_ID", "FCT", "Total_Bytes"])

    for i in range(1, traffic_intensity_max+1):
        iteration_fcts = []
        for j in range(1, iterations+1):
        
            source_sink_num = random.sample(range(1, 16), 2)
            source_name = f"h_{source_sink_num[0]}"
            sink_name   = f"h_{source_sink_num[1]}"
            seed = random.randint(0, 100000) 
            
            run_test(traffic_type, i, 10, seed, source_name, sink_name,node_bw)
            run_data = data_analysis.tshark_get_data_from_pcap(PCAP_PATH)
            
            with open(csv_filename, mode='a', newline='') as f:
                writer = csv.writer(f)
                
                for stream_id, data in run_data.items():
                    fct = data["fct"]
                    total_bytes = data["total_bytes"]
                    
                    writer.writerow([i, j, source_name, sink_name, stream_id, fct, total_bytes])
                    
                    iteration_fcts.append(fct)
                    
            print(f"[Logg] Intensity {i} done, iteration {j}. Data saved.")

        if iteration_fcts:
            mean_result.append(np.mean(iteration_fcts))
        
    print(f"Evaluation completed. Results written to {csv_filename}")
    data_analysis.calculate_fct_ci(mean_result, summary_filename)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Mininet simulation for Flow Completion Time (FCT).")
    
    parser.add_argument(
        "--type", 
        choices=["web", "data", "both"], 
        default="both", 
        help="Which traffic type to run (web, data, or both)."
    )
    parser.add_argument(
        "--intensity", 
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

    print(f"Starting test: Type={args.type}, Max Intensity={args.intensity}, Iterations={args.iterations} Node bandwidth={args.bandwidth} Mbps")

    if args.type in ["data", "both"]:
        print("\n--- Running Data Mining ---")
        evaluate_test(
            traffic_type=DATA_MINING, 
            traffic_intensity_max=args.intensity, 
            iterations=args.iterations, 
            csv_filename="fct_data_mining.csv", 
            summary_filename="summary_data_mining.txt",
            node_bw=args.bandwidth
        )

    if args.type in ["web", "both"]:
        print("\n--- Running Web Search ---")
        evaluate_test(
            traffic_type=WEB_SEARCH, 
            traffic_intensity_max=args.intensity, 
            iterations=args.iterations, 
            csv_filename="fct_web_search.csv", 
            summary_filename="summary_web_search.txt",
            node_bw=args.bandwidth
        )

