# ElSwitcher-Backend

## NOTA:
Se asume que se tiene [docker](https://www.docker.com/) y python instalados.
Si en vez de [docker](https://www.docker.com/) se quiere usar otra forma de hostear una base de datos mysql, todo debería funcionar reemplazando el [paso 3](#3-hostear-un-servidor-de-mysql), adaptando las configuraciones del [paso 5](#4-crear-una-base-de-datos-con-el-nombre-deseado-digamos-nombre_db) como corresponda.

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

#### 3. Hostear un servidor de mysql

Con docker:
Obtener una imagen de mysql usando

```
docker pull mysql
```

Crear y correr un container de docker con el puerto 3306 expuesto

```
docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=some_password --name nombre_deseado mysql
```

#### 4. Crear una base de datos con el nombre deseado (digamos nombre_db).

#### 5. Crear un archivo llamado .env y escribir en el:

```
DB_NAME=nombre_db
DB_HOST=127.0.0.1
DB_PASSWORD=some_password
DB_DIALECT=mysql+pymysql
DB_USER=root
```

Donde nombre_db y some_password son los valores que se asignaron en los pasos anteriores.

#### 6. Moverse a la carpeta app.

```
cd app
```

#### 7. Ejecutar

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