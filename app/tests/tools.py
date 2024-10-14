import re
from sqlalchemy import inspect
from database import Base

# TODO: Hacer una funcion que devuelva un array con todas los objetos de la base de datos
# Esta funcion serviria para pasar su resultado a capturar_metadata o capturar_str
# Y asi poder comparar todas las tablas de la base de datos


def capturar_metadata(objetos: list) -> dict:
    '''
    Devuelve un diccionario donde una clave es una tupla (__tablename__, id)
    y su valor es un diccionario con la metadata de la tabla, donde las claves
    son los nombres de las columnas y los valores son sus valores en el objeto.
    '''
    assert len(objetos) > 0, 'La lista no puede estar vacía'
    assert all([isinstance(obj, Base) for obj in objetos]), 'Todos los objetos deben ser instancias de models'
    assert all([hasattr(obj, '__tablename__') for obj in objetos]), 'Todos los objetos deben tener __tablename__'
    assert all([hasattr(obj, 'id') for obj in objetos]), 'Todos los objetos deben tener id'

    metadata = {}
    for obj in objetos:
        # Inicializa un diccionario vacío para la metadata de la tabla
        metadata[obj.__tablename__, obj.id] = {}

        # Itera sobre las columnas de la tabla
        for column in inspect(obj).mapper.columns:
            # Obtiene el nombre de la columna y su valor en el objeto
            column_name = column.key
            column_value = getattr(obj, column_name)

            # Agrega la columna y su valor al diccionario de metadata
            metadata[obj.__tablename__, obj.id][column_name] = column_value

        # TODO: Captura de propiedades híbridas

    return metadata

def comparar_capturas_metadata(metadata_inicial: dict, metadata_final: dict) -> dict:
    '''
    Recibe dos diccionarios de metadata y devuelve un diccionario con las 
    diferencias entre ambas.
    
    Por ejemplo, si recibie:
    metadata_inicial ={
        ('tabla1', id1): {
            'clave1': valor1,
            'clave2': valor2
        },
        ('tabla2', id2): {
            'clave1': valor1,
            'clave2': valor2
        }
    }

    metadata_final ={
        ('tabla1', id1): {
            'clave1': valor1,
            'clave2': valor2
        },
        ('tabla2', id2): {
            'clave1': valor1,
            'clave2': valor2
        }
    }

    Devolverá:

    {
        ('tabla1', id1): [
            ('clave1', valor_inicial_1, valor_final_1),
            ('clave2', valor_inicial_2, valor_final_2)
        ],
        ('tabla2', id2): [
            ('clave1', valor_inicial_1, valor_final_1),
            ('clave2', valor_inicial_2, valor_final_2)
        ]
    }

    donde ('clave1', valor_inicial_1, valor_final_1) es una tupla que indica que
    la clave1 tenía el valor valor_inicial_1 en la metadata inicial y
    valor_final_1 en la metadata final.
    '''

    diferencias = {}

    for clave_tabla, tabla_inicial in metadata_inicial.items():
        tabla_final = metadata_final.get(clave_tabla, None)
        if tabla_final is None :
            diferencias[clave_tabla] = None
            continue
        
        assert len(tabla_inicial) == len(tabla_final), 'La cantidad de columnas debe ser la misma'
        assert isinstance(clave_tabla, tuple), f'La clave de la tabla debe ser una tupla en vez de {type(clave_tabla)}'
        assert isinstance(clave_tabla[0], str), f'El primer elemento de la clave de la tabla debe ser un string en vez de {type(clave_tabla[0])}'
        assert isinstance(clave_tabla[1], int), f'El segundo elemento de la clave de la tabla debe ser un entero en vez de {type(clave_tabla[1])}'

        # Lista de cambios detectados para esta tabla
        cambios_actuales = []

        for clave, valor_inicial in tabla_inicial.items():
            valor_final = tabla_final.get(clave, None)
            assert valor_final is not None, f'La clave {clave} no está en la metadata final'

            if valor_inicial != valor_final:
                cambios_actuales.append((clave, valor_inicial, valor_final))

        if cambios_actuales:
            # Guardamos los cambios en el diccionario con la clave (nombre_tabla, id_tabla)
            diferencias[clave_tabla] = cambios_actuales

    return diferencias


def capturar_str(objetos: list) -> dict:
    '''
    Devuelve un dicionario donde una clave es una tupla (__tablename__, id) 
    y su valor es un string del formato de salida de __str__ de los modelos.
    '''
    assert len(objetos) > 0, 'La lista no puede estar vacía'
    assert all([isinstance(obj, Base) for obj in objetos]), 'Todos los objetos deben ser instancias de models'
    assert all([hasattr(obj, '__tablename__') for obj in objetos]), 'Todos los objetos deben tener __tablename__'
    assert all([hasattr(obj, 'id') for obj in objetos]), 'Todos los objetos deben tener id'

    return {(obj.__tablename__, obj.id): str(obj) for obj in objetos}


