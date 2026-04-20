import json

def secure(data):
    secure=int(input("🛡 Enter Your 4 Digit Pin:"))
    if secure==data["pin"]:
        print("🛡 Pin Verified ✔")
        return True
    else:
        return False
def atm_process(choice, data):
    if choice == 1 or choice == 2:
        if not secure(data):
            return "❌ Access Denied: Wrong Pin!"

    if choice == 1:
        return f"💰 Account Balance: {data['balance']}"
    
    elif choice == 2:
        amount = int(input("Enter Withdrawal Amount: "))
        if data["balance"] >= amount:
            data["balance"] -= amount
            save_data(data)
            return f"✅ Withdrawal Successful! New Balance: {data['balance']}"
        else:
            return "⚠️ Insufficient Funds!"
            
    elif choice == 3:
        mob=int(input("Enter last 4 digit mobile :"))
        if mob==int(str(current_data['mobile'])[-4:]):
            print(f"Depositing for {data['name']}...")
            deposit = int(input("Enter Deposit Amount: "))
            data["balance"] += deposit
            save_data(data)
            return f"💰 Deposit Successful! New Balance: {data['balance']}"
        else:
            print("Check Again Mobile Number Wrong")
def save_data(data):
    with open("card.json", "w") as f:
        json.dump(data, f, indent=4)

while True:

    with open("card.json", "r") as f:
        current_data = json.load(f)

    print("\n--- WELCOME TO ALVEN ATM ---")
    choice = int(input("[1]:Balance\n[2]:Withdraw\n[3]:Deposit\nEnter: "))
    
    result = atm_process(choice, current_data)
    print(result)

    stay = input("\n[1]:Main Menu\n[Any Key]:Exit\nEnter: ")
    if stay != "1":
        print("Have A Nice Day! 👋")
        break