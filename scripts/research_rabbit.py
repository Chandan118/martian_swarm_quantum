"""
Research Rabbit - AI Research Assistant for Martian Swarm Project
Helps debug code, research topics, and improve experiments
"""

import json
import subprocess
import os
import sys
import re
from datetime import datetime


class ResearchRabbit:
    """
    AI-powered research assistant for the Martian Swarm Quantum project.
    
    Features:
    - Code debugging and fixing
    - Research topic exploration
    - Experiment optimization
    - Literature review
    - Bug detection
    """
    
    def __init__(self, project_root):
        self.project_root = project_root
        self.conversation_history = []
        self.knowledge_base = self.load_knowledge_base()
        
    def load_knowledge_base(self):
        """Load project-specific knowledge"""
        return {
            'ros2': ['humble', 'nodes', 'topics', 'services', 'actions'],
            'snn': ['lif-neuron', 'spiking', 'obstacle-avoidance', 'neuromorphic'],
            'quantum': ['qubo', 'optimization', 'map-merging', 'annealing'],
            'gazebo': ['world', 'model', 'physics', 'sensors'],
            'chaos': ['blackout', 'mesh-network', 'resilience', 'fault-tolerance']
        }
        
    def analyze_code(self, file_path):
        """Analyze code for potential issues"""
        issues = []
        
        if not os.path.exists(file_path):
            return [{'error': 'File not found', 'path': file_path}]
            
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Check for common issues
        for i, line in enumerate(lines, 1):
            # Check for TODO/FIXME
            if 'TODO' in line or 'FIXME' in line:
                issues.append({
                    'line': i,
                    'type': 'todo',
                    'message': line.strip(),
                    'severity': 'info'
                })
                
            # Check for potential bugs
            if 'except:' in line and 'except Exception' not in line:
                issues.append({
                    'line': i,
                    'type': 'bare-except',
                    'message': 'Bare except clause may catch unexpected exceptions',
                    'severity': 'warning'
                })
                
            # Check for empty except blocks
            if i < len(lines) and 'except' in line:
                next_lines = lines[i:i+3]
                if all(l.strip() == '' or l.strip().startswith('#') for l in next_lines[1:]):
                    issues.append({
                        'line': i,
                        'type': 'empty-except',
                        'message': 'Empty except block - errors are silently ignored',
                        'severity': 'error'
                    })
                    
            # Check for TODO in comments
            if re.match(r'^\s*#.*\b(BUG|HACK|XXX)\b', line, re.IGNORECASE):
                issues.append({
                    'line': i,
                    'type': 'marker',
                    'message': line.strip(),
                    'severity': 'warning'
                })
                
        return issues
        
    def fix_code(self, file_path, issue):
        """Attempt to fix a specific code issue"""
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        line_num = issue.get('line', 0) - 1
        
        if issue['type'] == 'empty-except':
            # Add basic error logging
            if line_num < len(lines):
                indent = len(lines[line_num]) - len(lines[line_num].lstrip())
                lines[line_num] = lines[line_num].rstrip() + ' Exception as e:\n'
                lines.insert(line_num + 1, ' ' * (indent + 4) + f'print(f"Error: {{e}}")\n')
                
        elif issue['type'] == 'bare-except':
            # Replace bare except with specific exception
            if line_num < len(lines):
                lines[line_num] = lines[line_num].replace('except:', 'except Exception as e:')
                
        with open(file_path, 'w') as f:
            f.writelines(lines)
            
        return True
        
    def search_code(self, query):
        """Search codebase for relevant code"""
        results = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith(('.py', '.m', '.cpp', '.h', '.xml', '.launch.py')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                # Find line numbers
                                for i, line in enumerate(content.split('\n'), 1):
                                    if query.lower() in line.lower():
                                        results.append({
                                            'file': filepath,
                                            'line': i,
                                            'content': line.strip()
                                        })
                    except:
                        pass
                        
        return results
        
    def suggest_improvements(self, code_context):
        """Use AI to suggest code improvements"""
        suggestions = []
        
        # Basic pattern-based suggestions
        if 'for' in code_context and 'range(len(' in code_context:
            suggestions.append({
                'type': 'pythonic',
                'message': 'Consider using enumerate() instead of range(len())',
                'confidence': 0.9
            })
            
        if 'import *' in code_context:
            suggestions.append({
                'type': 'imports',
                'message': 'Avoid wildcard imports, specify exact imports',
                'confidence': 0.95
            })
            
        if '==' in code_context and ('True' in code_context or 'False' in code_context):
            suggestions.append({
                'type': 'boolean',
                'message': 'Use "if x:" instead of "if x == True:"',
                'confidence': 0.9
            })
            
        # Check for missing type hints
        if 'def ' in code_context and ': ' not in code_context.split('def ')[1].split(':')[0]:
            suggestions.append({
                'type': 'type-hints',
                'message': 'Consider adding type hints for better code documentation',
                'confidence': 0.7
            })
            
        return suggestions
        
    def generate_documentation(self, code_file):
        """Generate documentation for a code file"""
        docs = {
            'file': code_file,
            'generated': datetime.now().isoformat(),
            'functions': [],
            'classes': [],
            'imports': []
        }
        
        with open(code_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
        in_docstring = False
        current_docstring = []
        
        for i, line in enumerate(lines):
            # Find classes
            if line.startswith('class '):
                class_name = re.search(r'class (\w+)', line)
                if class_name:
                    docs['classes'].append({
                        'name': class_name.group(1),
                        'line': i + 1,
                        'docstring': ''
                    })
                    
            # Find functions
            if line.startswith('def '):
                func_match = re.search(r'def (\w+)\((.*?)\)', line)
                if func_match:
                    docs['functions'].append({
                        'name': func_match.group(1),
                        'params': func_match.group(2),
                        'line': i + 1,
                        'docstring': ''
                    })
                    
            # Find imports
            if line.startswith('import ') or line.startswith('from '):
                docs['imports'].append(line.strip())
                
        return docs
        
    def run_diagnostics(self):
        """Run diagnostic checks on the project"""
        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'checks': []
        }
        
        # Check ROS 2 workspace
        ws_path = os.path.join(self.project_root, 'ros2_ws')
        if os.path.exists(ws_path):
            diagnostics['checks'].append({
                'name': 'ros2_workspace',
                'status': 'ok',
                'message': 'ROS 2 workspace found'
            })
            
            # Check for build artifacts
            if os.path.exists(os.path.join(ws_path, 'build')):
                diagnostics['checks'].append({
                    'name': 'ros2_build',
                    'status': 'ok',
                    'message': 'ROS 2 workspace appears to be built'
                })
            else:
                diagnostics['checks'].append({
                    'name': 'ros2_build',
                    'status': 'warning',
                    'message': 'ROS 2 workspace not built yet'
                })
        else:
            diagnostics['checks'].append({
                'name': 'ros2_workspace',
                'status': 'error',
                'message': 'ROS 2 workspace not found'
            })
            
        # Check Docker
        docker_path = os.path.join(self.project_root, 'docker')
        if os.path.exists(docker_path):
            dockerfiles = [f for f in os.listdir(docker_path) if f.startswith('Dockerfile')]
            diagnostics['checks'].append({
                'name': 'docker',
                'status': 'ok' if dockerfiles else 'warning',
                'message': f'{len(dockerfiles)} Dockerfile(s) found'
            })
            
        # Check MATLAB scripts
        matlab_path = os.path.join(self.project_root, 'matlab_scripts')
        if os.path.exists(matlab_path):
            m_files = [f for f in os.listdir(matlab_path) if f.endswith('.m')]
            diagnostics['checks'].append({
                'name': 'matlab',
                'status': 'ok',
                'message': f'{len(m_files)} MATLAB script(s) found'
            })
            
        # Check Gazebo worlds
        gazebo_path = os.path.join(self.project_root, 'gazebo_worlds')
        if os.path.exists(gazebo_path):
            world_files = []
            for root, dirs, files in os.walk(gazebo_path):
                world_files.extend([f for f in files if f.endswith('.world')])
                
            diagnostics['checks'].append({
                'name': 'gazebo',
                'status': 'ok',
                'message': f'{len(world_files)} Gazebo world(s) found'
            })
            
        return diagnostics
        
    def chat(self, message):
        """Interactive chat for research assistance"""
        response = {
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'response': '',
            'suggestions': [],
            'actions': []
        }
        
        # Parse user intent
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['debug', 'fix', 'error', 'bug']):
            response['response'] = "I can help debug your code! Please provide the file path or paste the code you'd like me to analyze."
            
        elif any(word in message_lower for word in ['research', 'find', 'search']):
            topic = message_lower.replace('research', '').replace('find', '').replace('search', '').strip()
            response['response'] = f"I'll search for information about '{topic}' in the project and relevant literature."
            response['suggestions'] = self.knowledge_base.get(topic, [])
            
        elif any(word in message_lower for word in ['improve', 'optimize', 'better']):
            response['response'] = "I can suggest optimizations for your code. Which specific component would you like to improve?"
            response['suggestions'] = [
                'SNN Controller',
                'Chaos Monkey',
                'Quantum Map Merge',
                'ROS 2 Communication'
            ]
            
        elif any(word in message_lower for word in ['test', 'experiment', 'run']):
            response['response'] = "I can help set up experiments. What would you like to test?"
            response['suggestions'] = [
                'Run full simulation',
                'Test chaos monkey',
                'Benchmark SNN performance',
                'Test map merging'
            ]
            
        else:
            response['response'] = "I'm here to help with your Martian Swarm Quantum research project! I can assist with:"
            response['suggestions'] = [
                "Debugging code issues",
                "Researching topics",
                "Optimizing algorithms",
                "Running experiments",
                "Generating documentation",
                "Fixing bugs"
            ]
            
        self.conversation_history.append(response)
        return response


