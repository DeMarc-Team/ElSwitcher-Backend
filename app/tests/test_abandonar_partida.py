from tests_setup import client, TestingSessionLocal
from models import Partida, Jugador, Juego
import pytest

@pytest.fixture(scope="function")
def test_db():
    db = TestingSessionLocal()
    
    creador1 = Jugador(nombre="Creador", partida_id=1, es_creador=True)
    jugador2 = Jugador(nombre="Jugador1", partida_id=1)
    jugador3 = Jugador(nombre="Jugador2", partida_id=1)
    partida_no_iniciada = Partida(nombre_partida="partida_no_iniciada", nombre_creador="Creador", iniciada=False, jugadores=[creador1, jugador2, jugador3])

    db.add(creador1)
    db.add(jugador2)
    db.add(jugador3)
    db.add(partida_no_iniciada)

    creador2 = Jugador(nombre="Creador", partida_id=2, es_creador=True)
    jugador5 = Jugador(nombre="Jugador1", partida_id=2)
    jugador6 = Jugador(nombre="Jugador2", partida_id=2)
    jugador7 = Jugador(nombre="Jugador3", partida_id=2)
    partida_iniciada = Partida(nombre_partida="partida_iniciada", nombre_creador="Creador", iniciada=True, jugadores=[creador2, jugador5, jugador6, jugador7])
    juego2 = Juego(partida_id=2, partida=partida_iniciada, jugadores=[creador2, jugador5, jugador6, jugador7])

    db.add(creador2)
    db.add(jugador5)
    db.add(jugador6)
    db.add(jugador7)
    db.add(partida_iniciada)
    db.add(juego2)
    db.commit()
    db.close()

    yield db

    db.query(Juego).delete()
    db.query(Partida).delete()
    db.query(Jugador).delete()
    db.commit()
    db.close()

def test_abandonar_partida_no_iniciada_403(test_db):
    '''Test de creador abandonando su partida no iniciada'''
    id_creador = 1
    id_partida_no_iniciada = 1
    
    # Verificamos precondiciones
    assert test_db.query(Partida).filter((Partida.id == id_partida_no_iniciada) & (Partida.iniciada == False)).first() is not None, "Precondición 1 no valida"
    assert test_db.query(Jugador).filter((Jugador.id_jugador == id_creador) & (Jugador.es_creador == True) & (Jugador.partida_id == id_partida_no_iniciada)).first() is not None, "Precondición 2 no valida"
    assert test_db.query(Jugador).filter(Jugador.partida_id == id_partida_no_iniciada).count() == 3, "Precondición 3 no valida"
    
    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida_no_iniciada}/jugadores/{id_creador}")
    
    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    detail = f"El creador con ID {id_creador} no puede abandonar la partida con ID {id_partida_no_iniciada} antes de iniciarla."
    assert response.json()['detail'] == detail, f"Fallo: Se esperaba '{detail}', pero se obtuvo {response.json()['detail']}"

    # Verificamos que se haya no influido correctamente en la db
    partida = test_db.query(Partida).filter(Partida.id == id_partida_no_iniciada).first()
    assert partida is not None, "Fallo: La partida no debería haber sido eliminada."
    assert len(partida.jugadores) == 3, "Fallo: La cantidad de jugadores no debería haber cambiado."
    assert test_db.query(Jugador).filter(Jugador.id_jugador == id_creador).first() is not None, "Fallo: El jugador no debería haber sido eliminado."
    assert partida.iniciada == False, "Fallo: La partida no debería haber sido iniciada."
    assert partida.juego == [], f"Fallo: La partida no debería tener un juego y se obtuvo {partida.juego}"

