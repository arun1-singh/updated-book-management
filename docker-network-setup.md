# 🐳 Docker Manual Network Setup — MSSQL + Flask App

> **Topic:** Connecting MSSQL and app.py containers using manual Docker networking commands (without Docker Compose)

---

## 📋 Table of Contents

1. [Why localhost Fails](#1-why-localhost-fails)
2. [Fresh Setup — All Steps](#2-fresh-setup--all-steps)
3. [Already Running Containers](#3-already-running-containers)
4. [Verify the Connection](#4-verify-the-connection)
5. [How Docker DNS Works](#5-how-docker-dns-works)
6. [Quick Reference](#6-quick-reference)

---

## 1. Why localhost Fails

Each container has its **own** localhost — it refers only to itself, not to other containers.

```
┌─────────────────────────────────────────┐
│           Docker Host Machine           │
│                                         │
│  ┌─────────────┐     ┌───────────────┐  │
│  │  app.py     │     │  MSSQL        │  │
│  │  container  │     │  container    │  │
│  │             │     │               │  │
│  │ localhost = │  ✗  │ 172.17.0.3    │  │
│  │ itself only │─────▶               │  │
│  └─────────────┘     └───────────────┘  │
│                                         │
│  Each container has its OWN localhost   │
└─────────────────────────────────────────┘
```

### Default Bridge vs Custom Network

| Network Type | DNS by container name | Use `localhost`? |
|---|---|---|
| Default bridge (auto) | ❌ No | ❌ No |
| Custom named bridge | ✅ Yes | ❌ No |
| No Docker (app runs on host) | — | ✅ Yes |

> **Fix:** Create a custom bridge network and use the **container name** as the hostname.

---

## 2. Fresh Setup — All Steps

### Step 1 — Create a custom bridge network
```bash
docker network create app-network
```

---

### Step 2 — Run the MSSQL container on that network
```bash
docker run -d \
  --name mssql-container \
  --network app-network \
  -e ACCEPT_EULA=Y \
  -e SA_PASSWORD=YourStrong@Passw0rd \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2019-latest
```

| Flag | Purpose |
|---|---|
| `--name mssql-container` | Sets the container name — this becomes the DNS hostname |
| `--network app-network` | Attaches it to your custom network |
| `-e ACCEPT_EULA=Y` | Required by Microsoft's MSSQL image |
| `-e SA_PASSWORD` | SA user password — match this in your `.env` |
| `-p 1433:1433` | Exposes MSSQL port to host (for tools like SSMS) |

---

### Step 3 — Run your app container on the same network
```bash
docker run -d \
  --name app-container \
  --network app-network \
  -p 5001:5001 \
  your-app-image
```

---

### Step 4 — Update your `.env`

Use the **MSSQL container name** as the server value:
```env
MSSQL_SERVER=mssql-container
MSSQL_DATABASE=books_db
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourStrong@Passw0rd
MSSQL_DRIVER=ODBC Driver 17 for SQL Server
MSSQL_TRUST_CERT=yes
JWT_SECRET_KEY=your-secret-key
```

> Docker's DNS automatically resolves `mssql-container` to its IP within the same network — no hardcoded IPs needed.

---

## 3. Already Running Containers

If your containers are **already running** without a shared network, connect them after the fact:

### Step 1 — Create the network
```bash
docker network create app-network
```

### Step 2 — Connect both containers to it
```bash
docker network connect app-network mssql-container
docker network connect app-network app-container
```

### Step 3 — Update `.env`
```env
MSSQL_SERVER=mssql-container
```

### Step 4 — Restart the app container to pick up the change
```bash
docker restart app-container
```

> ⚠️ You do **not** need to restart the MSSQL container — only the app needs to re-read the env and reconnect.

---

## 4. Verify the Connection

### Check which containers are on the network
```bash
docker network inspect app-network
```

Look for both `mssql-container` and `app-container` in the `Containers` section of the output.

### Test DNS resolution from inside the app container
```bash
docker exec -it app-container ping mssql-container
```

### Test port 1433 is reachable
```bash
docker exec -it app-container bash -c "apt-get install -y telnet && telnet mssql-container 1433"
```

### List all networks on your machine
```bash
docker network ls
```

---

## 5. How Docker DNS Works

```
docker network create app-network
          ↓
docker run --name mssql-container --network app-network ...
          ↓
Docker registers "mssql-container" as a DNS entry on app-network
          ↓
app-container resolves MSSQL_SERVER=mssql-container → 172.18.0.2
          ↓
pyodbc connects successfully ✅
```

### The Golden Rule
> **Same network + container name = automatic DNS resolution. No IPs needed.**

### Why not use the container IP directly?

```bash
docker inspect mssql-container | grep IPAddress
# → 172.17.0.3
```

| Approach | Works? | Problem |
|---|---|---|
| `MSSQL_SERVER=172.17.0.3` | ✅ Now | IP changes on every container restart |
| `MSSQL_SERVER=mssql-container` | ✅ Always | Stable — name never changes |

---

## 6. Quick Reference

### All commands in order (fresh setup)
```bash
# 1. Create network
docker network create app-network

# 2. Start MSSQL
docker run -d --name mssql-container --network app-network \
  -e ACCEPT_EULA=Y \
  -e SA_PASSWORD=YourStrong@Passw0rd \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2019-latest

# 3. Start app
docker run -d --name app-container --network app-network \
  -p 5001:5001 \
  your-app-image

# 4. Verify
docker network inspect app-network
```

### Already running containers
```bash
docker network create app-network
docker network connect app-network mssql-container
docker network connect app-network app-container
docker restart app-container
```

### Useful inspect commands
```bash
docker network ls                          # list all networks
docker network inspect app-network        # see containers on network
docker inspect mssql-container            # see full container details + IP
docker exec -it app-container ping mssql-container  # test DNS
```

---

### Checklist

- [ ] Custom network created: `docker network create app-network`
- [ ] MSSQL container running with `--network app-network`
- [ ] App container running with `--network app-network`
- [ ] `.env` updated: `MSSQL_SERVER=mssql-container`
- [ ] `docker network inspect app-network` shows both containers
- [ ] Ping test passes from app container to MSSQL container

---

*Session conducted on June 11, 2026*
