"""
Model imports for SQLAlchemy.

This file imports all models from the various domains to ensure they are registered
with SQLAlchemy's metadata system. This is necessary for auto-generation of database
schema and synchronization.

Add imports for all models in the application here.
"""

# Import Base to make sure it's initialized before other models
from db.base import Base

# Import all models from domains
# For example:
# from domains.auth.models import User, Role, Permission
# from domains.products.models import Product, Category
# from domains.orders.models import Order, OrderItem

# When adding new models, import them here so they are registered with Base.metadata 