"""Tipos de banco de dados compatíveis com SQLite e PostgreSQL."""
import uuid
from sqlalchemy import types as sqltypes
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class UUIDType(sqltypes.TypeDecorator):
    """Tipo UUID multi-dialect.
    
    - PostgreSQL: usa UUID nativo (preserva schema existente em produção)
    - SQLite:      usa String(36) para compatibilidade
    """
    impl = sqltypes.String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            # UUID nativo do PostgreSQL (preserva schema existente em produção)
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        # Fallback para SQLite e outros bancos
        return dialect.type_descriptor(sqltypes.String(36))

    def process_bind_param(self, value, dialect):
        if value is not None:
            # PostgreSQL: retorna UUID nativo (o driver PG já sabe lidar)
            # SQLite/outros: retorna string (SQLite não aceita UUID objects)
            if dialect.name == "postgresql":
                return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value) if not isinstance(value, uuid.UUID) else value
        return value