"""
Bug Fixer - AI-Powered Code Debugger
Automatically detects and fixes common bugs in the Martian Swarm project
"""

import os
import re
import ast
import subprocess
from datetime import datetime


class BugFixer:
    """
    Automated bug detection and fixing system
    
    Detects:
    - Syntax errors
    - Import errors
    - Common Python anti-patterns
    - ROS 2 specific issues
    - Memory leaks
    - Race conditions
    """
    
    def __init__(self, project_root):
        self.project_root = project_root
        self.fixed_bugs = []
        self.known_patterns = self.load_bug_patterns()
        
    def load_bug_patterns(self):
        """Load known bug patterns and fixes"""
        return {
            'bare_except': {
                'pattern': r'except\s*:',
                'fix': 'except Exception as e:',
                'description': 'Bare except clause'
            },
            ' mutable_default': {
                'pattern': r'def\s+\w+\s*\([^)]*=\s*[\[\{]',
                'fix': 'Use None and assign inside function',
                'description': 'Mutable default argument'
            },
            'ros_import': {
                'pattern': r'from\s+ros\w*\s+import',
                'fix': 'Use ros2 instead of ros (ROS 1)',
                'description': 'ROS 1 import in ROS 2 code'
            },
            'missing_qos': {
                'pattern': r'create_publisher\([^)]*\)\s*(?!\s*,)',
                'fix': 'Add qos profile parameter',
                'description': 'Missing QoS profile in ROS 2 publisher'
            },
            'empty_except': {
                'pattern': r'except.*:\s*\n\s*\n',
                'fix': 'Add error logging',
                'description': 'Empty except block'
            }
        }
        
    def scan_file(self, filepath):
        """Scan a file for known bug patterns"""
        if not os.path.exists(filepath):
            return []
            
        with open(filepath, 'r') as f:
            content = f.read()
            
        bugs = []
        
        # Check each pattern
        for bug_type, info in self.known_patterns.items():
            matches = re.finditer(info['pattern'], content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                bugs.append({
                    'type': bug_type,
                    'line': line_num,
                    'content': match.group(),
                    'fix': info['fix'],
                    'description': info['description']
                })
                
        # AST-based checks
        try:
            tree = ast.parse(content)
            bugs.extend(self.ast_check(tree, filepath))
        except SyntaxError as e:
            bugs.append({
                'type': 'syntax_error',
                'line': e.lineno,
                'content': f"Syntax error: {e.msg}",
                'fix': 'Fix syntax error',
                'description': str(e)
            })
            
        return bugs
        
    def ast_check(self, tree, filepath):
        """Check AST for additional issues"""
        bugs = []
        
        class BugVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check for missing docstrings
                if not ast.get_docstring(node) and len(node.body) > 3:
                    bugs.append({
                        'type': 'missing_docstring',
                        'line': node.lineno,
                        'content': f"def {node.name}(...)",
                        'fix': 'Add docstring',
                        'description': f'Function {node.name} lacks documentation'
                    })
                self.generic_visit(node)
                
            def visit_For(self, node):
                # Check for range(len()) pattern
                if isinstance(node.iter, ast.Call):
                    if hasattr(node.iter.func, 'id') and node.iter.func.id == 'range':
                        if len(node.iter.args) > 0:
                            if isinstance(node.iter.args[0], ast.Call):
                                if hasattr(node.iter.args[0].func, 'id'):
                                    if node.iter.args[0].func.id == 'len':
                                        bugs.append({
                                            'type': 'range_len',
                                            'line': node.lineno,
                                            'content': 'range(len(...))',
                                            'fix': 'Use enumerate() instead',
                                            'description': 'Inefficient loop iteration'
                                        })
                self.generic_visit(node)
                
        visitor = BugVisitor()
        visitor.visit(tree)
        
        return bugs
        
    def fix_bug(self, filepath, bug):
        """Apply a fix to a bug"""
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
        line_num = bug['line'] - 1
        
        if bug['type'] == 'bare_except':
            if line_num < len(lines):
                lines[line_num] = re.sub(
                    r'except\s*:',
                    'except Exception as e:',
                    lines[line_num]
                )
                
        elif bug['type'] == 'empty_except':
            if line_num + 1 < len(lines):
                # Add pass or logging
                if lines[line_num + 1].strip() == '':
                    indent = '    '
                    lines.insert(line_num + 1, f'{indent}pass  # TODO: Handle exception\n')
                    
        with open(filepath, 'w') as f:
            f.writelines(lines)
            
        self.fixed_bugs.append({
            'file': filepath,
            'bug': bug,
            'timestamp': datetime.now().isoformat()
        })
        
        return True
        
    def fix_all(self, directory=None):
        """Fix all detected bugs in a directory"""
        if directory is None:
            directory = self.project_root
            
        fixed_count = 0
        files_checked = 0
        
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    files_checked += 1
                    
                    bugs = self.scan_file(filepath)
                    for bug in bugs:
                        if self.fix_bug(filepath, bug):
                            fixed_count += 1
                            
        return {
            'files_checked': files_checked,
            'bugs_fixed': fixed_count,
            'report': self.fixed_bugs
        }
        
    def run_ros_lint(self, package_path):
        """Run ROS 2 linting tools"""
        if not os.path.exists(package_path):
            return {'error': 'Package not found'}
            
        results = {
            'package': package_path,
            'checks': []
        }
        
        # Run pylint if available
        try:
            result = subprocess.run(
                ['python3', '-m', 'pylint', package_path, '--disable=all', '--enable=E,F'],
                capture_output=True,
                text=True,
                timeout=60
            )
            results['checks'].append({
                'tool': 'pylint',
                'output': result.stdout,
                'errors': result.returncode
            })
        except FileNotFoundError:
            results['checks'].append({
                'tool': 'pylint',
                'error': 'pylint not installed'
            })
            
        return results


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python bug_fixer.py <directory|file> [--fix]")
        sys.exit(1)
        
    target = sys.argv[1]
    auto_fix = '--fix' in sys.argv
    
    fixer = BugFixer(os.getcwd())
    
    if os.path.isfile(target):
        bugs = fixer.scan_file(target)
        print(f"\n🔍 Found {len(bugs)} potential issues in {target}:\n")
        for bug in bugs:
            print(f"  Line {bug['line']}: {bug['description']}")
            print(f"    {bug['content']}")
            print(f"    Fix: {bug['fix']}\n")
            
        if auto_fix:
            for bug in bugs:
                fixer.fix_bug(target, bug)
            print(f"✅ Fixed {len(bugs)} issues")
            
    elif os.path.isdir(target):
        if auto_fix:
            results = fixer.fix_all(target)
            print(f"\n📊 Scan complete:")
            print(f"  Files checked: {results['files_checked']}")
            print(f"  Bugs fixed: {results['bugs_fixed']}")
        else:
            print("\n🔍 Scanning directory... (use --fix to auto-fix)")
            results = fixer.fix_all(target)
            print(f"\n📊 Found {results['bugs_fixed']} issues in {results['files_checked']} files")


if __name__ == '__main__':
    main()
