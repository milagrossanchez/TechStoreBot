"""Pruebas de la tool `registrar_pedido` sin llamar a la API de Claude (solo la lógica local)."""
import json

from app.services.claude_client import _ejecutar_tool
from app.services.db import init_db


def test_ejecutar_tool_registrar_pedido_producto_valido():
    init_db()
    resultado = json.loads(
        _ejecutar_tool("registrar_pedido", {"producto_id": "AUD-002", "cantidad": 1}, "test-chat-tool-ok")
    )

    assert resultado["ok"] is True
    assert resultado["producto"] == "EchoFit Sport"
    assert resultado["total"] == 129.90


def test_ejecutar_tool_registrar_pedido_producto_inexistente():
    resultado = json.loads(
        _ejecutar_tool("registrar_pedido", {"producto_id": "NO-EXISTE"}, "test-chat-tool-error")
    )

    assert resultado["ok"] is False
    assert "error" in resultado


def test_ejecutar_tool_herramienta_desconocida():
    resultado = json.loads(_ejecutar_tool("otra_herramienta", {}, "test-chat-tool-unknown"))

    assert resultado["ok"] is False
