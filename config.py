# config.py — Central configuration for VIOLA Analyzer

# --- GEMINI ---
GEMINI_API_KEY = "INSERT-GEMINI-API_KEY"
GEMINI_MODEL   = "INSERT-GEMINI_MODEL"

# --- OSC ---
OSC_IP   = "127.0.0.1"
OSC_PORT = 8000

# --- INITIAL SYNTHESIS STATE ---
INITIAL_PARAMS = {
    "p": 1.0,    # pitch      [0.5 – 2.0]
    "f": 1.0,    # fragmentation [0.1 – 20.0 Hz]
    "d": 0.5,    # dynamics LFO [0.1 – 9.0 Hz]
    "t": 1000.0, # timbre cutoff [100 – 8000 Hz]
}

# --- PROCESSING ---
K_INTERVAL        = 60    # seconds between analysis cycles
SIMULATION_DURATION = 600 # seconds for the timed simulation (10 min)

# --- LATENCY THRESHOLDS (ms) ---
RAMP_HIGH_CONF = 0   # thinked for future implementation
RAMP_LOW_CONF  = 0   # thinked for future implementation
CONFIDENCE_THRESHOLD = 0.7 #thinked for future implementation