def test_abandonar_partida_no_iniciada_200(test_db):
    '''Test de jugadores abandonando la partida no iniciada'''
    id_jugador = 2
    id_partida_no_iniciada = 1

    # Verificamos precondiciones
    assert test_db.query(Partida).filter((Partida.id == id_partida_no_iniciada) & (Partida.iniciada == False)).first() is not None, "Precondición 1 no valida"
    assert test_db.query(Jugador).filter((Jugador.id_jugador == id_jugador) & (Jugador.es_creador == False) & (Jugador.partida_id == id_partida_no_iniciada)).first() is not None, "Precondición 2 no valida"
    assert test_db.query(Jugador).filter(Jugador.partida_id == id_partida_no_iniciada).count() == 3, "Precondición 3 no valida"

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida_no_iniciada}/jugadores/{id_jugador}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert response.json() == {"detail": "El jugador abandonó la partida exitosamente"}, f"Fallo: Se esperaba '{{'message': 'El jugador abandonó la partida exitosamente'}}', pero se obtuvo {response.json()}"

    # Verificamos que se haya influido correctamente en la db
    partida = test_db.query(Partida).filter(Partida.id == id_partida_no_iniciada).first()
    assert partida is not None, "Fallo: La partida no debería haber sido eliminada."
    assert len(partida.jugadores) == 2, "Fallo: La cantidad de jugadores no debería haber cambiado."
    assert test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first() is None, "Fallo: El jugador debería haber sido eliminado."
    assert partida.iniciada == False, "Fallo: La partida no debería haber sido iniciada."
    assert partida.juego == [], f"Fallo: La partida no debería tener un juego y se obtuvo {partida.juego}"

    test_db.commit()

    # Testeamos si al salirse otro jugador no se elimina la partida
    id_jugador = 3

    # Verificamos precondiciones
    assert test_db.query(Partida).filter((Partida.id == id_partida_no_iniciada) & (Partida.iniciada == False)).first() is not None, "Precondición 1 no valida"
    assert test_db.query(Jugador).filter((Jugador.id_jugador == id_jugador) & (Jugador.es_creador == False) & (Jugador.partida_id == id_partida_no_iniciada)).first() is not None, "Precondición 2 no valida"
    assert test_db.query(Jugador).filter(Jugador.partida_id == id_partida_no_iniciada).count() == 2, "Precondición 3 no valida"

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida_no_iniciada}/jugadores/{id_jugador}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    detail = f"El jugador abandonó la partida exitosamente" 
    assert response.json() == {"detail": detail}, f"Fallo: Se esperaba '{{'detail': detail}}', pero se obtuvo {response.json()}"

    # Verificamos que se haya influido correctamente en la db
    jugador = test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first()
    partida = test_db.query(Partida).filter(Partida.id == id_partida_no_iniciada).first()
    assert jugador is None, "Fallo: El jugador debería haber sido eliminado."
    assert partida is not None, "Fallo: La partida no debería haber sido eliminada."
    assert len(partida.jugadores) == 1, f"Fallo: El creador deberia estar solo en la partida, en cambio hay {len(partida.jugadores)}."
    assert test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first() is None, "Fallo: El jugador debería haber sido eliminado."
    assert partida.iniciada == False, "Fallo: La partida no debería haber sido iniciada."
    assert partida.juego == [], f"Fallo: La partida no debería tener un juego y se obtuvo {partida.juego}"

