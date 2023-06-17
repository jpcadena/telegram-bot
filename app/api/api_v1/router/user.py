"""
User API Router
This module provides CRUD (Create, Retrieve, Update, Delete) operations
 for users.
"""
import logging

from fastapi import APIRouter

logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix="/users", tags=["users"])
