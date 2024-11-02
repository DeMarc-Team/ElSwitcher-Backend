from sqlalchemy import inspect
from sqlalchemy.sql import text
from models import Base, Partida, Jugador 
from database import engine

def verificar_permisos(inspector, engine):
    """Verifica si se tienen permisos para acceder a la base de datos y realiza comprobaciones adicionales."""
    with engine.connect() as connection:
        try:
            inspector = inspect(engine)

            connection.execute(text("SELECT 1"))
            print("Permisos verificados: Acceso a la base de datos permitido.")

            tablas = inspector.get_table_names()
            print("Tablas disponibles en la base de datos:", tablas)

            # Comprobar el acceso a tablas
            for tabla in tablas:
                if tabla in tablas:
                    print(f"Permisos confirmados para la tabla: {tabla}")
                    connection.execute(text(f"SELECT * FROM {tabla} LIMIT 1"))
                else:
                    print(f"Fallo: No se tiene acceso a la tabla '{tabla}' o no existe.")

            # Verificación de columnas en cada tabla
            for tabla in tablas:
                if tabla in tablas:
                    columnas = inspector.get_columns(tabla)
                    columnas_nombres = [col['name'] for col in columnas]
                    print(f"Columnas en la tabla '{tabla}': {columnas_nombres}")

            print("Verificación de permisos completada.")
        
        except Exception as e:
            print(f"Error al verificar permisos: {e}")
            raise

def verificar_columnas(inspector, tabla, columnas_esperadas):
    columnas_creadas = inspector.get_columns(tabla)
    columnas_creadas_nombres = [col['name'] for col in columnas_creadas]
    print(f"\nColumnas de la tabla {tabla}:\n",columnas_creadas_nombres)

    assert len(columnas_esperadas) == len(columnas_creadas_nombres), f"Fallo: La cantidad de columnas en '{tabla}' no es la esperada. Se esperaban {len(columnas_esperadas)} pero se encontraron {len(columnas_creadas_nombres)}"
    assert columnas_esperadas == columnas_creadas_nombres, f"Fallo: No se crearon todas las columnas en '{tabla}'. Se esperaban {columnas_esperadas}, pero se encontraron {columnas_creadas_nombres}"

def test_db_creation(): #test_db):
    '''
    Test para verificar la correcta creación de la base de datos.

    Atencion: Este test se realiza sobre la base de datos real,
    no sobre la base de datos de prueba.
    '''
    #inspector = inspect(test_db.get_bind()) # El test se hace sobre la db real para verificar que se crearon las tablas
    inspector = inspect(engine)

    verificar_permisos(inspector, engine)

    # Verificamos que las tablas existen
    tablas_esperadas = ['cartas_de_figura', 'cartas_de_movimiento', 'jugadores', 'movimientos_parciales' ,'partidas']
    tablas_creadas = inspector.get_table_names()
    print("\nTablas creadas:\n",tablas_creadas)

    assert len(tablas_esperadas) == len(tablas_creadas), f"Fallo: La cantidad de tablas creadas no es la esperada. Se esperaban {len(tablas_esperadas)} pero se encontraron {len(tablas_creadas)}"
    assert tablas_esperadas == tablas_creadas, f"Fallo: No se crearon todas las tablas esperadas. Se esperaban {tablas_esperadas} pero se encontraron {tablas_creadas}"
    
    verificar_columnas(inspector, "partidas", ['id', 'nombre_partida', 'nombre_creador', 'iniciada', 'tablero'])
    verificar_columnas(inspector, "jugadores", ['id_jugador', 'nombre', 'es_creador', 'partida_id', 'orden'])
    verificar_columnas(inspector, "cartas_de_movimiento", ['id', 'movimiento', 'jugador_id'])
    verificar_columnas(inspector, "cartas_de_figura", ['id', 'figura', 'revelada', 'bloqueada', 'jugador_id'])

    # test_db.close()