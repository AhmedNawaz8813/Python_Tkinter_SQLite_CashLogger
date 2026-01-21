import sqlite3
import matplotlib.pyplot as plt
from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Main Log in Window Setup
root = Tk()
root.title('Login Page')
root.geometry('600x400') 
root.configure(background='grey')


#  profile page 
def show_profile(name):
    profile_label.config(text=f"Welcome, {name}!")
    profile_frame.pack(fill="both", expand=True)
    login_frame.pack_forget()
    

# Log in logic, using data base, to either create a new user, if registering, or retrieve data from database to check if user exists when logging in
def handle_login():
    email = email_input.get()
    password = password_input.get()

    conn = sqlite3.connect("Cash_Logger2.db")
    c = conn.cursor()
    c.execute("SELECT ID, name FROM User WHERE name=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()

    if user:
        user_id, name = user
        messagebox.showinfo('Login Successful', f'Welcome, {name}!')
        show_profile(name)
        root.destroy()
        add_expense_form(user_id,name) 
    else:
        messagebox.showerror('Login Failed', 'Incorrect Email or Password')


# Logic to handle registration
def handle_registration():
    email = email_input.get()
    password = password_input.get()

    conn = sqlite3.connect("Cash_Logger2.db")
    c = conn.cursor()
    c.execute("SELECT * FROM User WHERE name=?", (email,))
    existing_user = c.fetchone()

    if existing_user:
        messagebox.showerror("Error", "User already exists!")
    else:
        c.execute("INSERT INTO User (name, password) VALUES (?, ?)", (email, password))
        conn.commit()
        messagebox.showinfo("Success", f"User {email} Successfully Created")

    conn.close()

    #Adding Expense Data into Database
def submit(user_id, date_entry, amount_entry, category_entry, desc_entry, Display_Data):
    conn = sqlite3.connect("Cash_Logger2.db")
    c = conn.cursor()

    # Insert Expense ONLY if expense fields are filled
    if date_entry.get() and amount_entry.get() and category_entry.get():
        c.execute("INSERT INTO Expenses (User_ID, Date, Amount, Category, Description) VALUES (?, ?, ?, ?, ?)",
                  (user_id, date_entry.get(), amount_entry.get(), category_entry.get(), desc_entry.get()))
        messagebox.showinfo("Success", "Expense Added Successfully!")
        
        # Clear expense fields
        date_entry.delete(0, END)
        amount_entry.delete(0, END)
        category_entry.delete(0, END)
        desc_entry.delete(0, END)

    conn.commit()
    conn.close()



#Assisting function for the  visualize function, since calculated percentages were alittle off, and still are, but only by a small amount
def autopct_format(pct):
    return f'{round(pct)}%'

def visualize(name, user_id):
    conn = sqlite3.connect("Cash_Logger2.db")
    cursor = conn.cursor()

    # Retrieve total expenses of the user
    cursor.execute("SELECT SUM(amount) FROM Expenses WHERE user_id = ?", (user_id,))
    total_expenses = cursor.fetchone()[0]
    total_expenses = total_expenses if total_expenses is not None else 0  # Replace None with 0

    # Retrieve total income of the user
    cursor.execute("SELECT SUM(amount) FROM Income WHERE user_id = ?", (user_id,))
    total_income = cursor.fetchone()[0]
    total_income = total_income if total_income is not None else 0  # Replace None with 0

    conn.close()


    labels = ['Income', 'Expenses']
    values = [total_income, total_expenses]

   # Creating the pie chart for data visualization
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels,autopct='%1.0f%%'  , startangle=90, colors=['#4CAF50', '#FF5733'])
    ax.axis('equal') 

    
    pie_window = Toplevel()
    pie_window.title(f"Expenses & Income Statistics for {name}")
    
    
    canvas = FigureCanvasTkAgg(fig, master=pie_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)







    #Function to submit income data into database
def submit_income(Income_Entry, Source_Entry, Income_Date_Entry, user_id, Display_Data):
    conn = sqlite3.connect("Cash_Logger2.db")
    c = conn.cursor()


     # Insert Income into database, but only when user enters income data, ensuring no null values are stored
    if Income_Entry.get() and Source_Entry.get() and Income_Date_Entry.get():
        c.execute("INSERT INTO INCOME (User_ID , Amount, Source, Date) VALUES (?, ?, ?, ?)",
                  (user_id, Income_Entry.get(), Source_Entry.get(), Income_Date_Entry.get()))
        messagebox.showinfo("Success", "Income Added Successfully!")
        
        # Clear income fields
        Income_Entry.delete(0, END)
        Source_Entry.delete(0, END)
        Income_Date_Entry.delete(0, END)

        conn.commit()
        conn.close()



    # Assitance function for display data, retrieving expense data
