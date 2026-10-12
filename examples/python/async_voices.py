"""Read the voice catalogue without creating a job."""
import asyncio
from classive import AsyncClassive

async def main():
    async with AsyncClassive() as client:
        print((await client.voices.list())["data"])

if __name__ == "__main__": asyncio.run(main())
