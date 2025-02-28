import mock
import pytest

from factory import (
    crear_partida,
    unir_jugadores,
    iniciar_partida,
    consumir_carta_movimiento,
    consumir_cantidad_cartas_figura_reveladas,
    consumir_cantidad_cartas_movimiento,
    cartear_figuras,
    test_temporizadores_turno,
)
from websockets_manager.ws_partidas_manager import ACTUALIZAR_TURNO, ACTUALIZAR_TABLERO, SINCRONIZAR_TURNO
from tools import get_all_tables, capturar_metadata as capturar, comparar_capturas, verificar_diccionarios, seleccionar_parametros, verificar_tuplas
from constantes_juego import SEGUNDOS_TEMPORIZADOR_TURNO

@pytest.mark.parametrize("numero_de_jugadores, numero_de_reveadas, numero_de_movimientos", seleccionar_parametros([(2, 3, 4),(0, 1, 2),(0, 1, 2)],3))
@pytest.mark.asyncio
async def test_terminar_turno_reponer_cartas(client, test_db, test_ws_messages, mock_timeGmt, numero_de_jugadores, numero_de_reveadas,numero_de_movimientos):
    '''
    Test que chequea que al terminar el turno de un jugador, se reponen los movimeintos y las figuras reveladas que se descartaron.
    '''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws_messages[ACTUALIZAR_TURNO] = [{'partida_id': 1}]
    test_ws_messages[ACTUALIZAR_TABLERO] = [{'partida_id': 1}]
    test_ws_messages[SINCRONIZAR_TURNO] = [{'partida_id': 1, 'inicio': mock_timeGmt, 'duracion': SEGUNDOS_TEMPORIZADOR_TURNO}]

    # Inicializamos la precondicion
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=numero_de_jugadores-1)
    iniciar_partida(test_db, partida)
    jugador_inicial = partida.jugador_del_turno
    consumir_cantidad_cartas_figura_reveladas(test_db, jugador_inicial, cantidad=3-numero_de_reveadas)
    consumir_cantidad_cartas_movimiento(test_db, jugador_inicial, cantidad=3-numero_de_movimientos)
    
    # Realizamos la petición
    captura_inicial = capturar(get_all_tables(test_db))
    
    
    response = client.put(test_db, f'/juego/{partida.id}/jugadores/{jugador_inicial.id_jugador}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
    await test_temporizadores_turno.wait_for_all_tasks()
    
    captura_final = capturar(get_all_tables(test_db))
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    # Verificamos que se hayan reinsertado las figuras
    numero_de_figuras_reveladas = len([figura for figura in jugador_inicial.mazo_cartas_de_figura if figura.revelada])
    numero_esperado = min(3,len(jugador_inicial.mazo_cartas_de_figura))
    assert numero_de_figuras_reveladas == numero_esperado, f"Fallo: Se esperaba que el jugador tuviera {numero_esperado} figuras reveladas, pero tiene {numero_de_figuras_reveladas}."
    assert not eliminadas, f"Fallo: Se esperaba que no se eliminara ninguna tabla, pero se eliminaron {eliminadas}."
    modificaciones_esperadas_en = {'jugadores': ['orden'], 'cartas_de_figura': ['revelada']}
    assert verificar_diccionarios(modificaciones, modificaciones_esperadas_en), f"Fallo: Las modificaciones no fueron las esperadas."
    assert verificar_tuplas(creadas, ['cartas_de_movimiento']), f"Fallo: Se esperaba que se crearan cartas de movimiento, pero no se crearon."
    
@pytest.mark.asyncio
async def test_terminar_turno(client, test_db, test_ws_counts, mock_timeGmt):
    '''Test que chequea el funcionamiento en el escenario exitoso del endpoint para terminar_turno.'''

    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)
    jugador_inicial = partida.jugador_del_turno
    segundo_jugador = partida.jugadores[1]

    captura_inicial = capturar(get_all_tables(test_db))

    # Pasamos el turno
    response = client.put(test_db, f'/juego/{partida.id}/jugadores/{jugador_inicial.id_jugador}/turno')
    await test_temporizadores_turno.wait_for_all_tasks()
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."

    captura_final = capturar(get_all_tables(test_db))
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    modificaciones_eperadas = {
        ('jugadores', 1): [('orden', 0, 3)], 
        ('jugadores', 2): [('orden', 1, 0)], 
        ('jugadores', 3): [('orden', 2, 1)], 
        ('jugadores', 4): [('orden', 3, 2)]
        }
    assert modificaciones == modificaciones_eperadas, f"Fallo: Se esperaba que no se modificara ninguna tabla, pero se modificaron {modificaciones}."
    assert not eliminadas, f"Fallo: Se esperaba que no se eliminara ninguna tabla, pero se eliminaron {eliminadas}."
    assert not creadas, f"Fallo: Se esperaba que no se creara ninguna tabla, pero se crearon {creadas}."

    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws_counts[ACTUALIZAR_TURNO] = 1
    test_ws_counts[ACTUALIZAR_TABLERO] = 1
    test_ws_counts[SINCRONIZAR_TURNO] = 1

