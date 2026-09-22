from mininet.net import Mininet
import topology
import data_analysis
import os
import traffic_generation
import csv
import random
import numpy as np

DATA_MINING = 2 
WEB_SEARCH  = 1
PCAP_PATH = "/tmp/traffic.pcap"

def run_test(traffic_type:int, traffic_intensity:int, traffic_generation_time:int, seed:int, source_name: str, sink_name:str):
    MyTopology = topology.MyTopo()
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

def evaluate_test(traffic_type:int, traffic_intensity_max:int, iterations:int, csv_filename:str, summary_filename:str):
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
            
            run_test(traffic_type, i, 10, seed, source_name, sink_name)
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


fct_data_mining = "fct_data_mining.csv"
summary_data_mining = "summary_data_mining.txt"
evaluate_test(DATA_MINING,5,2,fct_data_mining,summary_data_mining)


fct_web_search = "fct_web_search.csv"
summary_web_search = "summary_web_search.txt"
evaluate_test(WEB_SEARCH,10,10,fct_web_search,summary_web_search)
