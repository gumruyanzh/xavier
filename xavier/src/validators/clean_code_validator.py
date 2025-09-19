"""
Xavier Framework - Clean Code Validator
Enforces Clean Code principles and SOLID design patterns
"""

import ast
import re
import os
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging


@dataclass
class CleanCodeViolation:
    """Clean Code principle violation"""
    severity: str  # Critical, High, Medium, Low
    principle: str  # Which Clean Code principle
    file_path: str
    line_number: int
    message: str
    suggestion: str


@dataclass
class SOLIDViolation:
    """SOLID principle violation"""
    principle: str  # SRP, OCP, LSP, ISP, DIP
    file_path: str
    class_name: str
    message: str
    suggestion: str


@dataclass
class IoCPattern:
    """Inversion of Control pattern detection"""
    pattern_type: str  # DI, ServiceLocator, Factory, etc.
    implemented: bool
    location: str
    quality_score: float


class CleanCodeAnalyzer:
    """Analyzes code for Clean Code compliance"""

    def __init__(self):
        self.logger = logging.getLogger("Xavier.CleanCode")
        self.max_function_lines = 20
        self.max_class_lines = 200
        self.max_line_length = 120
        self.max_cyclomatic_complexity = 10
        self.max_function_parameters = 3
        self.max_class_methods = 10

    def analyze_file(self, file_path: str) -> List[CleanCodeViolation]:
        """Analyze a file for Clean Code violations"""
        violations = []

        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Check based on file type
        if file_path.endswith('.py'):
            violations.extend(self._analyze_python(content, lines, file_path))
        elif file_path.endswith(('.ts', '.js')):
            violations.extend(self._analyze_typescript(content, lines, file_path))
        elif file_path.endswith('.go'):
            violations.extend(self._analyze_go(content, lines, file_path))

        # Common checks
        violations.extend(self._check_line_length(lines, file_path))
        violations.extend(self._check_naming_conventions(content, file_path))
        violations.extend(self._check_comments(lines, file_path))
        violations.extend(self._check_duplication(lines, file_path))

        return violations

    def _analyze_python(self, content: str, lines: List[str], file_path: str) -> List[CleanCodeViolation]:
        """Python-specific Clean Code analysis"""
        violations = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check function length
                    function_lines = node.end_lineno - node.lineno
                    if function_lines > self.max_function_lines:
                        violations.append(CleanCodeViolation(
                            severity="High",
                            principle="Single Responsibility",
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Function '{node.name}' is {function_lines} lines long (max: {self.max_function_lines})",
                            suggestion=f"Break down '{node.name}' into smaller functions"
                        ))

                    # Check parameter count
                    param_count = len(node.args.args)
                    if param_count > self.max_function_parameters:
                        violations.append(CleanCodeViolation(
                            severity="Medium",
                            principle="Function Arguments",
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Function '{node.name}' has {param_count} parameters (max: {self.max_function_parameters})",
                            suggestion="Consider using a parameter object or builder pattern"
                        ))

                    # Check cyclomatic complexity
                    complexity = self._calculate_complexity(node)
                    if complexity > self.max_cyclomatic_complexity:
                        violations.append(CleanCodeViolation(
                            severity="High",
                            principle="Cyclomatic Complexity",
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Function '{node.name}' has complexity of {complexity} (max: {self.max_cyclomatic_complexity})",
                            suggestion="Reduce conditional logic and extract methods"
                        ))

                elif isinstance(node, ast.ClassDef):
                    # Check class size
                    class_lines = node.end_lineno - node.lineno
                    if class_lines > self.max_class_lines:
                        violations.append(CleanCodeViolation(
                            severity="High",
                            principle="Single Responsibility",
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Class '{node.name}' is {class_lines} lines long (max: {self.max_class_lines})",
                            suggestion=f"Split '{node.name}' into smaller, focused classes"
                        ))

                    # Check method count
                    method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                    if method_count > self.max_class_methods:
                        violations.append(CleanCodeViolation(
                            severity="Medium",
                            principle="Class Cohesion",
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Class '{node.name}' has {method_count} methods (max: {self.max_class_methods})",
                            suggestion="Consider splitting responsibilities into multiple classes"
                        ))

        except SyntaxError as e:
            self.logger.error(f"Syntax error in {file_path}: {e}")

        return violations

    def _analyze_typescript(self, content: str, lines: List[str], file_path: str) -> List[CleanCodeViolation]:
        """TypeScript/JavaScript Clean Code analysis"""
        violations = []

        # Function length check
        function_pattern = r'(function\s+\w+|const\s+\w+\s*=\s*\(.*?\)\s*=>|\w+\s*\(.*?\)\s*\{)'
        in_function = False
        function_start = 0
        function_name = ""
        brace_count = 0

        for i, line in enumerate(lines, 1):
            if not in_function:
                match = re.search(function_pattern, line)
                if match:
                    in_function = True
                    function_start = i
                    function_name = match.group(0).split('(')[0].strip()
                    brace_count = line.count('{') - line.count('}')
            else:
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    function_lines = i - function_start
                    if function_lines > self.max_function_lines:
                        violations.append(CleanCodeViolation(
                            severity="High",
                            principle="Single Responsibility",
                            file_path=file_path,
                            line_number=function_start,
                            message=f"Function at line {function_start} is {function_lines} lines long",
                            suggestion="Break down into smaller functions"
                        ))
                    in_function = False

        # Check for any/unknown types (TypeScript)
        if file_path.endswith('.ts') or file_path.endswith('.tsx'):
            any_count = content.count(': any')
            if any_count > 0:
                violations.append(CleanCodeViolation(
                    severity="Medium",
                    principle="Type Safety",
                    file_path=file_path,
                    line_number=0,
                    message=f"Found {any_count} uses of 'any' type",
                    suggestion="Use specific types instead of 'any'"
                ))

        return violations

    def _analyze_go(self, content: str, lines: List[str], file_path: str) -> List[CleanCodeViolation]:
        """Go-specific Clean Code analysis"""
        violations = []

        # Function length check
        function_pattern = r'func\s+(\w+|\(\w+\s+\*?\w+\)\s+\w+)\s*\('
        in_function = False
        function_start = 0
        function_name = ""
        brace_count = 0

        for i, line in enumerate(lines, 1):
            if not in_function:
                match = re.search(function_pattern, line)
                if match:
                    in_function = True
                    function_start = i
                    function_name = match.group(1)
                    brace_count = line.count('{') - line.count('}')
            else:
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    function_lines = i - function_start
                    if function_lines > self.max_function_lines:
                        violations.append(CleanCodeViolation(
                            severity="High",
                            principle="Single Responsibility",
                            file_path=file_path,
                            line_number=function_start,
                            message=f"Function '{function_name}' is {function_lines} lines long",
                            suggestion="Break down into smaller functions"
                        ))
                    in_function = False

        # Check for proper error handling
        if 'panic(' in content and 'recover()' not in content:
            violations.append(CleanCodeViolation(
                severity="High",
                principle="Error Handling",
                file_path=file_path,
                line_number=0,
                message="Using panic without recover",
                suggestion="Handle errors explicitly instead of panicking"
            ))

        return violations

    def _check_line_length(self, lines: List[str], file_path: str) -> List[CleanCodeViolation]:
        """Check for lines that are too long"""
        violations = []

        for i, line in enumerate(lines, 1):
            if len(line) > self.max_line_length:
                violations.append(CleanCodeViolation(
                    severity="Low",
                    principle="Readability",
                    file_path=file_path,
                    line_number=i,
                    message=f"Line is {len(line)} characters (max: {self.max_line_length})",
                    suggestion="Break long lines for better readability"
                ))

        return violations

    def _check_naming_conventions(self, content: str, file_path: str) -> List[CleanCodeViolation]:
        """Check variable and function naming"""
        violations = []

        # Check for single-letter variables (except common ones like i, j, k in loops)
        single_letter_pattern = r'\b([a-z])\b(?!\s*(?:in|for|range))'
        matches = re.findall(single_letter_pattern, content)

        # Filter out common acceptable single letters
        acceptable = {'i', 'j', 'k', 'n', 'x', 'y', 'z'}
        bad_names = [m for m in matches if m not in acceptable]

        if len(bad_names) > 5:
            violations.append(CleanCodeViolation(
                severity="Medium",
                principle="Meaningful Names",
                file_path=file_path,
                line_number=0,
                message=f"Found {len(bad_names)} single-letter variable names",
                suggestion="Use descriptive variable names"
            ))

        # Check for abbreviations
        common_abbreviations = ['tmp', 'temp', 'val', 'num', 'str', 'obj', 'arr']
        for abbr in common_abbreviations:
            if re.search(rf'\b{abbr}\d*\b', content, re.IGNORECASE):
                violations.append(CleanCodeViolation(
                    severity="Low",
                    principle="Meaningful Names",
                    file_path=file_path,
                    line_number=0,
                    message=f"Found abbreviation '{abbr}' in variable names",
                    suggestion="Use full, descriptive names instead of abbreviations"
                ))
                break

        return violations

    def _check_comments(self, lines: List[str], file_path: str) -> List[CleanCodeViolation]:
        """Check for code smell in comments"""
        violations = []

        todo_count = 0
        fixme_count = 0
        commented_code_lines = 0

        for i, line in enumerate(lines, 1):
            # Check for TODO/FIXME comments
            if 'TODO' in line or 'FIXME' in line:
                todo_count += 1

            # Check for commented-out code
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                # Heuristic: if it contains common code patterns, it's likely commented code
                if any(pattern in stripped for pattern in ['=', '(', ')', '{', '}', 'if ', 'for ', 'while ', 'def ', 'function ']):
                    commented_code_lines += 1

        if todo_count > 3:
            violations.append(CleanCodeViolation(
                severity="Low",
                principle="Comments",
                file_path=file_path,
                line_number=0,
                message=f"Found {todo_count} TODO/FIXME comments",
                suggestion="Address TODOs or move them to issue tracker"
            ))

        if commented_code_lines > 10:
            violations.append(CleanCodeViolation(
                severity="Medium",
                principle="Comments",
                file_path=file_path,
                line_number=0,
                message=f"Found {commented_code_lines} lines of commented-out code",
                suggestion="Remove commented-out code (use version control instead)"
            ))

        return violations

    def _check_duplication(self, lines: List[str], file_path: str) -> List[CleanCodeViolation]:
        """Check for code duplication"""
        violations = []

        # Simple duplication detection: find repeated blocks
        block_size = 5
        seen_blocks = {}

        for i in range(len(lines) - block_size):
            block = tuple(lines[i:i+block_size])
            block_str = '\n'.join(block).strip()

            # Skip empty or trivial blocks
            if len(block_str) < 50:
                continue

            if block in seen_blocks:
                violations.append(CleanCodeViolation(
                    severity="High",
                    principle="DRY (Don't Repeat Yourself)",
                    file_path=file_path,
                    line_number=i+1,
                    message=f"Duplicate code block detected (lines {i+1}-{i+block_size})",
                    suggestion="Extract duplicate code into a reusable function"
                ))
                break  # Only report first duplication
            else:
                seen_blocks[block] = i

        return violations

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity


