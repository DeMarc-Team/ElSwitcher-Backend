
# Como lanzar los test
 Como estamos usando *pytest* para el testing, simplemente hay que usar:
```bash
 $ app > pytest
```
Parado sobre el directorio _app_.


### Para agregar mas test:

1. Crear un archivo test_<funcionalidad_a_testear>.py
2. Definir la función test data (Si hace falta).
3. Escribir el test utilizando respetando las [convenciones y usar las ayudas](#convencionesayudas)


### Convenciones/ayudas:
    - No crear archivos llamados test_ que no sean de tests con pytest
    - No crear test con pytest si su nombre no inicia con test_
        - En pytest, no necesitas llamar explícitamente a las funciones de prueba.
        - El propio pytest se encarga de descubrir y ejecutar las funciones qu comienzan con test_
        - que es tu fixture. pytest detecta que necesitas esa fixture y la ejecuta 
        - automáticamente antes de ejecutar test_get_jugadores. 
        - Esto prepara el entorno de prueba (crea y carga datos en la base de datos).
