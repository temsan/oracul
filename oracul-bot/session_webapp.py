#!/usr/bin/env python3
"""
Минимальный Telegram Web App для управления пользовательской сессией.

Запуск:
  uvicorn session_webapp:app --host 0.0.0.0 --port 8088
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


AUTH_STORAGE_PATH = Path(__file__).parent / "data" / "user_auth_sessions.json"
DEFAULT_TTL = max(5, int(os.getenv("DEFAULT_SESSION_TTL_MINUTES", "60")))
TTL_OPTIONS = sorted(
    {
        *(
            int(x.strip())
            for x in os.getenv("SESSION_TTL_OPTIONS_MINUTES", "15,60,180,720,1440").split(",")
            if x.strip().isdigit() and int(x.strip()) >= 5
        ),
        DEFAULT_TTL,
    }
)


class SessionPreferences(BaseModel):
    ttl_minutes: int = Field(ge=5, le=10080)
    session_mode: str


app = FastAPI(title="Oracul Session Web App", version="1.0.0")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_store() -> dict[str, Any]:
    if not AUTH_STORAGE_PATH.exists():
        return {}
    try:
        return json.loads(AUTH_STORAGE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_store(data: dict[str, Any]):
    AUTH_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUTH_STORAGE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def _session_active(record: dict[str, Any]) -> bool:
    session = record.get("string_session")
    expires = record.get("expires_at")
    if not session or not expires:
        return False
    try:
        expires_dt = datetime.fromisoformat(expires)
        if expires_dt.tzinfo is None:
            expires_dt = expires_dt.replace(tzinfo=timezone.utc)
        return expires_dt > datetime.now(timezone.utc)
    except Exception:
        return False


@app.get("/", response_class=HTMLResponse)
async def index(user_id: str = ""):
    user_id_js = user_id if user_id.isdigit() else ""
    return HTMLResponse(
        f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Oracul Session Control</title>
  <style>
    :root {{
      --bg: #f3f6f9;
      --card: #ffffff;
      --text: #14212b;
      --muted: #587080;
      --accent: #0f766e;
      --accent-soft: #d9f3f0;
      --danger: #b91c1c;
      --radius: 14px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: radial-gradient(circle at 15% 15%, #d6ebe8 0, var(--bg) 45%);
      color: var(--text);
      font-family: "Segoe UI", "Arial", sans-serif;
      padding: 20px;
    }}
    .wrap {{ max-width: 640px; margin: 0 auto; }}
    .card {{
      background: var(--card);
      border-radius: var(--radius);
      padding: 18px;
      box-shadow: 0 14px 40px rgba(20, 33, 43, 0.08);
      margin-bottom: 14px;
    }}
    h1 {{ font-size: 22px; margin: 0 0 12px; }}
    .muted {{ color: var(--muted); font-size: 14px; }}
    .status {{ font-weight: 700; }}
    .ok {{ color: var(--accent); }}
    .bad {{ color: var(--danger); }}
    .row {{ display: flex; gap: 10px; align-items: center; margin-top: 10px; flex-wrap: wrap; }}
    .btn {{
      border: 0;
      padding: 10px 14px;
      border-radius: 10px;
      cursor: pointer;
      background: #e8eef2;
      color: var(--text);
      font-weight: 600;
    }}
    .btn.active {{ background: var(--accent); color: #fff; }}
    .btn.save {{ background: var(--accent); color: #fff; }}
    input[type="number"], select {{
      border: 1px solid #c6d4de;
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 14px;
    }}
    .ttl-chip {{
      padding: 8px 10px;
      border-radius: 9px;
      background: var(--accent-soft);
      color: #0f4f49;
      cursor: pointer;
      font-size: 13px;
      border: 0;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Управление сессией</h1>
      <div class="muted">Отдельная сессия для каждого пользователя бота.</div>
      <div class="row">
        <label for="userId">Telegram User ID</label>
        <input id="userId" type="number" value="{user_id_js}" placeholder="Например, 574973834" />
        <button class="btn" id="loadBtn">Загрузить</button>
      </div>
    </div>

    <div class="card">
      <div>Статус: <span id="statusValue" class="status bad">не загружено</span></div>
      <div class="row"><span class="muted">Режим сессии:</span></div>
      <div class="row">
        <button class="btn" id="modePersistent">TTL</button>
        <button class="btn" id="modeTemporary">Временный чат</button>
      </div>

      <div class="row"><span class="muted">TTL, минут</span></div>
      <div class="row" id="ttlQuick"></div>
      <div class="row">
        <input id="ttlValue" type="number" min="5" max="10080" value="{DEFAULT_TTL}" />
      </div>

      <div class="row">
        <button class="btn save" id="saveBtn">Сохранить</button>
      </div>
      <div class="muted" id="resultText"></div>
    </div>
  </div>

<script>
  const ttlOptions = {json.dumps(TTL_OPTIONS)};
  const defaultTtl = {DEFAULT_TTL};
  let mode = "persistent";

  const userInput = document.getElementById("userId");
  const ttlInput = document.getElementById("ttlValue");
  const statusValue = document.getElementById("statusValue");
  const resultText = document.getElementById("resultText");
  const modePersistent = document.getElementById("modePersistent");
  const modeTemporary = document.getElementById("modeTemporary");
  const ttlQuick = document.getElementById("ttlQuick");

  function refreshModeButtons() {{
    modePersistent.classList.toggle("active", mode === "persistent");
    modeTemporary.classList.toggle("active", mode === "temporary");
  }}

  function renderTtlQuick() {{
    ttlQuick.innerHTML = "";
    ttlOptions.forEach((ttl) => {{
      const btn = document.createElement("button");
      btn.className = "ttl-chip";
      btn.textContent = `${{ttl}}м`;
      btn.onclick = () => ttlInput.value = ttl;
      ttlQuick.appendChild(btn);
    }});
  }}

  async function loadSession() {{
    const userId = userInput.value.trim();
    if (!userId) return;
    resultText.textContent = "Загрузка...";
    const res = await fetch(`/api/session/${{userId}}`);
    if (!res.ok) {{
      resultText.textContent = "Не удалось загрузить данные.";
      return;
    }}
    const data = await res.json();
    mode = data.session_mode || "persistent";
    ttlInput.value = data.ttl_minutes || defaultTtl;
    statusValue.textContent = data.active ? "активна" : "неактивна";
    statusValue.className = `status ${{data.active ? "ok" : "bad"}}`;
    resultText.textContent = "Данные обновлены.";
    refreshModeButtons();
  }}

  async function saveSession() {{
    const userId = userInput.value.trim();
    if (!userId) {{
      resultText.textContent = "Укажите User ID.";
      return;
    }}
    const ttl = parseInt(ttlInput.value, 10);
    if (!ttl || ttl < 5) {{
      resultText.textContent = "TTL должен быть >= 5.";
      return;
    }}
    resultText.textContent = "Сохраняю...";
    const res = await fetch(`/api/session/${{userId}}/preferences`, {{
      method: "POST",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{ ttl_minutes: ttl, session_mode: mode }})
    }});
    if (!res.ok) {{
      resultText.textContent = "Ошибка сохранения.";
      return;
    }}
    resultText.textContent = "Сохранено.";
    await loadSession();
  }}

  document.getElementById("loadBtn").onclick = loadSession;
  document.getElementById("saveBtn").onclick = saveSession;
  modePersistent.onclick = () => {{ mode = "persistent"; refreshModeButtons(); }};
  modeTemporary.onclick = () => {{ mode = "temporary"; refreshModeButtons(); }};

  renderTtlQuick();
  refreshModeButtons();
  if (userInput.value) loadSession();
</script>
</body>
</html>"""
    )


