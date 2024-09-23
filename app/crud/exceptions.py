class PartidaNotFoundError(Exception):
    """Excepción lanzada cuando una partida no se encuentra."""
    def __init__(self, partida_id):
        self.partida_id = partida_id
        super().__init__(f"Partida con ID {self.partida_id} no encontrada.")

class PartidaLlenaError(Exception):
    """Excepción lanzada cuando la partida está llena."""
    def __init__(self, partida_id, max_jugadores):
        self.partida_id = partida_id
        self.max_jugadores = max_jugadores
        super().__init__(f"Partida con ID {self.partida_id} está llena. Máximo de jugadores: {self.max_jugadores}.")

class PartidaYaIniciada(Exception):
    """Excepción lanzada cuando una partida ya está iniciada y se la intenta iniciar de nuevo."""
    def __init__(self, partida_id):
        self.partida_id = partida_id
        super().__init__(f"La partida con ID {self.partida_id} ya está iniciada.")
        
class JuegoNotFoundError(Exception):
    """Excepción lanzada cuando un juego (asociado a una partida) no se encuentra."""
    def __init__(self, partida_id):
        self.partida_id = partida_id
        super().__init__(f"Juego de la partida con ID {self.partida_id} no encontrado.")
        