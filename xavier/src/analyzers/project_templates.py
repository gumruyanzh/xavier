"""
Xavier Framework - Project Templates
Pre-defined templates for common project types
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ProjectTemplate:
    """Template for a project type"""
    name: str
    description: str
    tech_stack: Dict[str, Any]
    initial_structure: List[str]
    initial_files: Dict[str, str]
    default_stories: List[Dict[str, Any]]


class ProjectTemplates:
    """Collection of project templates"""

    @staticmethod
    def get_template(template_name: str) -> ProjectTemplate:
        """Get a specific project template"""
        templates = {
            "web_application": ProjectTemplates.web_application_template(),
            "rest_api": ProjectTemplates.rest_api_template(),
            "ecommerce": ProjectTemplates.ecommerce_template(),
            "blog": ProjectTemplates.blog_template(),
            "mobile": ProjectTemplates.mobile_template(),
            "microservices": ProjectTemplates.microservices_template(),
            "cli_tool": ProjectTemplates.cli_tool_template()
        }
        return templates.get(template_name, ProjectTemplates.web_application_template())

    @staticmethod
    def web_application_template() -> ProjectTemplate:
        """Template for a full-stack web application"""
        return ProjectTemplate(
            name="Web Application",
            description="Full-stack web application with React frontend and Python backend",
            tech_stack={
                "frontend": {
                    "framework": "React",
                    "language": "TypeScript",
                    "styling": "Tailwind CSS",
                    "state_management": "Redux Toolkit",
                    "build_tool": "Vite"
                },
                "backend": {
                    "language": "Python",
                    "framework": "FastAPI",
                    "orm": "SQLAlchemy",
                    "validation": "Pydantic"
                },
                "database": {
                    "primary": "PostgreSQL",
                    "cache": "Redis"
                },
                "testing": {
                    "backend": "pytest",
                    "frontend": "Jest + React Testing Library",
                    "e2e": "Cypress"
                },
                "devops": {
                    "containerization": "Docker",
                    "ci_cd": "GitHub Actions",
                    "deployment": "Docker Compose"
                }
            },
            initial_structure=[
                "frontend/",
                "frontend/src/",
                "frontend/src/components/",
                "frontend/src/pages/",
                "frontend/src/services/",
                "frontend/src/store/",
                "frontend/src/utils/",
                "frontend/public/",
                "backend/",
                "backend/app/",
                "backend/app/api/",
                "backend/app/core/",
                "backend/app/models/",
                "backend/app/services/",
                "backend/tests/",
                "docker/",
                "scripts/",
                ".github/workflows/"
            ],
            initial_files={
                "docker-compose.yml": """version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
""",
                "backend/requirements.txt": """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
pydantic==2.5.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
""",
                "frontend/package.json": """{
  "name": "frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "jest",
    "test:coverage": "jest --coverage"
  }
}
""",
                ".github/workflows/ci.yml": """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage
"""
            },
            default_stories=[
                {
                    "title": "Setup Development Environment",
                    "story_points": 3,
                    "priority": "Critical"
                },
                {
                    "title": "Create Database Schema",
                    "story_points": 5,
                    "priority": "Critical"
                },
                {
                    "title": "Implement API Structure",
                    "story_points": 5,
                    "priority": "Critical"
                },
                {
                    "title": "Setup Frontend Routing",
                    "story_points": 3,
                    "priority": "High"
                }
            ]
        )

    @staticmethod
    def rest_api_template() -> ProjectTemplate:
        """Template for a REST API"""
        return ProjectTemplate(
            name="REST API",
            description="RESTful API with FastAPI and PostgreSQL",
            tech_stack={
                "backend": {
                    "language": "Python",
                    "framework": "FastAPI",
                    "orm": "SQLAlchemy",
                    "validation": "Pydantic"
                },
                "database": {
                    "primary": "PostgreSQL",
                    "cache": "Redis"
                },
                "testing": {
                    "framework": "pytest",
                    "api_testing": "httpx"
                },
                "documentation": {
                    "api_docs": "OpenAPI/Swagger",
                    "format": "Automatic via FastAPI"
                },
                "devops": {
                    "containerization": "Docker",
                    "ci_cd": "GitHub Actions"
                }
            },
            initial_structure=[
                "app/",
                "app/api/",
                "app/api/v1/",
                "app/core/",
                "app/models/",
                "app/schemas/",
                "app/services/",
                "app/db/",
                "tests/",
                "tests/unit/",
                "tests/integration/",
                "alembic/",
                "scripts/"
            ],
            initial_files={
                "Dockerfile": """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
                "requirements.txt": """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
pydantic==2.5.0
alembic==1.12.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
""",
                "app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API",
    description="REST API with FastAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
