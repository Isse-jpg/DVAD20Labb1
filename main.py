from mininet.net import Mininet
import topology
import sys


def simple_test():
    
    
    MyTopology = topology.MyTopo()
    net = Mininet(MyTopology)
    net.start()
    print(topology.gen_size(1))

    net.stop()

simple_test()

