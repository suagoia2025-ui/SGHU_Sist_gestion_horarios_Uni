#!/usr/bin/env python3
"""
Script de limpieza del proyecto SGHU
Elimina archivos temporales, cache y archivos generados
"""
import os
import shutil
from pathlib import Path


def remove_pycache(root_dir: Path):
    """Elimina directorios __pycache__"""
    removed = 0
    for pycache_dir in root_dir.rglob("__pycache__"):
        if "venv" not in str(pycache_dir):
            try:
                shutil.rmtree(pycache_dir)
                print(f"✅ Eliminado: {pycache_dir}")
                removed += 1
            except Exception as e:
                print(f"❌ Error eliminando {pycache_dir}: {e}")
    return removed


def remove_pyc_files(root_dir: Path):
    """Elimina archivos .pyc y .pyo"""
    removed = 0
    for ext in ["*.pyc", "*.pyo"]:
        for pyc_file in root_dir.rglob(ext):
            if "venv" not in str(pyc_file):
                try:
                    pyc_file.unlink()
                    print(f"✅ Eliminado: {pyc_file}")
                    removed += 1
                except Exception as e:
                    print(f"❌ Error eliminando {pyc_file}: {e}")
    return removed


def clean_logs(logs_dir: Path, keep_recent: bool = True):
    """Limpia archivos de log antiguos"""
    if not logs_dir.exists():
        return 0
    
    removed = 0
    for log_file in logs_dir.glob("*.log*"):
        # Mantener el log principal si keep_recent es True
        if keep_recent and log_file.name == "sghu.log":
            continue
        
        try:
            # Si es un archivo de backup (sghu.log.1, sghu.log.2, etc.)
            if log_file.suffix.isdigit() or ".log." in log_file.name:
                log_file.unlink()
                print(f"✅ Eliminado log backup: {log_file}")
                removed += 1
        except Exception as e:
            print(f"❌ Error eliminando {log_file}: {e}")
    
    return removed


def clean_pytest_cache(root_dir: Path):
    """Elimina directorios .pytest_cache"""
    removed = 0
    for cache_dir in root_dir.rglob(".pytest_cache"):
        if "venv" not in str(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"✅ Eliminado: {cache_dir}")
                removed += 1
            except Exception as e:
                print(f"❌ Error eliminando {cache_dir}: {e}")
    return removed


def clean_coverage_files(root_dir: Path):
    """Elimina archivos de coverage"""
    removed = 0
    for pattern in [".coverage", "htmlcov", ".coverage.*"]:
        for item in root_dir.rglob(pattern):
            if "venv" not in str(item):
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    print(f"✅ Eliminado: {item}")
                    removed += 1
                except Exception as e:
                    print(f"❌ Error eliminando {item}: {e}")
    return removed


def clean_egg_info(root_dir: Path):
    """Elimina directorios *.egg-info"""
    removed = 0
    for egg_dir in root_dir.rglob("*.egg-info"):
        if "venv" not in str(egg_dir):
            try:
                shutil.rmtree(egg_dir)
                print(f"✅ Eliminado: {egg_dir}")
                removed += 1
            except Exception as e:
                print(f"❌ Error eliminando {egg_dir}: {e}")
    return removed


def main():
    """Función principal"""
    print("🧹 Limpieza del proyecto SGHU\n")
    
    # Directorio raíz del proyecto
    root_dir = Path(__file__).parent.parent
    logs_dir = root_dir / "logs"
    
    total_removed = 0
    
    print("1️⃣  Eliminando __pycache__...")
    total_removed += remove_pycache(root_dir)
    
    print("\n2️⃣  Eliminando archivos .pyc y .pyo...")
    total_removed += remove_pyc_files(root_dir)
    
    print("\n3️⃣  Limpiando logs antiguos...")
    total_removed += clean_logs(logs_dir, keep_recent=True)
    
    print("\n4️⃣  Eliminando .pytest_cache...")
    total_removed += clean_pytest_cache(root_dir)
    
    print("\n5️⃣  Eliminando archivos de coverage...")
    total_removed += clean_coverage_files(root_dir)
    
    print("\n6️⃣  Eliminando *.egg-info...")
    total_removed += clean_egg_info(root_dir)
    
    print(f"\n✅ Limpieza completada. Total de elementos eliminados: {total_removed}")
    print("\n💡 Nota: Los archivos en venv/ no se eliminan por seguridad.")


if __name__ == "__main__":
    main()

