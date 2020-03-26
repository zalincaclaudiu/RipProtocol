import socket
import struct
import sys
import threading
import time

global addresses
global packet

class RipPackage(object):
 
    def __init__(self):
        self.command=b'\x00'
        self.vers=b'\x02'
        self.addressFam=b'\x00\x02'
        self.routeTag=b'\x00\x00'
        self.ipAdress=b'\x00\x00\x00\x00'
        self.netMask= b'\x00\x00\x00\x00'
        self.nextHop=b'\x00\x00\x00\x00'
        self.metric=b'\x00\x00\x00\x00'
 
        self.thePack=b''
 
    def ip_to_int(self,ip):
        l=ip.split('.')
        for i in range(0, len(l)):
            l[i] = int(l[i])
        return struct.pack("BBBB",l[0],l[1],l[2],l[3])
 
    def set_client_ip(self,ip):
        if type(ip)==str:
            self.ipAdress=self.ip_to_int(ip)
        elif type(ip)==int:
            self.ipAdress=ip
 
    def set_netMask(self,netMask):
        if type(netMask) == str:
            self.netMask = self.ip_to_int(netMask)
        elif type(netMask) == int:
            self.netMask = netMask
 
    def pack(self):
        self.thePack+=(self.command[0:1]+self.vers[0:1]+self.addressFam[0:2]+self.routeTag[0:2]+self.ipAdress[0:4]+self.netMask[0:4]+self.nextHop[0:4]+self.metric[0:4])
 
 
    def add_addIp(self,ip,netMask):
        self.thePack+=(self.addressFam[0:2]+self.routeTag[0:2]+self.ip_to_int(ip)[0:4]+self.ip_to_int(netMask)[0:4]+self.nextHop[0:4]+self.metric[0:4])
 
    def getPack(self):
        return self.thePack



def castReceive():

    multicast_group='224.0.0.9'
    server_address=('224.0.0.9',10000)
    #addresses=[]
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
 
    sock.bind(server_address)

    group=socket.inet_aton(multicast_group)
    mreq=struct.pack('4sL',group,socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP,socket.IP_ADD_MEMBERSHIP,mreq)

    while True:
        print('the multicast waiting to receive message')
        data, address=sock.recvfrom(1024)

        #print("Message sent to multicast: "+data)
        i=6
        while(i<len(data)):
            ip=''
            for j in range(0,4):
                ip+=(str(int.from_bytes(data[(i+j):(i+j+1)],"big"))+'.')
            i+=20
            ip=ip[:-1]
            if ip not in addresses:
                packet.add_addIp(ip,'255.255.255.0')
                addresses.append(ip)
        print("Address: "+str(address))
        print("TABELA DE RUTARE:")
        print(addresses)
        #if address not in addresses:
            #addresses.append(address)
        #print(addresses)
        sock.sendto(packet.getPack(),address)
    sock.close()


def receive(socket,i):
    while True:
        data,socketAddress=socket.recvfrom(2048)
        #i=6
        #while(i<len(data)):
            #ip=''
            #for j in range(0,4):
                #ip+=(str(int.from_bytes(data[(i+j):(i+j+1)],"big"))+'.')
            #i+=20
            #ip=ip[:-1]
            #if ip not in addresses:
                #packet.add_addIp(ip,'255.255.255.0')
                #addresses.append(ip)        
        print("The socket address which sent the message: "+str(socketAddress))
    print("Socketul "+ str(i)+" done")


addresses=[]

mctr=threading.Thread(name='Multicast receive',target=castReceive,);
mctr.start()

packet=RipPackage()
packet.set_client_ip('192.168.1.5')
packet.set_netMask('255.255.255.0')
packet.pack()
packet.add_addIp('192.168.10.7','255.255.255.0')
print(packet.getPack())
print(type(packet.getPack()))



socket2_1Name='192.168.1.5'
socket2_1Port=12001
socket2_2Name='192.168.10.7'
socket2_2Port=12002

multicast_group=('224.0.0.9',10000)

ttl=struct.pack('b',1)
socket2_1=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
socket2_1.bind((socket2_1Name,socket2_1Port))
socket2_1.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,ttl)
print("Socket 2_1 is ready to use!")

socket2_2=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
socket2_2.bind((socket2_2Name,socket2_2Port))
socket2_2.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,ttl)
print("Socket 2_2 is ready to use!")


p1=threading.Thread(name="Thread1",target=receive,args=(socket2_1,1,))
p1.start()
p2=threading.Thread(name="Thread2",target=receive,args=(socket2_2,2,))
p2.start()

while(True):
    time.sleep(30)
    socket2_1.sendto(packet.getPack(),multicast_group)
    socket2_2.sendto(packet.getPack(),multicast_group)

mctr.join()
p1.join()
p2.join()
socket2_1.close()
socket2_2.close()
print("Program done")
