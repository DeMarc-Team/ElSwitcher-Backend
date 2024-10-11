import re

def capturar(arr) -> list:
    '''
    Convierte una lista de objetos de models en una lista de cadenas para comparar.
    '''
    output = []
    assert len(arr) > 0, 'La lista no puede estar vacía'
    assert all([hasattr(obj, '__dict__') for obj in arr]), 'Todos los objetos deben ser instancias de models'
    
    assert len(arr) == 1, 'Capacidad para pasar mas de un objeto a la vez vetada temporalmente, es necesario modificar el código para que funcione correctamente'
    
    for obj in arr:
        output.append(str(obj))

    return output


def __limpiar_y_convertir(cadena: str) -> dict:
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
        clave, valor = par.split('=')

        # Elimina espacios en blanco y asigna la clave al diccionario
        clave = clave.strip()

        # Limpia el valor y verifica su tipo
        valor = valor.strip()
        if valor.isdigit():  # Verifica si es un número entero
            diccionario[clave] = int(valor)
        elif valor == 'True':  # Verifica si es True
            diccionario[clave] = True
        elif valor == 'False':  # Verifica si es False
            diccionario[clave] = False
        else:  # Cualquier otro valor se asigna como cadena
            diccionario[clave] = valor

    return diccionario

def comparar_capturas(capturas_iniciales: list, capturas_finales:list) -> list:
    '''
    Devuelve una lista con los cambios entre dos capturas
    Formato de retorno: [(clave, valor_inicial, valor_final)]
    '''
    assert len(capturas_iniciales) == len(capturas_finales), 'Las listas deben tener la misma longitud'
    assert all([isinstance(captura, str) for captura in capturas_iniciales]), 'Las capturas iniciales deben ser cadenas'
    assert all([isinstance(captura, str) for captura in capturas_finales]), 'Las capturas finales deben ser cadenas'

    assert len(capturas_iniciales) == 1 and len(capturas_finales) == 1, 'Capacidad para pasar mas de un objeto a la vez vetada temporalmente, es necesario modificar el código para que funcione correctamente'
    
    cambios = []
    for captura_inicial, captura_final in zip(capturas_iniciales, capturas_finales):
        captura_inicial = __limpiar_y_convertir(captura_inicial)
        captura_final= __limpiar_y_convertir(captura_final)

        for clave, valor_inicial in captura_inicial.items():
            valor_final = captura_final[clave]
            if valor_inicial != valor_final:
                cambios.append((clave, captura_inicial[clave], captura_final[clave]))
                                           
    return cambios