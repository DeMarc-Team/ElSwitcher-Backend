import re
from database import Base

def __ordenar_objetos(objetos: list) -> list:
    '''
    Ordena los objetos de una lista por el nombre de su tabla y su id.
    '''
    assert all([hasattr(obj, '__tablename__') for obj in objetos]), 'Todos los objetos deben tener un __tablename__'
    assert all([hasattr(obj, 'id') for obj in objetos]), 'Todos los objetos deben tener un campo id'
    
    return sorted(objetos, key=lambda obj: (obj.__tablename__, obj.id))

def capturar(objetos) -> list:
    '''
    Convierte una lista de objetos de models en una lista de cadenas para comparar.
    Las cadenas son del formato de salida de __str__ de los modelos.
    Ordena los objetos por el nombre de su tabla y su id.
    '''
    assert len(objetos) > 0, 'La lista no puede estar vacía'
    assert all([isinstance(obj, Base) for obj in objetos]), 'Todos los objetos deben ser instancias de models'

    objetos = __ordenar_objetos(objetos)

    return [str(obj) for obj in objetos]


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

def comparar_capturas(capturas_iniciales: list, capturas_finales:list) -> list:
    '''
    Devuelve una lista de listas de tuplas con los cambios entre la i-esima 
    captura de ambos inputs.
    
    Por ejemplo, si recibie:
    
    capturas_iniciales = [captura_inicial_1,captura_inicial_2]
    
    capturas_finales = [captura_final_1,captura_final_2]

    Devolverá algo de la forma: 
    
    [[tuplas de cambios captura_inicial_1],[tuplas de cambios captura_inicial_2]]
    
    donde cada tupla es de la forma (clave, valor_inicial, valor_final)
    '''
    assert len(capturas_iniciales) == len(capturas_finales), 'Las listas deben tener la misma longitud'
    assert all([isinstance(captura, str) for captura in capturas_iniciales]), 'Las capturas iniciales deben ser cadenas'
    assert all([isinstance(captura, str) for captura in capturas_finales]), 'Las capturas finales deben ser cadenas'

    cambios = []
    for captura_inicial, captura_final in zip(capturas_iniciales, capturas_finales):
        assert captura_inicial.count('=') == captura_final.count('='), 'La cantidad de pares clave=valor debe ser la misma'
        cambios_actuales = []
        
        captura_inicial = __limpiar_y_convertir(captura_inicial)
        captura_final= __limpiar_y_convertir(captura_final)

        for clave, valor_inicial in captura_inicial.items():
            valor_final = captura_final.get(clave, None)
            assert valor_final is not None, f'La clave {clave} no está en la captura final'
            if valor_inicial != valor_final:
                cambios_actuales.append((clave, valor_inicial, valor_final))

        cambios.append(cambios_actuales)

    return cambios