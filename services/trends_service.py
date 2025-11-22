from datetime import datetime

import xml.etree.ElementTree as ET
import requests
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    picture: Optional[str] = None


@dataclass
class TrendItem:
    title: str
    traffic: str
    pub_date: str
    picture: Optional[str] = None
    picture_source: Optional[str] = None
    news_items: Optional[List[NewsItem]] = None

    def __post_init__(self):
        if self.news_items is None:
            self.news_items = []


class GoogleTrendsParser:
    NAMESPACES = {
        'ht': 'https://trends.google.com/trending/rss',
        'atom': 'http://www.w3.org/2005/Atom'
    }

    def __init__(self, geo='AR'):
        self.geo = geo
        self.url = f'https://trends.google.com/trending/rss?geo={geo}'

    def fetch_trends(self):
        """Descarga y parsea los trends desde Google"""
        response = requests.get(self.url)
        response.raise_for_status()
        return self.parse_xml(response.text)

    def parse_xml(self, xml_content):
        """Parsea el contenido XML y retorna lista de trends"""
        root = ET.fromstring(xml_content)
        trends = []

        for item in root.findall('.//item'):
            trend = self._parse_trend_item(item)
            trends.append(trend)

        return trends

    def _parse_trend_item(self, item):
        """Parsea un item individual del trend"""
        title = self._get_text(item, 'title')
        traffic = self._get_text(item, 'ht:approx_traffic')
        pub_date = self._get_text(item, 'pubDate')
        picture = self._get_text(item, 'ht:picture')
        picture_source = self._get_text(item, 'ht:picture_source')

        news_items = []

        for news in item.findall('ht:news_item', self.NAMESPACES):
            news_item = NewsItem(
                title=self._get_text(news, 'ht:news_item_title'),
                url=self._get_text(news, 'ht:news_item_url'),
                source=self._get_text(news, 'ht:news_item_source'),
                picture=self._get_text(news, 'ht:news_item_picture')
            )
            news_items.append(news_item)

        return TrendItem(
            title=title,
            traffic=traffic,
            pub_date=pub_date,
            picture=picture,
            picture_source=picture_source,
            news_items=news_items
        )

    def _get_text(self, element, tag):
        """Obtiene el texto de un tag, maneja namespaces"""

        if ':' in tag:
            ns, tag_name = tag.split(':')
            found = element.find(f'{{{self.NAMESPACES[ns]}}}{tag_name}')
        else:
            found = element.find(tag)
        
        return found.text if found is not None and found.text else ''



def parse_pub_date(pub_date_str: str) -> str:
    """
    Convierte la fecha del formato 'Fri, 21 Nov 2025 11:30:00 -0800' 
    al formato '%Y-%m-%d %H:%M:%S'
    """
    try:
        # Parsear la fecha original
        dt = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
        # Retornar en el formato solicitado
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error parseando fecha '{pub_date_str}': {e}")
        return pub_date_str

def transform_trends(trend_items: List[Any]) -> Dict[str, List[Dict[str, str]]]:
    """
    Transforma la lista de TrendItem en el formato de diccionario solicitado.
    """
    result = {}
    
    for trend in trend_items:
        news_list = []
        
        for news in trend.news_items:
            news_dict = {
                'title': news.title,
                'url': news.url,
                'source': news.source,
                'pub_date': parse_pub_date(trend.pub_date)
            }
            news_list.append(news_dict)
        
        result[trend.title] = news_list
    
    return result


class TrendsService:
    def __init__(self) -> None:
        self.parser = GoogleTrendsParser(geo='AR')
    
    def get_trends_rss(self):
        return transform_trends(self.parser.fetch_trends())