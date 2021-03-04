package main

import (
	"fmt"
	"net"
)

func main() {
	src := "0.0.0.0:6000"
	listener, err := net.ListenPacket("udp", src)
	if err != nil {
		fmt.Println(err.Error())
	}
	defer listener.Close()

	fmt.Printf("UDP server start and listening on %s.\n", src)

	for {
		buf := make([]byte, 1024)
		n, addr, err := listener.ReadFrom(buf)
		if err != nil {
			continue
		}
		go serve(listener, addr, buf[:n])

	}
}

func serve(listener net.PacketConn, addr net.Addr, buf []byte) {
	fmt.Printf("%s\t: %s\n", addr, buf)
	listener.WriteTo([]byte("message recived!\n"), addr)
}