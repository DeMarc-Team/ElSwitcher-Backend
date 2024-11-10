from models import Partida, Jugador
from websockets_manager.ws_home_manager import ACTUALIZAR_PARTIDAS

def test_create_partida_publica(client, test_db, test_ws_messages):
    '''Test para crear una partida'''
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    nueva_partida = {
        "nombre_partida": "Partida_nueva",
        "nombre_creador": "Jugador_nuevo",
        'privada': False,
        'contraseña': '',
    }
    response = client.post(test_db, "/partidas", json=nueva_partida)
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {  'nombre_partida': 'Partida_nueva',
                            'nombre_creador': 'Jugador_nuevo',
                            'id': 1,
                            'id_creador': 1,
                            'iniciada': False}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

    respuesta_esperada = {  'nombre_partida': 'Partida_nueva',
                            'nombre_creador': 'Jugador_nuevo',
                            'id': 1,
                            'id_creador': 1,
                            'iniciada': False}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

    # Verificamos que la partida se haya creado correctamente en la db
    partida = test_db.query(Partida).filter(Partida.id == 1).first()
    print(partida)
    
    assert partida.nombre_partida == "Partida_nueva", f"Fallo: Se esperaba Partida_nueva como nombre de la partida, pero se obtuvo {partida.nombre_partida}"
    assert partida.nombre_creador == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador de la partida, pero se obtuvo {partida.nombre_creador}"
    assert partida.iniciada == False, f"Fallo: Se esperaba False como estado de la partida, pero se obtuvo {partida.iniciada}"
    assert len(partida.jugadores) == 1, f"Fallo: Se esperaba 1 jugador en la partida, pero se obtuvo {len(partida.jugadores)}"
    
    creador = test_db.query(Jugador).filter(Jugador.id_jugador == 1).first()
    print(creador)

    assert creador.nombre == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador, pero se obtuvo {creador.nombre}"
    assert creador.es_creador == True, f"Fallo: Se esperaba True como es_creador del creador, pero se obtuvo {creador.es_creador}"
    assert creador.partidas == partida, f"Fallo: Se esperaba la partida creada como partida del creador, pero se obtuvo {creador.partidas}"
    assert creador.orden == 0, f"Fallo: Se esperaba 0 como orden del creador, pero se obtuvo {creador.orden}"

    test_db.close()



def test_create_partida_privada(client, test_db, test_ws_messages):
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]

    partida_privada = {
        "nombre_partida": "privadita",
        "nombre_creador": "Antonio",
        'privada': True,
        'contraseña': '1234',
    }
    response = client.post(test_db, "/partidas", json=partida_privada)

    
    respuesta_esperada = {  'nombre_partida': 'privadita',
                            'nombre_creador': 'Antonio',
                            'id': 1,
                            'id_creador': 1,
                            'iniciada': False}
    
    verificar_respuesta_de_api(response, 200, respuesta_esperada)
    verificar_efectos_en_db(test_db, partida_privada, response.json()['id'])
    test_db.close()


def test_create_partida_privada_contra_vacia(client,test_db,test_ws_messages):
    """
        Crear una partida con contraseña vacia
        provoca que sea simplemente publica sin importar el
        valor del campo 'privada' al llamar a la API.
    """
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    partida_privada = {
        "nombre_partida": "privadinha",
        "nombre_creador": "Antonio2",
        'privada': True,
        'contraseña': '',
    }
    response = client.post(test_db, "/partidas", json=partida_privada)

    respuesta_esperada = {
        "nombre_partida": "privadinha",
        "nombre_creador": "Antonio2",
        'id': 1,
        'id_creador': 1,
        'iniciada': False
    }


    
    verificar_respuesta_de_api(response, 200, respuesta_esperada)

    partida_privada['privada'] = False # En este caso setear la contraseña vacia, hace que se ignore el campo 'privada' y la partida sea publica
    verificar_efectos_en_db(test_db, partida_privada, response.json()['id'])


    test_db.close()

def test_create_partida_privada_contra_nula(client,test_db,test_ws_messages):
    """
        Crear una partida con contraseña nula
        hace que sea pública.
    """
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    partida_privada = {
        "nombre_partida": "privadinha",
        "nombre_creador": "Antonio2",
        'privada': False,
        'contraseña': None
    }
    response = client.post(test_db,"/partidas", json=partida_privada)

    respuesta_esperada = {
        "nombre_partida": "privadinha",
        "nombre_creador": "Antonio2",
        'id': 1,
        'id_creador': 1,
        'iniciada': False
    }


    
    verificar_respuesta_de_api(response, 200, respuesta_esperada)

    partida_privada['contraseña'] = '' # Si la contraseña es nula, al crearla se reemplza por el valor por defecto de las partidas públicas
    verificar_efectos_en_db(test_db, partida_privada, response.json()['id'])


    test_db.close()

def test_create_partida_privada_contra_faltante(client,test_db,test_ws_messages):
    """
        Crear una partida con contraseña nula
        hace que sea pública.
    """
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    partida_privada = {
        "nombre_partida": "privadinha",
        "nombre_creador": "Antonio2",
        'privada': True,

    }
    response = client.post(test_db, "/partidas", json=partida_privada)

    respuesta_esperada = {
        "nombre_partida": "privadinha",
        "nombre_creador": "Antonio2",
        'id': 1,
        'id_creador': 1,
        'iniciada': False
    }


    
    verificar_respuesta_de_api(response, 200, respuesta_esperada)

    partida_privada['contraseña'] = '' # Si la contraseña no se agrega, al crearla se reemplza por el valor por defecto de las partidas públicas
    partida_privada['privada'] = False # No setear la contraseña hace que se ignore el campo 'privada' y la partida sea publica
    verificar_efectos_en_db(test_db, partida_privada, response.json()['id'])


    test_db.close()


def verificar_efectos_en_db(test_db, datos_esperados, id_partida):
    """
    Dada una id de partida, la busca en la base de datos
    y se asegura que coincida con los datos esperados

    Args:
        test_db: Session de la db
        datos_esperados (Dict): Datos con los que se corrobora
        id_partida (Int): ID de la partida en la db
    """
    partida_en_db = test_db.query(Partida).filter(Partida.id == id_partida).first()
    
    assert datos_esperados['nombre_partida'] == partida_en_db.nombre_partida
    assert datos_esperados['nombre_creador'] == partida_en_db.nombre_creador
    assert datos_esperados['privada'] == partida_en_db.privada
    assert datos_esperados['contraseña'] == partida_en_db.contraseña


def verificar_respuesta_de_api(response, status_code_esperado, respuesta_esperada):
    """Utilizando la response de la request hecha con client. Verifica
    que el código de respuesta y los datos coincidan.

    Args:
        response : Objeto response resultado de una llamada de client.method
        status_code_esperado (Int): 
        respuesta_esperada ( Dict ): Datos con los que se corrobora correcto
    """
    assert response.status_code == status_code_esperado, f"Fallo: Se esperaba el estado {status_code_esperado}, pero se obtuvo {response.status_code}"
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"