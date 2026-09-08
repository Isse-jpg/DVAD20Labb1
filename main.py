from mininet.net import Mininet
import topology
import traffic_generation
import sys

MyTopology = topology.MyTopo()
net = Mininet(MyTopology)
net.start()
net.stop()


