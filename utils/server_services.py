import pandas as pd
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
from typing import Optional
from contextlib import contextmanager
import urllib.parse
import socket

class MSServerConnector:
    """
    Clase para gestionar conexiones y consultas a Microsoft SQL Server.
    """
    
    def __init__(
        self,
        server: str,
        database: str,
        username: str,
        password: str,
        driver: str = "ODBC Driver 18 for SQL Server",
        trust_server_certificate: bool = True,
        timeout: int = 5 #(segundos)

    ):
        """
        Inicializa el conector de MS SQL Server.
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.trust_server_certificate = trust_server_certificate
        self._engine: Optional[Engine] = None
        self.timeout = timeout

    @property
    def connection_string(self) -> str:
        """Genera y retorna la cadena de conexión."""
        trust_cert = "yes" if self.trust_server_certificate else "no"
        driver_formatted = self.driver.replace(" ", "+")
        
        password_encoded = urllib.parse.quote_plus(self.password)
        username_encoded = urllib.parse.quote_plus(self.username)

        # Mantenemos LoginTimeout en la URL para el driver
        return (
            f"mssql+pyodbc://{username_encoded}:{password_encoded}@{self.server}/{self.database}"
            f"?driver={driver_formatted}"
            f"&TrustServerCertificate={trust_cert}"
            f"&LoginTimeout={self.timeout}"
        )
    
    def _check_tcp_reachability(self):
        """
        Intenta abrir un socket TCP crudo contra el servidor.
        Esto falla rápido si el host no responde, respetando estrictamente el timeout de Python.
        """
        host = self.server
        port = 1433  # Puerto default SQL Server
        
        # Manejo básico de formatos "host,port" o "host:port"
        if "," in self.server:
            parts = self.server.split(",")
            host = parts[0]
            try:
                port = int(parts[1])
            except:
                pass
        elif ":" in self.server:
            parts = self.server.split(":")
            host = parts[0]
            try:
                port = int(parts[1])
            except:
                pass
        
        print(f"🕵️  [TCP Check] Verificando {host}:{port} con timeout de {self.timeout}s...")
        try:
            # create_connection usa el timeout de Python, que es muy preciso
            with socket.create_connection((host, port), timeout=self.timeout):
                print(">>>[TCP Check] Servidor accesible.")
        except socket.timeout:
            raise SQLAlchemyError(f"Timeout estricto ({self.timeout}s) alcanzado al intentar conectar TCP a {host}:{port}")
        except (ConnectionRefusedError, OSError) as e:
            raise SQLAlchemyError(f"Error de red al conectar a {host}:{port}: {e}")

    def connect(self) -> None:
        """Establece la conexión con la base de datos."""
        try:
            # 1. PRIMERO: Verificación estricta de red (Fail Fast)
            self._check_tcp_reachability()

            # 2. SEGUNDO: Intento de conexión ODBC
            print(f"🔌 Estableciendo conexión ODBC con BD: {self.database}...")
            
            # Pasamos timeout también a connect_args por redundancia
            connect_args = {"timeout": self.timeout}

            self._engine = sqlalchemy.create_engine(
                self.connection_string,
                connect_args=connect_args,
                pool_pre_ping=True
            )

            # Verificar que el engine funcione realmente
            with self._engine.connect() as conn:
                conn.execution_options(timeout=self.timeout).execute(sqlalchemy.text("SELECT 1"))

            print(">>> Conexión establecida con éxito.")
            
        except SQLAlchemyError as e:
            print(f"❌ Error al establecer conexión: {e}")
            raise
    
    def disconnect(self) -> None:
        if self._engine:
            self._engine.dispose()
            self._engine = None
            print("Conexión cerrada.")
    
    @contextmanager
    def get_engine(self):
        try:
            if not self._engine:
                self.connect()
            yield self._engine
        finally:
            pass
    
    def execute_query(self, query: str) -> pd.DataFrame:
        try:
            if not self._engine:
                self.connect()
            
            data = pd.read_sql(query, self._engine)
            return data
            
        except SQLAlchemyError as e:
            print(f"Ocurrió un error al ejecutar la consulta: {e}")
            return pd.DataFrame()
    
    def execute_query_with_params(self, query: str, params: dict) -> pd.DataFrame:
        try:
            if not self._engine:
                self.connect()
            
            data = pd.read_sql(sqlalchemy.text(query), self._engine, params=params)
            return data
            
        except SQLAlchemyError as e:
            print(f"Ocurrió un error al ejecutar la consulta: {e}")
            return pd.DataFrame()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def __del__(self):
        self.disconnect()