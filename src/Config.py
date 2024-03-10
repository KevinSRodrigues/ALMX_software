from screeninfo import get_monitors

NAME_APP = "CiviStock"

VERSION = "1.0.0"
OBRAS = ["AEBES-PRONTO-SOCORRO",
        "SANTA-CASA-EXPANSÃO",
        "VISTA-SUL",
        "VISTA-DA-MONTANHA",
        "AEBES-UNACON",
        "EMESCAM"]

# Config conexão com o db
class CONSTANTS:

    CONN_DB = None
    MAQUINA = None

class Monitor:

    def Monitor(self):

        monitores = get_monitors()
        monitor = monitores[0]
        width_screen = monitor.width
        height_screen = monitor.height

        return width_screen, height_screen