"""Pruebas de persistencia (historial de mensajes y pedidos) sobre SQLite temporal."""
from app.services.db import crear_pedido, guardar_mensaje, init_db, obtener_historial


def test_guardar_y_obtener_historial_respeta_orden():
    init_db()
    chat_id = "test-chat-historial"
    guardar_mensaje(chat_id, "user", "Hola")
    guardar_mensaje(chat_id, "assistant", "Hola, ¿en qué te ayudo?")

    historial = obtener_historial(chat_id)

    assert len(historial) == 2
    assert historial[0] == {"role": "user", "content": "Hola"}
    assert historial[1] == {"role": "assistant", "content": "Hola, ¿en qué te ayudo?"}


def test_obtener_historial_respeta_limite():
    init_db()
    chat_id = "test-chat-limite"
    for i in range(15):
        guardar_mensaje(chat_id, "user", f"mensaje {i}")

    historial = obtener_historial(chat_id, limite=5)

    assert len(historial) == 5
    assert historial[-1]["content"] == "mensaje 14"  # el más reciente queda al final


def test_crear_pedido_calcula_datos_correctos():
    init_db()
    producto = {"id": "TEST-001", "nombre": "Producto de prueba", "precio": 99.9}

    pedido = crear_pedido("test-chat-pedido", producto, cantidad=2)

    assert pedido.id is not None
    assert pedido.producto_id == "TEST-001"
    assert pedido.producto_nombre == "Producto de prueba"
    assert pedido.cantidad == 2
    assert pedido.estado == "pendiente"