def fetch_Data_From_Database(user_id):
    conn = sqlite3.connect("Cash_Logger2.db")
    c = conn.cursor()

    c.execute("Select ID , User_ID , Date , Amount , Category , Description from Expenses WHERE User_ID = ?", (user_id,))
    expenses = c.fetchall()

    c.close()

    return expenses


def fetch_Income_From_Database(user_id):
    conn = sqlite3.connect("Cash_Logger2.db")
    c = conn.cursor()
    c.execute("SELECT ID , User_ID , Amount , Source , Date FROM INCOME WHERE User_ID = ?", (user_id,))
    income = c.fetchall()
    conn.close()
    return income


    #Displaying data, retrieved from database
def Display_Data_Function(user_id, parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()

   
    parent_frame.grid_rowconfigure(0, weight=1) 
    parent_frame.grid_columnconfigure([0, 1, 2, 3, 4, 5], weight=1)  

    
    Label(parent_frame, text="Expense History", font=("Arial", 12, "bold"), bg="grey").grid(row=0, column=0, columnspan=6, pady=10, sticky="nsew")
    
    #Displaying Expense Data
    expense_data = fetch_Data_From_Database(user_id)
    if not expense_data:
        Label(parent_frame, text="No Expenses Available", font=("Arial", 12), bg="grey").grid(row=1, column=0, columnspan=6, pady=10)
    else:
        headers = ["ID", "User ID", "Date", "Amount", "Category", "Description"]
        for col, text in enumerate(headers):
            Label(parent_frame, text=text, font=("Arial", 10, "bold"), bg="grey", borderwidth=1, relief="solid").grid(row=1, column=col, sticky="nsew")
        for row_index, record in enumerate(expense_data, start=2):
            for col_index, value in enumerate(record):
                Label(parent_frame, text=value, bg="grey", borderwidth=1, relief="solid").grid(row=row_index, column=col_index, sticky="nsew")

    
    income_start_row = len(expense_data) + 3  # Add an extra row to separate the expense and income data

    # Displaying Income Data
    Label(parent_frame, text="Income History", font=("Arial", 12, "bold"), bg="grey").grid(row=income_start_row, column=0, columnspan=5, pady=10, sticky="nsew")
    
    
    income_data = fetch_Income_From_Database(user_id)
    if not income_data:
        Label(parent_frame, text="No Income Available", font=("Arial", 12), bg="grey").grid(row=income_start_row + 1, column=0, columnspan=5, pady=10)
        return
    
    headers_income = ["ID", "User ID", "Amount", "Source", "Date"]
    for col, text in enumerate(headers_income):
        Label(parent_frame, text=text, font=("Arial", 10, "bold"), bg="grey", borderwidth=1, relief="solid").grid(row=income_start_row + 1, column=col, sticky="nsew")
    
    for row_index, record in enumerate(income_data, start=income_start_row + 2):  # Start income data from the next row after header
        for col_index, value in enumerate(record):
            Label(parent_frame, text=value, bg="grey", borderwidth=1, relief="solid").grid(row=row_index, column=col_index, sticky="nsew")



#Refresh Button to display new data, if user just entered into database
def refresh(user_id, parent_frame):
    Display_Data_Function(user_id, parent_frame)
   


#Taking input from user, for expense, and income 
def add_expense_form(user_id,name):
    root2 = Tk()
    root2.title('Profile View')
    root2.geometry('900x700') 
    root2.configure(background='grey')


    register_container = Frame(root2, bg="grey", width=400, height=500)  
    register_container.pack(pady=20, padx=20, side=LEFT)  
    
    Display_data = Frame(root2, bg="white")
    Display_data.pack(side=TOP,padx=20,pady=20) 
    Display_data.configure(bg="white")

    
    register_container.columnconfigure(0, weight=1)  

    Label(register_container, text=f"Welcome, {name}!", bg="grey", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

    Label(register_container, text="Enter Expense Amount", bg="grey").grid(row=1, column=0, sticky="w", padx=10, pady=2)
    amount_entry = Entry(register_container, width=30)
    amount_entry.grid(row=2, column=0, sticky="w", padx=10, pady=5, ipady=4)

    Label(register_container, text="Enter Category for Expense", bg="grey").grid(row=3, column=0, sticky="w", padx=10, pady=2)
    category_entry = Entry(register_container, width=30)
    category_entry.grid(row=4, column=0, sticky="w", padx=10, pady=5, ipady=4)

    Label(register_container, text="Enter Description for Expense", bg="grey").grid(row=5, column=0, sticky="w", padx=10, pady=2)
    desc_entry = Entry(register_container, width=30)
    desc_entry.grid(row=6, column=0, sticky="w", padx=10, pady=5, ipady=4)

    Label(register_container, text="Enter Date for Expense (DD-MM-YY)", bg="grey").grid(row=7, column=0, sticky="w", padx=10, pady=2)
    date_entry = Entry(register_container, width=30)
    date_entry.grid(row=8, column=0, sticky="w", padx=10, pady=5, ipady=4)

    Frame(register_container, height=1, width=200, bg="Black", relief="sunken", bd=2).grid(row=9, column=0, sticky="w", padx=10, pady=2)

    Label(register_container, text="Enter Income Amount", bg="grey").grid(row=10, column=0, sticky="w", padx=10, pady=2)
    Income_Entry = Entry(register_container, width=30)
    Income_Entry.grid(row=11, column=0, sticky="w", padx=10, pady=5, ipady=4)

    Label(register_container, text="Enter Source of Income", bg="grey").grid(row=12, column=0, sticky="w", padx=10, pady=2)
    Source_Entry = Entry(register_container, width=30)
    Source_Entry.grid(row=13, column=0, sticky="w", padx=10, pady=5, ipady=4)

    Label(register_container, text="Enter Date for Income (DD-MM-YY)", bg="grey").grid(row=14, column=0, sticky="w", padx=10, pady=2)
    Income_Date_Entry = Entry(register_container, width=30)
    Income_Date_Entry.grid(row=15, column=0, sticky="w", padx=10, pady=5, ipady=4)

    Button(register_container, text="Add Income to Database", bg="grey", command=lambda:submit_income(Income_Entry, Source_Entry, Income_Date_Entry, user_id, Display_data)).grid(row=16, column=0, sticky="w", padx=10, pady=10)

    Button(register_container, text="Add Expense to Database",
           command=lambda: submit(user_id, date_entry, amount_entry, category_entry, desc_entry,Display_data), bg="grey").grid(
        row=17, column=0, sticky="w", padx=10, pady=10)

    show = Label(Display_data, text="Displaying Data", bg="grey", font=("Arial", 12, "bold"))
    show.grid(row=0, column=0,) 

    Button(register_container, text="View History", bg="grey", command=lambda: refresh(user_id, Display_data)).grid(row=18, column=0, sticky="w", padx=10, pady=10)

    Display_Data_Function(user_id, Display_data)
    Button(register_container, text="View Expenses & Income Statistics", command=lambda: visualize(name,user_id), bg="grey").grid(row=19, column=0, sticky="w", padx=10, pady=10)
    





# Main Page entries, and GUI
login_frame = Frame(root, bg="grey")
login_frame.pack(fill="both", expand=True)

original_image = Image.open(r"C:\Users\ahmed\Desktop\FAST\23P-0550_CS-4A\money.jpeg")
resized_image = original_image.resize((250, 250), Image.Resampling.LANCZOS)
image = ImageTk.PhotoImage(resized_image)
Label(login_frame, image=image, bg="grey").pack(side=RIGHT, padx=20)

login_container = Frame(login_frame, bg="grey")
login_container.pack(side=LEFT, padx=20)

Label(login_container, text='Expense Tracker', fg='black', bg='grey', font=('verdana', 25)).pack(pady=(10, 5))

Label(login_container, text='Enter Name', fg='black', bg='grey').pack(pady=(10, 2))
email_input = Entry(login_container, width=30)  #started out with entering 'email', changed it to name upon double checking assignment requirement
email_input.pack(pady=(2, 10), ipady=4)

Label(login_container, text='Enter Password', fg='black', bg='grey').pack(pady=(10, 2))
password_input = Entry(login_container, width=30, show="*")
password_input.pack(pady=(2, 10), ipady=4)

Button(login_container, text='Log in', bg='grey', fg='black', command=handle_login).pack(pady=(10, 5))
Button(login_container, text="Register", bg='grey', fg='black', command=handle_registration).pack(pady=(5, 5))
Frame(login_container, height=1, width=350, bg="white", relief="sunken", bd=2).pack(pady=(20, 10))
quit_button = Button(login_container, text="Quit Program", bg='RED', fg='black', command=root.quit, font=("Arial", 10, "bold"))
quit_button.pack(pady=(10, 10))

# Profile Frame
profile_frame = Frame(root, bg="lightgrey")
profile_label = Label(profile_frame, text="", font=("Verdana", 14), bg="lightgrey")
profile_label.pack(pady=20)


root.mainloop()