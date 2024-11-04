from factory import crear_partida, unir_jugadores, iniciar_partida, abandonar_partida
from tools import get_all_tables, comparar_capturas, capturar_metadata as capturar
from verifications import check_response
from constantes_juego import SEGUNDOS_TEMPORIZADOR_TURNO

def test_get_cronometro_partida_iniciada_200(client, test_db, mock_timeGmt):
    '''
    Prueba que se pueda obtener el cronometro de una partida iniciada
    '''
    partida, creador = crear_partida(test_db)
    unir_jugadores(test_db, partida, 2)
    iniciar_partida(test_db, partida)
    
    captura_inicial = capturar(get_all_tables(test_db))
    response = client.get(f"juego/{partida.id}/cronometro")
    check_response(response, 200, {'inicio': mock_timeGmt, 'duracion': SEGUNDOS_TEMPORIZADOR_TURNO})
    captura_final = capturar(get_all_tables(test_db))
    
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)
    assert not modificaciones, f"Se detectaron modificaciones inesperadas en las tablas: {modificaciones}"
    assert not eliminadas, f"Se detectaron eliminaciones inesperadas en las tablas: {eliminadas}"
    assert not creadas, f"Se detectaron creaciones inesperadas en las tablas: {creadas}"
    

def test_get_cronometro_partida_no_iniciada_403(client, test_db):
    '''
    Prueba que no se pueda obtener el cronometro de una partida no iniciada
    '''
    partida, creador = crear_partida(test_db)
    unir_jugadores(test_db, partida, 2)
    
    captura_inicial = capturar(get_all_tables(test_db))
    response = client.get(f"juego/{partida.id}/cronometro")
    check_response(response, 403, {'detail': 'La partida con ID 1 no esta iniciada.'})
    captura_final = capturar(get_all_tables(test_db))
    
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)
    
    assert not modificaciones, f"Se detectaron modificaciones inesperadas en las tablas: {modificaciones}"
    assert not eliminadas, f"Se detectaron eliminaciones inesperadas en las tablas: {eliminadas}"
    assert not creadas, f"Se detectaron creaciones inesperadas en las tablas: {creadas}"
    