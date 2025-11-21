"""
Parser para extraer información de programas desde archivos markdown.
"""
import re
from pathlib import Path
from typing import Dict, List, Optional


class ProgramParser:
    """Parser para archivos markdown de programas"""
    
    def __init__(self, docs_path: str):
        self.docs_path = Path(docs_path)
        self.programs = []
    
    def parse_all_programs(self) -> List[Dict]:
        """Parsea todos los archivos de programas en docs/"""
        program_files = list(self.docs_path.glob("programa_tecnico_*.md"))
        
        for file_path in program_files:
            program_data = self.parse_program_file(file_path)
            if program_data:
                self.programs.append(program_data)
        
        return self.programs
    
    def parse_program_file(self, file_path: Path) -> Optional[Dict]:
        """Parsea un archivo markdown de programa"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extraer información general
            code_match = re.search(r'\*\*Código del Programa\*\*:\s*(\w+)', content)
            name_match = re.search(r'\*\*Nombre del Programa\*\*:\s*(.+)', content)
            duration_match = re.search(r'\*\*Duración\*\*:\s*(.+)', content)
            modality_match = re.search(r'\*\*Modalidad\*\*:\s*(.+)', content)
            
            if not code_match or not name_match:
                print(f"⚠️  No se pudo parsear {file_path.name}")
                return None
            
            program_code = code_match.group(1)
            program_name = name_match.group(1).strip()
            duration = duration_match.group(1).strip() if duration_match else "4 semestres"
            modality = modality_match.group(1).strip() if modality_match else ""
            
            # Extraer materias
            subjects = self._parse_subjects(content)
            
            return {
                'code': program_code,
                'name': program_name,
                'duration': duration,
                'modality': modality,
                'subjects': subjects
            }
        except Exception as e:
            print(f"❌ Error parseando {file_path.name}: {e}")
            return None
    
    def _parse_subjects(self, content: str) -> List[Dict]:
        """Extrae materias del contenido markdown"""
        subjects = []
        
        # Buscar sección de materias
        # Patrón mejorado para capturar materias con prerrequisitos
        pattern = r'(\d+)\.\s+\*\*(.+?)\*\*\s*\n\s*-\s*Créditos:\s*(\d+)\s*\n\s*-\s*Horas semanales:\s*(\d+)\s*\n\s*-\s*Prerrequisitos:\s*(.+?)(?=\n\d+\.\s+\*\*|\n##|$)'
        
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            number = int(match.group(1))
            name = match.group(2).strip()
            credits = int(match.group(3))
            hours = int(match.group(4))
            prerequisites = match.group(5).strip()
            
            # Normalizar prerrequisitos
            if prerequisites.lower() in ['ninguno', 'ninguna', '[por definir]']:
                prerequisites = None
            else:
                prerequisites = prerequisites.strip()
            
            subjects.append({
                'number': number,
                'name': name,
                'credits': credits,
                'hours_per_week': hours,
                'prerequisites': prerequisites
            })
        
        return subjects


if __name__ == "__main__":
    # Test del parser
    parser = ProgramParser("/Users/ricardo_suarez1983/SGHU_Sist_gestion_horarios_Uni/docs")
    programs = parser.parse_all_programs()
    
    print(f"✅ Programas encontrados: {len(programs)}")
    for prog in programs:
        print(f"  - {prog['code']}: {prog['name']} ({len(prog['subjects'])} materias)")

