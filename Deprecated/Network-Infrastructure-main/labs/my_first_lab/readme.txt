The contents of the "shared" folder are shared between your host computer and all the running containers of kathara.
You can find this folder in the network containers in the path: /shared

This folder contains two .pcap files containing some captured packet.
In order to create them we launched tcpdump on R1 to listen for packets on interface eth1:
	tcpdump -i eth1 -w shared/my_capture_tcp.pcap
You can open the .pcap file on your computer with wireshark, for example

We have launched netcat in server mode on port 8080 on s1 and netcat in client mode on pc1 using TCP.
We exchanged some data between the hosts: pc1 sends the string "hi i'm pc1 using TCP" and s1 replies with "hi i'm s1, now i'm closing the connection".

The same data is then exchanged using UDP, in the file shared/my_capture_udp.pcap
