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
	sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	sock.bind(server_address)

	group=socket.inet_aton(multicast_group)
	mreq=struct.pack('4sL',group,socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP,socket.IP_ADD_MEMBERSHIP,mreq)


	while True:
		print('the multicast waiting to receive message')
		data,address=sock.recvfrom(1024)
		print("Am receptionat mesaj")
		#print("Message sent to multicast: "+ data)
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
		#print("Message from socket: "+str(messageFromSocket))
		print("The socket address which sent the message: "+str(socketAddress))
	print("Socket "+str(i)+" done for receiving!")

addresses=[]

mctr=threading.Thread(name='Multicast Receive',target=castReceive,)
mctr.start()

packet=RipPackage()
packet.set_client_ip('192.168.10.6')
packet.set_netMask('255.255.255.0')
packet.pack()
packet.add_addIp('192.168.20.5','255.255.255.0')
print(packet.getPack())
print(type(packet.getPack()))

socket3_1Name='192.168.10.6'
socket3_1Port=12003

socket3_2Name='192.168.20.5'
socket3_2Port=12004

multicast_group=('224.0.0.9',10000)
ttl=struct.pack('b',2)

socket3_1=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
socket3_1.bind((socket3_1Name,socket3_1Port))
socket3_1.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,ttl)
print("Socket 3_1 is ready to use!")

socket3_2=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
socket3_2.bind((socket3_2Name,socket3_2Port))
socket3_2.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,ttl)
print("Socket 3_2 is ready to use!")

t1=threading.Thread(name="Thread1",target=receive,args=(socket3_1,1,))
t1.start()
t2=threading.Thread(name="Thread2",target=receive,args=(socket3_2,2,))
t2.start()

while(True):
	time.sleep(30)
	socket3_1.sendto(packet.getPack(),multicast_group)
	print("Trimit pachet")
	socket3_2.sendto(packet.getPack(),multicast_group)

mctr.join()
t1.join()
t2.join()
print(tabelaRutare)
socket3_1.close()
socket3_2.close()	
print("Script 3 done!")