def __limpiar_y_convertir(cadena: str) -> dict:
    assert isinstance(cadena, str), 'La captura debe ser una cadena'
    assert cadena.startswith('<') and cadena.endswith('>'), 'La captura debe estar entre < y >'
    assert cadena.count('(') == 1 and cadena.count(')') == 1, 'La captura debe tener un solo paréntesis'
    assert cadena.count('ñ@') == 0, 'La cadena no puede contener ñ@'
    assert cadena.count('[') == cadena.count(']'), 'La cantidad de corchetes debe ser par'

    # Encuentra todos los contenidos dentro de los paréntesis
    contenido = re.findall(r'\((.*?)\)', cadena)

    # Convierto a cadena y elimino comillas simples
    contenido = contenido[0].replace("'", "")

    # Cambio las comas por ñ@
    contenido = re.sub(r'\[(.*?)\]', lambda m: '[' + m.group(1).replace(',', 'ñ@') + ']', contenido)
    contenido = contenido.replace('], [', ']ñ@ [')

    # Divide el contenido por comas para obtener pares clave=valor
    pares = contenido.split(', ')

    # Recupero si hay los ñ@ y los reemplazo por comas
    pares = [par.replace('ñ@', ',') for par in pares]

    # Inicializa un diccionario vacío
    diccionario = {}

    for par in pares:
        # Divide cada par por '='
        assert par.count('=') == 1, 'Cada par debe tener un solo signo igual'
        clave, valor = par.split('=')

        # Elimina espacios en blanco y asigna la clave al diccionario
        clave = clave.strip()

        # Limpia el valor y verifica su tipo
        valor = valor.strip()
        # Intentamos primero convertir a número flotante y verificamos si es entero
        try:
            valor_float = float(valor)
            if valor_float.is_integer():
                diccionario[clave] = int(valor_float)  # Convertimos a entero si no tiene parte decimal
            else:
                diccionario[clave] = valor_float  # Dejamos como flotante si tiene decimales
        except ValueError:
            # Verificamos si es un booleano
            if valor == 'True':
                diccionario[clave] = True
            elif valor == 'False':
                diccionario[clave] = False
            else:
                # Asignamos como cadena cualquier otro valor
                diccionario[clave] = valor

    return diccionario

def comparar_capturas_str(capturas_iniciales:dict, capturas_finales:dict) -> dict:
    '''
    Recibe dos diccionarios de capturas y devuelve un diccionario con las 
    diferencias entre ambas.
    
    Por ejemplo, si recibie:
    capturas_iniciales ={
        ('tabla1', id1): captura_inicial_1,
        ('tabla2', id2): captura_inicial_2
    }

    capturas_finales ={
        ('tabla1', id1): captura_final_1,
        ('tabla2', id2): captura_final_2
    }

    Devolverá:

    {
        ('tabla1', id1): [
            ('clave1', valor_inicial_1, valor_final_1),
            ('clave2', valor_inicial_2, valor_final_2)
        ],
        ('tabla2', id2): [
            ('clave1', valor_inicial_1, valor_final_1),
            ('clave2', valor_inicial_2, valor_final_2)
        ]
    }

    donde ('clave1', valor_inicial_1, valor_final_1) es una tupla que indica que
    la clave1 tenía el valor valor_inicial_1 en la captura inicial y 
    valor_final_1 en la captura final.
    '''

    diferencias = {}

    for clave_tabla, captura_inicial in capturas_iniciales.items():
        captura_final = capturas_finales.get(clave_tabla, None)
        assert captura_final is not None, f'No existe la clave {clave_tabla} en las capturas finales'
        assert captura_inicial.count('=') == captura_final.count('='), 'La cantidad de pares clave=valor debe ser la misma'
        assert isinstance(clave_tabla, tuple), f'La clave de la tabla debe ser una tupla en vez de {type(clave_tabla)}'
        assert isinstance(clave_tabla[0], str), f'El primer elemento de la clave de la tabla debe ser un string en vez de {type(clave_tabla[0])}'
        assert isinstance(clave_tabla[1], int), f'El segundo elemento de la clave de la tabla debe ser un entero en vez de {type(clave_tabla[1])}'

        # Convertimos las capturas a diccionarios de clave=valor
        captura_inicial = __limpiar_y_convertir(captura_inicial)
        captura_final = __limpiar_y_convertir(captura_final)

        # Lista de cambios detectados para esta tabla
        cambios_actuales = []

        for clave, valor_inicial in captura_inicial.items():
            valor_final = captura_final.get(clave, None)
            assert valor_final is not None, f'La clave {clave} no está en la captura final'
            
            if valor_inicial != valor_final:
                cambios_actuales.append((clave, valor_inicial, valor_final))

        if cambios_actuales:
            # Guardamos los cambios en el diccionario con la clave (nombre_tabla, id_tabla)
            diferencias[clave_tabla] = cambios_actuales

    return diferencias