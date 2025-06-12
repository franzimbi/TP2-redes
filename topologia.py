from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
import sys

setLogLevel('info')

if len(sys.argv) != 2:
    print("sudo python3 topologia.py <numero de switches>")
    exit(1)

try:
    n_switches = int(sys.argv[1])
    if n_switches < 1:
        raise ValueError
except ValueError:
    print("valor de switches invalido")
    exit(1)

net = Mininet(controller=RemoteController, link=TCLink)

# crear switches
switches = []
for i in range(1, n_switches + 1):
    switches.append(net.addSwitch(f's{i}'))

# crear hosts izquierdos
h1 = net.addHost('h1', ip='10.0.0.1', mac='00:00:00:00:00:01')
h2 = net.addHost('h2', ip='10.0.0.2', mac='00:00:00:00:00:02')

# crear hosts derechos
h3 = net.addHost('h3', ip='10.0.0.3', mac='00:00:00:00:00:03')
h4 = net.addHost('h4', ip='10.0.0.4', mac='00:00:00:00:00:04')

net.addLink(h1, switches[0])
net.addLink(h2, switches[0])
net.addLink(h3, switches[-1])
net.addLink(h4, switches[-1])

# conectar switches intermedios
for i in range(len(switches) - 1):
    net.addLink(switches[i], switches[i + 1])

net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
net.start()
print("Hosts:")
for h in [h1, h2, h3, h4]:
    print(f" {h.name} -> IP: {h.IP()}, MAC: {h.MAC()}")

CLI(net)
net.stop()
