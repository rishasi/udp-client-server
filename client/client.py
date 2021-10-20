import socket
import sys
import time

# Create socket for server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
print("Do Ctrl+c to exit the program !!")

server_ip = sys.argv[1]

# Find local hostname
local_ip = socket.gethostbyname(socket.gethostname());

# Let's send data through UDP protocol
count = 0
while count < 150:
    count_in_str = "% s" % count
    send_data = "Message number " + count_in_str + " from: "
    s.sendto(send_data.encode('utf-8') + local_ip.encode('utf-8'), (server_ip, 20001))
    print("\n\n 1. Client Sent : ", send_data + local_ip, "\n\n")
    data, address = s.recvfrom(4096)
    print("\n\n 2. Client received : ", data.decode('utf-8'), "\n\n")
    count = count + 1
    time.sleep(1)
# close the socket
s.close()
