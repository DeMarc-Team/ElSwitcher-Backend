# Makefile for managing the ElSwitcher-Backend project
#
# Targets:
# - run: Activa el entorno virtual y corre la aplicación.
# - venv: Crea un entorno virutal de python e instala las dependencias necesarias.
# - test: Corre los tests del proyecto.
# - test_w_coverage: Corre los tests y muestra el reporte de coverage.
# - clean: Removes generated files such as __pycache__, .pyc, and .pyo files.
# - clean_full: Utiliza la regla anterior y además elimina el entorno virtual.


# Ejemplos de uso mas interesantes:

#  Para correr solo el test llamado 'test_get_tablero':
#  - opción 1: make test TESTS="app/tests/test_get_tablero.py"
#  - opción 2: make test TESTS=app/tests/test_get_tablero.py
#  Nota: No es necesario poner comillas si se corre un solo archivo de test.

#  Para correr solo los archivos de test test_get_tablero y test_get_jugadores":
# - make test TESTS="app/tests/test_get_tablero.py app/tests/test_get_jugadores.py"

#  Para correr todos los test con el prefijo "test_get_":
#  - make test TESTS="app/tests/test_get_*"


venv=venv/bin/activate

run: venv
	@echo "Lanzando la aplicación..."
	. $(venv) && cd app && uvicorn main:app --reload

venv:
	@echo "Creando el entorno virtual de Python..."
	@test -d venv || python3 -m venv venv
	@. $(venv) && pip install --upgrade pip && pip install -r requirements.txt

# Comando para ejecutar los tests
test: venv
	@echo "Ejecutando los tests..."
	@. $(venv) && pytest $(TESTS)

test_w_coverage: venv
	@echo "Ejecutando los tests..."
	@. $(venv) && coverage run -m pytest $(TESTS) && coverage report

# Limpiar archivos generados
clean:
	@echo "Limpiando archivos..."
	@rm -rf __pycache__ *.pyc *.pyo

# Limpiar archivos generados y el entorno virtual
full_clean: clean
	@echo "Limpiando el entorno virtual..."
	@rm -rf venv
