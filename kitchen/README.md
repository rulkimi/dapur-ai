# Project Documentation

This README compiles the configuration rules from the `.cursor/rules` directory, which defines the project structure, standards, and best practices.

## Table of Contents

1. Project Structure Overview
2. Core Module
3. Database Module
4. Domains

## Project Structure Overview

### Directory Base Structure

```
project/
├── core/           # Core functionality and configurations
├── db/             # Database-related functionality
├── domains/        # Business domains (feature modules)
├── main.py         # Application entry point
├── pyproject.toml  # Project metadata and build configuration
├── requirements.txt # Project dependencies
├── docker-compose.yml # Docker configuration
└── .gitignore      # Git ignore rules
```

### Standards to Follow

1. **Domain-Driven Design**: Organize code by business domains, not technical layers.
2. **Clean Architecture**: Follow separation of concerns with clear boundaries between layers.
3. **Repository Pattern**: Use repositories to abstract data access logic.
4. **SOLID Principles**: Adhere to Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles.
5. **Type Hints**: Use Python type annotations throughout the codebase.
6. **Documentation**: Document all modules, classes, and functions with docstrings.
7. **Testing**: Write tests for all components (unit, integration, and end-to-end).

### Professional Practices

1. **Version Control**: 
   - Use meaningful commit messages
   - Create feature branches for new development
   - Submit changes through pull requests
   - Conduct code reviews

2. **Code Quality**:
   - Follow PEP 8 style guide
   - Use linters and formatters (black, isort, flake8, mypy)
   - Maintain high test coverage
   - Document complex logic

3. **Dependency Management**:
   - Pin dependency versions
   - Regularly update dependencies
   - Audit for security vulnerabilities

4. **Logging and Monitoring**:
   - Implement structured logging
   - Add appropriate log levels
   - Set up monitoring for production

## Core Module

The `core` module serves as the central foundation for the application, containing critical components used throughout the entire system.

### Structure

- `config.py`: Application configuration and environment settings management
- `security.py`: Security features including authentication, authorization, token management, and password handling

### Standards to Follow

1. **Minimal Dependencies**: Keep external dependencies to a minimum.
2. **Comprehensive Documentation**: All functions, classes, and modules must be well-documented.
3. **Type Annotations**: Use Python type hints throughout.
4. **Error Handling**: Implement proper error handling with specific exceptions.
5. **Configuration Isolation**: Keep all configuration parameters in `config.py`.
6. **Backwards Compatibility**: Maintain backward compatibility whenever possible.
7. **Comprehensive Testing**: Maintain high test coverage for core functionality.

### Professional Practices

1. **Security First**: Follow security best practices for all core components.
2. **Code Review**: All changes to core modules should undergo thorough peer review.
3. **Performance Awareness**: Core components must be optimized for performance.
4. **Separation of Concerns**: Each file should have a clear, single responsibility.
5. **Abstraction**: Expose clean interfaces that hide implementation details.

## Database Module

The database module follows a clean architecture approach with a repository pattern implementation.

### Structure

- `base.py`: Defines the base ORM model with common fields and functionality
- `session.py`: Handles database connection, session management, and initialization
- `repository.py`: Implements the repository pattern for data access abstraction

### Standards and Best Practices

#### Naming Conventions
- Use snake_case for database tables, columns, and file names
- Use PascalCase for model classes
- Use plural for table names (users, products, etc.)
- Prefix pivot/junction tables with their related tables (e.g., user_role)

#### Model Design
- Every model should inherit from `Base`
- Include appropriate type hints for all fields
- Use appropriate SQLAlchemy column types and constraints
- Document complex model relationships and constraints
- Keep models focused and cohesive (single responsibility)

#### Repository Pattern
- Each model should have its own repository extending `BaseRepository`
- Implement custom methods for specific business logic in dedicated repositories
- Keep repository methods focused on data access operations
- Avoid business logic in repositories

## Domains

The `domains` directory implements a domain-driven design (DDD) approach for organizing the application's business logic.

### Structure

Each domain folder follows a consistent structure:

