"""
This script handles CRUD (Create, Read, Update, Delete) operations for
 User objects in the database.
"""
import logging
from typing import Optional, Union

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorators import benchmark, with_logging
from app.core.security.exception import DatabaseException
from app.core.security.password import get_password_hash
from app.crud.filter import (
    IndexFilter,
    UniqueFilter,
    get_index_filter,
    get_unique_filter,
)
from app.crud.specification import IdSpecification
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserSuperCreate

logger: logging.Logger = logging.getLogger(__name__)


class UserRepository:
    """
    This class handles all operations (CRUD) related to a User in the
     database.
    """

    def __init__(self, session: AsyncSession, index_filter: IndexFilter,
                 unique_filter: UniqueFilter):
        self.session: AsyncSession = session
        self.index_filter: IndexFilter = index_filter
        self.unique_filter: UniqueFilter = unique_filter
        self.model: User = User

    async def read_by_id(self, _id: IdSpecification) -> Optional[User]:
        """
        Retrieve a user from the database by its id
        :param _id: The id of the user
        :type _id: IdSpecification
        :return: The user with the specified id, or None if no such
            user exists
        :rtype: Optional[User]
        """
        async with self.session as session:
            try:
                user: User = await self.index_filter.filter(
                    _id, session, self.model)
            except SQLAlchemyError as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            return user

    @with_logging
    @benchmark
    async def create_user(
            self, user: Union[UserCreate, UserSuperCreate],
    ) -> User:
        """
        Create a new user in the database.
        :param user: An object containing the information of the user
         to create
        :type user: Union[UserCreate, UserSuperCreate]
        :return: The created user object
        :rtype: User
        """
        hashed_password = await get_password_hash(user.password)
        user_in = user.copy(update={"password": hashed_password})
        user_create: User = User(**user_in.dict())
        async with self.session as session:
            try:
                session.add(user_create)
                await session.commit()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise DatabaseException(str(sa_exc)) from sa_exc
            created_user: Optional[User] = await self.read_by_id(
                IdSpecification(user_create.id))
            if created_user is None:
                raise DatabaseException("User could not be created.")
            return created_user


async def get_user_repository() -> UserRepository:
    """
    Create a UserRepository with an async database session, an index
     filter, and a unique filter.
    :return: A UserRepository instance
    :rtype: UserRepository
    """
    return UserRepository(await get_session(), await get_index_filter(),
                          await get_unique_filter())