@pytest.mark.asyncio
async def test_vuelta_completa(client, test_db, test_ws_counts):
    '''Test que chequea el funcionamiento de una vuelta completa de turnos.'''

    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)

    # Pasamos una ronda completa de turnos
    orden_de_turnos = await pasar_ronda_completa(client, test_db, partida)
    id_jugador_inicial = orden_de_turnos[0]

    # Obtenemos el id del nuevo jugador actual
    id_jugador_final = partida.jugador_id
        
    # Verificamos que los turnos "hayan dado la vuelta completa"
    assert id_jugador_inicial == id_jugador_final, f"Fallo: Se esperaba que el último jugador fuera el mismo que el inicial, pero eso no ocurrió."
    assert len(partida.jugadores) == 4, f"Fallo: Se esperaba que la cantidad de jugadores fuera la misma, pero no es así."

    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws_counts[ACTUALIZAR_TURNO] = len(partida.jugadores)
    test_ws_counts[ACTUALIZAR_TABLERO] = len(partida.jugadores)
    test_ws_counts[SINCRONIZAR_TURNO] = len(partida.jugadores)

@pytest.mark.asyncio
async def test_varias_rondas(client, test_db, test_ws_counts):
    '''Test sobre la confiabilidad de los turnos a lo largo de varias rondas.'''
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)

    # Hacemos una primera ronda para identificar el orden por id
    orden_de_turnos = await pasar_ronda_completa(client, test_db, partida)

    # Verificamos que se haya pasado por todos los jugadores
    n_ids_que_jugaron = len(set(orden_de_turnos))
    assert n_ids_que_jugaron == len(
        partida.jugadores
    ), f"Fallo: Se esperaba que se haya pasado por todos los jugadores ({len(partida.jugadores)}, pero solo jugaron {n_ids_que_jugaron}), "

    # Hacemos 4 rondas mas para ver si tal orden se mantiene
    for i in range(0, 4):
        nuevo_orden = await pasar_ronda_completa(client, test_db, partida)
        assert nuevo_orden == orden_de_turnos, "Fallo: El orden de la primera ronda no coincide con el de la ronda con i={i}."

    assert len(partida.jugadores) == 4, f"Fallo: Se esperaba que la cantidad de jugadores fuera la misma, pero no es así."

    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws_counts[ACTUALIZAR_TURNO] = 5 * len(partida.jugadores)
    test_ws_counts[ACTUALIZAR_TABLERO] = 5 * len(partida.jugadores)
    test_ws_counts[SINCRONIZAR_TURNO] = 5 * len(partida.jugadores)

@pytest.mark.asyncio
async def test_reponer_cartas_movimiento(client, test_db):
    '''Test sobre la reposición de las cartas de movimiento al finalizar el turno del jugador.'''
    
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=2)
    with mock.patch("db.models.CartaMovimiento.random_movimiento", return_value="m1"):
        iniciar_partida(db=test_db, partida=partida)
    jugador_del_turno = partida.jugador_del_turno

    consumir_carta_movimiento(test_db, jugador_del_turno, "m1", cantidad=2)
    
    with mock.patch("db.models.CartaMovimiento.random_movimiento", mock.Mock(side_effect=["m2", "m3"])):
        response = client.put(test_db, f'juego/{partida.id}/jugadores/{jugador_del_turno.id_jugador}/turno')
        await test_temporizadores_turno.wait_for_all_tasks()
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
    
    movimientos = [mov.movimiento for mov in jugador_del_turno.mano_movimientos]
    
    assert movimientos == [
        "m1", "m2", "m3"
    ], "Fallo: Las cartas de movimiento del jugador no se repusieron como se esperaba."

