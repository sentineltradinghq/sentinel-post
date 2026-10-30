"""Configura OpenJarvis para usar el Lanzador Sentinel (respaldo del config incluido)."""
import json, shutil, sys
from datetime import datetime
from pathlib import Path
import tomlkit

base = Path.home() / ".openjarvis"
cfg = base / "config.toml"
lanzador = base / "lanzador.py"

doc = tomlkit.parse(cfg.read_text(encoding="utf-8")) if cfg.exists() else tomlkit.document()
if cfg.exists():
    shutil.copy(cfg, cfg.with_name(f"config.toml.bak-{datetime.now():%Y%m%d-%H%M%S}"))

uv = shutil.which("uv") or "uv"
servidor = {"name": "lanzador", "command": uv,
            "args": ["run", "--with", "mcp", "python", str(lanzador)]}

doc.setdefault("engine", tomlkit.table())
doc["engine"].setdefault("default", "ollama")
doc.setdefault("intelligence", tomlkit.table())
doc["intelligence"].setdefault("default_model", "qwen3.5:9b")
doc.setdefault("agent", tomlkit.table())
doc["agent"]["default_agent"] = "orchestrator"
doc.setdefault("tools", tomlkit.table())
mcp = doc["tools"].setdefault("mcp", tomlkit.table())
existentes = []
try:
    existentes = json.loads(mcp.get("servers", "") or "[]")
    if isinstance(existentes, dict):
        existentes = [existentes]
except Exception:
    existentes = []
existentes = [s for s in existentes if s.get("name") != "lanzador"] + [servidor]
mcp["enabled"] = True
mcp["servers"] = json.dumps(existentes)

cfg.write_text(tomlkit.dumps(doc), encoding="utf-8")
print("Listo: lanzador configurado en", cfg)
print("uv:", uv)
