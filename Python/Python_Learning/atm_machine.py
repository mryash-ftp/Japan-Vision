import json
while True:
    def menu(user):
        if user==1:
          pin=int(input("Enter Your 4 Digit Pin :"))
          with open("card.json", "r") as f:
             data = json.load(f)
          if pin==data["pin"]:
             with open("card.json", "r") as f:
                 data = json.load(f)
            
             return f"Account balance : {data["balance"]}" 
          else:
               return "Enter Correct Security Pin"
              
        elif user==2:
         pin=int(input("Enter Your 4 Digit Pin :"))
         with open("card.json", "r") as f:
             data = json.load(f)
         if pin==data["pin"]:
             withdraw = int(input("Enter amount to withdraw: "))
             if data["balance"] >= withdraw:
              data["balance"] = data["balance"] - withdraw

              with open("card.json", "w") as f:
                     json.dump(data,f,indent=4)
              with open("card.json", "r") as f:
                 data = json.load(f)
              print("Withdrawal Successful!") 
              return f"New Balance:{data["balance"]}"
             else:
                 return "Insufficient Funds!"
         else:
             return "Enter Correct Security Pin" 
        
        elif user==3:
         deposit=int(input("Enter Your Deposit Amount:"))
         with open("card.json", "r") as f:
             data = json.load(f)
             data["balance"] = data["balance"] + deposit

         with open("card.json", "w") as f:
                     json.dump(data,f,indent=4)
    
        print( "Deposit Successful!")
        with open("card.json", "r") as f:
             data = json.load(f)
        return f"New Balance:{data["balance"]}"
        
    choice = int(input("[1]:Balance\n[2]:Withdraw\n[3]:Deposit\nEnter: "))
    vari=menu(choice)
    print(vari)
    Return=input(f"Choise [1]:Menu\n[2]:Exit\nEnter:")
    if Return!="1":
        print("Have A Nice Day")
        break;
