import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Database:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._init_connection_pool()
        self._init_tables()
    
    def _init_connection_pool(self):
        """
        Inicializa el pool de conexiones a PostgreSQL
        """
        try:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "licitaciones_db"),
                user=os.getenv("DB_USER", "licitaciones_user"),
                password=os.getenv("DB_PASSWORD", "")
            )
            print("✅ Pool de conexiones PostgreSQL inicializado")
        except Exception as e:
            print(f"❌ Error conectando a PostgreSQL: {str(e)}")
            raise
    
    def _init_tables(self):
        """
        Ejecuta el script SQL de inicialización si las tablas no existen
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar si las tablas existen
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'licitaciones'
                )
            """)
            
            tables_exist = cursor.fetchone()[0]
            
            if not tables_exist:
                print("📋 Creando tablas en PostgreSQL...")
                
                # Leer y ejecutar script SQL
                sql_file = Path(__file__).parent / "init_db.sql"
                with open(sql_file, 'r') as f:
                    sql_script = f.read()
                
                cursor.execute(sql_script)
                conn.commit()
                print("Tablas creadas exitosamente")
            else:
                print("Tablas ya existen")
            
            cursor.close()
            self.return_connection(conn)
        
        except Exception as e:
            print(f"Error inicializando tablas: {str(e)}")
            raise
    
    def get_connection(self):
        """
        Obtiene una conexión del pool
        """
        return self._pool.getconn()
    
    def return_connection(self, conn):
        """
        Devuelve una conexión al pool
        """
        self._pool.putconn(conn)
    
    def execute(self, query: str, params: tuple = ()) -> int:
        """
        Ejecuta una query que modifica datos (INSERT, UPDATE, DELETE)
        Retorna el ID del registro insertado o el número de filas afectadas
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Si es un INSERT, intentar obtener el ID
            if query.strip().upper().startswith('INSERT'):
                # Para PostgreSQL con RETURNING
                if 'RETURNING' in query.upper():
                    result = cursor.fetchone()
                    lastrowid = result[0] if result else None
                else:
                    lastrowid = cursor.lastrowid
            else:
                lastrowid = cursor.rowcount
            
            conn.commit()
            cursor.close()
            return lastrowid
        
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.return_connection(conn)
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """
        Obtiene un registro como diccionario
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            row = cursor.fetchone()
            cursor.close()
            return dict(row) if row else None
        finally:
            self.return_connection(conn)
    
    def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Obtiene múltiples registros como lista de diccionarios
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in rows]
        finally:
            self.return_connection(conn)
    
    def close(self):
        """
        Cierra todas las conexiones del pool
        """
        if self._pool:
            self._pool.closeall()
            print("⏹️  Pool de conexiones cerrado")

# Singleton
db = Database()
