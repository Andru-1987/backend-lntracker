from dataclasses import dataclass


@dataclass
class DatabaseQueryStore:
    all_news_lanacion:str = r"""
WITH sitios_web AS (
    SELECT
        DISTINCT 
        [web_id],
        [sitio_global]
    FROM [sitemap].[web]
    WHERE sitio_global IS NOT NULL
), 

rrss AS (
    SELECT         
        sw.sitio_global,
        CAST(h.home_timestamp AS DATE) AS date_published,
        CONVERT(VARCHAR(8), h.home_timestamp, 8) AS time_published,
        nh.noticia_seccion AS categoria,
        nh.noticia_titulo,
        nh.noticia_url,
        STRING_AGG(k.keyword, ',') AS keywords
    FROM sitios_web AS sw
    LEFT JOIN sitemap.home AS h ON h.web_id = sw.web_id
    LEFT JOIN sitemap.noticiaHoy AS nh ON nh.home_id = h.home_id
    LEFT JOIN sitemap.noticiaHoy_keyword AS nhk ON nhk.noticia_id = nh.noticia_id
    LEFT JOIN  sitemap.keyword  AS k ON  nhk.keyword_id = k.keyword_id
        WHERE 1=1
            AND sitio_global LIKE  '%La Nación%'
            AND h.home_timestamp >= CAST(CAST(GETDATE() AS DATE) AS DATETIME)
            AND nh.noticia_id IS NOT NULL
            AND k.keyword IS NOT NULL
            AND nh.noticia_titulo IS NOT NULL
            AND nh.noticia_seccion NOT IN ('clima','horoscopos')
            -- filtro para categorias
            AND nh.noticia_seccion LIKE '%{categoria}%'
            
    GROUP BY
        sw.sitio_global,
        nh.noticia_id, 
        nh.noticia_seccion,
        nh.noticia_titulo,
        nh.noticia_url,
        h.home_timestamp
)

SELECT 
    DISTINCT
    noticia_titulo,
    noticia_url,
    categoria,
    time_published
FROM rrss """

    query_news_lanacion_by_categoria:str = r"""
WITH sitios_web AS (
    SELECT
        DISTINCT 
        [web_id],
        [sitio_global]
    FROM [sitemap].[web]
    WHERE sitio_global IS NOT NULL
), 

rrss AS (
    SELECT         
        sw.sitio_global,
        CAST(h.home_timestamp AS DATE) AS date_published,
        CONVERT(VARCHAR(8), h.home_timestamp, 8) AS time_published,
        nh.noticia_seccion AS categoria,
        nh.noticia_titulo,
        nh.noticia_url,
        STRING_AGG(k.keyword, ',') AS keywords
    FROM sitios_web AS sw
    LEFT JOIN sitemap.home AS h ON h.web_id = sw.web_id
    LEFT JOIN sitemap.noticiaHoy AS nh ON nh.home_id = h.home_id
    LEFT JOIN sitemap.noticiaHoy_keyword AS nhk ON nhk.noticia_id = nh.noticia_id
    LEFT JOIN  sitemap.keyword  AS k ON  nhk.keyword_id = k.keyword_id
        WHERE 1=1
            AND sitio_global LIKE  '%La Nación%'
            AND h.home_timestamp >= CAST(CAST(GETDATE() AS DATE) AS DATETIME)
            AND nh.noticia_id IS NOT NULL
            AND k.keyword IS NOT NULL
            AND nh.noticia_titulo IS NOT NULL
            AND nh.noticia_seccion NOT IN ('clima','horoscopos')
            -- filtro para categorias
            AND nh.noticia_seccion LIKE '%{categoria}%'
            
    GROUP BY
        sw.sitio_global,
        nh.noticia_id, 
        nh.noticia_seccion,
        nh.noticia_titulo,
        nh.noticia_url,
        h.home_timestamp
)

SELECT 
    DISTINCT
    noticia_titulo,
    noticia_url,
    time_published
FROM rrss """

    all_categories: str = r"""
WITH sitios_web AS (
    SELECT
        DISTINCT 
        [web_id],
        [sitio_global]
    FROM [sitemap].[web]
    WHERE sitio_global IS NOT NULL
), 

rrss AS (
    SELECT         
        sw.sitio_global,
        CAST(h.home_timestamp AS DATE) AS date_published,
        CONVERT(VARCHAR(8), h.home_timestamp, 8) AS time_published,
        nh.noticia_seccion AS categoria,
        nh.noticia_titulo,
        nh.noticia_url,
        STRING_AGG(k.keyword, ',') AS keywords
    FROM sitios_web AS sw
    LEFT JOIN sitemap.home AS h ON h.web_id = sw.web_id
    LEFT JOIN sitemap.noticiaHoy AS nh ON nh.home_id = h.home_id
    LEFT JOIN sitemap.noticiaHoy_keyword AS nhk ON nhk.noticia_id = nh.noticia_id
    LEFT JOIN  sitemap.keyword  AS k ON  nhk.keyword_id = k.keyword_id
        WHERE 1=1
            AND sitio_global LIKE  '%La Nación%'
            AND h.home_timestamp >= CAST(CAST(GETDATE() AS DATE) AS DATETIME)
            AND nh.noticia_id IS NOT NULL
            AND k.keyword IS NOT NULL
            AND nh.noticia_titulo IS NOT NULL
            AND nh.noticia_seccion NOT IN ('clima','horoscopos')
    GROUP BY
        sw.sitio_global,
        nh.noticia_id, 
        nh.noticia_seccion,
        nh.noticia_titulo,
        nh.noticia_url,
        h.home_timestamp
)
SELECT 
DISTINCT categoria
FROM rrss""" 