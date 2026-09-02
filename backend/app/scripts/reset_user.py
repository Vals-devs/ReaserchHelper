import asyncio
from sqlalchemy import text
from app.core.database import create_tables, engine

async def reset_user(email: str = "ival@gmail.com"):
    await create_tables()
    async with engine.begin() as conn:
        try:
            await conn.execute(
                text("UPDATE users SET plan_tier = 'free', storage_quota_bytes = 104857600 WHERE email = :email"),
                {"email": email}
            )
            print(f"User {email} has been reset to FREE plan (100 MB quota).")
        except Exception as e:
            print(f"Reset failed: {e}")

if __name__ == "__main__":
    asyncio.run(reset_user())
