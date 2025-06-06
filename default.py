def default_porcentajes():
    return {
        "Visual": 0,
        "Kinestésico": 0,
        "Auditivo": 0
    }
service_url = "https://zenith-api-38ka.onrender.com"
def default_preferencias():
    return {
        "Visual": {
            "Lectura": 0,  #
            "Graficos": 0, #
            "Diagramas": 0, #
            "Video": 0,  #
            "Imagenes": 0 #
        },
        "Auditivo": {
            "Escuchar_clase": 0, #
            "Grabaciones": 0, #
            "Musica": 0, 
            "Podcast": 0, 
            "Debates": 0 #
        },
        "Kinestesico": {
            "Experimentos": 0, # 
            "Simulaciones": 0, 
            "Proyectos": 0, 
            "Practica": 0, #
            "Juegos": 0 #
        }
    }
subcategorias_a_indice = {
    # Visual
    "Lectura": (0, "Visual"),
    "Grafico": (1, "Visual"),
    "Diagrama": (2, "Visual"),
    "Video": (3, "Visual"),
    "Imagen": (4, "Visual"),

    # Auditivo
    "Escuchar_clase": (5, "Auditivo"),
    "Grabacion": (6, "Auditivo"),
    "Musica": (7, "Auditivo"),
    "Podcast": (8, "Auditivo"),
    "Debate": (9, "Auditivo"),

    # Kinestésico
    "Experimento": (10, "Kinestésico"),
    "Simulacion": (11, "Kinestésico"),
    "Proyecto": (12, "Kinestésico"),
    "Practica": (13, "Kinestésico"),
    "Juego": (14, "Kinestésico"),
}


retroalimentacion_por_defecto = []