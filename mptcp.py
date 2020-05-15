#!/usr/bin/python

"""
linuxrouter.py: Example network with Linux IP router
This example converts a Node into a router using IP forwarding
already built into Linux.
The example topology creates a router and three IP subnets:
    - 192.168.1.0/24 (r0-eth1, IP: 192.168.1.1)
    - 172.16.0.0/12 (r0-eth2, IP: 172.16.0.1)
    - 10.0.0.0/8 (r0-eth3, IP: 10.0.0.1)
Each subnet consists of a single host connected to
a single switch:
    r0-eth1 - s1-eth1 - h1-eth0 (IP: 192.168.1.100)
    r0-eth2 - s2-eth1 - h2-eth0 (IP: 172.16.0.100)
    r0-eth3 - s3-eth1 - h3-eth0 (IP: 10.0.0.100)
The example relies on default routing entries that are
automatically created for each router interface, as well
as 'defaultRoute' parameters for the host interfaces.
Additional routes may be added to the router or hosts by
executing 'ip route' or 'route' commands on the router or hosts.
"""


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):

        
        router0 = self.addNode( 'r0', cls=LinuxRouter, ip='10.0.0.1/24' )
        router1 = self.addNode( 'r1', cls=LinuxRouter, ip='10.0.1.1/24' )

        # h1 = self.addHost( 'h1', ip='10.0.0.100/24',
        #                    defaultRoute='via 10.0.0.1' )
        # h2 = self.addHost( 'h2', ip='10.0.2.100/24',
        #                    defaultRoute='via 10.0.2.1' )

        s1, s2, s3, s4 = [ self.addSwitch( s ) for s in ( 's1', 's2', 's3', 's4' ) ]

        #Routers
        self.addLink( s1, router0, intfName2='r0-eth1',
                      params2={ 'ip' : '10.0.0.1/24'} )  # for clarity
        self.addLink( s2, router0, intfName2='r0-eth2',
                      params2={ 'ip' : '10.0.2.1/24' } )
        
        self.addLink( s3, router1, intfName2='r1-eth1',
                      params2={ 'ip' : '10.0.1.1/24'} )
		self.addLink( s4, router1, intfName2='r1-eth2',
                      params2={ 'ip' : '10.0.3.1/24' } )
        
        h1 = self.addNode( 'h1', cls=LinuxRouter, ip='10.0.0.100/24' )
       	h2 = self.addNode( 'h2', cls=LinuxRouter, ip='10.0.2.100/24' )

		#Hosts

        self.addLink( s1, h1, intfName2='h1-eth1',
                      params2={ 'ip' : '10.0.0.100/24' } )  # for clarity
        self.addLink( s2, h2, intfName2='h2-eth1',
                      params2={ 'ip' : '10.0.2.100/24' } )  # for clarity
        
        self.addLink( s3, h1, intfName2='h1-eth2',
                      params2={ 'ip' : '10.0.1.100/24' } )  # for clarity
		self.addLink( s4, h2, intfName2='h2-eth2',
                      params2={ 'ip' : '10.0.3.100/24' } )  # for clarity
        

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )  # controller is used by s1-s3
    net.start()
    info( '*** Routing Table on Router:\n' )
    info( net[ 'r0' ].cmd( 'route' ) )
    info( net[ 'r1' ].cmd( 'route' ) )

    net['h1'].cmd('tc qdisc add dev h1-eth1 root tbf rate 50mbit burst 1mbit latency 1ms')
    net['h1'].cmd('tc qdisc add dev h1-eth2 root tbf rate 50mbit burst 1mbit latency 1ms')
    net['h2'].cmd('tc qdisc add dev h2-eth1 root tbf rate 50mbit burst 1mbit latency 1ms')
    net['h2'].cmd('tc qdisc add dev h2-eth2 root tbf rate 50mbit burst 1mbit latency 1ms')
    net['r0'].cmd('tc qdisc add dev r0-eth1 root tbf rate 50mbit burst 1mbit latency 1ms')
    net['r0'].cmd('tc qdisc add dev r0-eth2 root tbf rate 50mbit burst 1mbit latency 1ms')
    net['r1'].cmd('tc qdisc add dev r1-eth1 root tbf rate 50mbit burst 1mbit latency 1ms')
    net['r1'].cmd('tc qdisc add dev r1-eth2 root tbf rate 50mbit burst 1mbit latency 1ms')

    net['h1'].cmd('ip route add 10.0.2.100 via 10.0.0.1 dev h1-eth1')
    net['h1'].cmd('ip route add 10.0.3.100 via 10.0.1.1 dev h1-eth2')

	net['h2'].cmd('ip route add 10.0.0.100 via 10.0.2.1 dev h2-eth1')
    net['h2'].cmd('ip route add 10.0.1.100 via 10.0.3.1 dev h2-eth2')



 #    net['h1'].cmd("ip rule add from 10.0.0.100 table 1")
	# net['h1'].cmd("ip rule add from 10.0.1.100 table 2")

	# net['h1'].cmd('ip route add 10.0.0.0/24 dev h1-eth0 scope link table 1')
 #  	net['h1'].cmd('ip route add default via 10.0.0.1 dev h1-eth0 table 1')

 #  	net['h1'].cmd('ip route add 10.0.1.0/24 dev h1-eth1 scope link table 2')
 #  	net['h1'].cmd('ip route add default via 10.0.1.1 dev h1-eth1 table 2')

 #  # default route for the selection process of normal internet-traffic
 #  	net['h1'].cmd('ip route add default scope global nexthop via 10.0.0.1 dev eth0')

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()