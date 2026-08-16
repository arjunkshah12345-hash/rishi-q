#!/usr/bin/env bash
# Submit frozen ISEF2027 preregistration materials to OSF.
# Requires: OSF_TOKEN (personal access token with nodes write scope)
# Does NOT unlock confirmatory analysis.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -z "${OSF_TOKEN:-}" ]]; then
  echo "OSF_TOKEN not set. Create a token at https://osf.io/settings/tokens/"
  echo "Then: export OSF_TOKEN=... && $0"
  echo "Interim timestamp: GitHub Release prereg-isef2027-v1"
  exit 2
fi

TITLE="RISHI-Q ISEF2027 Confirmatory Preregistration"
API="https://api.osf.io/v2"

echo "Creating OSF project..."
RESP=$(curl -sS -X POST "$API/nodes/" \
  -H "Authorization: Bearer $OSF_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  -d "{\"data\":{\"type\":\"nodes\",\"attributes\":{\"title\":\"$TITLE\",\"category\":\"project\",\"description\":\"Frozen confirmatory preregistration for RISHI-Q / ISEF2027. See protocol/osf/.\"}}}")

NODE_ID=$(python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["data"]["id"])' <<<"$RESP")
echo "Created node: $NODE_ID"
echo "https://osf.io/$NODE_ID/" | tee protocol/osf/OSF_NODE_URL.txt

# Upload files via waterbutler
for f in \
  protocol/osf/OSF_PREREGISTRATION.md \
  protocol/isef2027_prereg_TEMPLATE.yaml \
  protocol/osf/FREEZE_MANIFEST.sha256 \
  artifacts/isef2027/STUDENT_DECISIONS.yaml \
  ethics/isef2027_SRC_IRB_DETERMINATION.md
do
  name=$(basename "$f")
  echo "Uploading $name ..."
  curl -sS -X PUT \
    "https://files.osf.io/v1/resources/$NODE_ID/providers/osfstorage/?kind=file&name=$name" \
    -H "Authorization: Bearer $OSF_TOKEN" \
    --data-binary @"$f" >/tmp/osf_upload_"$name".json
done

# Record URL into prereg yaml if empty
python3 - <<PY
from pathlib import Path
p = Path("protocol/isef2027_prereg_TEMPLATE.yaml")
text = p.read_text()
url = Path("protocol/osf/OSF_NODE_URL.txt").read_text().strip()
if 'osf_or_aspredicted_url: ""' in text:
    p.write_text(text.replace('osf_or_aspredicted_url: ""', f'osf_or_aspredicted_url: "{url}"'))
    print("Wrote URL into prereg YAML:", url)
else:
    print("URL field already set; see", url)
PY

echo "DONE. Create a formal OSF Preregistration from the project UI if required by your fair."
echo "Do NOT unlock confirmatory scoring until the registration is public."