"""
            },
            default_stories=[
                {
                    "title": "Setup API Structure",
                    "story_points": 3,
                    "priority": "Critical"
                },
                {
                    "title": "Implement Authentication",
                    "story_points": 5,
                    "priority": "Critical"
                },
                {
                    "title": "Create CRUD Endpoints",
                    "story_points": 8,
                    "priority": "High"
                },
                {
                    "title": "Add API Documentation",
                    "story_points": 2,
                    "priority": "Medium"
                }
            ]
        )

    @staticmethod
    def ecommerce_template() -> ProjectTemplate:
        """Template for an e-commerce platform"""
        return ProjectTemplate(
            name="E-Commerce Platform",
            description="Full-featured e-commerce platform with cart, payments, and admin",
            tech_stack={
                "frontend": {
                    "framework": "Next.js",
                    "language": "TypeScript",
                    "styling": "Tailwind CSS",
                    "state_management": "Zustand",
                    "ui_components": "Radix UI"
                },
                "backend": {
                    "language": "Python",
                    "framework": "FastAPI",
                    "orm": "SQLAlchemy",
                    "task_queue": "Celery"
                },
                "database": {
                    "primary": "PostgreSQL",
                    "cache": "Redis",
                    "search": "Elasticsearch"
                },
                "payment": {
                    "provider": "Stripe",
                    "alternatives": ["PayPal", "Square"]
                },
                "storage": {
                    "images": "AWS S3",
                    "cdn": "CloudFront"
                },
                "testing": {
                    "backend": "pytest",
                    "frontend": "Jest + React Testing Library",
                    "e2e": "Playwright"
                }
            },
            initial_structure=[
                "frontend/",
                "backend/",
                "backend/app/",
                "backend/app/products/",
                "backend/app/orders/",
                "backend/app/users/",
                "backend/app/payments/",
                "backend/app/admin/",
                "shared/",
                "docker/"
            ],
            initial_files={
                "backend/app/products/models.py": """from sqlalchemy import Column, String, Float, Integer, Text, Boolean
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    sku = Column(String(100), unique=True)
""",
                "backend/app/orders/models.py": """from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
