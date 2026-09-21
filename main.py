from mininet.net import Mininet
from concurrent.futures import ThreadPoolExecutor, as_completed
import topology
import scipy.stats as t
import capture
import os
import traffic_generation
import sys
import time
import random
import numpy as np
from concurrent.futures import ProcessPoolExecutor
DATA_MINING = 2 
WEB_SEARCH  = 1

def run_test(traffic_type:int, traffic_intensity:int, traffic_generation_time:int, seed:int, source_name: str, sink_name:str):
    MyTopology = topology.MyTopo()
    net = Mininet(MyTopology)
    net.start()
    rng = np.random.default_rng(seed)

    source     = net.getNodeByName(source_name)
    sink       = net.getNodeByName(sink_name)
    result= traffic_generation.genDCTraffic(traffic_source=source,
                                             traffic_sink=sink,
                                             traffic_type=traffic_type,
                                             traffic_intensity=traffic_intensity,
                                             traffic_generation_time=traffic_generation_time,
                                             rng=rng)
    net.stop()
    return result

mean_result = list()
seed = random.randint(0,100000) 
source_sink_num = random.sample(range(1,16), 2)
source_name = f"h_{source_sink_num[0]}"
sink_name   = f"h_{source_sink_num[1]}"
result = run_test(DATA_MINING,1,10,seed,source_name,sink_name)
print(result)
'''for i in range(10):
    result = []
    for j in range(10):

        source_sink_num = random.sample(range(1,16), 2)
        source_name = f"h_{source_sink_num[0]}"
        sink_name   = f"h_{source_sink_num[1]}"
        seed = random.randint(0,100000) 
        result.append(run_test(DATA_MINING,i,10,seed,source_name,sink_name))
    mean_result.append(np.mean([result[i].get("fct") for i in range(10)]))



mean_fct = np.mean(mean_result)
std_dev = np.std(mean_result, ddof=1)
n = len(mean_result)
se = std_dev / np.sqrt(np.size(mean_result))
confidence_level = 0.95
t_crit = t.ppf(0.975, df=n - 1)
ci_half_width = t_crit * se
ci_lower = mean_fct - ci_half_width
ci_upper = mean_fct + ci_half_width

print(f"Medelvärde:              {mean_fct:.4f}")
print(f"Standardavvikelse:       {std_dev:.4f}")
print(f"Antal observationer:     {n}")
print(f"Standardfel:             {se:.4f}")
print(f"Konfidensnivå:           {confidence_level:.0%}")
print(f"Konfidensintervall:      [{ci_lower:.4f}, {ci_upper:.4f}]")
print(f"Felmarginal:             ±{ci_half_width:.4f}")'''

