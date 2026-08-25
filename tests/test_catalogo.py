"""Pruebas del retriever de catálogo (búsqueda por palabras clave usada como RAG)."""
from app.services.catalogo import buscar_productos, cargar_catalogo, formatear_contexto


def test_cargar_catalogo_no_esta_vacio():
    catalogo = cargar_catalogo()
    assert len(catalogo) > 0
    assert all("id" in producto and "nombre" in producto for producto in catalogo)


def test_buscar_productos_encuentra_por_categoria():
    resultados = buscar_productos("audífonos para hacer deporte")
    assert len(resultados) > 0
    assert any(p["categoria"] == "Audífonos" for p in resultados)


def test_buscar_productos_encuentra_por_etiqueta_novedoso():
    resultados = buscar_productos("algo novedoso para no perder mis cosas")
    ids = [p["id"] for p in resultados]
    assert "ACC-001" in ids  # AirTrack Tag


def test_buscar_productos_sin_coincidencias_usa_fallback():
    resultados = buscar_productos("xyzxyz términos sin sentido 123")
    assert len(resultados) > 0  # cae al catálogo completo (top_k) en vez de devolver vacío


def test_formatear_contexto_incluye_precio_y_stock():
    productos = buscar_productos("cargador rápido")
    contexto = formatear_contexto(productos)
    assert "Precio: S/" in contexto
    assert "Stock:" in contexto
