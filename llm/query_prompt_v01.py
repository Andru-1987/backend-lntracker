prompt = r"""
    Tus datos:
    Mis noticias: {lanacion_titulos}
    Noticias de la competencia: {competencia_titulos}
    Categoría objetivo: {categoria}
    CONTEXTO:
    Eres un analista de medios especializado en detectar brechas de cobertura periodística. Tu objetivo es identificar qué temas está cubriendo la competencia que tú no estás cubriendo.

    TAREA:
    - Analiza las noticias nuestras.
    - Analiza las noticias de la competencia.
    - Clasifícalas en tres grupos:

    1. CLASIFICACIÓN POR CATEGORÍA DE NUESTRAS NOTICIAS
    - Filtra solo las noticias con la categoria '{categoria}' de la competencia
    - Descarta noticias de otras categorías, o categorias que no tengan relacion con {categoria}
    - Usa esas noticias nuestras como noticias a analizar coincidencias.


    2. CLASIFICACIÓN POR CATEGORÍA
    - Filtra solo las noticias con la categoria '{categoria}' de la competencia
    - Descarta noticias de otras categorías, o categorias que no tengan relacion con {categoria}

    3. ANÁLISIS DE COINCIDENCIAS
    - Identifica noticias que hablan del MISMO EVENTO/HECHO que tus noticias
    - Criterios de coincidencia:
        * Mismo protagonista (empresa, persona, institución)
        * Mismo evento o anuncio específico
        * Mismo fenómeno categorico, evento o situacion en el mismo período
        * Misma medida gubernamental o decisión, etc
    - NO consideres coincidencia si solo comparten un tema general (ejemplo: ambas hablan de "dólar" pero de aspectos diferentes)

    4. IDENTIFICACIÓN DE BRECHAS (TEMAS ÚNICOS DE LA COMPETENCIA)
    - Detecta noticias del topico o tema que tú NO estás cubriendo
    - Asigna etiquetas temáticas a cada noticia única

    SISTEMA DE ETIQUETAS:
    Clasifica cada noticia con una o más de estas etiquetas:
    Genera etiquetas en base a mis noticias clasificadas. 
    Genera etiquetas en base a las noticias clasificadas de mi competencia. 


    CRITERIOS IMPORTANTES:
    - Sé estricto en las coincidencias: solo si hablan del MISMO hecho concreto
    - En "por_que_es_brecha" explica brevemente por qué no tengo esa noticia
    - En "oportunidad" sugiere el ángulo para cubrir ese tema
    - La "relevancia_para_mi_audiencia" debe considerar si es aplicable a Argentina
    - Prioriza brechas de alta relevancia para la audiencia argentina
    """