class SOLIDValidator:
    """Validates SOLID principles compliance"""

    def __init__(self):
        self.logger = logging.getLogger("Xavier.SOLID")

    def validate_file(self, file_path: str) -> List[SOLIDViolation]:
        """Validate SOLID principles in a file"""
        violations = []

        with open(file_path, 'r') as f:
            content = f.read()

        if file_path.endswith('.py'):
            violations.extend(self._validate_python_solid(content, file_path))
        elif file_path.endswith(('.ts', '.tsx')):
            violations.extend(self._validate_typescript_solid(content, file_path))
        elif file_path.endswith('.go'):
            violations.extend(self._validate_go_solid(content, file_path))

        return violations

    def _validate_python_solid(self, content: str, file_path: str) -> List[SOLIDViolation]:
        """Validate SOLID principles in Python code"""
        violations = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Single Responsibility Principle
                    public_methods = [n for n in node.body
                                    if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')]

                    if len(public_methods) > 7:
                        violations.append(SOLIDViolation(
                            principle="SRP",
                            file_path=file_path,
                            class_name=node.name,
                            message=f"Class '{node.name}' has {len(public_methods)} public methods",
                            suggestion="Split into smaller classes with single responsibilities"
                        ))

                    # Interface Segregation Principle
                    abstract_methods = [n for n in node.body
                                       if isinstance(n, ast.FunctionDef) and self._is_abstract(n)]

                    if len(abstract_methods) > 5:
                        violations.append(SOLIDViolation(
                            principle="ISP",
                            file_path=file_path,
                            class_name=node.name,
                            message=f"Interface '{node.name}' has {len(abstract_methods)} abstract methods",
                            suggestion="Split into smaller, more focused interfaces"
                        ))

                    # Dependency Inversion Principle
                    if self._has_concrete_dependencies(node):
                        violations.append(SOLIDViolation(
                            principle="DIP",
                            file_path=file_path,
                            class_name=node.name,
                            message=f"Class '{node.name}' depends on concrete implementations",
                            suggestion="Depend on abstractions, not concretions"
                        ))

        except SyntaxError:
            pass

        return violations

    def _validate_typescript_solid(self, content: str, file_path: str) -> List[SOLIDViolation]:
        """Validate SOLID principles in TypeScript code"""
        violations = []

        # Check for large interfaces
        interface_pattern = r'interface\s+(\w+)\s*\{([^}]+)\}'
        interfaces = re.findall(interface_pattern, content, re.DOTALL)

        for interface_name, interface_body in interfaces:
            method_count = len(re.findall(r'\w+\s*\([^)]*\)\s*:', interface_body))
            if method_count > 5:
                violations.append(SOLIDViolation(
                    principle="ISP",
                    file_path=file_path,
                    class_name=interface_name,
                    message=f"Interface '{interface_name}' has {method_count} methods",
                    suggestion="Split into smaller, role-specific interfaces"
                ))

        # Check for concrete dependencies
        if 'new ' in content and 'implements' in content:
            violations.append(SOLIDViolation(
                principle="DIP",
                file_path=file_path,
                class_name="",
                message="Found direct instantiation with 'new' keyword",
                suggestion="Use dependency injection or factory patterns"
            ))

        return violations

    def _validate_go_solid(self, content: str, file_path: str) -> List[SOLIDViolation]:
        """Validate SOLID principles in Go code"""
        violations = []

        # Check for large interfaces
        interface_pattern = r'type\s+(\w+)\s+interface\s*\{([^}]+)\}'
        interfaces = re.findall(interface_pattern, content, re.DOTALL)

        for interface_name, interface_body in interfaces:
            method_count = len(interface_body.strip().split('\n'))
            if method_count > 3:  # Go interfaces should be small
                violations.append(SOLIDViolation(
                    principle="ISP",
                    file_path=file_path,
                    class_name=interface_name,
                    message=f"Interface '{interface_name}' has {method_count} methods",
                    suggestion="Go interfaces should be small (1-3 methods)"
                ))

        # Check for struct with too many fields (SRP violation)
        struct_pattern = r'type\s+(\w+)\s+struct\s*\{([^}]+)\}'
        structs = re.findall(struct_pattern, content, re.DOTALL)

        for struct_name, struct_body in structs:
            field_count = len([line for line in struct_body.split('\n') if line.strip()])
            if field_count > 10:
                violations.append(SOLIDViolation(
                    principle="SRP",
                    file_path=file_path,
                    class_name=struct_name,
                    message=f"Struct '{struct_name}' has {field_count} fields",
                    suggestion="Consider splitting into smaller, focused structs"
                ))

        return violations

    def _is_abstract(self, node: ast.FunctionDef) -> bool:
        """Check if a method is abstract"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                return True
        return len(node.body) == 1 and isinstance(node.body[0], ast.Pass)

    def _has_concrete_dependencies(self, node: ast.ClassDef) -> bool:
        """Check if class has concrete dependencies"""
        for method in node.body:
            if isinstance(method, ast.FunctionDef) and method.name == '__init__':
                for stmt in method.body:
                    if isinstance(stmt, ast.Assign):
                        if isinstance(stmt.value, ast.Call):
                            if isinstance(stmt.value.func, ast.Name):
                                # Check if it's instantiating a concrete class
                                class_name = stmt.value.func.id
                                if class_name[0].isupper():  # Likely a class
                                    return True
        return False


class IoCValidator:
    """Validates Inversion of Control patterns"""

    def __init__(self):
        self.logger = logging.getLogger("Xavier.IoC")

    def analyze_project(self, project_path: str) -> List[IoCPattern]:
        """Analyze project for IoC patterns"""
        patterns = []

        # Look for dependency injection containers
        di_patterns = [
            'DependencyInjector',
            'ServiceContainer',
            'InjectionContainer',
            'DIContainer',
            'resolve',
            'inject',
            'provider'
        ]

        # Look for factory patterns
        factory_patterns = [
            'Factory',
            'Builder',
            'create',
            'make',
            'build'
        ]

        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith(('.py', '.ts', '.go', '.java')):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Check for DI patterns
                    for pattern in di_patterns:
                        if pattern in content:
                            patterns.append(IoCPattern(
                                pattern_type="Dependency Injection",
                                implemented=True,
                                location=file_path,
                                quality_score=0.8
                            ))
                            break

                    # Check for factory patterns
                    for pattern in factory_patterns:
                        if re.search(rf'class\s+\w*{pattern}', content, re.IGNORECASE):
                            patterns.append(IoCPattern(
                                pattern_type="Factory",
                                implemented=True,
                                location=file_path,
                                quality_score=0.7
                            ))
                            break

        # If no IoC patterns found
        if not patterns:
            patterns.append(IoCPattern(
                pattern_type="None",
                implemented=False,
                location="",
                quality_score=0.0
            ))

        return patterns


class EnterpriseCodeValidator:
    """Main validator for enterprise-grade code quality"""

    def __init__(self):
        self.clean_code = CleanCodeAnalyzer()
        self.solid = SOLIDValidator()
        self.ioc = IoCValidator()
        self.logger = logging.getLogger("Xavier.EnterpriseValidator")

    def validate_file(self, file_path: str) -> CodeQualityReport:
        """Comprehensive validation of a single file"""
        # Clean Code violations
        clean_violations = self.clean_code.analyze_file(file_path)

        # SOLID violations
        solid_violations = self.solid.validate_file(file_path)

        # Calculate scores
        clean_code_score = max(0, 100 - len(clean_violations) * 5)
        solid_score = max(0, 100 - len(solid_violations) * 10)

        # Combine violations
        all_violations = []
        all_violations.extend([v.message for v in clean_violations])
        all_violations.extend([v.message for v in solid_violations])

        return CodeQualityReport(
            clean_code_score=clean_code_score,
            violations=all_violations,
            complexity_score=self._calculate_overall_complexity(file_path),
            maintainability_index=(clean_code_score + solid_score) / 2,
            duplicate_code_blocks=[],
            ioc_compliance=False,  # Will be determined at project level
            solid_principles_compliance=len(solid_violations) == 0
        )

    def validate_project(self, project_path: str) -> Dict[str, Any]:
        """Validate entire project"""
        report = {
            "total_files": 0,
            "average_clean_code_score": 0,
            "solid_compliant": True,
            "ioc_patterns": [],
            "critical_violations": [],
            "suggestions": []
        }

        scores = []
        all_violations = []

        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith(('.py', '.ts', '.go', '.java')):
                    file_path = os.path.join(root, file)
                    file_report = self.validate_file(file_path)

                    report["total_files"] += 1
                    scores.append(file_report.clean_code_score)

                    if not file_report.solid_principles_compliance:
                        report["solid_compliant"] = False

                    # Collect critical violations
                    for violation in file_report.violations:
                        if "Critical" in violation or "High" in violation:
                            all_violations.append({
                                "file": file_path,
                                "violation": violation
                            })

        # Calculate averages
        if scores:
            report["average_clean_code_score"] = sum(scores) / len(scores)

        # Check IoC patterns
        ioc_patterns = self.ioc.analyze_project(project_path)
        report["ioc_patterns"] = [asdict(p) for p in ioc_patterns]

        # Add top violations
        report["critical_violations"] = all_violations[:10]

        # Generate suggestions
        if report["average_clean_code_score"] < 70:
            report["suggestions"].append("Focus on reducing function complexity and length")

        if not report["solid_compliant"]:
            report["suggestions"].append("Refactor to follow SOLID principles")

        if not any(p.implemented for p in ioc_patterns):
            report["suggestions"].append("Implement dependency injection for better testability")

        return report

    def _calculate_overall_complexity(self, file_path: str) -> int:
        """Calculate overall complexity score"""
        # Simplified complexity calculation
        with open(file_path, 'r') as f:
            content = f.read()

        # Count decision points
        decision_keywords = ['if', 'else', 'elif', 'for', 'while', 'switch', 'case']
        complexity = 1

        for keyword in decision_keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', content))

        return min(complexity, 100)  # Cap at 100