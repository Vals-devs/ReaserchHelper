import asyncio
from sqlalchemy import select, text
from app.core.database import async_session_factory
from app.models.user import User

async def reset_user(email: str = "ival@gmail.com"):
    async with async_session_factory() as db:
        # Reset specific user or all users to free plan
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            user.plan_tier = "free"
            user.storage_quota_bytes = 104857600
            await db.commit()
            print(f"User {email} has been reset to FREE plan (100 MB quota).")
        else:
            # Execute raw SQL update to catch any user with email
            await db.execute(
                text("UPDATE users SET plan_tier = 'free', storage_quota_bytes = 104857600 WHERE email = :email"),
                {"email": email}
            )
            await db.commit()
            print(f"Raw SQL update executed for user {email}.")

if __name__ == "__main__":
    asyncio.run(reset_user())
