# Video Intelligent Agent (VIA)

A minimal, demo-oriented stack for **Frigate**-driven video analytics on a **Mini PC or Jetson**, with a **remote LLM** (e.g. Mistral 7B on a **Local PC or Jetson** via llama.cpp HTTP).

## Architecture (two-machine)

```text
[Mini PC or Jetson]
  Frigate (events, clips)
        ↓ MQTT (Mosquitto in Docker)
  VMS adapter + ingest → Postgres (event store)
        ↓
  Skill layer + FastAPI
        ↓ HTTP
[Local PC or Jetson]
  LLM service (7B — llama.cpp server or Triton later)
```

Design choices from the original plan:

- **Adapter pattern**: one codebase, **Frigate first**; more VMS backends later.
- **LLM on a separate host**: simple HTTP to `/completion` is enough for MVP.
- **Skills**: plain Python functions (no heavy framework).

## Repository layout

```text
video-intel-agent/
  adapters/          # VMSAdapter + FrigateAdapter
  core/              # Normalized event schema (Pydantic)
  skills/            # search, aggregate (DB helpers)
  llm/               # Remote LLM HTTP client
  api/               # FastAPI (health, summary, stats)
  db/                # SQLAlchemy models + session
  docker/            # Legacy / split compose files
  docker-compose.yml # Mosquitto + Postgres + Frigate + ingest (recommended Mini PC or Jetson stack)
  mosquitto/         # Eclipse Mosquitto config + data/log mounts
  ingest.py          # MQTT frigate/events → Postgres
  requirements.txt
  pyproject.toml
```

## Quick start (development)

1. **Python 3.10+**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   # optional editable install so imports match tooling
   pip install -e .
   ```

2. **Postgres** — use `docker/docker-compose.postgres.yml` or a local instance. Default URL matches the compose file:

   ```bash
   cp .env.example .env
   docker compose -f docker/docker-compose.postgres.yml up -d
   ```

3. **Mosquitto** on the Mini PC or Jetson (Frigate publishes to `frigate/events`). Point `MQTT_HOST` in `.env` at the broker.

4. **Ingest** (writes events to DB):

   ```bash
   python ingest.py
   ```

5. **API**:

   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 9000
   ```

   - `GET /health` — liveness  
   - `GET /summary` — recent events + LLM summary (requires `LLM_BASE_URL` reachable)  
   - `GET /stats` — counts by label / camera  

Set `INIT_DB_ON_STARTUP=1` when starting the API the first time to create tables (or rely on `ingest.py`, which creates tables by default via `INIT_DB_ON_INGEST_STARTUP`).

## Docker stack (Mini PC or Jetson — recommended)

**Mosquitto runs in Docker** so Frigate, MQTT, and ingest share one network and use **service names** (`mosquitto`, `postgres`) instead of `localhost` inside containers.

```text
Frigate (Docker)
      ↓
Mosquitto (Docker)
      ↓
VIA ingest (Docker) → Postgres (Docker)
```

From the repo root:

```bash
cp config.yml.example config.yml
# Edit config.yml: set your RTSP URL
docker compose up -d
```

- Frigate UI: `http://<host>:5000`  
- MQTT test: `docker exec -it mosquitto mosquitto_sub -t "frigate/events"`  
- Ingest uses `MQTT_HOST=mosquitto` and `DATABASE_URL` pointing at `postgres` (set in `docker-compose.yml`).

**Avoid** using `localhost` for MQTT inside Frigate’s config when Frigate is in Docker — use `mosquitto` and port `1883` (see `config.yml.example`).

Split / legacy compose files still live under `docker/` (`docker-compose.frigate.yml`, `docker-compose.postgres.yml`).

## Frigate (Mini PC or Jetson)

- `config.yml.example` — minimal CPU detector + MQTT for the **root** `docker-compose.yml`  
- `docker/frigate.config.example.yml` — same idea when using compose files from `docker/`  
- `docker/docker-compose.frigate.yml` — Frigate-only compose if you already run MQTT/DB elsewhere

## LLM (Local PC or Jetson)

Example (llama.cpp server):

```bash
./server -m mistral-7b-instruct.gguf -c 4096 --host 0.0.0.0 --port 8000
```

On the machine running the API, set `LLM_BASE_URL` to the **Local PC or Jetson** where the LLM listens:

```bash
export LLM_BASE_URL=http://<LOCAL_PC_OR_JETSON_IP>:8000
```

The client posts JSON `{"prompt": "..."}` to `{LLM_BASE_URL}/completion` — align this with your server’s actual API if it differs.

## Environment variables

See `.env.example` for `DATABASE_URL`, MQTT, LLM base URL, and optional `INIT_DB_*` flags.

## Project TODO

MVP demo (in order):

1. [ ] Frigate running with a stable RTSP source and objects tracked (person, car, …).
2. [ ] Mosquitto reachable; `mosquitto_sub -t frigate/events` shows payloads.
3. [ ] `ingest.py` running; rows appear in `events` in Postgres.
4. [ ] FastAPI `/stats` returns sensible aggregates.
5. [ ] Local PC or Jetson llama.cpp (or compatible) server up; `/summary` returns an LLM response.

Later / non-MVP (do not block the first demo):

- [ ] MemryX SDK + custom detector path for Frigate (YOLO ONNX → MemryX).
- [ ] Triton or other serving if you outgrow llama.cpp.
- [ ] Extra VMS adapters behind `VMSAdapter`.
- [ ] Richer **event schema v1** (clips, zones, embeddings).
- [ ] Web UI, auth, multi-tenant.

## Demo footage ideas

Prefer clips with a **clear narrative**: loitering near an entrance, brief vehicle stop, back-and-forth walking, parking activity. Sources: YouTube search for parking lot / warehouse surveillance; datasets such as VIRAT / MOT for offline tests.

## License

Add a license file when you publish this repository.