def test_jugador_bloqueado(client, test_db, mock_timeGmt):
    '''Test sobre la no reposición de cartas de figura de un jugador bloqueado con varias cartas en su mano.'''
    
    partida, creador = crear_partida(test_db)
    jugador_del_turno = creador     # Esto es así por construcción
    unir_jugadores(test_db, partida, numero_de_jugadores=2)
    iniciar_partida(test_db, partida)
    
    cartear_figuras(test_db, jugador_del_turno, ["f1", "f2"], primera_figura_bloqueada=True)
    
    captura_inicial = capturar(get_all_tables(test_db))
    
    # Terminamos el turno
    response = client.put(test_db, f'/juego/{partida.id}/jugadores/{jugador_del_turno.id_jugador}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."

    captura_final = capturar(get_all_tables(test_db))
    
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)
    assert modificaciones == {
        ('jugadores', 1): [('orden', 0, 2)], 
        ('jugadores', 2): [('orden', 1, 0)], 
        ('jugadores', 3): [('orden', 2, 1)]}, \
            "Fallo: Se esperaba que solo se modificara el orden de los jugadores y nada más."
    assert eliminadas == [], "Fallo: Se esperaba que no se eliminaran elementos."
    assert creadas == [], "Fallo: Se esperaba que no hubieran creaciones."

def test_jugador_bloqueado_carta_revelada_libre(client, test_db, mock_timeGmt):
    '''Test sobre la no reposición de cartas de figura de un jugador bloqueado una única carta en la mano, la cual está libre.'''
    
    partida, creador = crear_partida(test_db)
    jugador_bloqueado = creador     # Esto es así por construcción
    unir_jugadores(test_db, partida, numero_de_jugadores=2)
    iniciar_partida(test_db, partida)
    
    jugador_bloqueado.bloqueado = True
    cartear_figuras(test_db, jugador_bloqueado, ["f1"], primera_figura_bloqueada=False)
    
    captura_inicial = capturar(get_all_tables(test_db))
    
    # Terminamos el turno del jugador bloqueado
    response = client.put(test_db, f'/juego/{partida.id}/jugadores/{jugador_bloqueado.id_jugador}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."

    captura_final = capturar(get_all_tables(test_db))
    
    assert jugador_bloqueado.bloqueado, f"Fallo: Se esperaba que el jugador se mantuviera bloqueado."
    
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)
    assert modificaciones == {
        ('jugadores', 1): [('orden', 0, 2)], 
        ('jugadores', 2): [('orden', 1, 0)], 
        ('jugadores', 3): [('orden', 2, 1)]}, \
            "Fallo: Se esperaba que solo se modificara el orden de los jugadores y nada más."
    assert eliminadas == [], "Fallo: Se esperaba que no se eliminaran elementos."
    assert creadas == [], "Fallo: Se esperaba que no hubieran creaciones."

