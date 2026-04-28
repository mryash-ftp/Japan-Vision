import tkinter as tk
from tkinter import messagebox
import pyperclip # pip install pyperclip

def generate_message():
    # .upper() lagane se naam hamesha CAPITAL rahega
    name = entry_name.get().strip().upper() 
    if not name:
        messagebox.showwarning("Input Error", "Please enter Customer Name")
        return
    
    shop = "RAJ PHOTO COPY CENTER"
    phone = "9140041393"

    if lang_var.get() == "Hindi":
        msg = (f"Your PAN Card is Ready! / आपका पैन कार्ड तैयार है!\n\n"
               f"नमस्ते {name},\n\n"
               f"बधाई हो! आपका पैन कार्ड सफलतापूर्वक बन गया है और आपका डिजिटल पैन (e-PAN) जारी कर दिया गया है।\n\n"
               f"✅ अटैचमेंट: आपके पैन कार्ड की PDF फाइल इस मैसेज के साथ भेजी जा रही है।\n"
               f"✅ डाक द्वारा: आपका असली प्लास्टिक पैन कार्ड जल्द ही आपके रजिस्टर्ड पते पर डाक (Post) द्वारा पहुंच जाएगा।\n"
               f"✅ संपर्क: आप अपनी शॉप पर आकर भी इसकी प्रिंटेड कॉपी ले सकते हैं या किसी भी अन्य जानकारी के लिए हमसे मिल सकते हैं।\n\n"
               f"Regards,\n{shop}\n{phone}")
    else:
        msg = (f"Your PAN Card is Ready! / आपका पैन कार्ड तैयार है!\n\n"
               f"Dear {name},\n\n"
               f"Congratulations! Your PAN Card application has been successfully processed and your digital PAN (e-PAN) has been generated.\n\n"
               f"✅ Attached: Please find the PDF copy of your PAN Card.\n"
               f"✅ Physical Copy: Your original plastic PAN card will be delivered to your registered address via Post (Dak) shortly.\n"
               f"✅ Collection: You can also visit our shop to collect your printed copy or for any further help.\n\n"
               f"Regards,\n{shop}\n{phone}")

    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, msg)

def copy_to_clipboard():
    message = output_box.get(1.0, tk.END).strip()
    if not message:
        messagebox.showwarning("Error", "Pehle message generate karein!")
        return
    pyperclip.copy(message)
    messagebox.showinfo("Success", "Message copy ho gaya! Ab WhatsApp par paste karein.")

def clear_all():
    entry_name.delete(0, tk.END)
    output_box.delete(1.0, tk.END)
    entry_name.focus()

# GUI Setup
root = tk.Tk()
root.title("Raj Photo Copy - PAN Notifier Pro")
root.geometry("600x680")
root.configure(bg="#0f172a")

# Header
tk.Label(root, text="PAN NOTIFICATION SYSTEM", font=("Segoe UI", 18, "bold"), fg="#38bdf8", bg="#0f172a").pack(pady=20)

# Input
tk.Label(root, text="Customer Name:", fg="white", bg="#0f172a").pack()
entry_name = tk.Entry(root, font=("Segoe UI", 12), width=35, bg="#1e293b", fg="white", insertbackground="white", justify="center")
entry_name.pack(pady=10)

# Language
lang_var = tk.StringVar(value="Hindi")
tk.Radiobutton(root, text="Hindi (हिंदी)", variable=lang_var, value="Hindi", fg="#38bdf8", bg="#0f172a", selectcolor="#1e293b").pack()
tk.Radiobutton(root, text="English", variable=lang_var, value="English", fg="#38bdf8", bg="#0f172a", selectcolor="#1e293b").pack()

# Buttons
btn_frame = tk.Frame(root, bg="#0f172a")
btn_frame.pack(pady=20)

tk.Button(btn_frame, text="GENERATE", command=generate_message, bg="#38bdf8", fg="black", font=("Segoe UI", 10, "bold"), width=12).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="COPY", command=copy_to_clipboard, bg="#f472b6", fg="black", font=("Segoe UI", 10, "bold"), width=12).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="CLEAR", command=clear_all, bg="#94a3b8", fg="black", font=("Segoe UI", 10, "bold"), width=12).grid(row=0, column=2, padx=5)

# Output
output_box = tk.Text(root, height=15, width=65, font=("Segoe UI", 9), bg="#1e293b", fg="#cbd5e1", padx=10, pady=10)
output_box.pack(pady=10)

root.mainloop()
