"""Carga y búsqueda simple sobre el catálogo de productos (fuente del contexto RAG)."""
import json
from pathlib import Path

CATALOGO_PATH = Path(__file__).resolve().parent.parent / "data" / "catalogo.json"


def cargar_catalogo() -> list[dict]:
    with open(CATALOGO_PATH, encoding="utf-8") as f:
        return json.load(f)


def buscar_productos(consulta: str, catalogo: list[dict] | None = None, top_k: int = 5) -> list[dict]:
    """Búsqueda por palabras clave sobre nombre, categoría, tipo y etiquetas.

    Sirve como retriever ligero para el contexto que se inyecta al LLM (RAG).
    """
    catalogo = catalogo or cargar_catalogo()
    terminos = [t.lower() for t in consulta.split() if len(t) > 2]
    if not terminos:
        return catalogo[:top_k]

    puntuados = []
    for prod in catalogo:
        texto = " ".join([
            prod["nombre"], prod["categoria"], prod["tipo"],
            " ".join(prod["etiquetas"]), " ".join(prod["caracteristicas"]),
        ]).lower()
        score = sum(texto.count(t) for t in terminos)
        if score > 0:
            puntuados.append((score, prod))

    puntuados.sort(key=lambda x: x[0], reverse=True)
    resultados = [p for _, p in puntuados[:top_k]]
    return resultados or catalogo[:top_k]


def formatear_contexto(productos: list[dict]) -> str:
    """Convierte productos a texto plano para inyectar como contexto al LLM."""
    bloques = []
    for p in productos:
        bloques.append(
            f"- ID: {p['id']} | {p['nombre']} ({p['categoria']} - {p['tipo']})\n"
            f"  Precio: S/ {p['precio']:.2f} | Stock: {p['stock']} | "
            f"Novedad: {'Sí' if p['novedad'] else 'No'}\n"
            f"  Colores: {', '.join(p['colores'])}\n"
            f"  Características: {'; '.join(p['caracteristicas'])}"
        )
    return "\n".join(bloques)
