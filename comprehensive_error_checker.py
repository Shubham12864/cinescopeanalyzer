#!/usr/bin/env python3
"""
Comprehensive Error Checker for CineScopeAnalyzer
This script checks for potential issues across the entire codebase.
"""

import os
import sys
import subprocess
import json
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class CineScopeErrorChecker:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_root = self.project_root / "backend"
        self.frontend_root = self.project_root / "frontend"
        self.errors = []
        self.warnings = []
        self.success_count = 0
        
    def log_error(self, category: str, message: str, file_path: str = ""):
        """Log an error with category and file information"""
        error_msg = f"[{category}] {message}"
        if file_path:
            error_msg += f" in {file_path}"
        self.errors.append(error_msg)
        logger.error(error_msg)
        
    def log_warning(self, category: str, message: str, file_path: str = ""):
        """Log a warning with category and file information"""
        warning_msg = f"[{category}] {message}"
        if file_path:
            warning_msg += f" in {file_path}"
        self.warnings.append(warning_msg)
        logger.warning(warning_msg)
        
    def log_success(self, message: str):
        """Log a successful check"""
        self.success_count += 1
        logger.info(f"✅ {message}")

    def check_python_syntax(self) -> None:
        """Check Python syntax errors in backend"""
        logger.info("🐍 Checking Python syntax...")
        
        python_files = list(self.backend_root.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                    
                # Check syntax
                ast.parse(source)
                
                # Check for common issues
                if 'import *' in source:
                    self.log_warning("PYTHON", "Wildcard import found", str(py_file))
                    
                if 'print(' in source and 'test' not in str(py_file).lower():
                    self.log_warning("PYTHON", "Print statement in production code", str(py_file))
                    
            except SyntaxError as e:
                self.log_error("PYTHON_SYNTAX", f"Syntax error: {e}", str(py_file))
            except Exception as e:
                self.log_warning("PYTHON", f"Could not parse file: {e}", str(py_file))
                
        self.log_success(f"Checked {len(python_files)} Python files for syntax")

    def check_imports(self) -> None:
        """Check for import issues"""
        logger.info("📦 Checking Python imports...")
        
        python_files = list(self.backend_root.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for relative import issues
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    if line.startswith('from .') or line.startswith('import .'):
                        # Check if it's in the right structure
                        relative_parts = line.count('.')
                        if relative_parts > 3:
                            self.log_warning("IMPORTS", f"Deep relative import on line {i}: {line}", str(py_file))
                            
                    if 'from typing import' in line and len(line) > 80:
                        self.log_warning("IMPORTS", f"Long typing import on line {i}", str(py_file))
                        
            except Exception as e:
                self.log_warning("IMPORTS", f"Could not check imports: {e}", str(py_file))
                
        self.log_success("Import structure checked")

    def check_environment_files(self) -> None:
        """Check for required environment files"""
        logger.info("🌍 Checking environment configuration...")
        
        required_files = [
            "backend/.env.example",
            "backend/requirements.txt",
            "frontend/package.json",
            "frontend/next.config.mjs"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.log_error("CONFIG", f"Missing required file: {file_path}")
            else:
                self.log_success(f"Found {file_path}")

    def check_docker_files(self) -> None:
        """Check Docker configuration"""
        logger.info("🐳 Checking Docker configuration...")
        
        docker_files = [
            "backend/Dockerfile",
            "frontend/Dockerfile", 
            "docker-compose.yml"
        ]
        
        for docker_file in docker_files:
            full_path = self.project_root / docker_file
            if full_path.exists():
                self.log_success(f"Found {docker_file}")
                
                # Basic Docker file validation
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        if 'FROM' not in content:
                            self.log_error("DOCKER", f"Invalid Dockerfile - no FROM statement", docker_file)
                        if 'backend/Dockerfile' in docker_file and 'python' not in content.lower():
                            self.log_warning("DOCKER", "Backend Dockerfile might not use Python", docker_file)
                except Exception as e:
                    self.log_warning("DOCKER", f"Could not validate {docker_file}: {e}")
            else:
                self.log_warning("DOCKER", f"Missing Docker file: {docker_file}")

    def check_api_endpoints(self) -> None:
        """Check API endpoint definitions"""
        logger.info("🌐 Checking API endpoints...")
        
        routes_dir = self.backend_root / "app" / "api" / "routes"
        if not routes_dir.exists():
            self.log_error("API", "API routes directory not found")
            return
            
        route_files = list(routes_dir.glob("*.py"))
        endpoints_found = []
        
        for route_file in route_files:
            try:
                with open(route_file, 'r') as f:
                    content = f.read()
                    
                # Look for FastAPI route decorators
                routes = re.findall(r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content)
                for method, path in routes:
                    endpoints_found.append(f"{method.upper()} {path}")
                    
            except Exception as e:
                self.log_warning("API", f"Could not check routes in {route_file}: {e}")
                
        if endpoints_found:
            self.log_success(f"Found {len(endpoints_found)} API endpoints")
            for endpoint in endpoints_found[:5]:  # Show first 5
                logger.info(f"  📍 {endpoint}")
        else:
            self.log_error("API", "No API endpoints found")

    def check_frontend_files(self) -> None:
        """Check frontend TypeScript/React files"""
        logger.info("⚛️ Checking frontend files...")
        
        if not self.frontend_root.exists():
            self.log_error("FRONTEND", "Frontend directory not found")
            return
            
        # Check for required frontend files
        required_frontend_files = [
            "app/page.tsx",
            "app/layout.tsx",
            "components.json",
            "tailwind.config.js"
        ]
        
        for file_path in required_frontend_files:
            full_path = self.frontend_root / file_path
            if full_path.exists():
                self.log_success(f"Found frontend/{file_path}")
            else:
                self.log_error("FRONTEND", f"Missing frontend file: {file_path}")
                
        # Check for TypeScript files
        tsx_files = list(self.frontend_root.rglob("*.tsx"))
        ts_files = list(self.frontend_root.rglob("*.ts"))
        
        if tsx_files or ts_files:
            self.log_success(f"Found {len(tsx_files)} .tsx and {len(ts_files)} .ts files")
        else:
            self.log_error("FRONTEND", "No TypeScript files found")

    def check_package_dependencies(self) -> None:
        """Check package dependencies"""
        logger.info("📋 Checking package dependencies...")
        
        # Check Python requirements
        requirements_file = self.backend_root / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    requirements = f.read()
                    
                required_packages = ['fastapi', 'pydantic', 'aiohttp']
                for package in required_packages:
                    if package in requirements:
                        self.log_success(f"Found {package} in requirements.txt")
                    else:
                        self.log_warning("DEPENDENCIES", f"Missing {package} in requirements.txt")
                        
            except Exception as e:
                self.log_warning("DEPENDENCIES", f"Could not check requirements.txt: {e}")
        
        # Check Node.js dependencies
        package_json = self.frontend_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                    
                dependencies = package_data.get('dependencies', {})
                required_frontend_packages = ['next', 'react', 'tailwindcss']
                
                for package in required_frontend_packages:
                    if package in dependencies:
                        self.log_success(f"Found {package} in package.json")
                    else:
                        self.log_warning("DEPENDENCIES", f"Missing {package} in package.json")
                        
            except Exception as e:
                self.log_warning("DEPENDENCIES", f"Could not check package.json: {e}")

    def check_security_issues(self) -> None:
        """Check for common security issues"""
        logger.info("🔒 Checking security issues...")
        
        # Check for hardcoded secrets
        all_files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.ts")) + list(self.project_root.rglob("*.tsx"))
        
        secret_patterns = [
            (r'api_key\s*=\s*["\'][^"\']+["\']', "API key"),
            (r'password\s*=\s*["\'][^"\']+["\']', "Password"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Secret"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Token")
        ]
        
        for file_path in all_files:
            if '.git' in str(file_path) or 'node_modules' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern, secret_type in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if 'demo' not in match.lower() and 'example' not in match.lower():
                            self.log_warning("SECURITY", f"Potential hardcoded {secret_type}: {match}", str(file_path))
                            
            except Exception as e:
                # Skip binary files or files with encoding issues
                continue
                
        self.log_success("Security scan completed")

    def check_file_permissions(self) -> None:
        """Check file permissions"""
        logger.info("🔐 Checking file permissions...")
        
        script_files = list(self.project_root.rglob("*.sh")) + list(self.project_root.rglob("*.bat"))
        
        for script_file in script_files:
            # Check if executable (Unix-like systems)
            if hasattr(os, 'access') and not os.access(script_file, os.X_OK):
                self.log_warning("PERMISSIONS", f"Script file not executable: {script_file}")
            else:
                self.log_success(f"Script file permissions OK: {script_file.name}")

    def check_api_connectivity(self) -> None:
        """Check if APIs are properly configured"""
        logger.info("🔌 Checking API configuration...")
        
        api_config_files = [
            self.backend_root / "app" / "core" / "omdb_api.py",
            self.backend_root / "app" / "core" / "tmdb_api.py"
        ]
        
        for api_file in api_config_files:
            if api_file.exists():
                self.log_success(f"Found API configuration: {api_file.name}")
                
                try:
                    with open(api_file, 'r') as f:
                        content = f.read()
                        
                    if 'api_key' in content or 'API_KEY' in content:
                        self.log_success(f"API key configuration found in {api_file.name}")
                    else:
                        self.log_warning("API", f"No API key configuration in {api_file.name}")
                        
                except Exception as e:
                    self.log_warning("API", f"Could not check {api_file}: {e}")
            else:
                self.log_error("API", f"Missing API configuration file: {api_file}")

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all error checks"""
        logger.info("🚀 Starting comprehensive error check...")
        
        # Run all checks
        self.check_python_syntax()
        self.check_imports()
        self.check_environment_files()
        self.check_docker_files()
        self.check_api_endpoints()
        self.check_frontend_files()
        self.check_package_dependencies()
        self.check_security_issues()
        self.check_file_permissions()
        self.check_api_connectivity()
        
        # Generate summary
        total_issues = len(self.errors) + len(self.warnings)
        
        summary = {
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "successes": self.success_count,
            "total_issues": total_issues,
            "status": "PASS" if len(self.errors) == 0 else "FAIL",
            "details": {
                "errors": self.errors,
                "warnings": self.warnings
            }
        }
        
        return summary

    def print_summary(self, summary: Dict[str, Any]) -> None:
        """Print a formatted summary"""
        print("\n" + "="*60)
        print("📊 CINESCOPEANALYZER ERROR CHECK SUMMARY")
        print("="*60)
        
        status_emoji = "✅" if summary["status"] == "PASS" else "❌"
        print(f"{status_emoji} Status: {summary['status']}")
        print(f"✅ Successes: {summary['successes']}")
        print(f"⚠️  Warnings: {summary['warnings']}")
        print(f"❌ Errors: {summary['errors']}")
        print(f"📈 Total Issues: {summary['total_issues']}")
        
        if summary["errors"]:
            print("\n🔴 ERRORS:")
            for error in summary["details"]["errors"]:
                print(f"  ❌ {error}")
                
        if summary["warnings"]:
            print("\n🟡 WARNINGS:")
            for warning in summary["details"]["warnings"][:10]:  # Show first 10
                print(f"  ⚠️  {warning}")
                
            if len(summary["details"]["warnings"]) > 10:
                print(f"  ... and {len(summary['details']['warnings']) - 10} more warnings")
        
        print("\n" + "="*60)
        
        if summary["status"] == "PASS":
            print("🎉 All checks passed! Your CineScopeAnalyzer is ready for deployment!")
        else:
            print("🔧 Please fix the errors above before deployment.")
        
        print("="*60)

def main():
    """Main function"""
    # Get project root (assuming script is in project root)
    project_root = Path(__file__).parent
    
    # Check if we're in the right directory
    if not (project_root / "backend").exists() or not (project_root / "frontend").exists():
        print("❌ Error: This script must be run from the CineScopeAnalyzer project root!")
        print("Current directory:", project_root)
        sys.exit(1)
    
    # Run error checker
    checker = CineScopeErrorChecker(str(project_root))
    summary = checker.run_all_checks()
    
    # Print summary
    checker.print_summary(summary)
    
    # Save detailed report
    report_file = project_root / "error_check_report.json"
    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if summary["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
