list1=[5,7,2,6,9,8]
list2=[10,11,12,4,9]

new_list1=[]
new_list2=[]

# List1 EVEN
for i in list1:
    if i%2==0:
        new_list1.append(i)
        
# List2 ODD
for x in list2:
    if x%2!=0:
        new_list2.append(x)

final_list = new_list1 + new_list2
print("Final merged:", final_list)
