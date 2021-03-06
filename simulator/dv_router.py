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
        #查表，如果在表里，而且延时符合条件，则发送
        #table 包含了每个host及其所在的端口
        #table Entry 是个列表
        #get latency一定注意，是表里的latency而不需要重新get一遍
        if packet.dst in self.table:
            port = self.table[packet.dst][1]
            ltcy=self.table[packet.dst][2] 
            # print(ltcy)
            if ltcy<INFINITY:
                self.send(packet=packet, port=port) 
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
        #遍历查看过期条目并删除
        to_del = []
        for host, entry in self.table.items():
            if api.current_time() > entry[3]: # time > expire_time为过期时间
                to_del.append(host)
        for i in to_del: 
            self.table.pop(i)

        # TODO: fill this in!

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.
        """
        #正确的修正延时和过期时间
        # print(self.table)
        new_table = TableEntry(dst=route_dst, port=port, latency=route_latency+self.ports.get_latency(port), expire_time=api.current_time()+self.ROUTE_TTL)
        # print("new_table: ", new_table)
        if not self.table.get(route_dst): #不在表里
            self.table[route_dst] = new_table
        else: #在表里比较延迟
            entry = self.table[route_dst]
            if api.current_time() >= entry[3]: #过期，更新(其实用不上)
                self.table[route_dst] = new_table
            if new_table[2] < entry[2]: #比较cost
                self.table[route_dst] = new_table
            if new_table[1] == entry[1]: #同一个端口问题
                self.table[route_dst] = new_table

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
