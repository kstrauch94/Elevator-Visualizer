# Default Config
HOST = "127.0.0.1"
PORT = 6000

MSG_SIZE = 4096

# Message types
# From client
BASE = "base"
SOLVE = "solve"
ADDREQS = "addreqs"
RESET = "reset"
ENCODING = "encoding"
# From server
SUCCESS = "success"
FAIL = "failure"
# Message end marker
DONE = "147258369"

# Dictionary Keys
ACTIONS = "actions"
REQUESTS = "requests"
STATS = "stats"
ELEVAMT = "elevamt"
FLOORAMT = "flooramt"
STARTPOS = "startpos"

# Request types
REQ_CALL     = "call"
REQ_DELIVER  = "deliver"