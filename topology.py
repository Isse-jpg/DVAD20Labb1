from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.cli import CLI

class MyTopo(Topo):
    def build(self):
        CoreSwitch = self.addSwitch('s0')
        FirstLevelSwitches = []
        SecondLevelSwitches = []
        UsedHosts = []
        h_number = 1 
        
        for i in range (4):
            FirstSw = self.addSwitch(f's1_{i}')
            self.addLink(FirstSw, CoreSwitch, bw=20, delay='1ms')
            FirstLevelSwitches.append(FirstSw)

            for j in range (2):
                SecondSw = self.addSwitch(f's2_{i}_{j}')
                self.addLink(SecondSw, FirstSw, bw=20, delay='1ms')
                SecondLevelSwitches.append(SecondSw)

                for k in range (2):
                    UsedH = self.addHost(f'h_{h_number}')
                    self.addLink(UsedH, SecondSw, bw=20, delay='1ms')
                    UsedHosts.append(UsedH)
                    h_number+=1
