### NOTA:
 Se asume que se tiene docker y python instalados.
Si en vez de docker se quiere usar otra forma de hostear un servidor mysql, debería igualmente funcionar reemplazando tales pasos de .

### Para iniciar la app

Para iniciar esta simple aplicación, se pueden seguir los siguientes pasos:

1. Dentro de la carpeta en la que está este propio README, crear un entorno virtual de python utilizando 

`python -m venv nombre_deseado_del_entorno`

Luego activar el mismo usando

`source nombre_deseado_del_entorno/bin/activate`

2. Instalar las dependencias requeridas utilizando

`pip install -r requirements.txt`

3. Hostear un servidor de mysql

Con docker:
Obtener una imagen de mysql usando

`docker pull mysql`

Crear y correr un container de docker con el puerto 3306 expuesto

`docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password --name nombre_deseado mysql`

4. Crear una base de datos con el nombre deseado (digamos nombre_db).

5. Crear un archivo llamado .env y escribir en el:

`DB_NAME=nombre_db`
<br>
`DB_HOST=127.0.0.1`
<br>
`DB_PASSWORD=password`
<br>
`DB_DIALECT=mysql+pymysql`
<br>
`DB_USER=root`
<br>

Donde nombre_db y contraseña_deseada son los valores que se asignaron en los pasos anteriores.

5. Moverse a la carpeta app.

`cd app`

6. Ejecutar

`uvicorn main:app --reload`

<br>

---

<br>
Ahora debería estar corriendo la aplicación y debería poder accederse a su documentación de fastapi entrando en el navegador a:

`http://127.0.0.1:8000/docs`