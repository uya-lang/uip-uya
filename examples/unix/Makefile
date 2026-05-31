APP := /tmp/uya_uip_unix
UYA := ./uya/bin/uya
SOURCES := \
	examples/unix/main.uya \
	ports/uip/uip_base.uya \
	ports/uip/uip_core.uya \
	ports/uip/uip_proto.uya \
	ports/uip/uip_arp.uya

.PHONY: build run clean tap-up tap-down

build:
	$(UYA) build $(SOURCES) -o $(APP)

run: build
	$(APP)

tap-up:
	sudo ip tuntap add dev tap0 mode tap || true
	sudo ip addr add 192.168.0.1/24 dev tap0 || true
	sudo ip link set tap0 up

tap-down:
	sudo ip link del tap0 || true

clean:
	rm -f $(APP)
