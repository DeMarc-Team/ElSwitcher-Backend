import pytest

@pytest.fixture(autouse=True, scope='function')
def setup_db():
    # Limpiamos la base de datos antes de cada test
    from models import Base
    from database import engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Creamos la base de datos de prueba
    from models import Partida, Jugador, CartaFigura, CartaMovimiento
    from tests_setup import TestingSessionLocal

    db = TestingSessionLocal()
    try:
        db.query(CartaFigura).delete()
        db.query(CartaMovimiento).delete()
        db.query(Jugador).delete()
        db.query(Partida).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    yield

# Eliminamos la base de datos de prueba después de todos los tests
@pytest.fixture(autouse=True, scope='session')
def teardown_db():
    import os

    yield

    try:
        db_path = db_path = os.path.join(os.path.dirname(__file__), 'test.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"El archivo de base de datos {db_path} ha sido eliminado.")
        else:
            print(f"El archivo de base de datos {db_path} no existe.")
    except Exception as e:
        print(f"Error al eliminar el archivo de base de datos: {e}")
