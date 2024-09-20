
class PartidaNotFoundError(Exception):
    """Excepción lanzada cuando una partida no se encuentra."""
    def __init__(self, partida_id):
        super().__init__(f"Partida con ID {partida_id} no encontrada.")
        self.partida_id = partida_id
