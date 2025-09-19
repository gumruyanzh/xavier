"""
Xavier Framework - Intelligent Project Analyzer
Analyzes project descriptions to suggest tech stacks and generate initial stories
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ProjectAnalysis:
    """Result of project analysis"""
    project_type: str
    suggested_tech_stack: Dict[str, Any]
    detected_features: List[str]
    performance_requirements: List[str]
    suggested_stories: List[Dict[str, Any]]
    suggested_epics: List[Dict[str, Any]]
    estimated_complexity: str  # Small, Medium, Large, Enterprise


class ProjectAnalyzer:
    """Analyzes project descriptions to make intelligent suggestions"""

    def __init__(self):
        self.feature_patterns = self._init_feature_patterns()
        self.tech_suggestions = self._init_tech_suggestions()

    def _init_feature_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for feature detection"""
        return {
            "authentication": [
                r"\bauth\w*\b", r"\blogin\b", r"\bsign\s*up\b", r"\bregist\w*\b",
                r"\bpassword\b", r"\boauth\b", r"\bjwt\b", r"\bsso\b"
            ],
            "payment": [
                r"\bpayment\b", r"\bstripe\b", r"\bpaypal\b", r"\bcheckout\b",
                r"\bbilling\b", r"\bsubscription\b", r"\bprice\b", r"\bcart\b"
            ],
            "database": [
                r"\bdata\s*base\b", r"\bpostgres\b", r"\bmysql\b", r"\bmongo\b",
                r"\bsql\b", r"\bnosql\b", r"\bredis\b", r"\bcache\b"
            ],
            "api": [
                r"\bapi\b", r"\brest\b", r"\bgraphql\b", r"\bendpoint\b",
                r"\bwebhook\b", r"\bintegration\b", r"\bmicroservice\b"
            ],
            "real_time": [
                r"\breal\s*time\b", r"\bwebsocket\b", r"\bchat\b", r"\bnotification\b",
                r"\blive\b", r"\bstream\b", r"\bpush\b"
            ],
            "admin": [
                r"\badmin\b", r"\bdashboard\b", r"\banalytics\b", r"\breport\b",
                r"\bmanagement\b", r"\bCMS\b", r"\bback\s*office\b"
            ],
            "mobile": [
                r"\bmobile\b", r"\bandroid\b", r"\bios\b", r"\bresponsive\b",
                r"\bapp\b", r"\breact\s*native\b", r"\bflutter\b"
            ],
            "search": [
                r"\bsearch\b", r"\bfilter\b", r"\belastic\b", r"\bsolr\b",
                r"\bindex\b", r"\bquery\b", r"\bfull\s*text\b"
            ],
            "file_handling": [
                r"\bupload\b", r"\bfile\b", r"\bimage\b", r"\bvideo\b",
                r"\bs3\b", r"\bstorage\b", r"\bmedia\b", r"\bcdn\b"
            ],
            "email": [
                r"\bemail\b", r"\bmail\b", r"\bsmtp\b", r"\bsendgrid\b",
                r"\bnewsletter\b", r"\bnotif\w*\b"
            ],
            "social": [
                r"\bsocial\b", r"\bshare\b", r"\blike\b", r"\bcomment\b",
                r"\bfollow\b", r"\bfriend\b", r"\bprofile\b", r"\bfeed\b"
            ],
            "ecommerce": [
                r"\becommerce\b", r"\bshop\b", r"\bproduct\b", r"\bcatalog\b",
                r"\border\b", r"\binventory\b", r"\bvendor\b", r"\bmerchant\b"
            ],
            "blog": [
                r"\bblog\b", r"\bpost\b", r"\barticle\b", r"\bcontent\b",
                r"\bpublish\b", r"\beditor\b", r"\bmarkdown\b"
            ],
            "security": [
                r"\bsecurity\b", r"\bencrypt\b", r"\b2fa\b", r"\bpermission\b",
                r"\brole\b", r"\baccess\s*control\b", r"\brbac\b"
            ]
        }

    def _init_tech_suggestions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize technology suggestions based on requirements"""
        return {
            "high_performance": {
                "backend": ["Go", "Rust", "C++"],
                "database": ["PostgreSQL", "ScyllaDB", "Redis"],
                "cache": ["Redis", "Memcached"]
            },
            "rapid_development": {
                "backend": ["Python/FastAPI", "Node.js/Express", "Ruby on Rails"],
                "frontend": ["React", "Vue.js"],
                "database": ["PostgreSQL", "MongoDB"]
            },
            "enterprise": {
                "backend": ["Java/Spring", "C#/.NET", "Python/Django"],
                "frontend": ["Angular", "React"],
                "database": ["Oracle", "PostgreSQL", "SQL Server"]
            },
            "startup": {
                "backend": ["Python/FastAPI", "Node.js", "Go"],
                "frontend": ["React", "Vue.js", "Next.js"],
                "database": ["PostgreSQL", "MongoDB"],
                "deployment": ["Docker", "Kubernetes", "Vercel"]
            },
            "microservices": {
                "backend": ["Go", "Node.js", "Python/FastAPI"],
                "messaging": ["RabbitMQ", "Kafka", "Redis Streams"],
                "database": ["PostgreSQL", "MongoDB", "Cassandra"],
                "orchestration": ["Kubernetes", "Docker Swarm"]
            }
        }

    def analyze(self, project_name: str, description: str,
                tech_stack: Optional[Dict[str, Any]] = None) -> ProjectAnalysis:
        """
        Analyze project description and generate recommendations

        Args:
            project_name: Name of the project
            description: Detailed project description
            tech_stack: Optional pre-defined tech stack

        Returns:
            ProjectAnalysis with recommendations
        """
        # Detect features
        detected_features = self._detect_features(description)

        # Determine project type
        project_type = self._determine_project_type(detected_features, description)

        # Detect performance requirements
        performance_reqs = self._detect_performance_requirements(description)

        # Suggest or validate tech stack
        if tech_stack:
            suggested_stack = self._validate_and_enhance_tech_stack(
                tech_stack, detected_features, performance_reqs
            )
        else:
            suggested_stack = self._suggest_tech_stack(
                project_type, detected_features, performance_reqs
            )

        # Generate initial stories and epics
        epics = self._generate_epics(project_name, detected_features, project_type)
        stories = self._generate_stories(detected_features, project_type)

        # Estimate complexity
        complexity = self._estimate_complexity(detected_features, stories)

        return ProjectAnalysis(
            project_type=project_type,
            suggested_tech_stack=suggested_stack,
            detected_features=detected_features,
            performance_requirements=performance_reqs,
            suggested_stories=stories,
            suggested_epics=epics,
            estimated_complexity=complexity
        )

    def _detect_features(self, description: str) -> List[str]:
        """Detect features mentioned in the description"""
        description_lower = description.lower()
        detected = []

        for feature, patterns in self.feature_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    if feature not in detected:
                        detected.append(feature)
                    break

        return detected

    def _determine_project_type(self, features: List[str], description: str) -> str:
        """Determine the type of project"""
        description_lower = description.lower()

        # Check for specific project types
        if "ecommerce" in features or "shop" in description_lower:
            return "ecommerce"
        elif "blog" in features or "article" in description_lower:
            return "blog"
        elif "api" in features and "frontend" not in description_lower:
            return "api"
        elif "mobile" in features:
            return "mobile"
        elif "dashboard" in description_lower or "admin" in features:
            return "admin_dashboard"
        elif "microservice" in description_lower:
            return "microservices"
        elif any(word in description_lower for word in ["website", "web app", "webapp"]):
            return "web_application"
        elif "cli" in description_lower or "command" in description_lower:
            return "cli_tool"
        else:
            return "web_application"  # Default

    def _detect_performance_requirements(self, description: str) -> List[str]:
        """Detect performance requirements from description"""
        requirements = []
        description_lower = description.lower()

        # Performance indicators
        if any(word in description_lower for word in ["high traffic", "scalable", "scale", "million"]):
            requirements.append("high_scalability")

        if any(word in description_lower for word in ["real-time", "realtime", "live", "instant"]):
            requirements.append("real_time")

        if any(word in description_lower for word in ["fast", "performance", "speed", "quick"]):
            requirements.append("high_performance")

        if any(word in description_lower for word in ["secure", "security", "encryption"]):
            requirements.append("high_security")

        if any(word in description_lower for word in ["global", "international", "multi-region"]):
            requirements.append("global_deployment")

        return requirements

    def _suggest_tech_stack(self, project_type: str, features: List[str],
                           performance_reqs: List[str]) -> Dict[str, Any]:
        """Suggest appropriate tech stack based on analysis"""
        stack = {}

        # Backend suggestions
        if "high_performance" in performance_reqs or "high_scalability" in performance_reqs:
            stack["backend"] = {
                "language": "Go",
                "framework": "Gin",
                "alternatives": ["Python/FastAPI", "Node.js/Express"]
            }
        elif project_type == "api":
            stack["backend"] = {
                "language": "Python",
                "framework": "FastAPI",
                "alternatives": ["Go/Gin", "Node.js/Express"]
            }
        else:
            stack["backend"] = {
                "language": "Python",
                "framework": "FastAPI",
                "alternatives": ["Django", "Node.js/Express"]
            }

        # Frontend suggestions
        if project_type != "api" and project_type != "cli_tool":
            if project_type == "mobile":
                stack["frontend"] = {
                    "framework": "React Native",
                    "alternatives": ["Flutter", "Native"]
                }
            elif project_type == "admin_dashboard":
                stack["frontend"] = {
                    "framework": "React",
                    "ui_library": "Ant Design",
                    "alternatives": ["Vue.js/Element", "Angular/Material"]
                }
            else:
                stack["frontend"] = {
                    "framework": "React",
                    "styling": "Tailwind CSS",
                    "alternatives": ["Vue.js", "Next.js"]
                }

        # Database suggestions
        if "ecommerce" in features or "transaction" in performance_reqs:
            stack["database"] = {
                "primary": "PostgreSQL",
                "cache": "Redis",
                "search": "Elasticsearch" if "search" in features else None
            }
        elif "blog" in features or "content" in features:
            stack["database"] = {
                "primary": "PostgreSQL",
                "cache": "Redis" if "high_scalability" in performance_reqs else None
            }
        else:
            stack["database"] = {
                "primary": "PostgreSQL",
                "cache": "Redis" if performance_reqs else None
            }

        # Additional services
        if "authentication" in features:
            stack["auth"] = {
                "method": "JWT",
                "providers": ["OAuth2", "Social Login"] if "social" in features else []
            }

        if "payment" in features:
            stack["payment"] = {
                "provider": "Stripe",
                "alternatives": ["PayPal", "Square"]
            }

        if "file_handling" in features:
            stack["storage"] = {
                "provider": "AWS S3",
                "alternatives": ["Google Cloud Storage", "Azure Blob"]
            }

        if "email" in features:
            stack["email"] = {
                "provider": "SendGrid",
                "alternatives": ["AWS SES", "Mailgun"]
            }

        if "real_time" in features:
            stack["realtime"] = {
                "technology": "WebSockets",
                "alternatives": ["Server-Sent Events", "Socket.io"]
            }

        # DevOps
        stack["devops"] = {
            "containerization": "Docker",
            "orchestration": "Kubernetes" if "microservices" in project_type else "Docker Compose",
            "ci_cd": "GitHub Actions",
            "monitoring": "Prometheus + Grafana" if performance_reqs else "Basic logging"
        }

        # Testing
        stack["testing"] = {
            "backend": self._get_test_framework(stack.get("backend", {}).get("language", "Python")),
            "frontend": "Jest + React Testing Library" if stack.get("frontend") else None,
            "e2e": "Cypress" if stack.get("frontend") else "Postman/Newman"
        }

        return stack

    def _get_test_framework(self, language: str) -> str:
        """Get appropriate test framework for language"""
        frameworks = {
            "Python": "pytest",
            "Go": "go test",
            "JavaScript": "Jest",
            "TypeScript": "Jest",
            "Java": "JUnit",
            "C#": "xUnit",
            "Ruby": "RSpec"
        }
        return frameworks.get(language, "unittest")

    def _validate_and_enhance_tech_stack(self, tech_stack: Dict[str, Any],
                                        features: List[str],
                                        performance_reqs: List[str]) -> Dict[str, Any]:
        """Validate provided tech stack and add missing components"""
        enhanced = tech_stack.copy()

        # Add missing testing frameworks
        if "testing" not in enhanced:
            backend_lang = enhanced.get("backend", {}).get("language", "Python")
            enhanced["testing"] = {
                "backend": self._get_test_framework(backend_lang),
                "frontend": "Jest" if enhanced.get("frontend") else None
            }

        # Add cache if needed for performance
        if performance_reqs and "cache" not in enhanced.get("database", {}):
            if "database" not in enhanced:
                enhanced["database"] = {}
            enhanced["database"]["cache"] = "Redis"

        # Add required services based on features
        if "authentication" in features and "auth" not in enhanced:
            enhanced["auth"] = {"method": "JWT"}

        if "file_handling" in features and "storage" not in enhanced:
            enhanced["storage"] = {"provider": "AWS S3"}

        # Add DevOps if missing
        if "devops" not in enhanced:
            enhanced["devops"] = {
                "containerization": "Docker",
                "ci_cd": "GitHub Actions"
            }

        return enhanced

    def _generate_epics(self, project_name: str, features: List[str],
                       project_type: str) -> List[Dict[str, Any]]:
        """Generate initial epics based on detected features"""
        epics = []

        # Core functionality epic
        epics.append({
            "title": f"Core {project_type.replace('_', ' ').title()} Functionality",
            "description": f"Implement the core features of {project_name}",
            "priority": "Critical"
        })

        # Feature-based epics
        if "authentication" in features:
            epics.append({
                "title": "User Authentication & Authorization",
                "description": "Implement complete user management system",
                "priority": "Critical"
            })

        if "payment" in features:
            epics.append({
                "title": "Payment Processing",
                "description": "Integrate payment gateway and billing system",
                "priority": "High"
            })

        if "admin" in features:
            epics.append({
                "title": "Admin Dashboard",
                "description": "Build administrative interface and controls",
                "priority": "High"
            })

        if "mobile" in features:
            epics.append({
                "title": "Mobile Application",
                "description": "Develop mobile app for iOS and Android",
                "priority": "High"
            })

        # Always add these
        epics.append({
            "title": "Testing & Quality Assurance",
            "description": "Achieve 100% test coverage and implement E2E tests",
            "priority": "High"
        })

        epics.append({
            "title": "DevOps & Deployment",
            "description": "Set up CI/CD pipeline and deployment infrastructure",
            "priority": "Medium"
        })

        return epics

    def _generate_stories(self, features: List[str], project_type: str) -> List[Dict[str, Any]]:
        """Generate initial user stories based on detected features"""
        stories = []

        # Always include setup story
        stories.append({
            "title": "Project Setup and Configuration",
            "as_a": "developer",
            "i_want": "to set up the project structure and dependencies",
            "so_that": "I can start development with proper foundation",
            "acceptance_criteria": [
                "Project structure created",
                "Dependencies installed",
                "Development environment configured",
                "Git repository initialized"
            ],
            "story_points": 3,
            "priority": "Critical"
        })

        # Authentication stories
        if "authentication" in features:
            stories.extend([
                {
                    "title": "User Registration",
                    "as_a": "new user",
                    "i_want": "to create an account",
                    "so_that": "I can access the application",
                    "acceptance_criteria": [
                        "Registration form with validation",
                        "Email verification",
                        "Password strength requirements",
                        "Success/error messages"
                    ],
                    "story_points": 5,
                    "priority": "Critical"
                },
                {
                    "title": "User Login",
                    "as_a": "registered user",
                    "i_want": "to log into my account",
                    "so_that": "I can access my data",
                    "acceptance_criteria": [
                        "Login form with validation",
                        "JWT token generation",
                        "Remember me option",
                        "Password reset link"
                    ],
                    "story_points": 5,
                    "priority": "Critical"
                }
            ])

        # E-commerce stories
        if "ecommerce" in features:
            stories.extend([
                {
                    "title": "Product Catalog",
                    "as_a": "customer",
                    "i_want": "to browse products",
                    "so_that": "I can find items to purchase",
                    "acceptance_criteria": [
                        "Product listing page",
                        "Product detail page",
                        "Search functionality",
                        "Category filtering"
                    ],
                    "story_points": 8,
                    "priority": "High"
                },
                {
                    "title": "Shopping Cart",
                    "as_a": "customer",
                    "i_want": "to add items to cart",
                    "so_that": "I can purchase multiple items",
                    "acceptance_criteria": [
                        "Add to cart functionality",
                        "Update quantities",
                        "Remove items",
                        "Cart persistence"
                    ],
                    "story_points": 5,
                    "priority": "High"
                }
            ])

        # Blog stories
        if "blog" in features:
            stories.extend([
                {
                    "title": "Create Blog Post",
                    "as_a": "content creator",
                    "i_want": "to write and publish posts",
                    "so_that": "I can share content",
                    "acceptance_criteria": [
                        "Rich text editor",
                        "Image upload",
                        "Draft/publish states",
                        "Categories and tags"
                    ],
                    "story_points": 5,
                    "priority": "High"
                },
                {
                    "title": "View Blog Posts",
                    "as_a": "reader",
                    "i_want": "to read blog posts",
                    "so_that": "I can consume content",
                    "acceptance_criteria": [
                        "Post listing page",
                        "Individual post view",
                        "Comments section",
                        "Share buttons"
                    ],
                    "story_points": 3,
                    "priority": "High"
                }
            ])

        # API stories
        if "api" in features or project_type == "api":
            stories.append({
                "title": "RESTful API Endpoints",
                "as_a": "API consumer",
                "i_want": "to access data via API",
                "so_that": "I can integrate with the system",
                "acceptance_criteria": [
                    "CRUD endpoints implemented",
                    "API documentation (OpenAPI/Swagger)",
                    "Authentication/authorization",
                    "Rate limiting",
                    "Error handling"
                ],
                "story_points": 8,
                "priority": "Critical"
            })

        # Admin stories
        if "admin" in features:
            stories.append({
                "title": "Admin Dashboard",
                "as_a": "administrator",
                "i_want": "to manage the system",
                "so_that": "I can control operations",
                "acceptance_criteria": [
                    "User management interface",
                    "Content management",
                    "System statistics",
                    "Activity logs"
                ],
                "story_points": 8,
                "priority": "Medium"
            })

        # Search stories
        if "search" in features:
            stories.append({
                "title": "Search Functionality",
                "as_a": "user",
                "i_want": "to search for content",
                "so_that": "I can find what I need quickly",
                "acceptance_criteria": [
                    "Search bar implementation",
                    "Full-text search",
                    "Search filters",
                    "Search results page",
                    "Search suggestions"
                ],
                "story_points": 5,
                "priority": "Medium"
            })

        # Always include testing story
        stories.append({
            "title": "Unit Test Coverage",
            "as_a": "developer",
            "i_want": "comprehensive test coverage",
            "so_that": "I can ensure code quality",
            "acceptance_criteria": [
                "100% test coverage for business logic",
                "Unit tests for all components",
                "Integration tests for APIs",
                "Test documentation"
            ],
            "story_points": 8,
            "priority": "High"
        })

        return stories

    def _estimate_complexity(self, features: List[str], stories: List[Dict[str, Any]]) -> str:
        """Estimate project complexity based on features and stories"""
        total_points = sum(story.get("story_points", 0) for story in stories)
        feature_count = len(features)

        if total_points > 100 or feature_count > 10:
            return "Enterprise"
        elif total_points > 50 or feature_count > 6:
            return "Large"
        elif total_points > 25 or feature_count > 3:
            return "Medium"
        else:
            return "Small"

    def generate_project_summary(self, analysis: ProjectAnalysis) -> str:
        """Generate a human-readable project summary"""
        summary = []

        summary.append(f"Project Type: {analysis.project_type.replace('_', ' ').title()}")
        summary.append(f"Estimated Complexity: {analysis.estimated_complexity}")
        summary.append(f"\nDetected Features ({len(analysis.detected_features)}):")

        for feature in analysis.detected_features:
            summary.append(f"  • {feature.replace('_', ' ').title()}")

        if analysis.performance_requirements:
            summary.append(f"\nPerformance Requirements:")
            for req in analysis.performance_requirements:
                summary.append(f"  • {req.replace('_', ' ').title()}")

        summary.append(f"\nSuggested Tech Stack:")
        for component, details in analysis.suggested_tech_stack.items():
            if isinstance(details, dict):
                summary.append(f"  {component.title()}:")
                for key, value in details.items():
                    if value and key != "alternatives":
                        summary.append(f"    • {key}: {value}")
            else:
                summary.append(f"  {component.title()}: {details}")

        summary.append(f"\nGenerated {len(analysis.suggested_epics)} Epics and {len(analysis.suggested_stories)} User Stories")

        return "\n".join(summary)