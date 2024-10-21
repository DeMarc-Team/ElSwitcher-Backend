from tests_setup import client, TestingSessionLocal
from factory import crear_partida, unir_jugadores, iniciar_partida
import mock

# Tests


def test_get_cartas_figura_happy_path(test_db):
    """Test para obtener las cartas de figura de los jugadores en una partida iniciada"""
    # Creamos 3 partidas: una no iniciada, una iniciada y una llena
    partida, creador = crear_partida(
        db=test_db, nombre_partida="partida_no_iniciada", nombre_creador="Creador1"
    )
    jugadores = [creador] + unir_jugadores(
        db=test_db, partida=partida, numero_de_jugadores=2
    )

    with mock.patch("models.CartaFigura.random_figura", return_value="fig01"):
        iniciar_partida(db=test_db, partida=partida)

    for j in jugadores:
        response = client.get(
            f"/juego/{partida.id}/jugadores/{j.id_jugador}/cartas_figura"
        )
        assert (
            response.status_code == 200
        ), f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        j_cartas = response.json()
        for carta in j_cartas:
            assert (
                carta["figura"] == "fig01"
            ), f"Fallo: Se esperaba la figura 'fig01', pero se obtuvo {carta['figura']}"
            assert carta["revelada"] == True


def test_get_cartas_figura_jugador_no_iniciada(test_db):
    """Test para obtener las cartas de figura de un jugador en una partida no iniciada"""
    partida, _ = crear_partida(
        db=test_db, nombre_partida="partida_no_iniciada", nombre_creador="Creador1"
    )
    jugadores = unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=2)

    j1_id = jugadores[0].id_jugador

    response = client.get(f"/juego/{partida.id}/jugadores/{j1_id}/cartas_figura")
    assert (
        response.status_code == 200
    ), f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

    j1_cartas = response.json()
    assert (
        j1_cartas == []
    ), f"Fallo: Se esperaba una lista vacía, pero se obtuvo {j1_cartas}"


def test_get_cartas_figura_jugador_partida_llena_no_iniciada(test_db):
    """Test para obtener las cartas de figura de un jugador en una partida llena pero no iniciada"""
    partida, creador = crear_partida(
        db=test_db,
        nombre_partida="partida_llena_no_iniciada",
        nombre_creador="Creador1",
    )

    jugadores = [creador] + unir_jugadores(
        db=test_db, partida=partida, numero_de_jugadores=3
    )

    for j in jugadores:
        response = client.get(
            f"/juego/{partida.id}/jugadores/{j.id_jugador}/cartas_figura"
        )
        assert (
            response.status_code == 200
        ), f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

        j_cartas = response.json()
        assert (
            j_cartas == []
        ), f"Fallo: Se esperaba una lista vacía, pero se obtuvo {j_cartas}"
