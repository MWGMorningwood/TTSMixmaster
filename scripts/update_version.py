#!/usr/bin/env python3
"""
Version management script for TTSMixmaster
Updates version numbers across all project files
"""

import re
import sys
from pathlib import Path
from typing import Dict, List


class VersionManager:
    """Manages version updates across project files"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def update_version(self, new_version: str) -> None:
        """Update version in all relevant files"""
        
        # Remove 'v' prefix if present
        if new_version.startswith('v'):
            new_version = new_version[1:]
            
        print(f"Updating version to {new_version}")
        
        updates = [
            self._update_pyproject_toml,
            self._update_main_py,
            self._update_init_py,
            self._update_inno_setup_fallback,
        ]
        
        for update_func in updates:
            try:
                update_func(new_version)
            except Exception as e:
                print(f"Warning: {update_func.__name__} failed: {e}")
                
    def _update_pyproject_toml(self, version: str) -> None:
        """Update version in pyproject.toml"""
        file_path = self.project_root / "pyproject.toml"
        if not file_path.exists():
            return
            
        content = file_path.read_text(encoding='utf-8')
        content = re.sub(
            r'version\s*=\s*["\'][^"\']*["\']',
            f'version = "{version}"',
            content
        )
        file_path.write_text(content, encoding='utf-8')
        print(f"Updated {file_path}")
        
    def _update_main_py(self, version: str) -> None:
        """Update version in main.py"""
        file_path = self.project_root / "main.py"
        if not file_path.exists():
            return
            
        content = file_path.read_text(encoding='utf-8')
        
        # Look for __version__ = "..."
        if re.search(r'__version__\s*=', content):
            content = re.sub(
                r'__version__\s*=\s*["\'][^"\']*["\']',
                f'__version__ = "{version}"',
                content
            )
        else:
            # Add version at the top after imports
            lines = content.split('\n')
            insert_index = 0
            
            # Find where to insert (after last import or at beginning)
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')):
                    insert_index = i + 1
                elif line.strip() == '' and insert_index > 0:
                    break
                    
            lines.insert(insert_index, f'__version__ = "{version}"')
            content = '\n'.join(lines)
            
        file_path.write_text(content, encoding='utf-8')
        print(f"Updated {file_path}")
        
    def _update_init_py(self, version: str) -> None:
        """Update version in src/__init__.py"""
        file_path = self.project_root / "src" / "__init__.py"
        if not file_path.exists():
            return
            
        content = file_path.read_text(encoding='utf-8')
        
        if re.search(r'__version__\s*=', content):
            content = re.sub(
                r'__version__\s*=\s*["\'][^"\']*["\']',
                f'__version__ = "{version}"',
                content
            )
        else:
            content = f'__version__ = "{version}"\n' + content
            
        file_path.write_text(content, encoding='utf-8')
        print(f"Updated {file_path}")
        
    def _update_inno_setup_fallback(self, version: str) -> None:
        """Update fallback version in Inno Setup script"""
        file_path = self.project_root / "installer" / "TTSMixmaster.iss"
        if not file_path.exists():
            return
            
        content = file_path.read_text(encoding='utf-8')
        
        # Add a fallback version definition
        if '#define MyAppVersionFallback' not in content:
            lines = content.split('\n')
            
            # Find where to insert (after other #define statements)
            insert_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('#define'):
                    insert_index = i + 1
                    
            lines.insert(insert_index, f'#define MyAppVersionFallback "{version}"')
            content = '\n'.join(lines)
            
            file_path.write_text(content, encoding='utf-8')
            print(f"Updated {file_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <version>")
        print("Example: python update_version.py 1.0.0")
        sys.exit(1)
        
    version = sys.argv[1]
    project_root = Path(__file__).parent.parent
    
    version_manager = VersionManager(project_root)
    version_manager.update_version(version)
    
    print(f"Version updated to {version}")


if __name__ == "__main__":
    main()
