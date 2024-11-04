from factory import crear_partida, unir_jugadores, iniciar_partida, prohibir_color
from tools import capturar_metadata as capturar, comparar_capturas, get_all_tables
from verifications import check_response

def test_get_color_prohibido_None_200(client, test_db, test_ws_messages):
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, 2)
    iniciar_partida(test_db, partida)
    
    captura_inicial = capturar(get_all_tables(test_db))
    response = client.get(f"/juego/{partida.id}/colorProhibido")
    check_response(response, 200, {"color": None})
    captura_final = capturar(get_all_tables(test_db))
    
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)
    
    assert modificaciones == {}, f"No se esperaban modificaciones, pero se encontro {modificaciones}"
    assert eliminadas == [], f"No se esperaban eliminaciones, pero se encontro {eliminadas}"
    assert creadas == [], f"No se esperaban creaciones, pero se encontro {creadas}"
    
def test_get_color_prohibido_1_200(client, test_db, test_ws_messages):
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, 2)
    iniciar_partida(test_db, partida)
    prohibir_color(test_db, partida, 1)
    
    captura_inicial = capturar(get_all_tables(test_db))
    response = client.get(f"/juego/{partida.id}/colorProhibido")
    check_response(response, 200, {"color": 1})
    captura_final = capturar(get_all_tables(test_db))
    
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)
    
    assert modificaciones == {}, f"No se esperaban modificaciones, pero se encontro {modificaciones}"
    assert eliminadas == [], f"No se esperaban eliminaciones, pero se encontro {eliminadas}"
    assert creadas == [], f"No se esperaban creaciones, pero se encontro {creadas}"
    
    
    
    
    
    