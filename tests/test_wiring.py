import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from geologix.core.server import app


def _extract_refs(html_text: str):
    script_srcs = re.findall(r"<script[^>]+src=[\"']([^\"']+)[\"']", html_text, flags=re.IGNORECASE)
    link_hrefs = re.findall(r"<link[^>]+href=[\"']([^\"']+)[\"']", html_text, flags=re.IGNORECASE)
    return script_srcs + link_hrefs


def test_ui_asset_references_exist():
    backend_root = Path(__file__).resolve().parent.parent
    ui_root = backend_root.parent / "UI"
    assert ui_root.exists(), f"UI folder not found: {ui_root}"

    html_files = sorted(ui_root.glob("variant-*.html"))
    index_html = ui_root / "index.html"
    if index_html.exists():
        html_files.append(index_html)

    missing = []
    ui_root_resolved = ui_root.resolve()

    for html_path in html_files:
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        for ref in _extract_refs(text):
            ref = ref.strip()
            if not ref:
                continue
            if re.match(r"^[a-zA-Z]+://", ref) or ref.startswith("data:") or ref.startswith("//"):
                continue

            target = (ui_root / ref).resolve()
            try:
                target.relative_to(ui_root_resolved)
            except ValueError:
                missing.append(f"{html_path.name} -> {ref} (outside UI root)")
                continue

            if not target.exists():
                missing.append(f"{html_path.name} -> {ref}")

    assert not missing, "Missing UI asset references:\n" + "\n".join(missing)


def test_backend_endpoints():
    client = TestClient(app)

    health = client.get("/api/health")
    assert health.status_code == 200
    health_data = health.json()
    assert health_data.get("status") == "healthy"

    stats = client.get("/api/stats")
    assert stats.status_code == 200
    stats_data = stats.json()
    assert stats_data.get("success") is True
    assert isinstance(stats_data.get("categories"), dict)

    search = client.get("/api/search", params={"q": "audit", "source": "all", "limit": 3})
    assert search.status_code == 200
    search_data = search.json()
    assert isinstance(search_data, list)

    tools = client.get("/api/tools")
    assert tools.status_code == 200
    tools_data = tools.json()
    assert isinstance(tools_data.get("tools"), list)
    assert isinstance(tools_data.get("categories"), dict)
    assert isinstance(tools_data.get("total"), int)

    tool_exec = client.post(
        "/api/tools/execute",
        json={"tool_name": "calculator", "params": {"expression": "1+1"}},
    )
    assert tool_exec.status_code == 200
    tool_exec_data = tool_exec.json()
    assert tool_exec_data.get("result") == 2

    create_chat = client.post("/api/chats", json={"folder_id": "default"})
    assert create_chat.status_code == 200
    create_chat_data = create_chat.json()
    chat_id = create_chat_data.get("chat_id")
    assert isinstance(chat_id, str) and chat_id

    get_chat = client.get(f"/api/chats/{chat_id}")
    assert get_chat.status_code == 200
    get_chat_data = get_chat.json()
    assert get_chat_data.get("id") == chat_id

    delete_chat = client.delete(f"/api/chats/{chat_id}")
    assert delete_chat.status_code == 200
    delete_chat_data = delete_chat.json()
    assert delete_chat_data.get("success") is True


def run():
    test_ui_asset_references_exist()
    test_backend_endpoints()
    print("SUCCESS: wiring checks passed")


if __name__ == "__main__":
    run()
