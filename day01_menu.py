# VidyaLoan - Day 01 Menu System

while True:

    print("\n========== VIDYALOAN MENU ==========")

    print("1. About VidyaLoan")
    print("2. Sample Questions")
    print("3. Check Basic Loan Eligibility")
    print("0. Exit")

    print("====================================")

    choice = input("Enter your choice: ")

    # Option 1
    if choice == "1":

        print("\n--- ABOUT VIDYALOAN ---")

        print("VidyaLoan is a student loan assistance platform.")
        print("It provides education loan information.")
        print("It helps students understand basic eligibility.")

    # Option 2
    elif choice == "2":

        print("\n--- SAMPLE QUESTIONS ---")

        print("1. What is an education loan?")
        print("2. What documents are required?")
        print("3. Who can apply for a student loan?")
        print("4. How can I check loan eligibility?")

    # Option 3
    elif choice == "3":

        print("\n--- BASIC ELIGIBILITY CHECK ---")

        income = float(input("Enter monthly family income: "))
        credit_score = int(input("Enter credit score: "))

        # Sample eligibility rule
        if income >= 15000 and credit_score >= 650:

            print("Basic sample criteria are satisfied.")

        elif income >= 15000 and credit_score < 650:

            print("Income criteria satisfied.")
            print("Credit score is below the sample threshold.")

        else:

            print("Monthly income is below the sample threshold.")

        print("Note: Actual loan approval depends on the bank.")

    # Option 0
    elif choice == "0":

        print("\nThank you for using VidyaLoan!")
        print("Exiting program...")

        break

    # Invalid option
    else:

        print("\nInvalid choice!")
        print("Please enter 1, 2, 3 or 0.")