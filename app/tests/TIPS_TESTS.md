# ¿Como crear tests y que hay que tener en cuenta?

## Como crear un test

Crear un archivo test_nombre.py con el siguiente formato:

```python
@pytest.fixture(scope="function")
def test_data():
    db = TestingSessionLocal()
    # Se crean entidades en la base de datos
    # ...
    yield  # Este es el punto donde se ejecutan las pruebas
    # Limpieza de la base de datos

def test_get_jugadores(test_data):
    response = client.get("partidas/1/jugadores")
    assert response.status_code == 200
    assert len(response.json()) == 2
```

La función de prueba test_get_jugadores tiene como parámetro test_data, que es el fixture test_data(). Pytest detecta que se necesita esa fixture y la ejecuta
automáticamente antes de ejecutar test_get_jugadores.
scope="function" significa que se ejecutará antes de cada función de prueba.

Fixture: Sirven para configurar condiciones previas a las pruebas y limpiar después de ellas. Esto prepara el entorno de prueba (crea y carga datos en la base de datos).

## Como correr los tests

Ejecutar comando: `pytest`

## Cómo Funciona pytest

**Descubrimiento de Pruebas**: pytest escanea recursivamente el directorio de pruebas para encontrar archivos que cumplan con el patrón test*... . por lo que no hay que crear archivos llamados test* que no sean de tests con pytest ni test con pytest si su nombre no inicia con test\_

**Ejecutar Pruebas**: Al ejecutar pytest, se ejecutan todas las funciones de prueba encontradas, y el resultado se muestra en la terminal.
Y la base de datos de tests es la misma por lo que hay que limpiarla siempre antes de cada test.

**Reportes**: pytest proporciona un resumen detallado de las pruebas ejecutadas, incluyendo cuántas pasaron y cuántas fallaron.
