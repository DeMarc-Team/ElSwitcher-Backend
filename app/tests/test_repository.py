import pytest
from unittest.mock import MagicMock, patch
from crud.repository import BaseRepository, PartidaRepo, JugadoresRepo, CartasFiguraRepo, CartasMovimientoRepo, session
from factory import crear_partida, unir_jugadores, iniciar_partida
from models import Partida, Jugador, CartaFigura, CartaMovimiento


def test_get_partida_by_id(test_db):
    partida, _ = crear_partida(test_db, nombre_partida="aca", nombre_creador="Elpepe")
    partida_id = partida.id

    result = PartidaRepo().get_by_id(partida_id)
    assert result.id == partida.id
    assert result.nombre_partida == partida.nombre_partida

def test_get_all_partidas(test_db):
    partida1, _ = crear_partida(test_db, nombre_partida="La gran partida", nombre_creador="Elpepe")
    partida2, _ = crear_partida(test_db, nombre_partida="La mejor partida", nombre_creador="Elpepe")
    partida3, _ = crear_partida(test_db, nombre_partida="La epica partida", nombre_creador="Elpepe")

    result = PartidaRepo().get_all()
    assert len(result) == 3
    assert result[0].id == partida1.id
    assert result[1].id == partida2.id
    assert result[2].id == partida3.id
    assert result[0].nombre_partida == partida1.nombre_partida
    assert result[1].nombre_partida == partida2.nombre_partida
    assert result[2].nombre_partida == partida3.nombre_partida

def test_get_jugador_del_turno(test_db):
    partida, jugadores = crear_partida(test_db, nombre_partida="La gran partida", nombre_creador="Elpepe")
    unir_jugadores(test_db, partida, 2)
    iniciar_partida(test_db, partida)
    session.commit()

    result = PartidaRepo().get_jugador_del_turno(partida.id)

    assert result.id == partida.jugador_del_turno.id
    assert result.nombre == partida.jugador_del_turno.nombre

    assert len(result.mazo_cartas_de_figura) == len(partida.jugador_del_turno.mazo_cartas_de_figura)
    for carta_result in result.mazo_cartas_de_figura:
        assert carta_result.figura in [ carta.figura for carta in partida.jugador_del_turno.mazo_cartas_de_figura ]


def test_delete_partida(test_db):
    partida = Partida(nombre_partida="La gran partida", nombre_creador="Elpepe")
    test_db.add(partida)
    test_db.commit()

    PartidaRepo().delete(partida)

    assert test_db.query(Partida).filter(Partida.id == partida.id).first() == None


def test_get_jugador_by_id(test_db):
    partida, creador = crear_partida(test_db, nombre_partida="La gran partida", nombre_creador="Elpepe")
    result = JugadoresRepo().get_by_id(creador.id)
    assert result.id == creador.id
    assert result.nombre == creador.nombre

def test_get_all_jugadores(test_db):
    partida, creador = crear_partida(test_db, nombre_partida="La gran partida", nombre_creador="Elpepe")
    jugadores = [creador] + unir_jugadores(test_db, partida, 2)
    jugador1 = jugadores[0]
    jugador2 = jugadores[1]
    jugador3 = jugadores[2]

    result = JugadoresRepo().get_all()
    assert len(result) == 3
    assert result[0].id == jugador1.id
    assert result[1].id == jugador2.id
    assert result[2].id == jugador3.id
    assert result[0].nombre == jugador1.nombre
    assert result[1].nombre == jugador2.nombre
    assert result[2].nombre == jugador3.nombre

def test_delete_jugador(test_db):
    jugador = Jugador(nombre="Elpepe", partida_id = 1)
    test_db.add(jugador)
    test_db.commit()

    JugadoresRepo().delete(jugador)

    assert test_db.query(Jugador).filter(Jugador.id == jugador.id).first() == None


def test_get_cartas_figura_de_jugador(test_db):
    partida, jugadores = crear_partida(test_db, nombre_partida="La gran partida", nombre_creador="Elpepe")
    unir_jugadores(test_db, partida, 2)
    iniciar_partida(test_db, partida)
    session.commit()

    jugador = partida.jugador_del_turno

    traidas_por_repositorio = CartasFiguraRepo().get_all()
    traidas_por_la_db = test_db.query(CartaFigura).all()

    assert len(traidas_por_repositorio) == len(traidas_por_la_db)

    for carta_result in traidas_por_repositorio:
        assert carta_result.figura in [ carta.figura for carta in traidas_por_la_db ]
        assert carta_result.id in [ carta.id for carta in traidas_por_la_db ]

def test_get_carta_figura_by_id(test_db):
    carta = CartaFigura(figura="k1")
    test_db.add(carta)
    test_db.commit()

    result = CartasFiguraRepo().get_by_id(carta.id)

    assert result.id == carta.id
    assert result.figura == carta.figura
    

def test_delete_carta_figura(test_db):
    carta = CartaFigura(figura="k1")
    test_db.add(carta)
    test_db.commit()

    CartasFiguraRepo().delete(carta)

    assert test_db.query(CartaFigura).filter(CartaFigura.id == carta.id).first() == None

def test_get_cartas_movimiento(test_db):
    partida, jugadores = crear_partida(test_db, nombre_partida="La gran partida", nombre_creador="Elpepe")
    unir_jugadores(test_db, partida, 2)
    iniciar_partida(test_db, partida)
    session.commit()

    jugador = partida.jugador_del_turno

    traidas_por_repositorio = CartasMovimientoRepo().get_all()
    traidas_por_la_db = test_db.query(CartaMovimiento).all()

    assert len(traidas_por_repositorio) == len(traidas_por_la_db)

    for carta_result in traidas_por_repositorio:
        assert carta_result.movimiento in [ carta.movimiento for carta in traidas_por_la_db ]
        assert carta_result.id in [ carta.id for carta in traidas_por_la_db ]

def test_get_cartas_movimiento_by_id(test_db):
    carta = CartaMovimiento(movimiento="k1")
    test_db.add(carta)
    test_db.commit()

    result = CartasMovimientoRepo().get_by_id(carta.id)

    assert result.id == carta.id
    assert result.movimiento == carta.movimiento
    

def test_delete_cartas_movimiento(test_db):
    carta = CartaMovimiento(movimiento="k1")
    test_db.add(carta)
    test_db.commit()

    CartasMovimientoRepo().delete(carta)

    assert test_db.query(CartaMovimiento).filter(CartaMovimiento.id == carta.id).first() == None