@app.get("/api/session/{user_id}")
async def get_session(user_id: int):
    store = _load_store()
    record = store.get(str(user_id), {})
    ttl = record.get("ttl_minutes", DEFAULT_TTL)
    mode = record.get("session_mode", "persistent")
    return {
        "user_id": user_id,
        "active": _session_active(record),
        "ttl_minutes": ttl if isinstance(ttl, int) and ttl >= 5 else DEFAULT_TTL,
        "session_mode": mode if mode in {"persistent", "temporary"} else "persistent",
        "expires_at": record.get("expires_at"),
    }


@app.post("/api/session/{user_id}/preferences")
async def update_preferences(user_id: int, payload: SessionPreferences):
    if payload.session_mode not in {"persistent", "temporary"}:
        raise HTTPException(status_code=400, detail="session_mode must be persistent or temporary")
    if payload.ttl_minutes < 5:
        raise HTTPException(status_code=400, detail="ttl_minutes must be >= 5")

    store = _load_store()
    key = str(user_id)
    record = store.get(key, {})
    record["ttl_minutes"] = payload.ttl_minutes
    record["session_mode"] = payload.session_mode
    record["updated_at"] = _now_iso()

    if record.get("expires_at"):
        expires = datetime.now(timezone.utc)
        expires = expires.replace(microsecond=0)
        expires = expires.timestamp() + payload.ttl_minutes * 60
        record["expires_at"] = datetime.fromtimestamp(expires, tz=timezone.utc).isoformat()

    store[key] = record
    _save_store(store)
    return {"ok": True}
