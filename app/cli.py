# app/cli.py

from app.records import count_by, get_by_id, load_records, search


def show(record):
    category = record.get("category", "scheme_rule")
    print(f"[{record.get('id')}] {record.get('scheme_name')} ({category})")
    print(f"    Eligible : {record.get('who_is_eligible')}")
    print(f"    Income   : {record.get('income_limit')}")
    print(f"    Limit    : {record.get('loan_limit')}")
    print(f"    Benefit  : {record.get('benefit')}")
    print(f"    Source   : {record.get('source_url')}\n")


def main():
    while True:
        print("\n1) Print all  2) Search  3) Count by category  4) Get by id  0) Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            for record in load_records():
                show(record)
        elif choice == "2":
            results = search(input("Keyword: "))
            print(f"{len(results)} result(s)\n")
            for record in results:
                show(record)
        elif choice == "3":
            for category, count in count_by("category").items():
                print(f"{category}: {count}")
        elif choice == "4":
            try:
                record = get_by_id(int(input("Id: ")))
            except ValueError:
                print("Please enter a number.")
                continue
            show(record) if record else print("Not found.")
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
