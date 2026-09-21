import time
import asyncio
import pyshark
def monitor_flow(
    flow_id,
    process,
    start_time,
    flow_size,
    results,
    results_lock
):
    return_code = process.wait()
    stop_time = time.monotonic()

    result = {
        "size": flow_size,
        "fct": stop_time - start_time,
        "return_code": return_code,
    }

    with results_lock:
        results[flow_id] = result

def monitor_flow_pyshark(pcap_file: str):
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
