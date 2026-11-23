#!/usr/bin/env bash
set -euo pipefail

PREFIX="/opt/fanoosdesk-server"
STATE_DIR="/var/lib/fanoosdesk-server"
CONF_DIR="/etc/fanoosdesk-server"

if [[ ${EUID} -ne 0 ]]; then
  echo "Please run as root: sudo ./uninstall.sh [--purge]" >&2
  exit 1
fi

systemctl disable --now fanoos-hbbs.service fanoos-hbbr.service 2>/dev/null || true
rm -f /etc/systemd/system/fanoos-hbbs.service
rm -f /etc/systemd/system/fanoos-hbbr.service
systemctl daemon-reload
systemctl reset-failed 2>/dev/null || true

rm -rf "${PREFIX}"
rm -f /usr/local/bin/fanoos-server

if [[ "${1:-}" == "--purge" ]]; then
  rm -rf "${STATE_DIR}" "${CONF_DIR}"
  userdel fanoosdesk 2>/dev/null || true
  groupdel fanoosdesk 2>/dev/null || true
  echo "Fanoos Desk Server removed, including keys and database."
else
  echo "Fanoos Desk Server removed. Data and keys were preserved in ${STATE_DIR}."
  echo "Run './uninstall.sh --purge' if you also want to remove persistent data."
fi
