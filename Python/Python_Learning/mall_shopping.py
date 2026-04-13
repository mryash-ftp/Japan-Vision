def mall_shopping(a, wallet):
    item_dict = {"Rice": 50, "Milk": 30, "Book": 25, "Sushi": 60, "Bento": 80}
    
    if a in item_dict:
        print(f"Yes! {a} is available. Do you want to buy it?\n[1] Yes\n[2] No")
        ask1 = input("Enter Choice: ")
        
        if ask1 == "1":
            price = item_dict[a]
            print(f"Product Price: {price} | Your Wallet: {wallet}")
            
            ask2 = input(f"Confirm purchase?\n[1] Yes\n[2] No\nEnter Choice: ")
            if ask2 == "1":
                qty = int(input("Enter Quantity: "))
                total_cost = price * qty
                
        
                if qty > 0 and wallet >= total_cost:
                    wallet -= total_cost  
                    print(f"{'-'*40}\nSuccessfully Purchased!\nProduct: {a}\nQuantity: {qty}\nTotal: {total_cost}\nRemaining Wallet: {wallet}\nThanks for shopping!")
                    return wallet
                else:
                    if qty <= 0:
                        print("Error: Minimum quantity should be 1.")
                    else:
                        print(f"Error: Low Balance! Required: {total_cost}, Available: {wallet}")
                    return wallet
            else:
                print("Purchase cancelled.")
                return wallet
        else:
            print("Have a nice day!")
            return wallet
    else:
        print("Sorry, item not available.")
        return wallet

print(f"{'-'*40}\n       Welcome Dear Customer\n{'-'*40}")
customer_wallet = 800
customer_choice = input("What do you want to buy? ").capitalize()


customer_wallet = mall_shopping(customer_choice, customer_wallet)
