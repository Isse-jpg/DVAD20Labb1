import numpy as np
import argparse
from scipy.stats import t
import asyncio
import pyshark
import matplotlib.pyplot as plt
import subprocess

def tshark_get_data_from_pcap(pcap_file: str):
    cmd = [
        "tshark", "-r", pcap_file,
        "-Y", "tcp",
        "-T", "fields",
        "-e", "tcp.stream",
        "-e", "frame.time_epoch",
        "-e", "frame.len"
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    
    streams = {}
    results = {}
    
    for line in process.stdout:
        parts = line.strip().split('\t')
        
        if len(parts) == 3:
            try:
                stream_id = int(parts[0].split(',')[0]) # Split ifall tshark returnerar listor vid retransmissions
                pkt_time = float(parts[1])
                pkt_len = int(parts[2].split(',')[0])
                
                if stream_id not in streams:
                    streams[stream_id] = {
                        "start_time": pkt_time,
                        "end_time": pkt_time,
                        "total_bytes": 0
                    }
                
                streams[stream_id]["end_time"] = pkt_time
                streams[stream_id]["total_bytes"] += pkt_len
            except ValueError:
                continue
                
    process.wait()
    
    for stream_id, data in streams.items():
        results[stream_id] = {
            "stream_id": stream_id,
            "fct": data["end_time"] - data["start_time"],
            "total_bytes": data["total_bytes"]
        }
        
    return results
def calculate_fct_ci_numpy(file_name):

    data = np.genfromtxt(file_name, delimiter=',', usecols=(0, 1, 5))

    data = data[~np.isnan(data).any(axis=1)]

    intensities = np.unique(data[:, 0])

    results = {}

    for intensity in intensities:
        intensity_data = data[data[:, 0] == intensity]

        iterations = np.unique(intensity_data[:, 1])
        iter_means = []

        for iteration in iterations:

            fct_values = intensity_data[intensity_data[:, 1] == iteration][:, 2]
            iter_means.append(np.mean(fct_values))

        n = len(iter_means)
        mean_val = np.mean(iter_means)

        if n < 2:
            results[intensity] = {'Mean': mean_val, 'CI_Error': 0.0}
        else:
            std_val = np.std(iter_means, ddof=1)
            se = std_val / np.sqrt(n)
            t_crit = t.ppf(0.975, df=n-1)
            ci_error = t_crit * se

            results[intensity] = {'Mean': mean_val, 'CI_Error': ci_error}

    return results

def plot_fct_results(results_dict, label="Web Search", color="blue", save_path=None):
    intensities = list(results_dict.keys())
    means = [results_dict[i]['Mean'] for i in intensities]
    errors = [results_dict[i]['CI_Error'] for i in intensities]

    plt.figure(figsize=(8, 5))
    plt.errorbar(intensities, means, yerr=errors, fmt='-o', capsize=5, color=color, label=label)

    plt.xlabel('Traffic intensity')
    plt.ylabel('Flow Completion Time (s)')
    plt.title(f'FCT vs Traffic intensity ({label})')
    plt.xticks(intensities) 
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    if save_path:
        plt.savefig(save_path)
        print(f"[Log] Graph saved as: {save_path}")
    else:
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run analysis of mininet FCT")
    
    parser.add_argument(
        "--input", 
        type=str, 
        help="input filename (must be a CSV file!)"
    ) 

    parser.add_argument(
        "--graph", 
        type=bool, 
        default=True,
        help="Generate graph of data."
    ) 
    parser.add_argument(
        "--type",
        choices=["web","data mining"],
        type=str,
        default="web",
        help="Type of traffic to analyse")
    parser.add_argument(
        "--graph_file_name",
        type=str,
        default="output.png",
        help="name of graph output file")

    args = parser.parse_args()
    
    result = calculate_fct_ci_numpy(args.input)
    print(result)
    if args.graph:
        label = f"{args.type} traffic"
        plot_fct_results(results_dict=result,label=label,save_path=args.graph_file_name)


