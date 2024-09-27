# ¿Como crear tests y que hay que tener en cuenta?

## LEER!!! antes de crear tu primer test

- Se creara un archivo de test por endpoint.
- Los nombres de los archivos de test con pytest deben iniciar con `test_`.
- No crear ningun archivo que inicie con `test_` si no es un test de pytest!!
- En un mismo archivo se puede testear mas de un escenario para el mismo endpoint, cada uno debe tener su propia funcion y debe iniciar su nombre con `test_`.
- Solo añadr prints a los test para debug y para cuando fallan, si tienen exito no se mostrara ningun print al correr con pytest.
- Siempre luego de un test, borrar todo lo subido a la db!!!!
- Si se esta haciendo el unitest de un endpoint solo se lo deberia llamar a el, no utilizar otros endpoints (que no haya mas de una linea del estilo client.get("partidas/1/jugadores")). Crear la base de datos en el fixture y si se necesita acceder, acceder desde el test como se muestra en el ejemplo.
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

def test_nombre_codigo(test_data):
    response = client.get("partidas/1/jugadores")
    print(response) # Para debug en caso de error
    # Testeo si se respondio correctamente:
    assert ... , mensaje de error
    # Testeo si se actualizo la db correctamente:
    db = test_data #(o TestingSessionLocal)
    # Query ...
    assert ... , mensaje de error
    db.close()
```

La función de prueba tiene como parámetro test_data, que es el fixture test_data(). Pytest detecta que se necesita esa fixture y la ejecuta
automáticamente antes de ejecutarla.
scope="function" significa que se ejecutará antes de cada función de prueba.

Fixture: Sirven para configurar condiciones previas a las pruebas y limpiar después de ellas. Esto prepara el entorno de prueba (crea y carga datos en la base de datos).

## Como correr los tests

Para correr todos los test ejecutar el comando `pytest` o `app > pytest` parado sobre el directorio _app_.
Para correr un solo test añadir la ruta desde la app al mismo luego de pytest.

### Correr los test con Coverage

Con `pytest --cov=app` podremos ver en terminal:
- **Stmts**: Número de sentencias cubiertas
- **Miss**: Número de sentencias no cubiertas
- **Cover**: Porcentaje de cobertura

Con `pytest --cov=app --cov-report=html` se generará un directorio htmlcov/ que contendrá un archivo index.html con un reporte visual de la cobertura de código, mostrando qué líneas de código están cubiertas y cuáles no.
El archivo htmlcov/index.html se puede abrir en el navegador con el comando `xdg-open htmlcov/index.html`.

#### Sobre Coverage

 La combinación de pytest y pytest-cov te permite ejecutar pruebas mientras generas un reporte de cobertura. De este modo, puedes asegurarte de que no solo el código está bien, sino que también estás cubriendo la mayor cantidad posible de lógica en tus pruebas.

## Cómo Funciona pytest

**Descubrimiento de Pruebas**: pytest escanea recursivamente el directorio de pruebas para encontrar archivos que cumplan con el patrón test_* . por lo que no hay que crear archivos llamados test_* que no sean de tests con pytest ni test con pytest si su nombre no inicia con test_

**Ejecutar Pruebas**: Al ejecutar pytest, se ejecutan todas las funciones de prueba encontradas, y el resultado se muestra en la terminal.
Y la base de datos de tests es la misma por lo que hay que limpiarla siempre antes de cada test.

**Reportes**: pytest proporciona un resumen detallado de las pruebas ejecutadas, incluyendo cuántas pasaron y cuántas fallaron.
