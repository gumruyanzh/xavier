"""
Xavier Framework - Test-First Development Enforcement
Ensures 100% test coverage before allowing task completion
"""

import os
import subprocess
import json
import ast
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging


@dataclass
class TestCoverageReport:
    """Test coverage analysis report"""
    total_lines: int
    covered_lines: int
    coverage_percentage: float
    uncovered_lines: List[int]
    missing_tests: List[str]
    test_files: List[str]
    all_tests_pass: bool
    test_count: int
    failed_tests: List[str]


@dataclass
class CodeQualityReport:
    """Code quality analysis report"""
    clean_code_score: float
    violations: List[str]
    complexity_score: int
    maintainability_index: float
    duplicate_code_blocks: List[str]
    ioc_compliance: bool
    solid_principles_compliance: bool


class ITestRunner(ABC):
    """Interface for test runners"""

    @abstractmethod
    def run_tests(self, test_path: str) -> Tuple[bool, Dict[str, Any]]:
        """Run tests and return results"""
        pass

    @abstractmethod
    def get_coverage(self, source_path: str, test_path: str) -> TestCoverageReport:
        """Get test coverage report"""
        pass


class PythonTestRunner(ITestRunner):
    """Test runner for Python projects"""

    def __init__(self):
        self.logger = logging.getLogger("Xavier.TestRunner.Python")

    def run_tests(self, test_path: str) -> Tuple[bool, Dict[str, Any]]:
        """Run Python tests using pytest"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", test_path, "-v", "--json-report"],
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse test results
            all_passed = result.returncode == 0
            test_output = result.stdout

            # Extract test counts
            test_count = len(re.findall(r"PASSED|FAILED", test_output))
            failed_count = len(re.findall(r"FAILED", test_output))

            return all_passed, {
                "test_count": test_count,
                "passed_count": test_count - failed_count,
                "failed_count": failed_count,
                "output": test_output
            }

        except subprocess.TimeoutExpired:
            return False, {"error": "Tests timed out after 5 minutes"}
        except Exception as e:
            return False, {"error": str(e)}

    def get_coverage(self, source_path: str, test_path: str) -> TestCoverageReport:
        """Get Python test coverage using coverage.py"""
        try:
            # Run coverage
            subprocess.run(
                ["python", "-m", "coverage", "run", "-m", "pytest", test_path],
                capture_output=True,
                timeout=300
            )

            # Get coverage report
            result = subprocess.run(
                ["python", "-m", "coverage", "report", "--format=json"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)

                # Get uncovered lines
                uncovered_lines = []
                for file_data in coverage_data.get("files", {}).values():
                    uncovered_lines.extend(file_data.get("missing_lines", []))

                return TestCoverageReport(
                    total_lines=coverage_data.get("totals", {}).get("num_statements", 0),
                    covered_lines=coverage_data.get("totals", {}).get("covered_lines", 0),
                    coverage_percentage=total_coverage,
                    uncovered_lines=uncovered_lines,
                    missing_tests=[],
                    test_files=[test_path],
                    all_tests_pass=True,
                    test_count=0,
                    failed_tests=[]
                )

        except Exception as e:
            self.logger.error(f"Coverage analysis failed: {e}")

        return TestCoverageReport(
            total_lines=0,
            covered_lines=0,
            coverage_percentage=0,
            uncovered_lines=[],
            missing_tests=["Unable to analyze coverage"],
            test_files=[],
            all_tests_pass=False,
            test_count=0,
            failed_tests=[]
        )


class TypeScriptTestRunner(ITestRunner):
    """Test runner for TypeScript/JavaScript projects"""

    def __init__(self):
        self.logger = logging.getLogger("Xavier.TestRunner.TypeScript")

    def run_tests(self, test_path: str) -> Tuple[bool, Dict[str, Any]]:
        """Run TypeScript tests using Jest"""
        try:
            result = subprocess.run(
                ["npm", "test", "--", "--coverage", "--json"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(test_path),
                timeout=300
            )

            all_passed = result.returncode == 0

            # Try to parse JSON output
            try:
                test_results = json.loads(result.stdout)
                return all_passed, {
                    "test_count": test_results.get("numTotalTests", 0),
                    "passed_count": test_results.get("numPassedTests", 0),
                    "failed_count": test_results.get("numFailedTests", 0)
                }
            except:
                return all_passed, {"output": result.stdout}

        except Exception as e:
            return False, {"error": str(e)}

    def get_coverage(self, source_path: str, test_path: str) -> TestCoverageReport:
        """Get TypeScript test coverage using Jest"""
        try:
            result = subprocess.run(
                ["npm", "test", "--", "--coverage", "--coverageReporters=json"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(source_path),
                timeout=300
            )

            # Parse coverage report
            coverage_file = os.path.join(
                os.path.dirname(source_path),
                "coverage",
                "coverage-final.json"
            )

            if os.path.exists(coverage_file):
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)

                total_statements = 0
                covered_statements = 0

                for file_coverage in coverage_data.values():
                    statements = file_coverage.get("s", {})
                    total_statements += len(statements)
                    covered_statements += sum(1 for v in statements.values() if v > 0)

                coverage_percentage = (covered_statements / total_statements * 100) if total_statements > 0 else 0

                return TestCoverageReport(
                    total_lines=total_statements,
                    covered_lines=covered_statements,
                    coverage_percentage=coverage_percentage,
                    uncovered_lines=[],
                    missing_tests=[],
                    test_files=[test_path],
                    all_tests_pass=result.returncode == 0,
                    test_count=0,
                    failed_tests=[]
                )

        except Exception as e:
            self.logger.error(f"Coverage analysis failed: {e}")

        return TestCoverageReport(
            total_lines=0,
            covered_lines=0,
            coverage_percentage=0,
            uncovered_lines=[],
            missing_tests=["Unable to analyze coverage"],
            test_files=[],
            all_tests_pass=False,
            test_count=0,
            failed_tests=[]
        )


class GoTestRunner(ITestRunner):
    """Test runner for Go projects"""

    def __init__(self):
        self.logger = logging.getLogger("Xavier.TestRunner.Go")

    def run_tests(self, test_path: str) -> Tuple[bool, Dict[str, Any]]:
        """Run Go tests"""
        try:
            result = subprocess.run(
                ["go", "test", "-v", test_path],
                capture_output=True,
                text=True,
                timeout=300
            )

            all_passed = result.returncode == 0
            test_output = result.stdout

            # Parse test results
            passed_count = len(re.findall(r"--- PASS:", test_output))
            failed_count = len(re.findall(r"--- FAIL:", test_output))

            return all_passed, {
                "test_count": passed_count + failed_count,
                "passed_count": passed_count,
                "failed_count": failed_count,
                "output": test_output
            }

        except Exception as e:
            return False, {"error": str(e)}

    def get_coverage(self, source_path: str, test_path: str) -> TestCoverageReport:
        """Get Go test coverage"""
        try:
            result = subprocess.run(
                ["go", "test", "-cover", "-coverprofile=coverage.out", test_path],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                # Parse coverage percentage
                coverage_match = re.search(r"coverage: (\d+\.\d+)%", result.stdout)
                coverage_percentage = float(coverage_match.group(1)) if coverage_match else 0

                return TestCoverageReport(
                    total_lines=100,  # Go doesn't provide line counts easily
                    covered_lines=int(coverage_percentage),
                    coverage_percentage=coverage_percentage,
                    uncovered_lines=[],
                    missing_tests=[],
                    test_files=[test_path],
                    all_tests_pass=True,
                    test_count=0,
                    failed_tests=[]
                )

        except Exception as e:
            self.logger.error(f"Coverage analysis failed: {e}")

        return TestCoverageReport(
            total_lines=0,
            covered_lines=0,
            coverage_percentage=0,
            uncovered_lines=[],
            missing_tests=["Unable to analyze coverage"],
            test_files=[],
            all_tests_pass=False,
            test_count=0,
            failed_tests=[]
        )


class TestFirstEnforcer:
    """Enforces test-first development methodology"""

    def __init__(self):
        self.logger = logging.getLogger("Xavier.TestEnforcer")
        self.test_runners: Dict[str, ITestRunner] = {
            "python": PythonTestRunner(),
            "typescript": TypeScriptTestRunner(),
            "javascript": TypeScriptTestRunner(),
            "go": GoTestRunner()
        }

    def validate_tests_exist(self, source_file: str) -> Tuple[bool, List[str]]:
        """Validate that tests exist for source file"""
        errors = []

        # Determine test file path
        test_file = self._get_test_file_path(source_file)

        if not os.path.exists(test_file):
            errors.append(f"Test file not found: {test_file}")
            errors.append("Tests must be written before implementation (TDD)")
            return False, errors

        # Check test file is not empty
        with open(test_file, 'r') as f:
            content = f.read().strip()
            if len(content) < 100:
                errors.append("Test file appears to be empty or minimal")
                errors.append("Write comprehensive tests before implementation")
                return False, errors

        return True, []

    def validate_test_coverage(self, source_file: str, required_coverage: float = 100.0) -> Tuple[bool, TestCoverageReport]:
        """Validate test coverage meets requirements"""
        # Detect language
        language = self._detect_language(source_file)

        if language not in self.test_runners:
            self.logger.error(f"No test runner for language: {language}")
            return False, TestCoverageReport(
                total_lines=0,
                covered_lines=0,
                coverage_percentage=0,
                uncovered_lines=[],
                missing_tests=["No test runner available"],
                test_files=[],
                all_tests_pass=False,
                test_count=0,
                failed_tests=[]
            )

        # Get test file
        test_file = self._get_test_file_path(source_file)

        # Run tests
        runner = self.test_runners[language]
        tests_pass, test_results = runner.run_tests(test_file)

        if not tests_pass:
            return False, TestCoverageReport(
                total_lines=0,
                covered_lines=0,
                coverage_percentage=0,
                uncovered_lines=[],
                missing_tests=["Tests are failing"],
                test_files=[test_file],
                all_tests_pass=False,
                test_count=test_results.get("test_count", 0),
                failed_tests=["See test output for details"]
            )

        # Get coverage
        coverage_report = runner.get_coverage(source_file, test_file)

        # Validate coverage meets requirements
        if coverage_report.coverage_percentage < required_coverage:
            coverage_report.missing_tests.append(
                f"Coverage {coverage_report.coverage_percentage:.1f}% is below required {required_coverage}%"
            )
            return False, coverage_report

        return True, coverage_report

    def enforce_test_first(self, task_id: str, source_files: List[str]) -> Tuple[bool, Dict[str, Any]]:
        """Enforce test-first development for a task"""
        results = {
            "task_id": task_id,
            "files_checked": len(source_files),
            "all_tests_exist": True,
            "coverage_met": True,
            "details": []
        }

        for source_file in source_files:
            # Check tests exist
            tests_exist, errors = self.validate_tests_exist(source_file)
            if not tests_exist:
                results["all_tests_exist"] = False
                results["details"].append({
                    "file": source_file,
                    "error": "Tests not found",
                    "messages": errors
                })
                continue

            # Check coverage
            coverage_met, coverage_report = self.validate_test_coverage(source_file)
            if not coverage_met:
                results["coverage_met"] = False
                results["details"].append({
                    "file": source_file,
                    "error": "Coverage insufficient",
                    "coverage": coverage_report.coverage_percentage,
                    "required": 100.0,
                    "uncovered_lines": coverage_report.uncovered_lines
                })

        success = results["all_tests_exist"] and results["coverage_met"]
        return success, results

    def _get_test_file_path(self, source_file: str) -> str:
        """Get test file path for source file"""
        base_name = os.path.basename(source_file)
        dir_name = os.path.dirname(source_file)

        # Common test file patterns
        if source_file.endswith(".py"):
            return os.path.join(dir_name, "test_" + base_name)
        elif source_file.endswith(".go"):
            return source_file.replace(".go", "_test.go")
        elif source_file.endswith((".ts", ".tsx")):
            return source_file.replace(".ts", ".test.ts").replace(".tsx", ".test.tsx")
        elif source_file.endswith((".js", ".jsx")):
            return source_file.replace(".js", ".test.js").replace(".jsx", ".test.jsx")
        else:
            return os.path.join(dir_name, "test_" + base_name)

    def _detect_language(self, source_file: str) -> str:
        """Detect programming language from file extension"""
        ext = os.path.splitext(source_file)[1].lower()
        language_map = {
            ".py": "python",
            ".go": "go",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript"
        }
        return language_map.get(ext, "unknown")