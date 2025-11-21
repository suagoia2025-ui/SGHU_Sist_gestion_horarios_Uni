"""
Script para visualizar tablas y datos de la base de datos.
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import inspect, text
from app.database import SessionLocal, engine


def show_all_tables():
    """Muestra todas las tablas organizadas por schema"""
    print("="*70)
    print("TABLAS DE LA BASE DE DATOS")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Obtener todas las tablas usando SQL
        result = db.execute(text("""
            SELECT 
                table_schema,
                table_name,
                (SELECT COUNT(*) 
                 FROM information_schema.columns 
                 WHERE columns.table_schema = tables.table_schema 
                 AND columns.table_name = tables.table_name) as column_count
            FROM information_schema.tables
            WHERE table_schema IN ('source', 'sghu', 'public')
            AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name;
        """))
        
        current_schema = None
        for row in result:
            schema, table_name, col_count = row
            
            if schema != current_schema:
                if current_schema is not None:
                    print()
                print(f"\n📁 Schema: {schema.upper()}")
                print("-" * 70)
                current_schema = schema
            
            # Contar registros
            try:
                count_result = db.execute(text(f'SELECT COUNT(*) FROM "{schema}"."{table_name}"'))
                record_count = count_result.scalar()
                print(f"  📊 {table_name:<40} ({col_count:>2} columnas, {record_count:>6} registros)")
            except Exception as e:
                print(f"  📊 {table_name:<40} ({col_count:>2} columnas, error al contar)")
        
        print("\n" + "="*70)
        
    finally:
        db.close()


def show_table_structure(schema: str, table_name: str):
    """Muestra la estructura de una tabla específica"""
    db = SessionLocal()
    try:
        print(f"\n📋 Estructura de la tabla: {schema}.{table_name}")
        print("="*70)
        
        # Obtener columnas
        result = db.execute(text(f"""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = '{schema}' 
            AND table_name = '{table_name}'
            ORDER BY ordinal_position;
        """))
        
        print(f"{'Columna':<30} {'Tipo':<20} {'Nulo':<8} {'Default'}")
        print("-"*70)
        for row in result:
            col_name, data_type, max_length, nullable, default = row
            type_str = f"{data_type}({max_length})" if max_length else data_type
            default_str = str(default)[:30] if default else "-"
            print(f"{col_name:<30} {type_str:<20} {nullable:<8} {default_str}")
        
        # Obtener foreign keys
        fk_result = db.execute(text(f"""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = '{schema}'
            AND tc.table_name = '{table_name}';
        """))
        
        fks = list(fk_result)
        if fks:
            print("\n🔗 Foreign Keys:")
            for fk in fks:
                constraint_name, col, fk_schema, fk_table, fk_col = fk
                print(f"  {col} -> {fk_schema}.{fk_table}.{fk_col}")
        
        # Contar registros
        count_result = db.execute(text(f'SELECT COUNT(*) FROM "{schema}"."{table_name}"'))
        record_count = count_result.scalar()
        print(f"\n📊 Total de registros: {record_count}")
        
    finally:
        db.close()


def show_sample_data(schema: str, table_name: str, limit: int = 5):
    """Muestra una muestra de datos de una tabla"""
    db = SessionLocal()
    try:
        print(f"\n📄 Muestra de datos: {schema}.{table_name} (primeros {limit} registros)")
        print("="*70)
        
        result = db.execute(text(f'SELECT * FROM "{schema}"."{table_name}" LIMIT {limit}'))
        
        rows = result.fetchall()
        if not rows:
            print("  (Tabla vacía)")
            return
        
        # Obtener nombres de columnas
        columns = result.keys()
        
        # Mostrar encabezados
        header = " | ".join(str(col)[:15] for col in columns)
        print(header)
        print("-" * len(header))
        
        # Mostrar datos
        for row in rows:
            values = " | ".join(str(val)[:15] if val is not None else "NULL" for val in row)
            print(values)
        
    finally:
        db.close()


def main():
    """Función principal"""
    import argparse
    parser = argparse.ArgumentParser(description='Visualizar tablas de la BD')
    parser.add_argument('--schema', type=str, help='Schema específico (source, sghu)')
    parser.add_argument('--table', type=str, help='Tabla específica')
    parser.add_argument('--structure', action='store_true', help='Mostrar estructura de tabla')
    parser.add_argument('--sample', action='store_true', help='Mostrar muestra de datos')
    parser.add_argument('--limit', type=int, default=5, help='Límite de registros en muestra')
    
    args = parser.parse_args()
    
    if args.table and args.schema:
        if args.structure:
            show_table_structure(args.schema, args.table)
        if args.sample:
            show_sample_data(args.schema, args.table, args.limit)
    else:
        show_all_tables()


if __name__ == "__main__":
    main()

