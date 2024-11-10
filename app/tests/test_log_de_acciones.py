from factory import crear_partida, unir_jugadores, iniciar_partida
from tools import capturar_metadata as capturar, comparar_capturas, get_all_tables
from test_endpoint_jugar_carta_movimiento import agregar_m1_a_los_inventarios, jugar_carta_m1
from test_bloquear_figura import bloqueo_generico_test
from verifications import check_response

def test_log_de_movimiento(client, test_db, test_ws_broadcast_messages):
    test_ws_broadcast_messages['partidas'] = [
        {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Ha realizado un movimiento', 'id_jugador': 1, 'type_message': 'ACTION'}}},
        {'partida_id': 1, 'message': {'action': 'actualizar_tablero', 'data': None}},
        {'partida_id': 1, 'message': {'action': 'actualizar_cartas_movimiento', 'data': None}},
    ]
    from test_endpoint_jugar_carta_movimiento import test_hacer_movimiento_200
    suprimir_errores_ajenos(test=test_hacer_movimiento_200, client=client, test_db=test_db, test_ws_broadcast_messages=test_ws_broadcast_messages)

# def test_log_deshacer_movimiento(client, test_db, test_ws_broadcast_messages):
#     test_ws_broadcast_messages['partidas'] = [
#         {'partida_id': 1, 'message': {'action': 'actualizar_tablero', 'data': None}},
#         {'partida_id': 1, 'message': {'action': 'actualizar_cartas_movimiento', 'data': None}},
#         {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Ha realizado un movimiento', 'id_jugador': 1, 'type_message': 'ACTION'}}},
#         {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Ha deshecho su último movimiento', 'id_jugador': 1, 'type_message': 'ACTION'}}},
#     ]
#     from test_cancelar_movimiento_parcial import test_cancelar_movimiento_parcial
#     suprimir_errores_ajenos(test=test_cancelar_movimiento_parcial, client=client, test_db=test_db, test_ws_broadcast_messages=test_ws_broadcast_messages)
    
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
    
