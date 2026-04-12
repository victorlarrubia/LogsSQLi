#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REMOTE_RAW="gdrive_logsqli:LogsSQLi/data/raw"

echo "[1/4] Convertendo logs/access.log para CSV estruturado..."
python "$SCRIPT_DIR/convert_access_to_csv.py"

echo
echo "[2/4] Garantindo payloads_dataset.csv em data/raw..."
cp "$PROJECT_DIR/payloads_dataset.csv" "$PROJECT_DIR/data/raw/payloads_dataset.csv"

echo
echo "[3/4] Sincronizando data/raw com Google Drive..."
rclone sync "$PROJECT_DIR/data/raw" "$REMOTE_RAW" -P

echo
echo "[4/4] Pipeline local finalizado com sucesso."
echo "Arquivos locais : $PROJECT_DIR/data/raw"
echo "Arquivos remotos: $REMOTE_RAW"
