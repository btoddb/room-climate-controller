#!/usr/bin/env bash
# Build the Room Climate Controller Lovelace card and deploy it into the
# integration's www/ directory.
#
# The integration serves the card at /room_climate_controller/ and auto-registers
# it as a frontend module (add_extra_js_url) with no-cache headers, so after this
# runs you only need to HARD-REFRESH the browser — there is no Lovelace resource
# to add and no Home Assistant restart required.
#
# Requires Node/npm (provided by the devcontainer's Node feature).

SCRIPTS_DIR=$(cd $(dirname $0); pwd)
HOME_DIR=$(dirname ${SCRIPTS_DIR})
echo "home dir = ${HOME_DIR}"

set -euo pipefail

CARD_DIR="${HOME_DIR}/custom_components/room_climate_controller/card"
COMPONENT_WWW="$(cd "$CARD_DIR/.." && pwd)/www"
cd "$CARD_DIR"

# --- 1. Bump patch version (package.json) and sync the console banner so you
#        can confirm in the browser console which build actually loaded. ---
OLD_VERSION=$(python3 -c "import json; print(json.load(open('package.json'))['version'])")
NEW_VERSION=$(python3 -c "p='${OLD_VERSION}'.split('.'); p[2]=str(int(p[2])+1); print('.'.join(p))")
python3 - "$NEW_VERSION" <<'PYEOF'
import json, re, sys
new = sys.argv[1]
data = json.load(open("package.json"))
data["version"] = new
open("package.json", "w").write(json.dumps(data, indent=2) + "\n")
src = open("src/index.ts").read()
src = re.sub(r"v\d+\.\d+\.\d+", f"v{new}", src, count=1)
open("src/index.ts", "w").write(src)
PYEOF
echo "Version: $OLD_VERSION -> $NEW_VERSION"

# --- 2. Install deps (clean, correct-platform native binaries) and build. ---
echo "Installing dependencies..."
npm install
echo "Building..."
npm run build

# --- 3. Deploy the bundle into the component's www/ directory. ---
echo "Deploying to $COMPONENT_WWW ..."
mkdir -p "$COMPONENT_WWW"
cp room-climate-control-card.js room-climate-control-card.js.map "$COMPONENT_WWW/"

echo "Done (v$NEW_VERSION). Hard-refresh your browser (Ctrl+Shift+R) to load the new card."
