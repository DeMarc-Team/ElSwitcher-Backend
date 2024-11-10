
from factory import crear_partida, unir_jugadores, iniciar_partida
from tools import capturar_metadata as capturar, comparar_capturas, get_all_tables
from verifications import check_response

from websockets_manager.ws_home_manager import ACTUALIZAR_PARTIDAS
from websockets_manager.ws_partidas_manager import SINCRONIZAR_MENSAJE

def test_enviar_un_mensaje(client, test_db ,test_ws_broadcast_messages):
    test_ws_broadcast_messages['partidas'] = [{'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Soy el mas crack de la partida', 'id_jugador': 1, 'type_message': 'USER'}}}]

    partida, creador = crear_partida(test_db)
    unir_jugadores(test_db, partida, 2)
    iniciar_partida(test_db, partida)
    
    captura_inicial = capturar(get_all_tables(test_db))
    
    respuesta = client.post(test_db, f"/juego/{partida.id}/jugadores/{creador.id}/chat", json={"message": "Soy el mas crack de la partida"})
    check_response(respuesta, 200, {"detail": f"Mensaje enviado correctamente por Creador"})

    captura_final = capturar(get_all_tables(test_db))
    
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)
    
    assert modificaciones == {}, f"No se esperaban modificaciones, pero se encontro {modificaciones}"
    assert eliminadas == [], f"No se esperaban eliminaciones, pero se encontro {eliminadas}"
    assert creadas == [], f"No se esperaban creaciones, pero se encontro {creadas}"


def test_enviar_varios_mensajes(client, test_db ,test_ws_broadcast_messages):
    test_ws_broadcast_messages['partidas'] = [
                                            {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: Soy el mas crack de la partida', 'id_jugador': 1, 'type_message': 'USER'}}},
                                            {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: No, yo soy el mas crack de la partida', 'id_jugador': 1, 'type_message': 'USER'}}},
                                            {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Jugador2: No, yo soy el mas crack de la partida', 'id_jugador': 2, 'type_message': 'USER'}}},
                                            {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: No, yo soy el mas crack de la partida', 'id_jugador': 1, 'type_message': 'USER'}}},
                                            {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Jugador2: No, yo soy el mas crack de la partida', 'id_jugador': 2, 'type_message': 'USER'}}},
                                            {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Creador: No, yo soy el mas crack de la partida', 'id_jugador': 1, 'type_message': 'USER'}}},
                                            {'partida_id': 1, 'message': {'action': 'sincronizar_mensaje', 'data': {'message': 'Jugador2: No, yo soy el mas crack de la partida', 'id_jugador': 2, 'type_message': 'USER'}}},
                                              ]

    partida, creador = crear_partida(test_db)
    jugador2 = unir_jugadores(test_db, partida, 1)[0]
    iniciar_partida(test_db, partida)
    
    captura_inicial = capturar(get_all_tables(test_db))
    
    response = client.post(test_db, f"/juego/{partida.id}/jugadores/{creador.id}/chat", json={"message": "Soy el mas crack de la partida"})
    check_response(response, 200, {"detail": f"Mensaje enviado correctamente por Creador"})
    for i in range(6):
        if (i % 2 == 0):
            response = client.post(test_db, f"/juego/{partida.id}/jugadores/{creador.id}/chat", json={"message": f"No, yo soy el mas crack de la partida"})
            check_response(response, 200, {"detail": f"Mensaje enviado correctamente por Creador"})
        else:
            response = client.post(test_db, f"/juego/{partida.id}/jugadores/{jugador2.id}/chat", json={"message": f"No, yo soy el mas crack de la partida"})
            check_response(response, 200, {"detail": f"Mensaje enviado correctamente por Jugador2"})

    captura_final = capturar(get_all_tables(test_db))
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)
    
    assert modificaciones == {}, f"No se esperaban modificaciones, pero se encontro {modificaciones}"
    assert eliminadas == [], f"No se esperaban eliminaciones, pero se encontro {eliminadas}"
    assert creadas == [], f"No se esperaban creaciones, pero se encontro {creadas}"