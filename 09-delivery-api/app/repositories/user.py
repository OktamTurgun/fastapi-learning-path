import uuid
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, Role, user_roles

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, **kwargs) -> User:
        user = User(**kwargs)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get(self, id) -> User | None:
        if isinstance(id, str):
            try:
                id = uuid.UUID(id)
            except ValueError:
                return None
        return await self.session.get(User, id)

    async def get_with_roles(self, id) -> User | None:
        if isinstance(id, str):
            try:
                id = uuid.UUID(id)
            except ValueError:
                return None
        stmt = select(User).where(User.id == id).options(selectinload(User.roles))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def assign_role(self, user: User, role: Role) -> None:
        stmt = insert(user_roles).values(user_id=user.id, role_id=role.id)
        await self.session.execute(stmt)
        await self.session.flush()


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()