import csv
import random
from datetime import datetime, timedelta

PRODUCTS = [
    ("Wireless Mouse", 29.99),
    ("Mechanical Keyboard", 89.99),
    ("USB-C Hub", 45.50),
    ("Monitor Stand", 34.99),
    ("Webcam HD", 59.99),
    ("Laptop Sleeve", 24.99),
    ("Desk Lamp", 42.00),
    ("Cable Organizer", 12.99),
    ("Mouse Pad XL", 19.99),
    ("Headphone Stand", 27.50),
]

REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]

FIRST_NAMES = [
    "alice", "bob", "carol", "dave", "eve", "frank", "grace", "heidi",
    "ivan", "judy", "karl", "lisa", "mike", "nancy", "oscar", "pat",
    "quinn", "rachel", "steve", "tina", "ursula", "victor", "wendy", "xander",
]

DOMAINS = ["example.com", "testmail.org", "demo.io", "sample.net", "mockdata.com"]

OUTPUT = "sample_data.csv"
NUM_ROWS = 550


def random_email() -> str:
    name = random.choice(FIRST_NAMES)
    num = random.randint(1, 99)
    domain = random.choice(DOMAINS)
    return f"{name}{num}@{domain}"


def main() -> None:
    random.seed(42)

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days

    # Build a pool of ~40 customers for repeat purchases
    customer_pool = [random_email() for _ in range(40)]

    rows = []
    for _ in range(NUM_ROWS):
        date = start_date + timedelta(days=random.randint(0, date_range))
        product, base_price = random.choice(PRODUCTS)

        # Add slight price variation (+/- 10%)
        price = round(base_price * random.uniform(0.9, 1.1), 2)
        quantity = random.choices(
            [1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5]
        )[0]
        region = random.choice(REGIONS)
        email = random.choice(customer_pool)

        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "product": product,
            "quantity": quantity,
            "price": price,
            "region": region,
            "customer_email": email,
        })

    # Inject a few intentionally bad rows for validation testing
    rows.append({"date": "not-a-date", "product": "Bad Item", "quantity": 1, "price": 10.0, "region": "Europe", "customer_email": "valid@email.com"})
    rows.append({"date": "2024-06-15", "product": "Negative Qty", "quantity": -3, "price": 25.0, "region": "Asia Pacific", "customer_email": "ok@test.com"})
    rows.append({"date": "2024-07-20", "product": "Bad Email", "quantity": 2, "price": 15.0, "region": "Europe", "customer_email": "not-an-email"})
    rows.append({"date": "2024-08-10", "product": "Zero Price", "quantity": 1, "price": 0, "region": "North America", "customer_email": "zero@price.com"})

    random.shuffle(rows)

    with open(OUTPUT, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["date", "product", "quantity", "price", "region", "customer_email"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows -> {OUTPUT}")


if __name__ == "__main__":
    main()
