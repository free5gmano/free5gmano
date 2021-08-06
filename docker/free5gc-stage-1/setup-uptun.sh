#/bin/bash
# Create a network tunnel device in container
ip tuntap add mode tun dev uptun
# Write the setup cidr with tunnel device
ip addr add 45.45.0.1/16 dev uptun
# Set the tunnel device NIC boot up
ip link set dev uptun up
# Follow free5gc iptables setting
sh -c 'echo 1 > /proc/sys/net/ipv4/ip_forward'
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -I INPUT -i uptun -j ACCEPT