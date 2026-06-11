#!/bin/bash

# =============================================================
#  install_odbc.sh
#  Installs Microsoft ODBC Driver 17 — Ubuntu 24.04 (Noble)
#  Run with: sudo bash install_odbc.sh
# =============================================================

set -e

# ── Colors ───────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
success(){ echo -e "${GREEN}[OK]${NC}    $1"; }
error()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── Root check ───────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
  error "Please run with sudo: sudo bash install_odbc.sh"
fi

# ── Step 1: Clean any previous broken install ────────────────
log "Step 1/6 — Cleaning any previous broken entries..."
rm -f /etc/apt/sources.list.d/mssql-release.list
rm -f /usr/share/keyrings/microsoft-prod.gpg
apt-key del EB3E94ADBE1229CF 2>/dev/null || true
success "Cleaned."

# ── Step 2: Install dependencies ─────────────────────────────
log "Step 2/6 — Installing dependencies..."
apt-get update -qq
apt-get install -y curl gnupg2 apt-transport-https lsb-release > /dev/null
success "Dependencies installed."

# ── Step 3: Add Microsoft GPG key (modern method) ────────────
log "Step 3/6 — Adding Microsoft GPG key..."
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
  | gpg --dearmor \
  | tee /usr/share/keyrings/microsoft-prod.gpg > /dev/null
success "GPG key added."

# ── Step 4: Add signed repository ────────────────────────────
log "Step 4/6 — Adding Microsoft repository..."
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/ubuntu/24.04/prod noble main" \
  | tee /etc/apt/sources.list.d/mssql-release.list > /dev/null
apt-get update -qq
success "Repository added."

# ── Step 5: Install ODBC Driver 17 + unixodbc-dev ────────────
log "Step 5/6 — Installing ODBC Driver 17..."
ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev > /dev/null
success "ODBC Driver 17 installed."

# ── Step 6: Verify ────────────────────────────────────────────
log "Step 6/6 — Verifying installation..."
if odbcinst -q -d | grep -q "ODBC Driver 17 for SQL Server"; then
  echo ""
  echo -e "${GREEN}================================================${NC}"
  echo -e "${GREEN}   ODBC Driver 17 installed successfully!      ${NC}"
  echo -e "${GREEN}================================================${NC}"
  echo ""
  echo -e "  Registered driver:"
  odbcinst -q -d
  echo ""
  echo -e "  You can now run: python3 mssql_app.py"
  echo ""
else
  error "Driver not detected. Run manually: odbcinst -q -d"
fi