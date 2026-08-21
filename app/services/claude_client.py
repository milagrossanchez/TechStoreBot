"""Orquestación del LLM: arma el contexto (RAG) y llama a la API de Claude."""
import os
import json

from anthropic import Anthropic

from app.services.catalogo import cargar_catalogo, buscar_productos, formatear_contexto
from app.services.db import crear_pedido

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """Eres el asistente de ventas de "TechStore", una tienda de productos tecnológicos
(audífonos, relojes inteligentes, cargadores y accesorios novedosos).

Tu objetivo:
1. Entender qué necesita el cliente (uso, presupuesto, preferencias).
2. Recomendar productos SOLO del catálogo que se te entrega como contexto — nunca inventes productos,
   precios o características que no estén en ese contexto.
3. Responder de forma breve, cálida y persuasiva, como un vendedor experto (no un manual técnico).
4. Si el cliente decide comprar, usa la herramienta `registrar_pedido` para dejar el pedido guardado.
5. Si no encuentras algo relevante en el contexto, dilo con honestidad y ofrece alternativas cercanas.
6. No respondas preguntas fuera del dominio de la tienda; redirige amablemente a productos tecnológicos.
"""

TOOLS = [
    {
        "name": "registrar_pedido",
        "description": "Registra un pedido confirmado por el cliente en la base de datos de la tienda.",
        "input_schema": {
            "type": "object",
            "properties": {
                "producto_id": {"type": "string", "description": "ID exacto del producto del catálogo, ej. AUD-001"},
                "cantidad": {"type": "integer", "description": "Cantidad de unidades solicitadas", "default": 1},
            },
            "required": ["producto_id"],
        },
    }
]


def _ejecutar_tool(nombre: str, entrada: dict, chat_id: str) -> str:
    if nombre == "registrar_pedido":
        catalogo = cargar_catalogo()
        producto = next((p for p in catalogo if p["id"] == entrada["producto_id"]), None)
        if not producto:
            return json.dumps({"ok": False, "error": "producto_id no encontrado en el catálogo"})
        cantidad = entrada.get("cantidad", 1)
        pedido = crear_pedido(chat_id, producto, cantidad)
        total = producto["precio"] * cantidad
        return json.dumps({
            "ok": True,
            "pedido_id": pedido.id,
            "producto": producto["nombre"],
            "cantidad": cantidad,
            "total": total,
        })
    return json.dumps({"ok": False, "error": "herramienta desconocida"})


def generar_respuesta(chat_id: str, mensaje_usuario: str, historial: list[dict]) -> str:
    productos_relevantes = buscar_productos(mensaje_usuario)
    contexto = formatear_contexto(productos_relevantes)

    system = f"{SYSTEM_PROMPT}\n\nCATÁLOGO RELEVANTE PARA ESTA CONSULTA:\n{contexto}"

    mensajes = historial + [{"role": "user", "content": mensaje_usuario}]

    respuesta = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=system,
        messages=mensajes,
        tools=TOOLS,
    )

    while respuesta.stop_reason == "tool_use":
        tool_uses = [b for b in respuesta.content if b.type == "tool_use"]
        resultados_tool = []
        for tool_use in tool_uses:
            resultado = _ejecutar_tool(tool_use.name, tool_use.input, chat_id)
            resultados_tool.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": resultado,
            })

        mensajes.append({"role": "assistant", "content": respuesta.content})
        mensajes.append({"role": "user", "content": resultados_tool})

        respuesta = client.messages.create(
            model=MODEL,
            max_tokens=800,
            system=system,
            messages=mensajes,
            tools=TOOLS,
        )

    texto_final = "".join(b.text for b in respuesta.content if b.type == "text")
    return texto_final.strip()
