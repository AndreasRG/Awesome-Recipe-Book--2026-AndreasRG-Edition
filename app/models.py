# -*- coding: utf-8 -*-
"""
SQLAlchemy ORM models for the Recipe API.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Association table for Recipe-Ingredient relationship
recipe_ingredients = Table(
    'recipe_ingredients',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'), primary_key=True),
    Column('amount', String),
    Column('unit', String),
)

# Association table for Recipe-Tag relationship
recipe_tags = Table(
    'recipe_tags',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
)


class User(Base):
    """User model for application users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"


class Recipe(Base):
    """Recipe model for storing recipe information."""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    time_minutes = Column(Integer, nullable=False)
    price = Column(String, nullable=False)
    link = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    image = Column(String, nullable=True)

    # Relationships
    ingredients = relationship(
        "Ingredient",
        secondary=recipe_ingredients,
        backref="recipes",
        cascade="all, delete"
    )
    tags = relationship(
        "Tag",
        secondary=recipe_tags,
        backref="recipes",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Recipe(id={self.id}, title={self.title}, time_minutes={self.time_minutes})>"


class Ingredient(Base):
    """Ingredient model for recipe ingredients."""
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)

    def __repr__(self):
        return f"<Ingredient(id={self.id}, name={self.name})>"


class Tag(Base):
    """Tag model for recipe categorization."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"