def test_abandonar_partida_iniciada_200(test_db):
    '''Test de jugadores abandonando la partida iniciada'''
    id_jugador = 5
    id_partida_iniciada = 2

    # Verificamos precondiciones
    assert test_db.query(Partida).filter((Partida.id == id_partida_iniciada) & (Partida.iniciada == True)).first() is not None, "Precondición 1 no valida"
    assert test_db.query(Jugador).filter((Jugador.id_jugador == id_jugador) & (Jugador.es_creador == False) & (Jugador.partida_id == id_partida_iniciada)).first() is not None, "Precondición 2 no valida"
    assert test_db.query(Jugador).filter(Jugador.partida_id == id_partida_iniciada).count() == 4, "Precondición 3 no valida"

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida_iniciada}/jugadores/{id_jugador}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert response.json() == {"detail": "El jugador abandonó la partida exitosamente"}, f"Fallo: Se esperaba '{{'message': 'El jugador abandonó la partida exitosamente'}}', pero se obtuvo {response.json()}"

    # Verificamos que se haya influido correctamente en la db
    partida = test_db.query(Partida).filter(Partida.id == id_partida_iniciada).first()
    assert partida is not None, "Fallo: La partida no debería haber sido eliminada."
    assert len(partida.jugadores) == 3, "Fallo: La cantidad de jugadores en la partida deberia ser 3."
    assert test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first() is None, "Fallo: El jugador debería haber sido eliminado."
    assert partida.iniciada == True, "Fallo: La partida debería estar iniciada."
    assert len(partida.juego[0].jugadores) == 3, f"Fallo: El juego debería tener 3 jugadores y se obtuvo {len(partida.juego[0].jugadores)}"

    test_db.commit()

    # Testeamos si se puede salir el creador sin que se elimine la partida
    id_jugador = 4

    # Verificamos precondiciones
    assert test_db.query(Partida).filter((Partida.id == id_partida_iniciada) & (Partida.iniciada == True)).first() is not None, "Precondición 1 no valida"
    assert test_db.query(Jugador).filter((Jugador.id_jugador == id_jugador) & (Jugador.es_creador == True) & (Jugador.partida_id == id_partida_iniciada)).first() is not None, "Precondición 2 no valida"
    assert test_db.query(Jugador).filter(Jugador.partida_id == id_partida_iniciada).count() == 3, "Precondición 3 no valida"

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida_iniciada}/jugadores/{id_jugador}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    detail = f"El jugador abandonó la partida exitosamente"
    assert response.json() == {"detail": detail}, f"Fallo: Se esperaba '{{'detail': '{detail}'}}', pero se obtuvo {response.json()}"

    # Verificamos que se haya influido correctamente en la db
    jugador = test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first()
    partida = test_db.query(Partida).filter(Partida.id == id_partida_iniciada).first()
    assert jugador is None, "Fallo: El jugador debería haber sido eliminado."
    assert partida is not None, "Fallo: La partida no debería haber sido eliminada."
    assert len(partida.jugadores) == 2, f"Fallo: La partida deberia tener 2 jugadores, en cambio hay {len(partida.jugadores)}."
    assert test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first() is None, "Fallo: El jugador debería haber sido eliminado."
    assert partida.iniciada == True, "Fallo: La partida debería estar iniciada."
    assert len(partida.juego[0].jugadores) == 2, f"Fallo: El juego debería tener 2 jugadores y se obtuvo {len(partida.juego[0].jugadores)}"

    test_db.commit()

    # Testeamos si se sale uno mas, que se elimine la partida
    id_jugador = 6

    # Verificamos precondiciones
    assert test_db.query(Partida).filter((Partida.id == id_partida_iniciada) & (Partida.iniciada == True)).first() is not None, "Precondición 1 no valida"
    assert test_db.query(Jugador).filter((Jugador.id_jugador == id_jugador) & (Jugador.es_creador == False) & (Jugador.partida_id == id_partida_iniciada)).first() is not None, "Precondición 2 no valida"
    assert test_db.query(Jugador).filter(Jugador.partida_id == id_partida_iniciada).count() == 2, "Precondición 3 no valida"

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida_iniciada}/jugadores/{id_jugador}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    detail = f"El jugador abandonó la partida exitosamente"
    assert response.json() == {"detail": detail}, f"Fallo: Se esperaba '{{'detail': '{detail}'}}', pero se obtuvo {response.json()}"

    # Verificamos que se haya influido correctamente en la db
    jugador = test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first()
    partida = test_db.query(Partida).filter(Partida.id == id_partida_iniciada).first()
    assert jugador is None, "Fallo: El jugador debería haber sido eliminado."
    assert partida is None, "Fallo: La partida debería haber sido eliminada."
    assert test_db.query(Jugador).filter(Jugador.id_jugador == 7).first() is None, "Fallo: El jugador restante debería haber sido eliminado."

def test_abandonar_partida_no_encontrada_404(test_db):
    '''Test de jugador abandonando partida no encontrada'''
    id_jugador = 2
    id_partida_no_encontrada = 3

    # Verificamos precondiciones
    assert test_db.query(Partida).filter(Partida.id == id_partida_no_encontrada).first() is None, "Precondición 1 no valida"
    assert test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first() is not None, "Precondición 2 no valida"

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida_no_encontrada}/jugadores/{id_jugador}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    detail = f"Partida con ID {id_partida_no_encontrada} no encontrada."
    assert response.json()['detail'] == detail, f"Fallo: Se esperaba '{detail}', pero se obtuvo {response.json()['detail']}"

    # Verificamos que no se haya influido en la db
    assert test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first() is not None, "Fallo: El jugador no debería haber sido eliminado."

def test_abandonar_partida_jugador_no_encontrado_404(test_db):
    '''Test de jugador abandonando partida que no es suya (vale para jugador no existente tambien)'''
    id_jugador = 4
    id_partida = 1

    # Verificamos precondiciones
    assert test_db.query(Partida).filter(Partida.id == id_partida).first() is not None, "Precondición 1 no valida"
    assert test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first() is not None, "Precondición 2 no valida"
    assert test_db.query(Jugador).filter((Jugador.id_jugador == id_jugador) & (Jugador.partida_id == id_partida)).first() is None, "Precondición 3 no valida"

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    detail = f"Jugador con ID {id_jugador} no encontrado en la partida con ID {id_partida}."
    assert response.json()['detail'] == detail, f"Fallo: Se esperaba '{detail}', pero se obtuvo {response.json()['detail']}"

    # Verificamos que no se haya influido en la db
    assert test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first() is not None, "Fallo: El jugador no debería haber sido eliminado."
    assert test_db.query(Partida).filter(Partida.id == id_partida).first() is not None, "Fallo: La partida no debería haber sido eliminada."
