# osc_handler.py — OSC client wrapper

from pythonosc import udp_client
from config import OSC_IP, OSC_PORT

_client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)


def send_params(params: dict, ramp_ms: int) -> None:
    """
    Broadcast synthesis parameters and ramp time over OSC.

    OSC addresses
    -------------
    /pitch          → params['p']
    /fragmentation  → params['f']
    /dynamics       → params['d']
    /timbre         → params['t']
    /ramp           → ramp_ms (float)
    """
    _client.send_message("/pitch",         float(params["p"]))
    _client.send_message("/fragmentation", float(params["f"]))
    _client.send_message("/dynamics",      float(params["d"]))
    _client.send_message("/timbre",        float(params["t"]))
    _client.send_message("/ramp",          float(ramp_ms))

    print(f"[OSC] → {OSC_IP}:{OSC_PORT}  "
          f"P:{params['p']:.2f}  F:{params['f']:.1f}  "
          f"D:{params['d']:.1f}  T:{params['t']:.0f}  ramp:{ramp_ms}ms")
