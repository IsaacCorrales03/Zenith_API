def default_porcentajes():
    return {
        'Visual': 0,
        'Kinestésico': 0,
        'Auditivo': 0
    }
service_url = "https://zenith-api-38ka.onrender.com"
def default_preferencias():
    return {
        'Visual': {
            'Lectura': 0, 
            'Graficos': 0, 
            'Diagramas': 0, 
            'Videos': 0, 
            'Imagenes': 0
        },
        'Auditivo': {
            'Escuchar_clase': 0, 
            'Grabaciones': 0, 
            'Musica': 0, 
            'Podcast': 0, 
            'Debates': 0
        },
        'Kinestesico': {
            'Experimentos': 0, 
            'Simulaciones': 0, 
            'Proyectos': 0, 
            'Practica': 0, 
            'Juegos': 0
        }
    }

retroalimentacion_por_defecto = []