"""
            },
            default_stories=[
                {
                    "title": "Product Catalog",
                    "story_points": 8,
                    "priority": "Critical"
                },
                {
                    "title": "Shopping Cart",
                    "story_points": 5,
                    "priority": "Critical"
                },
                {
                    "title": "Checkout Process",
                    "story_points": 8,
                    "priority": "Critical"
                },
                {
                    "title": "Payment Integration",
                    "story_points": 13,
                    "priority": "Critical"
                },
                {
                    "title": "Order Management",
                    "story_points": 5,
                    "priority": "High"
                },
                {
                    "title": "Admin Dashboard",
                    "story_points": 8,
                    "priority": "High"
                }
            ]
        )

    @staticmethod
    def blog_template() -> ProjectTemplate:
        """Template for a blog/CMS platform"""
        return ProjectTemplate(
            name="Blog Platform",
            description="Content management system with blog functionality",
            tech_stack={
                "frontend": {
                    "framework": "Next.js",
                    "language": "TypeScript",
                    "styling": "Tailwind CSS",
                    "markdown": "MDX"
                },
                "backend": {
                    "language": "Python",
                    "framework": "FastAPI",
                    "orm": "SQLAlchemy"
                },
                "database": {
                    "primary": "PostgreSQL",
                    "cache": "Redis"
                },
                "editor": {
                    "rich_text": "TipTap",
                    "markdown": "Monaco Editor"
                }
            },
            initial_structure=[
                "frontend/",
                "frontend/pages/",
                "frontend/components/",
                "backend/",
                "backend/app/",
                "backend/app/posts/",
                "backend/app/users/",
                "backend/app/comments/",
                "content/"
            ],
            initial_files={},
            default_stories=[
                {
                    "title": "Create Post Editor",
                    "story_points": 5,
                    "priority": "Critical"
                },
                {
                    "title": "Display Blog Posts",
                    "story_points": 3,
                    "priority": "Critical"
                },
                {
                    "title": "Comment System",
                    "story_points": 5,
                    "priority": "High"
                },
                {
                    "title": "Categories and Tags",
                    "story_points": 3,
                    "priority": "Medium"
                }
            ]
        )

    @staticmethod
    def mobile_template() -> ProjectTemplate:
        """Template for a mobile application"""
        return ProjectTemplate(
            name="Mobile Application",
            description="Cross-platform mobile app with React Native",
            tech_stack={
                "mobile": {
                    "framework": "React Native",
                    "language": "TypeScript",
                    "state_management": "Redux Toolkit",
                    "navigation": "React Navigation"
                },
                "backend": {
                    "language": "Node.js",
                    "framework": "Express",
                    "database_orm": "Prisma"
                },
                "database": {
                    "primary": "PostgreSQL",
                    "local_storage": "AsyncStorage"
                },
                "testing": {
                    "unit": "Jest",
                    "e2e": "Detox"
                }
            },
            initial_structure=[
                "mobile/",
                "mobile/src/",
                "mobile/src/screens/",
                "mobile/src/components/",
                "mobile/src/navigation/",
                "mobile/src/services/",
                "mobile/src/store/",
                "backend/",
                "backend/src/"
            ],
            initial_files={},
            default_stories=[
                {
                    "title": "Setup React Native Project",
                    "story_points": 3,
                    "priority": "Critical"
                },
                {
                    "title": "Implement Navigation",
                    "story_points": 3,
                    "priority": "Critical"
                },
                {
                    "title": "Create UI Components",
                    "story_points": 5,
                    "priority": "High"
                },
                {
                    "title": "API Integration",
                    "story_points": 5,
                    "priority": "High"
                }
            ]
        )

    @staticmethod
    def microservices_template() -> ProjectTemplate:
        """Template for a microservices architecture"""
        return ProjectTemplate(
            name="Microservices Architecture",
            description="Distributed system with multiple services",
            tech_stack={
                "services": {
                    "languages": ["Go", "Python", "Node.js"],
                    "api_gateway": "Kong",
                    "service_mesh": "Istio"
                },
                "messaging": {
                    "queue": "RabbitMQ",
                    "streaming": "Apache Kafka"
                },
                "database": {
                    "per_service": True,
                    "options": ["PostgreSQL", "MongoDB", "Redis"]
                },
                "devops": {
                    "containerization": "Docker",
                    "orchestration": "Kubernetes",
                    "ci_cd": "GitLab CI",
                    "monitoring": "Prometheus + Grafana"
                }
            },
            initial_structure=[
                "services/",
                "services/auth-service/",
                "services/user-service/",
                "services/product-service/",
                "services/order-service/",
                "api-gateway/",
                "k8s/",
                "docker/",
                "scripts/"
            ],
            initial_files={
                "docker-compose.yml": """version: '3.8'
services:
  auth-service:
    build: ./services/auth-service
    ports:
      - "8001:8001"

  user-service:
    build: ./services/user-service
    ports:
      - "8002:8002"

  product-service:
    build: ./services/product-service
    ports:
      - "8003:8003"

  api-gateway:
    build: ./api-gateway
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
      - user-service
      - product-service

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
"""
            },
            default_stories=[
                {
                    "title": "Setup Service Architecture",
                    "story_points": 8,
                    "priority": "Critical"
                },
                {
                    "title": "Implement API Gateway",
                    "story_points": 5,
                    "priority": "Critical"
                },
                {
                    "title": "Service Communication",
                    "story_points": 8,
                    "priority": "Critical"
                },
                {
                    "title": "Setup Kubernetes",
                    "story_points": 8,
                    "priority": "High"
                }
            ]
        )

    @staticmethod
    def cli_tool_template() -> ProjectTemplate:
        """Template for a CLI tool"""
        return ProjectTemplate(
            name="CLI Tool",
            description="Command-line interface tool",
            tech_stack={
                "language": "Python",
                "cli_framework": "Click",
                "packaging": "setuptools",
                "testing": {
                    "framework": "pytest",
                    "cli_testing": "click.testing"
                }
            },
            initial_structure=[
                "src/",
                "src/commands/",
                "src/utils/",
                "tests/",
                "docs/"
            ],
            initial_files={
                "setup.py": """from setuptools import setup, find_packages

setup(
    name="cli-tool",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "tool=src.main:cli",
        ],
    },
)
""",
                "src/main.py": """import click

@click.group()
def cli():
    \"\"\"CLI Tool\"\"\"
    pass

@cli.command()
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(name):
    \"\"\"Simple greeting command\"\"\"
    click.echo(f"Hello, {name}!")

if __name__ == "__main__":
    cli()
"""
            },
            default_stories=[
                {
                    "title": "Setup CLI Structure",
                    "story_points": 2,
                    "priority": "Critical"
                },
                {
                    "title": "Implement Core Commands",
                    "story_points": 5,
                    "priority": "Critical"
                },
                {
                    "title": "Add Configuration Support",
                    "story_points": 3,
                    "priority": "High"
                }
            ]
        )