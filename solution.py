from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(string):
# In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet(ID):
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.

    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.

    # Don’t send the packet yet , just return the final packet in this function.
    checkityCheckCheck = 0

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, checkityCheckCheck, ID, 1)
    now = time.time()
    data = struct.pack("d", now)
    checkityCheckCheck = checksum(header + data)


    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        checkityCheckCheck = htons(checkityCheckCheck) & 0xffff
    else:
        checkityCheckCheck = htons(checkityCheckCheck)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, checkityCheckCheck, ID, 1)
    #Fill in end

    # So the function ending should look like this

    packet = header + data
    return packet

def get_route(hostname):
    timeLeft = TIMEOUT

    tracelist2 = [] #This is your list to contain all traces

    for ttl in range(1,MAX_HOPS):
        tracelist1 = []  # This is your list to use when iterating through each trace
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)

            #Fill in start
            icmp = getprotobyname("icmp")
            # Make a raw socket named mySocket
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            myID = os.getpid() & 0xFFFF
            #Fill in end

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet(myID)
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    tracelist1.append("* * * Request timed out.")
                    #Fill in start
                    tracelist1.append(str(ttl))
                    tracelist1.append("0 ")
                    tracelist1.append("* ")
                    tracelist1.append("request timed out. ")

                    tracelist2.append(tracelist1)
                    #You should add the list above to your all traces list
                    #Fill in end
                recvPacket, addr = mySocket.recvfrom(1024)
                hopHostIP = addr[0]

                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    #Fill in start
                    tracelist1.append(str(ttl))
                    tracelist1.append("0 ")
                    tracelist1.append("* ")
                    tracelist1.append("request timed out. ")

                    tracelist2.append(tracelist1)
                    #You should add the list above to your all traces list
                    #Fill in end
            except timeout:
                continue

            else:
                #Fill in start
                header = struct.unpack_from("bbHHh", recvPacket, 20)
                types = header[0]

                #Fetch the icmp type from the IP packet
                #Fill in end
                try: #try to fetch the hostname
                    #Fill in start
                    hopDestHostname = gethostbyaddr(hopHostIP)[0]
                    #Fill in end
                except herror:   #if the host does not provide a hostname
                    #Fill in start
                    hopDestHostname = "Hostname not found"
                    #Fill in end

                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    tracelist1.append(str(ttl))

                    rtt = round(((timeReceived - t) * 1000), 2)
                    tracelist1.append(str(rtt))
                    tracelist1.append(hopHostIP)
                    tracelist1.append(hopDestHostname)

                    tracelist2.append(tracelist1)
                    #You should add your responses to your lists here
                    #Fill in end
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here
                    tracelist1.append(str(ttl))

                    rtt = round(((timeReceived - t) * 1000), 2)
                    tracelist1.append(str(rtt))
                    tracelist1.append(hopHostIP)
                    tracelist1.append(hopDestHostname)

                    tracelist2.append(tracelist1)
                    #Fill in end
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    #You should add your responses to your lists here and return your list if your destination IP is met
                    tracelist1.append(str(ttl))

                    rtt = round(((timeReceived - t) * 1000), 2)
                    tracelist1.append(str(rtt))
                    tracelist1.append(hopHostIP)
                    tracelist1.append(hopDestHostname)

                    tracelist2.append(tracelist1)
                    #Fill in end
                else:
                    #Fill in start
                    #If there is an exception/error to your if statements, you should append that to your list here
                    tracelist1.append(str(ttl))
                    tracelist1.append("*")
                    tracelist1.append("*")
                    tracelist1.append("*")

                    tracelist2.append(tracelist1)
                    #Fill in end
                break
            finally:
                mySocket.close()

    return tracelist2

if __name__ == '__main__':
    dest = "google.com"
    traces = get_route(dest)
    print("traceroute to " + str(dest))
    for i in range(len(traces)):
        print(traces[i][0] + "\t" + traces[i][1] + "ms" + "\t" + traces[i][2] + "\t" + traces[i][3])