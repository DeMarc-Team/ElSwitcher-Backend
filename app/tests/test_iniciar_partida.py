
from DB.models import Partida
from factory import crear_partida, unir_jugadores, iniciar_partida
from tools import get_all_tables, comparar_capturas, capturar_metadata as capturar, verificar_cantidad_tuplas, eliminar_tablas_laxas
from verifications import check_response
from constantes_juego import N_CARTAS_FIGURA_TOTALES, N_FIGURAS_REVELADAS
from websockets_manager.ws_home_manager import ACTUALIZAR_PARTIDAS
from websockets_manager.ws_partidas_manager import ACTUALIZAR_SALA_ESPERA, SINCRONIZAR_TURNO
from constantes_juego import SEGUNDOS_TEMPORIZADOR_TURNO

def test_iniciar_partida_200(client, test_db, test_ws_messages, mock_timeGmt):
    '''Test para iniciar una partida con suficientes jugadores'''
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    test_ws_messages[ACTUALIZAR_SALA_ESPERA] = [{'partida_id': 1}]
    test_ws_messages[SINCRONIZAR_TURNO] = [{'partida_id': 1, 'inicio': mock_timeGmt, 'duracion': SEGUNDOS_TEMPORIZADOR_TURNO}]
    
    partida, _ = crear_partida(db=test_db, nombre_partida="partida_con_2_jugadores", nombre_creador="Creador")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=2)

    captura_inicial = capturar(get_all_tables(test_db))
    response = client.put(test_db, "partidas/1")
    check_response(response, 200, {'details': 'Partida iniciada correctamente', 'partida_id': 1})
    captura_final = capturar(get_all_tables(test_db))
    
    # Calculamos la cantidad de cartas de figura que cada jugador deberia tener en esta partida
    n_cartas_fig_por_jugador = int(N_CARTAS_FIGURA_TOTALES/len(partida.jugadores))
    
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)
    
    modificaciones_esperadas = {
        ('partidas', 1): 
            [('duracion_turno', 0, SEGUNDOS_TEMPORIZADOR_TURNO), ('iniciada', False, True),
             ('inicio_turno', '0', mock_timeGmt)],
        } # se eliminaron los cambios en 'jugadores'
    eliminar_tablas_laxas(modificaciones, ['jugadores'])
    
    assert modificaciones == modificaciones_esperadas, f"Se detectaron modificaciones inesperadas en las tablas: {modificaciones}"
    assert not eliminadas, f"Se detectaron eliminaciones inesperadas en las tablas: {eliminadas}"
    assert verificar_cantidad_tuplas(creadas, [('cartas_de_movimiento', 9),('cartas_de_figura', 48)]), f"Se detectaron creaciones inesperadas en las tablas: {creadas}"

# ----------------------------------------------------------------

def test_iniciar_partida_con_jugadores_insuficientes_403(client, test_db):
    '''Test para iniciar una partida sin suficientes jugadores'''
    id_partida = 1
    partida, _ = crear_partida(db=test_db, nombre_partida="partida_con_1_jugador", nombre_creador="Creador")

    response = client.put(test_db, "partidas/1")
    print(f"Response: {response.json()}")
    
    # Verificamos la respuesta del servidor
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'Partida con ID 1 no tiene suficientes jugadores para iniciar. Mínimo de jugadores: 4.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada}, pero se obtuvo {response.json()}"
    
    # Verificamos la db
    partida = test_db.query(Partida).filter(Partida.id == 1).first()
    assert not partida.iniciada, f"Fallo: Se esperaba que la partida no estuviera iniciada, pero se obtuvo {partida.iniciada}"
    assert len(partida.jugadores) == 1, f"Fallo: Se esperaba que la partida tuviera 1 jugador, pero se obtuvo {len(partida.jugadores)}"
    assert partida.jugadores[0].es_creador, f"Fallo: Se esperaba que el jugador fuera el creador, pero se obtuvo {partida.jugadores[0].es_creador}"
    assert partida.jugadores[0].mano_movimientos == [], f"Fallo: Se esperaba que el jugador no tuviera cartas de movimiento, pero se obtuvo {partida.jugadores[0].mano_movimientos}"
    assert partida.jugadores[0].mazo_cartas_de_figura == [], f"Fallo: Se esperaba que el jugador no tuviera cartas de figura, pero se obtuvo {partida.jugadores[0].mazo_cartas_de_figura}"
    test_db.close()

# ----------------------------------------------------------------

def test_iniciar_partida_ya_iniciada_403(client, test_db):
    '''Test para iniciar una partida que ya esta iniciada'''
    partida, _ = crear_partida(db=test_db, nombre_partida="partida_ya_iniciada", nombre_creador="Creador")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=1)
    iniciar_partida(db=test_db, partida=partida)
    
    # 
    response = client.put(test_db, "partidas/1")
    print(f"Response: {response.json()}")
    
    # Verificamos la respuesta del servidor
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'La partida con ID 1 ya está iniciada.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada}, pero se obtuvo {response.json()}"
    
    # Verificamos la db
    partida = test_db.query(Partida).filter(Partida.id == 1).first()
    assert partida.iniciada, f"Fallo: Se esperaba que la partida estuviera iniciada, pero se obtuvo {partida.iniciada}"
    assert len(partida.jugadores) == 2, f"Fallo: Se esperaba que la partida tuviera 2 jugadores, pero se obtuvo {len(partida.jugadores)}"
    test_db.close()

# ----------------------------------------------------------------

def test_iniciar_partida_404(client, test_db):
    '''Test para iniciar una partida que no existe'''
    response = client.put(test_db, "partidas/1")
    print(f"Response: {response.json()}")
    
    # Verificamos la respuesta del servidor
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'Partida con ID 1 no encontrada.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada}, pero se obtuvo {response.json()}"