def main():
    """Main entry point for Research Rabbit"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    rabbit = ResearchRabbit(project_root)
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     🔬 Research Rabbit - Martian Swarm AI Assistant     ║
    ║                                                          ║
    ║  I help debug code, research topics, and optimize      ║
    ║  your experiments for the Martian Swarm Quantum project  ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'diagnostics':
            print("\n📊 Running project diagnostics...\n")
            results = rabbit.run_diagnostics()
            print(json.dumps(results, indent=2))
            
        elif command == 'analyze' and len(sys.argv) > 2:
            file_path = sys.argv[2]
            if not os.path.isabs(file_path):
                file_path = os.path.join(project_root, file_path)
            print(f"\n🔍 Analyzing {file_path}...\n")
            issues = rabbit.analyze_code(file_path)
            print(json.dumps(issues, indent=2))
            
        elif command == 'search' and len(sys.argv) > 2:
            query = sys.argv[2]
            print(f"\n🔎 Searching for: {query}...\n")
            results = rabbit.search_code(query)
            print(json.dumps(results, indent=2))
            
        else:
            print("Usage:")
            print("  python research_rabbit.py diagnostics")
            print("  python research_rabbit.py analyze <file>")
            print("  python research_rabbit.py search <query>")
    else:
        print("\nEnter your question or command:")
        user_input = input("> ")
        response = rabbit.chat(user_input)
        print(f"\n{response['response']}")
        if response['suggestions']:
            print("\nI can help with:")
            for s in response['suggestions']:
                print(f"  • {s}")


if __name__ == '__main__':
    main()
