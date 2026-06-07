#!/usr/bin/env bash
# Bumps patch version, builds the card, and updates the Lovelace resource URL in HA.
# Requires $SUPERVISOR_TOKEN (available automatically inside the HA container).
set -euo pipefail

CARD_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPONENT_WWW="$(cd "$CARD_DIR/.." && pwd)/www"
RESOURCE_ID="f7e8d9c0b1a2436586970809abcdef01"
RESOURCE_BASE="/room_climate_controller/room-climate-control-card.js"

# --- 1. Bump patch version in package.json ---
OLD_VERSION=$(python3 -c "import json; print(json.load(open('$CARD_DIR/package.json'))['version'])")
NEW_VERSION=$(python3 -c "
parts = '${OLD_VERSION}'.split('.')
parts[2] = str(int(parts[2]) + 1)
print('.'.join(parts))
")
python3 -c "
import json
path = '$CARD_DIR/package.json'
data = json.load(open(path))
data['version'] = '$NEW_VERSION'
open(path, 'w').write(json.dumps(data, indent=2) + '\n')
"
echo "Version: $OLD_VERSION → $NEW_VERSION"

# --- 2. Build ---
echo "Building..."
npm --prefix "$CARD_DIR" run build

# --- 3. Copy built files into the component's www/ directory ---
echo "Copying to component www/ ..."
mkdir -p "$COMPONENT_WWW"
cp "$CARD_DIR/room-climate-control-card.js" "$COMPONENT_WWW/"
cp "$CARD_DIR/room-climate-control-card.js.map" "$COMPONENT_WWW/"

# --- 4. Update Lovelace resource URL via HA WebSocket API ---
echo "Updating HA resource URL to ?v=$NEW_VERSION ..."
python3 << PYEOF
import socket, json, os, base64, struct

token = os.environ['SUPERVISOR_TOKEN']
resource_id = '$RESOURCE_ID'
new_url = '${RESOURCE_BASE}?v=$NEW_VERSION'

sock = socket.create_connection(('supervisor', 80), timeout=10)
key = base64.b64encode(os.urandom(16)).decode()
sock.sendall((
    'GET /core/websocket HTTP/1.1\r\n'
    'Host: supervisor\r\n'
    f'Authorization: Bearer {token}\r\n'
    'Upgrade: websocket\r\n'
    'Connection: Upgrade\r\n'
    f'Sec-WebSocket-Key: {key}\r\n'
    'Sec-WebSocket-Version: 13\r\n\r\n'
).encode())

buf = b''
while b'\r\n\r\n' not in buf:
    buf += sock.recv(1)

def ws_recv():
    hdr = sock.recv(2)
    length = hdr[1] & 0x7f
    if length == 126:
        length = struct.unpack('>H', sock.recv(2))[0]
    elif length == 127:
        length = struct.unpack('>Q', sock.recv(8))[0]
    data = b''
    while len(data) < length:
        data += sock.recv(length - len(data))
    return json.loads(data.decode())

def ws_send(obj):
    data = json.dumps(obj).encode()
    mask = os.urandom(4)
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
    length = len(data)
    if length < 126:
        header = bytes([0x81, 0x80 | length])
    elif length < 65536:
        header = bytes([0x81, 0xfe]) + struct.pack('>H', length)
    else:
        header = bytes([0x81, 0xff]) + struct.pack('>Q', length)
    sock.sendall(header + mask + masked)

ws_recv()  # auth_required
ws_send({'type': 'auth', 'access_token': token})
result = ws_recv()
if result.get('type') != 'auth_ok':
    print(f"ERROR: Auth failed: {result.get('message','')}")
    exit(1)

ws_send({'id': 1, 'type': 'lovelace/resources/update',
         'resource_id': resource_id, 'res_type': 'module', 'url': new_url})
result = ws_recv()
if result.get('success'):
    print(f"Resource updated: {new_url}")
else:
    print(f"ERROR: {result}")
    exit(1)
sock.close()
PYEOF

echo "Done. Hard-refresh your browser to load the new card."
