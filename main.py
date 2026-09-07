from mininet.net import Mininet
import scipy
import topology

def simple_test():
    MyTopology = topology.MyTopo()
    net = Mininet(MyTopology)
    net.start()
    print("testing ping")
    net.pingAll()
    net.stop()

simple_test()

def GenDCTraffic(traffic_source=str,traffic_sink=str,traffic_type=int,traffic_intensity=10,traffic_generation_time=int):
    pass
