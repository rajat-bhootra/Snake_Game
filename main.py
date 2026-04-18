import asyncio

from snake_game import ensure_highscores, start_menu


if __name__ == "__main__":
    ensure_highscores()
    asyncio.run(start_menu())
