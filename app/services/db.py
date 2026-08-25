"""Persistencia de conversaciones y pedidos (acceso a la base de datos)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL
from app.models import Base, Mensaje, Pedido

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def guardar_mensaje(chat_id: str, rol: str, contenido: str):
    with SessionLocal() as session:
        session.add(Mensaje(chat_id=chat_id, rol=rol, contenido=contenido))
        session.commit()


def obtener_historial(chat_id: str, limite: int = 12) -> list[dict]:
    with SessionLocal() as session:
        registros = (
            session.query(Mensaje)
            .filter(Mensaje.chat_id == chat_id)
            .order_by(Mensaje.creado_en.desc())
            .limit(limite)
            .all()
        )
    registros.reverse()
    return [{"role": r.rol, "content": r.contenido} for r in registros]


def crear_pedido(chat_id: str, producto: dict, cantidad: int = 1) -> Pedido:
    with SessionLocal() as session:
        pedido = Pedido(
            chat_id=chat_id,
            producto_id=producto["id"],
            producto_nombre=producto["nombre"],
            precio=producto["precio"],
            cantidad=cantidad,
        )
        session.add(pedido)
        session.commit()
        session.refresh(pedido)
        return pedido
