import asyncio
import json
import glob

LIMIT = 10000  # Лимит превышения по категории


async def read_file(filename: str):
    """Асинхронное чтение одного файла с транзакциями."""
    await asyncio.sleep(0)  # имитация асинхронной операции
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


async def process_category_sums(transactions: list[dict]):
    """Группировка транзакций по категориям и суммирование amount."""
    category_totals: dict[str, float] = {}

    for t in transactions:
        category = t["category"]
        amount = t["amount"]
        category_totals[category] = category_totals.get(category, 0) + amount

    return category_totals


async def main():
    print("[INFO] Чтение файлов с транзакциями...")
    files = glob.glob("transactions_*.json")

    if not files:
        print("[WARN] Не найдено ни одного файла transactions_*.json")
        return

    all_transactions: list[dict] = []

    # Асинхронно читаем все файлы (по очереди, но через await)
    for filename in files:
        data = await read_file(filename)
        all_transactions.extend(data)
        print(f"[INFO] Прочитан файл {filename}, транзакций: {len(data)}")

    # Обрабатываем все транзакции
    category_totals = await process_category_sums(all_transactions)

    print("\n[RESULT] Суммы по категориям:")
    for category, total in category_totals.items():
        print(f" - {category}: {total:.2f}")

    print(f"\n[ALERT] Категории с превышением лимита {LIMIT}:")
    has_alerts = False
    for category, total in category_totals.items():
        if total > LIMIT:
            has_alerts = True
            print(
                f" ! ВНИМАНИЕ: категория '{category}' превысила лимит {LIMIT}, "
                f"сумма = {total:.2f}"
            )

    if not has_alerts:
        print("Превышений лимитов не обнаружено.")


if __name__ == "__main__":
    asyncio.run(main())
