# ¿Como crear tests y que hay que tener en cuenta?

## LEER!!! antes de crear tu primer test

- Se creara un archivo de test por endpoint.
- Los nombres de los archivos de test con pytest deben iniciar con `test_`.
- No crear ningun archivo que inicie con `test_` si no es un test de pytest!!
- En un mismo archivo se puede testear mas de un escenario para el mismo endpoint, cada uno debe tener su propia funcion y debe iniciar su nombre con `test_`.
- Solo añadr prints a los test para debug y para cuando fallan, si tienen exito no se mostrara ningun print al correr con pytest.
- ... abajo mas informacion :)

## ¿Que testear?

- Cambios correspondientes en la db
- Cambios no correspondientes en la db
- Respuestas de exito y error cuendo deben

## Como crear un test

Crear un archivo test_nombre.py con el siguiente formato:
```python
@pytest.fixture(scope="function")
def test_data(): # Definir la función test data (Si hace falta).
    db = TestingSessionLocal()
    # Se crean entidades en la base de datos
    # ...
    yield  # Este es el punto donde se ejecutan las pruebas
    # Limpieza de la base de datos

def test_get_jugadores(test_data):
    response = client.get("partidas/1/jugadores")
    print(response) # Para debug en caso de error
    assert response.status_code == 200
    assert len(response.json()) == 2
```

La función de prueba test_get_jugadores tiene como parámetro test_data, que es el fixture test_data(). Pytest detecta que se necesita esa fixture y la ejecuta
automáticamente antes de ejecutar test_get_jugadores.
scope="function" significa que se ejecutará antes de cada función de prueba.

Fixture: Sirven para configurar condiciones previas a las pruebas y limpiar después de ellas. Esto prepara el entorno de prueba (crea y carga datos en la base de datos).

## Como correr los tests

Para correr todos los test ejecutar el comando `pytest` o `app > pytest` parado sobre el directorio _app_.
Para correr un solo test añadir la ruta desde la app al mismo luego de pytest.

## Cómo Funciona pytest

**Descubrimiento de Pruebas**: pytest escanea recursivamente el directorio de pruebas para encontrar archivos que cumplan con el patrón test_* . por lo que no hay que crear archivos llamados test_* que no sean de tests con pytest ni test con pytest si su nombre no inicia con test_

**Ejecutar Pruebas**: Al ejecutar pytest, se ejecutan todas las funciones de prueba encontradas, y el resultado se muestra en la terminal.
Y la base de datos de tests es la misma por lo que hay que limpiarla siempre antes de cada test.

**Reportes**: pytest proporciona un resumen detallado de las pruebas ejecutadas, incluyendo cuántas pasaron y cuántas fallaron.
