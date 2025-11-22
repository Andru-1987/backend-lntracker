from typing import Optional
from utils.server_services import MSServerConnector
from utils.query_store import DatabaseQueryStore
import pandas as pd


class Helper:
    @staticmethod
    def df_to_grouped_json(df):

        df["noticia_titulo"] = df["noticia_titulo"].str.strip()
        df = df.drop_duplicates(subset=["noticia_titulo"], keep="first")

        grouped = {}

        for _, row in df.iterrows():
            cat = row["categoria"]

            if cat not in grouped:
                grouped[cat] = []

            grouped[cat].append({
                "noticia_titulo": row["noticia_titulo"],
                "noticia_url": row["noticia_url"],
                "time_published": row["time_published"]
            })

        return grouped

    @staticmethod
    def df_to_dict_orient_record(df:pd.DataFrame):
        df["noticia_titulo"] = df["noticia_titulo"].str.strip()
        df = df.drop_duplicates(subset=["noticia_titulo"], keep="first")
        return df.to_dict(orient="records")
    
    @staticmethod
    def df_news_to_list(df:pd.DataFrame) -> list:
        df["noticia_titulo"] = df["noticia_titulo"].str.strip()
        df = df.drop_duplicates(subset=["noticia_titulo"], keep="first")
        return df.noticia_titulo.to_list()


class NewsWareHouseData:


    def __init__(self, connector: MSServerConnector):
        self.connector = connector

    def get_all_categories(self) -> list:

        query = DatabaseQueryStore.all_categories
        categorias_df = self.connector.execute_query(query)
        return categorias_df.categoria.to_list()


    def get_news_by_category(self, categoria: str) -> list:
        if not categoria:
            raise ValueError("El parámetro 'categoria' no puede estar vacío.")

        query = DatabaseQueryStore.query_news_lanacion_by_categoria.format(
            categoria=categoria
        )
        return Helper.df_to_dict_orient_record(self.connector.execute_query(query))


    def get_all_news(self, categoria: Optional[str] = None) -> pd.DataFrame:
        if categoria:
            query = DatabaseQueryStore.all_news_lanacion.format(
                categoria=categoria
            )
        else:
            # Usa la query completa sin filtro de categoría
            query = DatabaseQueryStore.all_news_lanacion.format(categoria="")

        return self.connector.execute_query(query)

    def get_news_custom_query(self, query_name: str, **params) -> pd.DataFrame:
        if not hasattr(DatabaseQueryStore, query_name):
            raise AttributeError(f"La consulta '{query_name}' no existe en DatabaseQueryStore.")

        query_template = getattr(DatabaseQueryStore, query_name)

        try:
            query = query_template.format(**params)
        except KeyError as e:
            raise ValueError(f"Falta el parámetro requerido: {str(e)}")

        return self.connector.execute_query(query)
    
    def get_all_news_json(self):
        df = self.get_all_news()
        return Helper.df_to_grouped_json(df)

    def get_all_news_category_list(self, categoria:str):

        query = DatabaseQueryStore.query_news_lanacion_by_categoria.format(
            categoria=categoria
        )
        
        df=self.connector.execute_query(query)

        return Helper.df_news_to_list(df)