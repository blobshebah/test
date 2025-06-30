#!/usr/bin/env python3
"""
Automatic Documentation Generator

This script scans a codebase and generates comprehensive documentation
templates for APIs, functions, and components.

Usage:
    python generate_docs.py [directory] [--output docs/] [--format markdown]

Requirements:
    - Python 3.7+
    - No external dependencies (uses only standard library)
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class FunctionInfo:
    """Information about a function or method."""
    name: str
    file_path: str
    line_number: int
    signature: str
    docstring: Optional[str] = None
    is_public: bool = True
    language: str = ""
    class_name: Optional[str] = None


@dataclass
class ClassInfo:
    """Information about a class or component."""
    name: str
    file_path: str
    line_number: int
    docstring: Optional[str] = None
    methods: List[FunctionInfo] = None
    is_public: bool = True
    language: str = ""
    
    def __post_init__(self):
        if self.methods is None:
            self.methods = []


@dataclass
class APIEndpoint:
    """Information about an API endpoint."""
    method: str
    path: str
    file_path: str
    line_number: int
    handler_function: str
    description: Optional[str] = None


class DocumentationGenerator:
    """Main class for generating documentation from source code."""
    
    def __init__(self, project_root: str, output_dir: str = "docs"):
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir)
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.api_endpoints: List[APIEndpoint] = []
        
        # File patterns to scan
        self.patterns = {
            'python': ['*.py'],
            'javascript': ['*.js', '*.jsx'],
            'typescript': ['*.ts', '*.tsx'],
            'java': ['*.java'],
            'cpp': ['*.cpp', '*.cc', '*.cxx', '*.hpp', '*.h'],
            'csharp': ['*.cs'],
            'go': ['*.go'],
            'rust': ['*.rs'],
            'php': ['*.php'],
            'ruby': ['*.rb']
        }
        
    def scan_directory(self) -> None:
        """Scan the project directory for source files."""
        print(f"Scanning directory: {self.project_root}")
        
        for language, patterns in self.patterns.items():
            for pattern in patterns:
                for file_path in self.project_root.rglob(pattern):
                    if self._should_skip_file(file_path):
                        continue
                    
                    print(f"Processing: {file_path}")
                    try:
                        self._analyze_file(file_path, language)
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_dirs = {
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'venv', 'env', 'build', 'dist', 'target', '.next'
        }
        
        return any(part in skip_dirs for part in file_path.parts)
    
    def _analyze_file(self, file_path: Path, language: str) -> None:
        """Analyze a single file for documentable items."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            print(f"Skipping binary file: {file_path}")
            return
        
        if language == 'python':
            self._analyze_python_file(file_path, content)
        elif language in ['javascript', 'typescript']:
            self._analyze_js_file(file_path, content, language)
        elif language == 'java':
            self._analyze_java_file(file_path, content)
        # Add more language analyzers as needed
    
    def _analyze_python_file(self, file_path: Path, content: str) -> None:
        """Analyze Python file for functions and classes."""
        lines = content.split('\n')
        current_class = None
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Class definitions
            class_match = re.match(r'^class\s+(\w+).*?:', stripped)
            if class_match:
                class_name = class_match.group(1)
                is_public = not class_name.startswith('_')
                docstring = self._extract_python_docstring(lines, i)
                
                class_info = ClassInfo(
                    name=class_name,
                    file_path=str(file_path),
                    line_number=i,
                    docstring=docstring,
                    is_public=is_public,
                    language='python'
                )
                self.classes.append(class_info)
                current_class = class_info
            
            # Function/method definitions
            func_match = re.match(r'^def\s+(\w+)\s*\((.*?)\).*?:', stripped)
            if func_match:
                func_name = func_match.group(1)
                params = func_match.group(2)
                is_public = not func_name.startswith('_')
                docstring = self._extract_python_docstring(lines, i)
                
                func_info = FunctionInfo(
                    name=func_name,
                    file_path=str(file_path),
                    line_number=i,
                    signature=f"def {func_name}({params})",
                    docstring=docstring,
                    is_public=is_public,
                    language='python',
                    class_name=current_class.name if current_class else None
                )
                
                if current_class:
                    current_class.methods.append(func_info)
                else:
                    self.functions.append(func_info)
            
            # Reset class context when we reach the end of a class
            if stripped and not line.startswith(' ') and not line.startswith('\t') and current_class:
                if not (stripped.startswith('class ') or stripped.startswith('def ') or stripped.startswith('#')):
                    current_class = None
    
    def _analyze_js_file(self, file_path: Path, content: str, language: str) -> None:
        """Analyze JavaScript/TypeScript file for functions and components."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Function declarations
            func_patterns = [
                r'function\s+(\w+)\s*\((.*?)\)',
                r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>',
                r'let\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>',
                r'var\s+(\w+)\s*=\s*function\s*\(([^)]*)\)',
            ]
            
            for pattern in func_patterns:
                match = re.search(pattern, stripped)
                if match:
                    func_name = match.group(1)
                    params = match.group(2) if len(match.groups()) > 1 else ""
                    
                    # Extract JSDoc comments
                    docstring = self._extract_jsdoc(lines, i - 1)
                    
                    func_info = FunctionInfo(
                        name=func_name,
                        file_path=str(file_path),
                        line_number=i,
                        signature=f"{func_name}({params})",
                        docstring=docstring,
                        is_public=True,  # JavaScript functions are typically public
                        language=language
                    )
                    self.functions.append(func_info)
                    break
            
            # React component detection
            component_patterns = [
                r'const\s+(\w+)\s*=\s*\(.*?\)\s*=>\s*{',
                r'function\s+(\w+)\s*\(.*?\)\s*{',
                r'class\s+(\w+)\s+extends\s+.*Component'
            ]
            
            for pattern in component_patterns:
                match = re.search(pattern, stripped)
                if match and self._looks_like_react_component(match.group(1)):
                    component_name = match.group(1)
                    docstring = self._extract_jsdoc(lines, i - 1)
                    
                    class_info = ClassInfo(
                        name=component_name,
                        file_path=str(file_path),
                        line_number=i,
                        docstring=docstring,
                        is_public=True,
                        language=language
                    )
                    self.classes.append(class_info)
                    break
    
    def _analyze_java_file(self, file_path: Path, content: str) -> None:
        """Analyze Java file for classes and methods."""
        lines = content.split('\n')
        current_class = None
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Class definitions
            class_match = re.search(r'(?:public|private|protected)?\s*class\s+(\w+)', stripped)
            if class_match:
                class_name = class_match.group(1)
                is_public = 'public' in stripped or ('private' not in stripped and 'protected' not in stripped)
                docstring = self._extract_javadoc(lines, i - 1)
                
                class_info = ClassInfo(
                    name=class_name,
                    file_path=str(file_path),
                    line_number=i,
                    docstring=docstring,
                    is_public=is_public,
                    language='java'
                )
                self.classes.append(class_info)
                current_class = class_info
            
            # Method definitions
            method_match = re.search(r'(?:public|private|protected)\s+.*?\s+(\w+)\s*\([^)]*\)\s*{?', stripped)
            if method_match and not re.search(r'\b(class|interface|enum)\b', stripped):
                method_name = method_match.group(1)
                is_public = 'public' in stripped
                docstring = self._extract_javadoc(lines, i - 1)
                
                func_info = FunctionInfo(
                    name=method_name,
                    file_path=str(file_path),
                    line_number=i,
                    signature=stripped,
                    docstring=docstring,
                    is_public=is_public,
                    language='java',
                    class_name=current_class.name if current_class else None
                )
                
                if current_class:
                    current_class.methods.append(func_info)
                else:
                    self.functions.append(func_info)
    
    def _extract_python_docstring(self, lines: List[str], func_line: int) -> Optional[str]:
        """Extract Python docstring from function definition."""
        # Look for docstring in the next few lines
        for i in range(func_line, min(func_line + 10, len(lines))):
            line = lines[i].strip()
            if line.startswith('"""') or line.startswith("'''"):
                # Found docstring start
                quote_char = '"""' if line.startswith('"""') else "'''"
                docstring_lines = []
                
                # Single line docstring
                if line.count(quote_char) >= 2:
                    return line.replace(quote_char, '').strip()
                
                # Multi-line docstring
                docstring_lines.append(line.replace(quote_char, ''))
                for j in range(i + 1, len(lines)):
                    if quote_char in lines[j]:
                        docstring_lines.append(lines[j].split(quote_char)[0])
                        break
                    docstring_lines.append(lines[j].strip())
                
                return '\n'.join(docstring_lines).strip()
        
        return None
    
    def _extract_jsdoc(self, lines: List[str], start_line: int) -> Optional[str]:
        """Extract JSDoc comment block."""
        # Look backwards for JSDoc comment
        for i in range(start_line, max(start_line - 20, -1), -1):
            line = lines[i].strip()
            if line.endswith('*/'):
                # Found end of comment, now find start
                comment_lines = []
                for j in range(i, max(i - 50, -1), -1):
                    comment_line = lines[j].strip()
                    if comment_line.startswith('/**'):
                        # Found start of JSDoc
                        comment_lines.reverse()
                        return '\n'.join(comment_lines)
                    if comment_line.startswith('*'):
                        comment_lines.append(comment_line[1:].strip())
                break
        
        return None
    
    def _extract_javadoc(self, lines: List[str], start_line: int) -> Optional[str]:
        """Extract Javadoc comment block."""
        return self._extract_jsdoc(lines, start_line)  # Same format as JSDoc
    
    def _looks_like_react_component(self, name: str) -> bool:
        """Check if a name looks like a React component."""
        return name[0].isupper() and len(name) > 1
    
    def generate_documentation(self) -> None:
        """Generate comprehensive documentation files."""
        self.output_dir.mkdir(exist_ok=True)
        
        # Generate main API documentation
        self._generate_api_overview()
        
        # Generate function documentation
        if self.functions:
            self._generate_functions_doc()
        
        # Generate class/component documentation
        if self.classes:
            self._generate_classes_doc()
        
        # Generate language-specific documentation
        self._generate_language_specific_docs()
        
        # Generate summary
        self._generate_summary()
        
        print(f"\nDocumentation generated in: {self.output_dir}")
    
    def _generate_api_overview(self) -> None:
        """Generate the main API overview documentation."""
        content = f"""# API Documentation

## Overview

This documentation covers the public APIs, functions, and components in this project.

**Generated on:** {self._get_current_date()}  
**Total Functions:** {len([f for f in self.functions if f.is_public])}  
**Total Classes/Components:** {len([c for c in self.classes if c.is_public])}  

## Quick Navigation

- [Functions](#functions)
- [Classes and Components](#classes-and-components)
- [API Reference](#api-reference)

## Architecture Overview

```
{self._generate_project_structure()}
```

## Getting Started

### Installation

```bash
# Add installation instructions here
git clone <repository-url>
cd <project-directory>
# Install dependencies
```

### Basic Usage

```
# Add basic usage examples here
```

## API Reference

See the following files for detailed API documentation:

- [`functions.md`](functions.md) - All public functions and utilities
- [`classes.md`](classes.md) - Classes, components, and their methods
- [`examples.md`](examples.md) - Usage examples and code snippets

"""
        
        self._write_file("README.md", content)
    
    def _generate_functions_doc(self) -> None:
        """Generate documentation for all functions."""
        content = "# Functions Documentation\n\n"
        
        # Group functions by file
        functions_by_file = {}
        for func in self.functions:
            if not func.is_public:
                continue
            
            file_path = func.file_path
            if file_path not in functions_by_file:
                functions_by_file[file_path] = []
            functions_by_file[file_path].append(func)
        
        for file_path, functions in functions_by_file.items():
            rel_path = os.path.relpath(file_path, self.project_root)
            content += f"## {rel_path}\n\n"
            
            for func in functions:
                content += self._format_function_documentation(func)
                content += "\n---\n\n"
        
        self._write_file("functions.md", content)
    
    def _generate_classes_doc(self) -> None:
        """Generate documentation for all classes and components."""
        content = "# Classes and Components Documentation\n\n"
        
        # Group classes by file
        classes_by_file = {}
        for cls in self.classes:
            if not cls.is_public:
                continue
            
            file_path = cls.file_path
            if file_path not in classes_by_file:
                classes_by_file[file_path] = []
            classes_by_file[file_path].append(cls)
        
        for file_path, classes in classes_by_file.items():
            rel_path = os.path.relpath(file_path, self.project_root)
            content += f"## {rel_path}\n\n"
            
            for cls in classes:
                content += self._format_class_documentation(cls)
                content += "\n---\n\n"
        
        self._write_file("classes.md", content)
    
    def _format_function_documentation(self, func: FunctionInfo) -> str:
        """Format documentation for a single function."""
        content = f"### `{func.name}`\n\n"
        
        if func.class_name:
            content += f"**Class:** `{func.class_name}`\n\n"
        
        content += f"**Signature:** `{func.signature}`\n\n"
        content += f"**File:** `{os.path.relpath(func.file_path, self.project_root)}:{func.line_number}`\n\n"
        content += f"**Language:** {func.language.title()}\n\n"
        
        if func.docstring:
            content += "**Description:**\n\n"
            content += f"```\n{func.docstring}\n```\n\n"
        else:
            content += "**Description:** *No description available*\n\n"
        
        # Add template for parameters, returns, examples
        content += "**Parameters:**\n\n"
        content += "| Parameter | Type | Description |\n"
        content += "|-----------|------|--------------|\n"
        content += "| *TODO* | *TODO* | *TODO* |\n\n"
        
        content += "**Returns:** *TODO*\n\n"
        
        content += "**Example:**\n\n"
        content += f"```{func.language}\n"
        content += f"// TODO: Add usage example for {func.name}\n"
        content += "```\n\n"
        
        return content
    
    def _format_class_documentation(self, cls: ClassInfo) -> str:
        """Format documentation for a single class."""
        content = f"### `{cls.name}`\n\n"
        
        content += f"**File:** `{os.path.relpath(cls.file_path, self.project_root)}:{cls.line_number}`\n\n"
        content += f"**Language:** {cls.language.title()}\n\n"
        
        if cls.docstring:
            content += "**Description:**\n\n"
            content += f"```\n{cls.docstring}\n```\n\n"
        else:
            content += "**Description:** *No description available*\n\n"
        
        # Add methods if any
        if cls.methods:
            content += "**Methods:**\n\n"
            for method in cls.methods:
                if method.is_public:
                    content += f"- [`{method.name}`](#{method.name.lower()}): {method.signature}\n"
            content += "\n"
            
            # Detailed method documentation
            content += "#### Methods Details\n\n"
            for method in cls.methods:
                if method.is_public:
                    content += f"##### `{method.name}`\n\n"
                    content += f"**Signature:** `{method.signature}`\n\n"
                    if method.docstring:
                        content += f"**Description:** {method.docstring}\n\n"
                    else:
                        content += "**Description:** *No description available*\n\n"
        
        # Add usage example template
        content += "**Example:**\n\n"
        content += f"```{cls.language}\n"
        content += f"// TODO: Add usage example for {cls.name}\n"
        content += "```\n\n"
        
        return content
    
    def _generate_language_specific_docs(self) -> None:
        """Generate language-specific documentation."""
        languages = set()
        for func in self.functions:
            languages.add(func.language)
        for cls in self.classes:
            languages.add(cls.language)
        
        for language in languages:
            if language:
                self._generate_language_doc(language)
    
    def _generate_language_doc(self, language: str) -> None:
        """Generate documentation for a specific language."""
        lang_functions = [f for f in self.functions if f.language == language and f.is_public]
        lang_classes = [c for c in self.classes if c.language == language and c.is_public]
        
        content = f"# {language.title()} API Reference\n\n"
        content += f"This document covers all {language.title()} APIs in the project.\n\n"
        content += f"**Functions:** {len(lang_functions)}\n"
        content += f"**Classes:** {len(lang_classes)}\n\n"
        
        if lang_classes:
            content += "## Classes\n\n"
            for cls in lang_classes:
                content += f"- [`{cls.name}`](classes.md#{cls.name.lower()})\n"
            content += "\n"
        
        if lang_functions:
            content += "## Functions\n\n"
            for func in lang_functions:
                content += f"- [`{func.name}`](functions.md#{func.name.lower()})\n"
            content += "\n"
        
        self._write_file(f"{language}.md", content)
    
    def _generate_summary(self) -> None:
        """Generate a summary of the documentation generation."""
        public_functions = [f for f in self.functions if f.is_public]
        public_classes = [c for c in self.classes if c.is_public]
        
        content = f"""# Documentation Summary

## Statistics

- **Total Files Scanned:** {len(set(f.file_path for f in self.functions + [FunctionInfo('', c.file_path, 0, '') for c in self.classes]))}
- **Public Functions:** {len(public_functions)}
- **Public Classes/Components:** {len(public_classes)}
- **Languages Detected:** {', '.join(set(f.language for f in self.functions + [FunctionInfo('', '', 0, '', language=c.language) for c in self.classes] if f.language))}

## Files Generated

- `README.md` - Main API overview
- `functions.md` - Function documentation
- `classes.md` - Class and component documentation
- `summary.md` - This summary file

## Language-specific Files

{self._list_language_files()}

## Next Steps

1. Review the generated documentation templates
2. Fill in missing descriptions and examples
3. Add parameter and return type information
4. Include usage examples
5. Set up automated documentation generation in your CI/CD pipeline

## Maintenance

Remember to regenerate documentation when:
- New public APIs are added
- Function signatures change
- Documentation comments are updated

Run the generator again with:
```bash
python generate_docs.py {self.project_root}
```
"""
        
        self._write_file("summary.md", content)
    
    def _list_language_files(self) -> str:
        """List generated language-specific files."""
        languages = set()
        for func in self.functions:
            if func.language:
                languages.add(func.language)
        for cls in self.classes:
            if cls.language:
                languages.add(cls.language)
        
        if not languages:
            return "- No language-specific files generated\n"
        
        return "\n".join(f"- `{lang}.md` - {lang.title()} API reference" for lang in sorted(languages)) + "\n"
    
    def _generate_project_structure(self) -> str:
        """Generate a simple project structure diagram."""
        return """
Project Structure
├── Source Files
│   ├── Functions (utilities, helpers)
│   ├── Classes (models, services)
│   └── Components (UI, widgets)
├── Documentation
│   ├── API Reference
│   ├── Usage Examples
│   └── Getting Started
└── Tests (if found)
"""
    
    def _get_current_date(self) -> str:
        """Get current date in ISO format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def _write_file(self, filename: str, content: str) -> None:
        """Write content to a file in the output directory."""
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated: {file_path}")


def main():
    """Main entry point for the documentation generator."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive documentation for a codebase"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan for source files (default: current directory)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="docs",
        help="Output directory for documentation (default: docs)"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "html", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist")
        sys.exit(1)
    
    print("🚀 Documentation Generator")
    print("=" * 50)
    
    generator = DocumentationGenerator(args.directory, args.output)
    
    try:
        generator.scan_directory()
        generator.generate_documentation()
        
        print("\n✅ Documentation generation completed successfully!")
        print(f"📁 Output directory: {generator.output_dir}")
        print(f"📄 Generated files: {len(list(generator.output_dir.glob('*.md')))} markdown files")
        
    except Exception as e:
        print(f"\n❌ Error generating documentation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()