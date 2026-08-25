"""Modelos de datos (SQLAlchemy ORM): definición de las tablas de la base de datos."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Mensaje(Base):
    """Un mensaje del historial de conversación (usuario o asistente)."""

    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String, index=True, nullable=False)
    rol = Column(String, nullable=False)  # "user" | "assistant"
    contenido = Column(Text, nullable=False)
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Pedido(Base):
    """Un pedido confirmado por un cliente."""

    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String, index=True, nullable=False)
    producto_id = Column(String, nullable=False)
    producto_nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    cantidad = Column(Integer, default=1)
    estado = Column(String, default="pendiente")  # pendiente | confirmado | cancelado
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))
