"""Create technically coherent local UDP and HTTP packet traffic."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

from scapy.all import Ether, IP, Raw, TCP, UDP

from encrypt_memory import KEY_RECIPE, encode_memory, split_encoded


UDP_PORT = 41842
CONTROL_IP = "10.77.14.5"
ARCHIVE_IP = "10.77.14.80"
BROADCAST_IP = "10.77.14.255"
CHALLENGE_FLAG = "ACM{spire_registry_breach_unraveled}"
COMPROMISED_TOWER = "VLT-707"
COMPROMISED_SERIAL = "SLT-8B19-ARC"
COMPROMISED_DEVICE = "folio-amber"
TRANSFER_ID = "MEM-ORIEL-72"
APPROVED_TOWERS = {
    "AST-014": "Astronomy Spire",
    "NWT-221": "North Watchtower",
    "RVN-332": "Raven Signal Tower",
    "WRP-418": "West Rampart Tower",
}


@dataclass
class CaptureClock:
    value: float = 1_764_480_000.0

    def stamp(self, packet: object, step: float = 0.075) -> object:
        packet.time = self.value  # type: ignore[attr-defined]
        self.value += step
        return packet


def _mac(index: int) -> str:
    return f"02:77:14:00:00:{index:02x}"


def _udp_broadcast(clock: CaptureClock, source_ip: str, source_mac: str, message: str) -> object:
    packet = (
        Ether(src=source_mac, dst="ff:ff:ff:ff:ff:ff")
        / IP(src=source_ip, dst=BROADCAST_IP)
        / UDP(sport=UDP_PORT, dport=UDP_PORT)
        / Raw(message.encode("ascii"))
    )
    return clock.stamp(packet, 0.11)


def _http_request(method: str, path: str, host: str, user_agent: str, body: str = "") -> bytes:
    headers = [
        f"{method} {path} HTTP/1.1",
        f"Host: {host}",
        f"User-Agent: {user_agent}",
        "Accept: application/json",
        "Connection: close",
    ]
    if body:
        headers.extend(
            [
                "Content-Type: application/x-www-form-urlencoded",
                f"Content-Length: {len(body.encode('ascii'))}",
            ]
        )
    return ("\r\n".join(headers) + "\r\n\r\n" + body).encode("ascii")


def _http_response(body: str, content_type: str = "application/json") -> bytes:
    encoded = body.encode("utf-8")
    headers = [
        "HTTP/1.1 200 OK",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(encoded)}",
        "Connection: close",
    ]
    return "\r\n".join(headers).encode("ascii") + b"\r\n\r\n" + encoded


def _tcp_exchange(
    clock: CaptureClock,
    client_ip: str,
    client_mac: str,
    client_port: int,
    request: bytes,
    response: bytes,
    sequence_seed: int,
) -> list[object]:
    """Build one complete, single-request HTTP TCP connection."""
    server_mac = _mac(0x50)
    client_seq = sequence_seed
    server_seq = sequence_seed + 50_000
    common_client = dict(src=client_ip, dst=ARCHIVE_IP)
    common_server = dict(src=ARCHIVE_IP, dst=client_ip)
    client_eth = dict(src=client_mac, dst=server_mac)
    server_eth = dict(src=server_mac, dst=client_mac)
    packets: list[object] = []

    packets.append(clock.stamp(Ether(**client_eth) / IP(**common_client) / TCP(sport=client_port, dport=80, flags="S", seq=client_seq, options=[("MSS", 1460), ("SAckOK", b""), ("WScale", 7)])))
    packets.append(clock.stamp(Ether(**server_eth) / IP(**common_server) / TCP(sport=80, dport=client_port, flags="SA", seq=server_seq, ack=client_seq + 1, options=[("MSS", 1460), ("SAckOK", b""), ("WScale", 7)])))
    packets.append(clock.stamp(Ether(**client_eth) / IP(**common_client) / TCP(sport=client_port, dport=80, flags="A", seq=client_seq + 1, ack=server_seq + 1)))

    request_seq = client_seq + 1
    response_seq = server_seq + 1
    request_end = request_seq + len(request)
    response_end = response_seq + len(response)
    packets.append(clock.stamp(Ether(**client_eth) / IP(**common_client) / TCP(sport=client_port, dport=80, flags="PA", seq=request_seq, ack=response_seq) / Raw(request)))
    packets.append(clock.stamp(Ether(**server_eth) / IP(**common_server) / TCP(sport=80, dport=client_port, flags="A", seq=response_seq, ack=request_end)))
    packets.append(clock.stamp(Ether(**server_eth) / IP(**common_server) / TCP(sport=80, dport=client_port, flags="PA", seq=response_seq, ack=request_end) / Raw(response)))
    packets.append(clock.stamp(Ether(**client_eth) / IP(**common_client) / TCP(sport=client_port, dport=80, flags="A", seq=request_end, ack=response_end)))
    packets.append(clock.stamp(Ether(**client_eth) / IP(**common_client) / TCP(sport=client_port, dport=80, flags="FA", seq=request_end, ack=response_end)))
    packets.append(clock.stamp(Ether(**server_eth) / IP(**common_server) / TCP(sport=80, dport=client_port, flags="A", seq=response_end, ack=request_end + 1)))
    packets.append(clock.stamp(Ether(**server_eth) / IP(**common_server) / TCP(sport=80, dport=client_port, flags="FA", seq=response_end, ack=request_end + 1)))
    packets.append(clock.stamp(Ether(**client_eth) / IP(**common_client) / TCP(sport=client_port, dport=80, flags="A", seq=request_end + 1, ack=response_end + 1)))
    return packets


def _agent(device: str, serial: str, tower: str) -> str:
    return f"HogMesh/2.7 (unit={device}; serial={serial}; relay={tower})"


def build_capture() -> tuple[list[object], list[dict[str, str]]]:
    """Return packets and a private timeline for the released static case."""
    clock = CaptureClock()
    packets: list[object] = []
    timeline: list[dict[str, str]] = []

    approved = ",".join(APPROVED_TOWERS)
    registry = f"WARDEN-REG/3; revision=74; approved={approved}; scope=castle-grounds"
    packets.append(_udp_broadcast(clock, CONTROL_IP, _mac(0x05), registry))
    timeline.append({"stage": "registry", "detail": "approved tower registry broadcast"})

    source_map = {
        "AST-014": ("10.77.14.11", _mac(0x11), "EAST"),
        "NWT-221": ("10.77.14.12", _mac(0x12), "NORTH"),
        "RVN-332": ("10.77.14.13", _mac(0x13), "WEST"),
        "WRP-418": ("10.77.14.14", _mac(0x14), "SOUTH"),
    }
    for round_number in range(3):
        for tower, (ip, mac, sector) in source_map.items():
            message = f"SPIRE-ANN/2; tower={tower}; state=READY; sector={sector}; cycle={round_number + 1}"
            packets.append(_udp_broadcast(clock, ip, mac, message))
    packets.append(_udp_broadcast(clock, "10.77.14.77", _mac(0x77), "SPIRE-ANN/2; tower=VLT-707; state=READY; sector=ARCHIVE; cycle=1"))
    packets.append(_udp_broadcast(clock, "10.77.14.77", _mac(0x77), "SPIRE-ANN/2; tower=VLT-707; state=READY; sector=ARCHIVE; cycle=2"))
    packets.append(_udp_broadcast(clock, CONTROL_IP, _mac(0x05), registry))
    for number in range(8):
        packets.append(
            clock.stamp(
                Ether(src=_mac(0x60 + number), dst="ff:ff:ff:ff:ff:ff")
                / IP(src=f"10.77.14.{140 + number}", dst=BROADCAST_IP)
                / UDP(sport=5353, dport=5353)
                / Raw(f"GARDEN-MESH; sensor={number:02d}; state=nominal".encode("ascii")),
                0.08,
            )
        )

    connections: list[tuple[str, str, str, str, str, bytes, bytes]] = []
    legitimate_devices = [
        ("10.77.14.31", _mac(0x31), "folio-cedar", "SLT-2A61-NTH", "NWT-221"),
        ("10.77.14.32", _mac(0x32), "folio-quartz", "SLT-4D22-RVN", "RVN-332"),
        ("10.77.14.33", _mac(0x33), "folio-elm", "SLT-7F08-AST", "AST-014"),
        ("10.77.14.34", _mac(0x34), "folio-birch", "SLT-1C90-WRP", "WRP-418"),
    ]
    for index in range(11):
        ip, mac, device, serial, tower = legitimate_devices[index % len(legitimate_devices)]
        agent = _agent(device, serial, tower)
        if index % 2:
            body = urlencode({"event": "heartbeat", "counter": str(index), "battery": "stable"})
            request = _http_request("POST", "/telemetry/heartbeat", "archive-gateway.castle.test", agent, body)
        else:
            request = _http_request("GET", "/catalogue/ping", "archive-gateway.castle.test", agent)
        connections.append((ip, mac, device, serial, tower, request, _http_response('{"status":"stored"}')))

    victim_agent = _agent(COMPROMISED_DEVICE, COMPROMISED_SERIAL, COMPROMISED_TOWER)
    diagnostic_request = _http_request("GET", "/relay/profile", "archive-gateway.castle.test", victim_agent)
    diagnostic_body = (
        '{"protocol":"memory-dispatch/1","cipher":"xor-repeat","encoding":"base64",'
        f'"key_recipe":"{KEY_RECIPE}","identifier_order":"serial|tower",'
        '"fragment_order":"part ascending"}'
    )
    connections.append(("10.77.14.67", _mac(0x67), COMPROMISED_DEVICE, COMPROMISED_SERIAL, COMPROMISED_TOWER, diagnostic_request, _http_response(diagnostic_body)))

    encoded = encode_memory(CHALLENGE_FLAG, COMPROMISED_SERIAL, COMPROMISED_TOWER)
    fragments = split_encoded(encoded, total=6)
    for index, fragment in enumerate(fragments, start=1):
        body = urlencode({"transfer": TRANSFER_ID, "part": index, "total": len(fragments), "data": fragment})
        request = _http_request("POST", "/archive/dispatch", "archive-gateway.castle.test", victim_agent, body)
        response = _http_response('{"accepted":true,"queue":"sealed"}')
        connections.append(("10.77.14.67", _mac(0x67), COMPROMISED_DEVICE, COMPROMISED_SERIAL, COMPROMISED_TOWER, request, response))
        timeline.append({"stage": "fragment", "detail": f"{TRANSFER_ID} part {index}/{len(fragments)}"})

    for index in range(2):
        body = urlencode({"event": "catalogue-sync", "page": str(index + 1)})
        request = _http_request("POST", "/catalogue/sync", "archive-gateway.castle.test", victim_agent, body)
        connections.append(("10.77.14.67", _mac(0x67), COMPROMISED_DEVICE, COMPROMISED_SERIAL, COMPROMISED_TOWER, request, _http_response('{"status":"indexed"}')))

    for index, (ip, mac, _device, _serial, _tower, request, response) in enumerate(connections):
        packets.extend(_tcp_exchange(clock, ip, mac, 47000 + index, request, response, 100_000 + index * 10_000))
    return packets, timeline

