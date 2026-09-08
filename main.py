from mininet.net import Mininet
import topology
import traffic_generation
import sys
import time
import random
import numpy as np
from concurrent.futures import ProcessPoolExecutor
DATA_MINING = 2 
WEB_SEARCH  = 1

def run_test(traffic_type=int, traffic_intensity=int, traffic_generation_time=int, seed=int):
    MyTopology = topology.MyTopo()
    net = Mininet(MyTopology)
    net.start()
    rng = np.random.default_rng(seed)
    source_sink_num = random.sample(range(1,16), 2)

    source     = net.getNodeByName(f"h_{source_sink_num[0]}")
    sink       = net.getNodeByName(f"h_{source_sink_num[1]}")
    result= traffic_generation.genDCTraffic(traffic_source=source,
                                             traffic_sink=sink,
                                             traffic_type=traffic_type,
                                             traffic_intensity=traffic_intensity,
                                             traffic_generation_time=traffic_generation_time,
                                             rng=rng)
    return result

    net.stop()

result = run_test(DATA_MINING,10,1,random.randint(0,100000))
print(result)
