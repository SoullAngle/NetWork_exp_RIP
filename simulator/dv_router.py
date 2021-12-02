"""
Your awesome Distance Vector router for CS 168

Based on skeleton code by:
  MurphyMc, zhangwen0411, lab352
"""

import sim.api as api
from cs168.dv import RoutePacket, \
                     Table, TableEntry, \
                     DVRouterBase, Ports, \
                     FOREVER, INFINITY

#在实验时，首先在cs168.dv中找到对应的数据结构

class DVRouter(DVRouterBase):

    # A route should time out after this interval
    ROUTE_TTL = 15

    # Dead entries should time out after this interval
    GARBAGE_TTL = 10

    # -----------------------------------------------
    # At most one of these should ever be on at once
    SPLIT_HORIZON = False
    POISON_REVERSE = False
    # -----------------------------------------------
    
    # Determines if you send poison for expired routes
    POISON_EXPIRED = False

    # Determines if you send updates when a link comes up
    SEND_ON_LINK_UP = False

    # Determines if you send poison when a link goes down
    POISON_ON_LINK_DOWN = False

    def __init__(self):
        """
        Called when the instance is initialized.
        DO NOT remove any existing code from this method.
        However, feel free to add to it for memory purposes in the final stage!
        """
        assert not (self.SPLIT_HORIZON and self.POISON_REVERSE), \
                    "Split horizon and poison reverse can't both be on"
        
        self.start_timer()  # Starts signaling the timer at correct rate.

        # Contains all current ports and their latencies.
        # See the write-up for documentation.
        self.ports = Ports()
        
        # This is the table that contains all current routes
        self.table = Table()
        self.table.owner = self


    def add_static_route(self, host, port):
        """
        Adds a static route to this router's table.

        Called automatically by the framework whenever a host is connected
        to this router.

        :param host: the host.
        :param port: the port that the host is attached to.
        :returns: nothing.
        """
        # `port` should have been added to `peer_tables` by `handle_link_up`
        # when the link came up.
        assert port in self.ports.get_all_ports(), "Link should be up, but is not."
        #=========================stage 1===============================================
        #构造静态路由表，目标：每一个直接连接的host都会被加入到表中
        ltcy=self.ports.get_latency(port) #get latency
        self.table[host]=TableEntry(dst=host, port=port, latency=ltcy, expire_time=FOREVER)
        # TODO: fill this in!

    def handle_data_packet(self, packet, in_port):
        """
        Called when a data packet arrives at this router.

        You may want to forward the packet, drop the packet, etc. here.

        :param packet: the packet that arrived.
        :param in_port: the port from which the packet arrived.
        :return: nothing.
        """
        #=================stage 2================================
        #update Table （利用上一个函数）
        # self.add_static_route(packet.src, in_port)
        #查表
        #table 包含了每个host及其所在的端口
        #table Entry 是个列表
        #get latency一定注意，是表里的latency而不需要重新get一遍
        if packet.dst in self.table:
            port = self.table[packet.dst][1]
            ltcy=self.table[packet.dst][2] 
            # print(ltcy)
            if ltcy<INFINITY:
                self.send(packet=packet, port=port) 
                return 

        #排除不发的port
        all_ports = self.ports.get_all_ports()
        not_send_ports = [] #根据Table获得所有不发送的port
        for host, entry in self.table.items():
            port = entry[1]   #get port
            not_send_ports.append(port)
        
        #剩余端口全发
        for i in all_ports:   #ports i
            if i in not_send_ports or i==in_port:
                continue
            else:
                #检查一下延时，如果超过INF，也不发
                ltcy=self.table[packet.dst][2] #get latency
                if ltcy>=INFINITY:
                    continue
                self.send(packet=packet, port=i)
        # TODO: fill this in!

    def send_routes(self, force=False, single_port=None):
        """
        Send route advertisements for all routes in the table.

        :param force: if True, advertises ALL routes in the table;
                      otherwise, advertises only those routes that have
                      changed since the last advertisement.
               single_port: if not None, sends updates only to that port; to
                            be used in conjunction with handle_link_up.
        :return: nothing.
        """
        for host, entry in self.table.items():
            pkt = RoutePacket(destination=host, latency=entry[2])
            self.send(packet=pkt, flood=True)
        # TODO: fill this in!

    def expire_routes(self):
        """
        Clears out expired routes from table.
        accordingly.
        """
        # TODO: fill this in!

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.
        """
        # TODO: fill this in!

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this router goes up.

        :param port: the port that the link is attached to.
        :param latency: the link latency.
        :returns: nothing.
        """
        self.ports.add_port(port, latency)

        # TODO: fill in the rest!

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this router does down.

        :param port: the port number used by the link.
        :returns: nothing.
        """
        self.ports.remove_port(port)

        # TODO: fill this in!

    # Feel free to add any helper methods!
