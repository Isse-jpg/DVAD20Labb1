import numpy as np
from scipy.stats import t
import asyncio
import pyshark
def tshark_get_data_from_pcap(pcap_file: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    #needed for python 3.14.7
    cap = pyshark.FileCapture(
        pcap_file,
        display_filter="tcp",
        keep_packets=False,
        eventloop=loop,
    )

    streams = {}
    results = {}
    for pkt in cap:
        try:
            stream_id = int(pkt.tcp.stream)
            pkt_time = float(pkt.sniff_timestamp)
            pkt_len = int(pkt.length)
            if stream_id not in streams:
                streams[stream_id] = {
                "start_time": pkt_time,
                "end_time": pkt_time,
                "total_bytes": 0
            }

            streams[stream_id]["end_time"] = pkt_time
            streams[stream_id]["total_bytes"] += pkt_len 
                
        
        except AttributeError:
            continue
    for stream_id,data in streams.items():
        results[stream_id] = {
                "stream_id": stream_id,
                "fct": data["end_time"] - data["start_time"],
                "total_bytes": data["total_bytes"]
        }
    cap.close()


    return results

def calculate_fct_ci(iteration_means, output_filename):
    values = np.array(iteration_means)
    n = len(values)
    
    if n < 2:
        print("[WARNING] At least 2 runs are required to calculate the confidence interval.")
        return

    mean_fct = np.mean(values)
    s = np.std(values, ddof=1)
    se = s / np.sqrt(n)
    t_crit = t.ppf(0.975, df=n - 1)
    ci_half_width = t_crit * se
    ci_lower = mean_fct - ci_half_width
    ci_upper = mean_fct + ci_half_width
    
    output_text = (
        "=== STATISTICAL SUMMARY ===\n"
        f"Mean:                    {mean_fct:.4f}\n"
        f"Standard Deviation:      {s:.4f}\n"
        f"Number of observations:  {n}\n"
        f"Standard Error:          {se:.4f}\n"
        f"Confidence Level:        95%\n"
        f"Confidence Interval:     [{ci_lower:.4f}, {ci_upper:.4f}]\n"
        f"Margin of Error:         ±{ci_half_width:.4f}\n"
    )
    
    print(output_text)
    
    with open(file=output_filename, mode='w', encoding='utf-8') as f:
        f.write(output_text)
