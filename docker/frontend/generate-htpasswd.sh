#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$(dirname "$0")"
out="$(dirname "$0")/.htpasswd"
user="${ADMIN_USER:-admin}"
pass="${ADMIN_PASS:-admin}"

if command -v htpasswd >/dev/null 2>&1; then
  htpasswd -bc "$out" "$user" "$pass"
else
  python3 - "$user" "$pass" <<'PY'
import sys,crypt,os
u,p=sys.argv[1:]
salt="".join([str(os.urandom(1)[0]%16) for _ in range(8)])
print(f"{u}:{crypt.crypt(p, '$6$'+salt)}")
PY
fi
echo "Wrote $out"