- `models.py`: Domain entity definitions and data models
- `repositories.py`: Data access layer and persistence logic
- `services.py`: Business logic and domain services
- `schemas.py`: Data validation schemas and DTOs (Data Transfer Objects)
- `routers.py`: API route definitions and handlers

### Standards to Follow

1. **Domain Isolation**: Each domain should be self-contained with minimal dependencies on other domains.
2. **Single Responsibility**: Each file should have a clear, singular responsibility.
3. **Dependency Direction**: Dependencies should flow inward (routers → services → repositories → models).
4. **Explicit Interfaces**: Public interfaces between domains should be well-defined and documented.
5. **Consistent Naming**: Follow consistent naming conventions across all domains.
6. **Error Handling**: Implement domain-specific error handling and validation.

### Professional Practices

1. **Documentation**: Document the purpose of each domain and its components.
2. **Testing**: Create comprehensive tests for each domain, focusing on business logic in services.
3. **Version Control**: Make atomic commits related to specific domains when possible.
4. **Code Reviews**: Pay special attention to cross-domain dependencies during reviews.
5. **Refactoring**: Regularly reassess domain boundaries and refactor as needed. 



# Change Log: Exception Handling System Implementation

## Overview

This change log documents the implementation of a comprehensive exception handling system that can be used across all domain modules in the application. The system provides a uniform way to handle and communicate errors, improving error consistency, debugging, and developer experience.

## Date
Created: March 02, 2025

### 1. Exception Hierarchy

Created a hierarchy of exception classes:

- **Base Exception**
  - `AppException`: Base class with status code, error code, message, and details

- **HTTP-specific Exceptions**
  - `BadRequestException` (400)
  - `UnauthorizedException` (401)
  - `ForbiddenException` (403)
  - `NotFoundException` (404)
  - `ConflictException` (409)

- **Domain-specific Exceptions**
  - `ValidationException` (extends BadRequest)
  - `ServiceException` (500)
  - `DatabaseException` (extends Service)
  - `ExternalServiceException` (extends Service)

### 2. FastAPI Integration

- Created exception handlers to automatically convert our custom exceptions to HTTP responses
- Integrated with SQLAlchemy to handle database errors
- Registered handlers in the main FastAPI application

### 3. Utility Functions

Added helper functions to simplify common exception patterns:

- `get_or_404`: Check if a result exists, otherwise raise NotFoundException
- `get_or_404_async`: Async version of get_or_404
- `handle_db_integrity_error`: Convert database integrity errors to appropriate domain exceptions
- `try_with_db_exception`: Execute a function and properly handle any database exceptions

### 4. Logging

- Added structured logging for all exceptions
- Included context information like error codes, paths, and additional details

## Benefits

- **Consistency**: All errors now follow the same format and structure
- **Type Safety**: Proper exception hierarchy for better error handling
- **Improved Developer Experience**: Clear, descriptive exceptions with detailed context
- **Better API Documentation**: Each exception maps to a specific HTTP status code
- **Reduced Boilerplate**: Utility functions eliminate repetitive code patterns
- **Enhanced Debugging**: Detailed logging with context information
- **Domain-Driven Design Support**: Exceptions reflect business domain concerns

## Usage Examples

### Basic Exception Usage

```python
from core.exceptions import NotFoundException

# In a service
def get_user(user_id: int):
    user = repository.get_user(user_id)
    if not user:
        raise NotFoundException(f"User with ID {user_id} not found")
    return user
```

### Using Utility Functions

```python
from core.exceptions import get_or_404

# In a service
def get_product(product_id: int):
    product = repository.get_product(product_id)
    return get_or_404(product, f"Product with ID {product_id} not found")
```

### Database Error Handling

```python
from core.exceptions import handle_db_integrity_error
from sqlalchemy.exc import IntegrityError

# In a repository
async def create_user(user_data: dict):
    try:
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        return user
    except IntegrityError as e:
        await self.session.rollback()
        handle_db_integrity_error(e, "User could not be created")
```

## Future Enhancements

- Add domain-specific error codes for more granular error identification
- Add request ID tracking for better error tracing
- Extend the system with domain-specific exception classes as needed
- Implement localization support for error messages