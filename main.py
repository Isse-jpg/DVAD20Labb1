from mininet.net import Mininet
import topology

def simple_test():
    MyTopology = topology.MyTopo()
    net = Mininet(MyTopology)
    net.start()
    print("testing ping")
    net.pingAll()
    net.stop()

simple_test()

