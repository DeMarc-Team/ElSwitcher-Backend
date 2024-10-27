from factory import crear_partida, unir_jugadores, iniciar_partida
import mock

def test_get_cartas_de_movimiento_happy_path(client, test_db):

    # Creamos 3 partidas: una no iniciada, una iniciada y una llena
    partida, creador = crear_partida(
        db=test_db, nombre_partida="partida_no_iniciada", nombre_creador="Creador1"
    )
    jugadores = [creador] + unir_jugadores(
        db=test_db, partida=partida, numero_de_jugadores=2
    )

    with mock.patch(
        "models.CartaMovimiento.random_movimiento", mock.Mock(return_value="mov01")
    ):
        iniciar_partida(db=test_db, partida=partida)

    for j in jugadores:
        response = client.get(
            f"/juego/{partida.id}/jugadores/{j.id_jugador}/cartas_movimiento"
        )
        assert (
            response.status_code == 200
        ), f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        j_cartas = response.json()
        assert j_cartas != []  # Se espera que haya cartas
        for carta in j_cartas:
            assert (
                carta["movimiento"] == "mov01"
            ), f"Fallo: Se esperaba la carta 'mov01', pero se obtuvo {carta['figura']}"


def test_get_cartas_movimiento_jugador_no_iniciada(client, test_db):
    """Test para obtener las cartas de movimiento de un jugador en una partida no iniciada"""
    partida, creador = crear_partida(
        db=test_db, nombre_partida="partida_no_iniciada", nombre_creador="Creador1"
    )
    jugadores = [creador] + unir_jugadores(
        db=test_db, partida=partida, numero_de_jugadores=2
    )

    for jugador in jugadores:
        response = client.get(
            f"/juego/{partida.id}/jugadores/{jugador.id_jugador}/cartas_figura"
        )
        assert (
            response.status_code == 200
        ), f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        j_cartas = response.json()
        assert j_cartas == []
