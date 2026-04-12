a="こんにちは"
b=len(a)
print(f"Before Reverse :\n{a}")
print("After Reverse :")
for i in range(-1,-(b+1),-1):
  print(a[i],end="")
  
"""
Result ;
Before Reverse :
こんにちは
After Reverse :
はちにんこ """
