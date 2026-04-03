#!/usr/bin/env python3
"""
MQTT subscriber: Frigate `frigate/events` → normalize → Postgres.

Run from repo root:
  python ingest.py
"""
from __future__ import annotations

import json
import logging
import os
import sys

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

from adapters.frigate import FrigateAdapter
from core.events import dict_to_normalized
from db.models import Event
from db.session import SessionLocal, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger("ingest")

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "frigate/events")
INIT_DB = os.getenv("INIT_DB_ON_INGEST_STARTUP", "1") == "1"

adapter = FrigateAdapter()


def on_message(_client: mqtt.Client, _userdata: object, msg: mqtt.MQTTMessage) -> None:
    try:
        data = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        LOG.warning("Skip non-JSON payload: %s", exc)
        return

    try:
        normalized = dict_to_normalized(adapter.ingest_event(data))
    except Exception as exc:
        LOG.exception("Adapter failed: %s", exc)
        return

    row = normalized.to_db_row()
    db = SessionLocal()
    try:
        db.add(Event(**row))
        db.commit()
        LOG.info("Stored event camera=%s label=%s", row.get("camera"), row.get("label"))
    except Exception as exc:
        LOG.exception("DB insert failed: %s", exc)
        db.rollback()
    finally:
        db.close()


def on_connect(
    client: mqtt.Client,
    _userdata: object,
    _flags: object,
    reason_code: object,
    _properties: object | None = None,
) -> None:
    if reason_code.is_failure:
        LOG.error("MQTT connect failed: %s", reason_code)
        return
    client.subscribe(MQTT_TOPIC)
    LOG.info("Subscribed to %s", MQTT_TOPIC)


def main() -> None:
    if INIT_DB:
        init_db()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    LOG.info("Connecting to MQTT %s:%s …", MQTT_HOST, MQTT_PORT)
    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    except OSError as exc:
        LOG.error("Cannot connect to MQTT: %s", exc)
        sys.exit(1)

    client.loop_forever()


if __name__ == "__main__":
    main()
