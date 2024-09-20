# ElSwitcher-Backend

### Para iniciar la app

Para iniciar esta simple aplicación, se pueden seguir los siguientes pasos:

#### 1. Dentro de la carpeta en la que está este propio README, crear un entorno virtual de python utilizando 

```
python -m venv nombre_deseado_del_entorno
```

Luego activar el mismo usando

```
source nombre_deseado_del_entorno/bin/activate
```

#### 2. Instalar las dependencias requeridas utilizando

```
pip install -r requirements.txt
```

#### 3. Moverse a la carpeta app.

```
cd app
```


#### 4. Ejecutar

```
uvicorn main:app --reload
```

<br>

---
### Resultado

Ahora debería estar corriendo la aplicación y debería poder accederse a su documentación de fastapi entrando en el navegador a:
<br>

```
http://127.0.0.1:8000/docs
```

## Estructura del proyecto

El proyecto será estructurado de la siguiente manera, respecto al tipo funcionalidad que implementa cada archivo:

```
ElSwitcher-Backend
│   README.md
│   requirements.txt => dependencias requeridas para python
│   ...
└───app
    │  main.py => archivo que determina la ejecución principal
    │  database.py => módulo que configura la conexión con la base de datos.
    │
    └───crud => implementaciones de las consultas/operaciones de datos del sistema.
    │   │  module1.py => operaciones de module1
    │   │  ...
    │   └──moduleN.py => operaciones de moduleN
    │
    └───models => definición de las clases/"tablas" para usar con sqlalchemy.
    │   │  module1.py => clases/tablas de module1
    │   │  ...
    │   └──moduleN.py => clases/tablas de moduleN
    │
    └───routers => definición de los endpoints específicos con fastapi.
    │   │  module1.py => endpoints de module1
    │   │  ...
    │   └──moduleN.py => endpoints de moduleN
    │
    └───schemas => definición de las clases para la emisión y validación de datos con pydantic.
        │  module1.py => clases de module1
        │  ...
        └──moduleN.py => clases de moduleN
```
