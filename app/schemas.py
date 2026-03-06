# -*- coding: utf-8 -*-
"""
Pydantic schemas for request/response validation in the Recipe API.
"""
from pydantic import BaseModel
from typing import Optional, List


# =====================
# User Schemas
# =====================

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: str
    password: str
    name: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True


# =====================
# Token Schemas
# =====================

class TokenCreate(BaseModel):
    """Schema for token creation (authentication)."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    email: str
    token: str


# =====================
# Ingredient Schemas
# =====================

class IngredientCreate(BaseModel):
    """Schema for creating an ingredient."""
    name: str

    class Config:
        from_attributes = True


class IngredientResponse(BaseModel):
    """Schema for ingredient response."""
    id: int
    name: str

    class Config:
        from_attributes = True


class IngredientWithAmountResponse(BaseModel):
    """Schema for ingredient response with amount and unit."""
    id: int
    name: str
    amount: Optional[str] = None
    unit: Optional[str] = None

    class Config:
        from_attributes = True


# =====================
# Tag Schemas
# =====================

class TagCreate(BaseModel):
    """Schema for creating a tag."""
    name: str

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    """Schema for tag response."""
    id: int
    name: str

    class Config:
        from_attributes = True


# =====================
# Recipe Schemas
# =====================

class RecipeCreate(BaseModel):
    """Schema for creating a recipe."""
    title: str
    time_minutes: int
    price: str
    link: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[int]] = None
    ingredients: Optional[List[dict]] = None

    class Config:
        from_attributes = True


class RecipeUpdate(BaseModel):
    """Schema for updating a recipe."""
    title: Optional[str] = None
    time_minutes: Optional[int] = None
    price: Optional[str] = None
    link: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[int]] = None
    ingredients: Optional[List[dict]] = None

    class Config:
        from_attributes = True


class RecipeResponse(BaseModel):
    """Schema for recipe response."""
    id: int
    title: str
    time_minutes: int
    price: str
    link: Optional[str] = None
    description: Optional[str] = None
    ingredients: List[IngredientWithAmountResponse] = []
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None

class TokenCreate(BaseModel):
    email: str
    password: str

class RecipeCreate(BaseModel):
    title: str
    time_minutes: int
    price: str
    link: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[int]] = None
    ingredients: Optional[List[int]] = None