# from typeguard import typechecked, TypeCheckError
import warnings
from inspect import signature
from functools import wraps


def safe_type_check(func):
    """
    Decorador que envuelve una función y captura las excepciones de tipo que se generan al ejecutarla.
    Si se produce una excepción de tipo, se imprime una advertencia y se retorna el valor de la función sin
    realizar la verificación de tipo.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        parametros = signature(func).parameters
        type_annotations = func.__annotations__
 
        # Verificar los tipos de los argumentos posicionales
        for arg, (nombre_parametro, parametro) in zip(args, parametros.items()):
            __check_parameter_type(func, arg, nombre_parametro, type_annotations)

        # Verificar los tipos de los argumentos con nombre (kwargs)
        for nombre_parametro, valor in kwargs.items():
            __check_parameter_type(func, arg, nombre_parametro, type_annotations)

        return func(*args, **kwargs)
    return wrapper

def __check_parameter_type(func, arg, nombre_parametro, type_annotations):
    """
    Si se espera un tipo y el argumento no es del tipo esperado, 
    se imprime una advertencia.
    """
    tipo_esperado = type_annotations.get(nombre_parametro, None)
    if tipo_esperado and not isinstance(arg, tipo_esperado):
        warnings.warn(f"Advertencia de tipo en '{func.__name__}': Se esperaba tipo {tipo_esperado.__name__} para '{nombre_parametro}', pero se recibió {type(arg).__name__}.", stacklevel=2)