def test_jugador_bloqueado_carta_revelada_bloqueada(client, test_db, mock_timeGmt):
    '''Test sobre la no reposición de cartas de figura de un jugador bloqueado una única carta en la mano, la cual está bloqueada.'''
    
    partida, creador = crear_partida(test_db)
    jugador_bloqueado = creador     # Esto es así por construcción
    unir_jugadores(test_db, partida, numero_de_jugadores=2)
    iniciar_partida(test_db, partida)
    
    jugador_bloqueado.bloqueado = True
    cartear_figuras(test_db, jugador_bloqueado, ["f1"], primera_figura_bloqueada=True)
    
    captura_inicial = capturar(get_all_tables(test_db))
    
    # Terminamos el turno del jugador bloqueado
    response = client.put(test_db, f'/juego/{partida.id}/jugadores/{jugador_bloqueado.id_jugador}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."

    captura_final = capturar(get_all_tables(test_db))
    
    assert jugador_bloqueado.bloqueado, f"Fallo: Se esperaba que el jugador se mantuviera bloqueado."
    
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    assert modificaciones == {
        ('jugadores', 1): [('orden', 0, 2)], 
        ('jugadores', 2): [('orden', 1, 0)], 
        ('jugadores', 3): [('orden', 2, 1)], 
        ('cartas_de_figura', 49): [('bloqueada', True, False)]}, \
            "Fallo: Se esperaba que solo se modificara el orden de los jugadores y una carta de figura."
    assert eliminadas == [], "Fallo: Se esperaba que no se eliminaran elementos."
    assert creadas == [], "Fallo: Se esperaba que no hubieran creaciones."

def test_jugador_bloqueado_sin_reveladas(client, test_db, mock_timeGmt):
    '''Test sobre la reposición de cartas de figura de un jugador bloqueado sin cartas en la mano.'''

    partida, creador = crear_partida(test_db)
    jugador_bloqueado = creador     # Esto es así por construcción
    unir_jugadores(test_db, partida, numero_de_jugadores=2)
    iniciar_partida(test_db, partida)

    jugador_bloqueado.bloqueado = True
    cartear_figuras(test_db, jugador_bloqueado, [])

    captura_inicial = capturar(get_all_tables(test_db))

    # Terminamos el turno del jugador bloqueado
    response = client.put(test_db, f'/juego/{partida.id}/jugadores/{jugador_bloqueado.id_jugador}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."

    captura_final = capturar(get_all_tables(test_db))

    assert not jugador_bloqueado.bloqueado, f"Fallo: Se esperaba que el jugador se desbloqueara."

    modificaciones, eliminadas, creadas = comparar_capturas(
        captura_inicial, captura_final
    )
    assert modificaciones == {
        ('jugadores', 1): [('bloqueado', True, False), ('orden', 0, 2)], 
        ('jugadores', 2): [('orden', 1, 0)], 
        ('jugadores', 3): [('orden', 2, 1)], 
        ('cartas_de_figura', 4): [('revelada', False, True)], 
        ('cartas_de_figura', 5): [('revelada', False, True)], 
        ('cartas_de_figura', 6): [('revelada', False, True)]}, \
            "Fallo: Se esperaba que solo se modificara el orden de los jugadores y 3 cartas (las que se revelaron)."
    assert eliminadas == [], "Fallo: Se esperaba que no se eliminaran elementos."
    assert creadas == [], "Fallo: Se esperaba que no hubieran creaciones."

def test_partida_inexistente_404(client, test_db, test_ws_counts):
    '''Test sobre los mensajes de error ante el envío de terminar turno a una partida inexistente.'''

    # Intentamos terminar el turno de una partida inexistente.
    response = client.put(test_db, f'juego/{999999}/jugadores/{999999}/turno')
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"

def test_partida_no_iniciada_403(client, test_db, test_ws_counts):
    '''Test sobre los mensajes de error ante el envío de terminar turno a una partida no iniciada.'''

    partida, _ = crear_partida(test_db)

    # Intentamos terminar el turno de una partida no iniciada.
    response = client.put(test_db, f'juego/{partida.id}/jugadores/{1}/turno')
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"

def test_jugador_sin_turno_403(client, test_db, test_ws_counts):
    '''Test sobre los mensajes de error ante el envío de terminar turno de un jugador que no posee el turno.'''

    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)

    # Intentamos terminar el turno de un jugador que no posee el turno
    response = client.put(test_db, f'juego/{partida.id}/jugadores/{3}/turno')
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"

# Auxiliares
async def pasar_ronda_completa(client, test_db, partida):
    '''
    Pasa una ronda completa de turnos y retorna una lista ordenada por turno de los ids de los jugadores que jugaron la ronda.
    '''
    
    orden_de_turnos = []
    id_jugador_anterior = None
    # Hacemos una primera ronda para identificar el orden por id
    for i in range(0, len(partida.jugadores)):

        # Obtenemos el id del jugador actual
        id_jugador_actual = partida.jugador_id

        # Verificamos que efectivamente se haya cambiado el turno
        assert id_jugador_actual != id_jugador_anterior, f"Fallo: Se esperaba un cambio de turno en el jugador {id_jugador_actual}, pero esto no ocurrió."

        orden_de_turnos.append(id_jugador_actual)
        id_jugador_anterior = id_jugador_actual

        # Terminamos el turno del jugador actual
        response = client.put(test_db, f'juego/{partida.id}/jugadores/{id_jugador_actual}/turno')
        await test_temporizadores_turno.wait_for_all_tasks()
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
        
    return orden_de_turnos