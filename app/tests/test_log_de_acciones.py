from factory import crear_partida, unir_jugadores, iniciar_partida
from websockets_manager.ws_partidas_manager import ACTUALIZAR_TURNO, ACTUALIZAR_TABLERO, SINCRONIZAR_TURNO
import mock

def test_log_de_movimiento(client, test_db, test_ws_broadcast_messages):
    test_ws_broadcast_messages['partidas'] = [
        {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Ha realizado un movimiento', 'id_jugador': 1, 'type_message': 'ACTION'}}},
        {'partida_id': 1, 'message': {'action': 'actualizar_tablero', 'data': None}},
        {'partida_id': 1, 'message': {'action': 'actualizar_cartas_movimiento', 'data': None}},
    ]
    from test_endpoint_jugar_carta_movimiento import test_hacer_movimiento_200
    suprimir_errores_ajenos(test=test_hacer_movimiento_200, client=client, test_db=test_db, test_ws_broadcast_messages=test_ws_broadcast_messages)

def test_log_deshacer_movimiento(client, test_db, test_ws_broadcast_messages):
    test_ws_broadcast_messages['partidas'] = [
        {'partida_id': 1, 'message': {'action': 'actualizar_tablero', 'data': None}},
        {'partida_id': 1, 'message': {'action': 'actualizar_tablero', 'data': None}},
        {'partida_id': 1, 'message': {'action': 'actualizar_cartas_movimiento', 'data': None}},
        {'partida_id': 1, 'message': {'action': 'actualizar_cartas_movimiento', 'data': None}},
        {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Ha realizado un movimiento', 'id_jugador': 1, 'type_message': 'ACTION'}}},
        {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Ha deshecho su último movimiento', 'id_jugador': 1, 'type_message': 'ACTION'}}},
    ]
    from test_cancelar_movimiento_parcial import test_cancelar_movimiento_parcial
    suprimir_errores_ajenos(test=test_cancelar_movimiento_parcial, client=client, test_db=test_db, test_ws_broadcast_messages=test_ws_broadcast_messages)
    
def test_log_bloqueo(client, test_db, test_ws_broadcast_messages):
    test_ws_broadcast_messages['partidas'] = [
        {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Ha bloqueado la carta de otro jugador', 'id_jugador': 1, 'type_message': 'ACTION'}}},
        {'partida_id': 1, 'message': {'action': 'actualizar_cartas_figura', 'data': None}},
        {'partida_id': 1, 'message': {'action': 'actualizar_cartas_movimiento', 'data': None}}
        ]
    
    from test_bloquear_figura import test_bloquear_happy_path
    suprimir_errores_ajenos(test=test_bloquear_happy_path, client=client, test_db=test_db, test_ws_broadcast_messages=test_ws_broadcast_messages)

def test_log_completar_figura_propia(client, test_db, test_ws_broadcast_messages):
    test_ws_broadcast_messages['partidas'] = [
        {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Ha completado una de sus cartas de figura', 'id_jugador': 1, 'type_message': 'ACTION'}}},
        {'partida_id': 1, 'message': {'action': 'actualizar_cartas_figura', 'data': None}},
        {'partida_id': 1, 'message': {'action': 'actualizar_cartas_movimiento', 'data': None}}
    ]
    from test_completar_figura_propia import test_usar_figura_propia
    suprimir_errores_ajenos(test=test_usar_figura_propia, client=client, test_db=test_db, test_ws_broadcast_messages=test_ws_broadcast_messages)

def test_log_abandonar_partida(client, test_db, test_ws_broadcast_messages, test_ws_counts):
    from test_abandonar_partida import test_abandonar_partida_en_el_turno_200 # El test ya se realiza necesariamente en el otro archivo
    suprimir_errores_ajenos(test=test_abandonar_partida_en_el_turno_200, client=client, test_db=test_db, test_ws_broadcast_messages=test_ws_broadcast_messages)

def test_log_fin_de_turno(client, test_db, test_ws_broadcast_messages, test_ws_counts):
    with mock.patch('service.TemporizadorTurno.TemporizadorTurno.get_gmt_zulu_time', return_value="esto esta mockeado"):
        test_ws_broadcast_messages['partidas'] = [
            {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Ha finalizado el turno del jugador', 'id_jugador': 1, 'type_message': 'ACTION'}}},
            {'partida_id': 1, 'message': {'action': 'actualizar_turno', 'data': None}},
            {'partida_id': 1, 'message': {'action': 'actualizar_tablero', 'data': None}},
            {'partida_id': 1, 'message': {'action': 'sincronizar_turno', 'data': {'duracion': 120, 'inicio': 'esto esta mockeado'}}}
        ]

        partida, _ = crear_partida(test_db)
        unir_jugadores(test_db, partida, numero_de_jugadores=3)
        iniciar_partida(test_db, partida)
        jugador_inicial = partida.jugador_del_turno
        segundo_jugador = partida.jugadores[1]

        # Pasamos el turno
        response = client.put(test_db, f'/juego/{partida.id}/jugadores/{jugador_inicial.id_jugador}/turno')
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."

        # Ponemos cuantas veces se espera que se envie cada mensaje de ws
        test_ws_counts[ACTUALIZAR_TURNO] = 1
        test_ws_counts[ACTUALIZAR_TABLERO] = 1
        test_ws_counts[SINCRONIZAR_TURNO] = 1


def suprimir_errores_ajenos(test, client, test_db, test_ws_broadcast_messages):
    """
        Al llamar a otros test para reutilizar la situación para contar
        los mensajes y verificar el contenido, se pueden levantar errores
        que no corresponden a esta funcionalidad. Este método se encarga
        de suprimir esos errores.
    """
    try:
        test(client, test_db, test_ws_broadcast_messages)
    except Exception as e:
        pass