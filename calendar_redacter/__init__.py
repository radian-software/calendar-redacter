import configparser
import json
import hashlib
import re
import shutil
import subprocess
from typing import Callable

from ics.grammar.parse import Container, ContentLine, calendar_string_to_containers

import calendar_redacter.config as cfg


def log(msg):
    print(f"[calendar-redacter] {msg}")


def format_vd_cfg(o):
    if isinstance(o, dict):
        return {k: format_vd_cfg(v) for k, v in o.items()}
    return json.dumps(o)


def redact_event(o):
    if isinstance(o, Container):
        if o.name == "VTIMEZONE":
            return o
        return Container(o.name, *list(filter(None, map(redact_event, o))))
    if isinstance(o, ContentLine):
        if o.name == "SUMMARY":
            return ContentLine("SUMMARY", value="Busy")
        if o.name in {"ORGANIZER", "ATTENDEE", "DESCRIPTION", "LOCATION", "CREATED"}:
            return None
        if o.name.startswith("X-JMAP-"):
            return None
        if o.name == "UID":
            return ContentLine("UID", value=hashlib.sha1(o.value.encode()).hexdigest())
        return o
    return o


def main():
    log("Doing initial setup")
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)
    vd_dir = cfg.DATA_DIR / "vdirsyncer-local"
    out_dir = cfg.DATA_DIR / "vdirsyncer-redacted"
    vd_cfg = configparser.ConfigParser()
    vd_cfg.update(
        format_vd_cfg(
            {
                "general": {
                    "status_path": str(cfg.DATA_DIR / "vdirsyncer-status"),
                },
                "storage local": {
                    "type": "filesystem",
                    "path": str(vd_dir),
                    "fileext": ".ics",
                },
                "storage redacted": {
                    "type": "filesystem",
                    "path": str(out_dir),
                    "fileext": ".ics",
                },
                "storage remote": {
                    "type": "caldav",
                    "url": cfg.CALDAV_URL,
                    "username": cfg.CALDAV_USERNAME,
                    "password": cfg.CALDAV_PASSWORD,
                },
                "pair download": {
                    "a": "local",
                    "b": "remote",
                    "collections": cfg.CALDAV_COLLECTIONS,
                    "conflict_resolution": "b wins",
                },
                "pair upload": {
                    "a": "redacted",
                    "b": "remote",
                    "collections": [cfg.CALDAV_REDACTED],
                    "conflict_resolution": "a wins",
                },
            }
        )
    )
    vd_cfg_file = cfg.DATA_DIR / "vdirsyncer-config"
    with open(vd_cfg_file, "w") as f:
        vd_cfg.write(f)
    # https://github.com/pimutils/vdirsyncer/issues/969#issuecomment-1047823700
    for coll in cfg.CALDAV_COLLECTIONS:
        (vd_dir / coll).mkdir(parents=True, exist_ok=True)
    log("Running vdirsyncer to download")
    run_vd = lambda *args: subprocess.run(
        ["vdirsyncer", f"--config={str(vd_cfg_file)}", *args], check=True
    )
    run_vd("discover", "download")
    run_vd("sync", "download")
    shutil.rmtree(out_dir, ignore_errors=True)
    (out_dir / cfg.CALDAV_REDACTED).mkdir(parents=True, exist_ok=True)
    for coll in cfg.CALDAV_COLLECTIONS:
        log(f"Redacting calendar {coll}")
        for ics in (vd_dir / coll).iterdir():
            with open(coll / ics) as f:
                ev = calendar_string_to_containers(f.read())[0]
            new_id = hashlib.sha1((coll + "_" + ics.name).encode()).hexdigest()
            with open(out_dir / cfg.CALDAV_REDACTED / (new_id + ".ics"), "w") as f:
                f.write(str(redact_event(ev)))
    log("Running vdirsyncer to upload")
    run_vd("discover", "upload")
    run_vd("sync", "upload")
