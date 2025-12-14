import asyncio
import json
import random
import time

CATEGORIES = ["food", "transport", "shopping", "health", "entertainment"]

async def generate_transaction():
    """Асинхронная генерация одной транзакции"""
    await asyncio.sleep(0)  # имитация асинхронности
    return {
        "timestamp": time.time(),
        "category": random.choice(CATEGORIES),
        "amount": round(random.uniform(100, 5000), 2)
    }

async def generate_batch(count: int):
    """Генерация транзакций пачками по 10"""
    batch = []
    file_index = 1

    for i in range(count):
        transaction = await generate_transaction()
        batch.append(transaction)

        if len(batch) == 10:
            filename = f"transactions_{file_index}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(batch, f, ensure_ascii=False, indent=4)

            print(f"[INFO] Сохранено 10 транзакций → {filename}")

            batch = []
            file_index += 1

    if batch:
        filename = f"transactions_{file_index}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(batch, f, ensure_ascii=False, indent=4)
        print(f"[INFO] Сохранены оставшиеся {len(batch)} транзакций → {filename}")

async def main():
    count = int(input("Введите количество транзакций: "))
    await generate_batch(count)

asyncio.run(main())
