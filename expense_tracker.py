#   Hello my name is Riham Khan and this is a Smart Expense Tracker I built using Tkinter for the interface 
#   and SQLite for storing data. It has tabs for adding expenses, viewing them, 
#   managing budgets, and visualizing trends with matplotlib. It's simple, 
#   responsive, and helps track spending easily.

# Imports and Initialization
import tkinter as tk
from tkinter import ttk, messagebox  # Tkinter components for UI and pop-ups
import sqlite3  # Database management
from datetime import datetime  # Date handling
import matplotlib.pyplot as plt  # Data visualization
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Embedding matplotlib in Tkinter
import pandas as pd  # Data manipulation (though not used in the code)
from tkcalendar import DateEntry  # Calendar widget for date selection


# Class Initialization
class ExpenseTracker:
    def __init__(self):
        self.root = tk.Tk()  # Initialize the main Tkinter window
        self.root.title("Smart Expense Tracker")  # Set window title
        self.root.geometry("800x600")  # Define window size
        
        self.init_database()  # Set up the SQLite database
        
        # Create a Notebook widget to organize tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True)
        
        # Initialize tabs for different functionalities
        self.add_expense_tab = ttk.Frame(self.notebook)
        self.view_expenses_tab = ttk.Frame(self.notebook)
        self.budget_tab = ttk.Frame(self.notebook)
        self.visualization_tab = ttk.Frame(self.notebook)
        
        # Add tabs to the notebook
        self.notebook.add(self.add_expense_tab, text="Add Expense")
        self.notebook.add(self.view_expenses_tab, text="View Expenses")
        self.notebook.add(self.budget_tab, text="Budget")
        self.notebook.add(self.visualization_tab, text="Visualize")
        
        # Set up the UI for each tab
        self.setup_add_expense_tab()
        self.setup_view_expenses_tab()
        self.setup_budget_tab()
        self.setup_visualization_tab()


    # Database Setup
    def init_database(self):
        # Connect to SQLite database (creates it if not existing)
        self.conn = sqlite3.connect('expenses.db')
        self.cursor = self.conn.cursor()
        
        # Create 'categories' table for expense categories
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                budget REAL
            )
        ''')
        
        # Create 'expenses' table to store expense records
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                amount REAL,
                category_id INTEGER,
                date DATE,
                description TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Insert default categories into 'categories' table
        default_categories = ['Groceries', 'Rent', 'Entertainment', 'Transportation', 'Clothes']
        for category in default_categories:
            try:
                self.cursor.execute('INSERT INTO categories (name, budget) VALUES (?, ?)', (category, 0.0))
            except sqlite3.IntegrityError:  # Skip if category already exists
                pass
        
        self.conn.commit()  # Save changes


    # Add Expense Tab
    def setup_add_expense_tab(self):
        # Input field for expense amount
        tk.Label(self.add_expense_tab, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.add_expense_tab)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Dropdown for selecting a category
        tk.Label(self.add_expense_tab, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.category_combo = ttk.Combobox(self.add_expense_tab, values=self.get_categories())
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Calendar widget for selecting a date
        tk.Label(self.add_expense_tab, text="Date:").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(self.add_expense_tab)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Input field for an expense description
        tk.Label(self.add_expense_tab, text="Description:").grid(row=3, column=0, padx=5, pady=5)
        self.description_entry = tk.Entry(self.add_expense_tab)
        self.description_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Button to submit the new expense
        tk.Button(self.add_expense_tab, text="Add Expense", command=self.add_expense).grid(row=4, column=0, columnspan=2, pady=20)


    # View Expenses Tab
    def setup_view_expenses_tab(self):
        # Table to display expense records
        self.expense_tree = ttk.Treeview(self.view_expenses_tab, columns=('Date', 'Category', 'Amount', 'Description'))
        self.expense_tree.heading('Date', text='Date')
        self.expense_tree.heading('Category', text='Category')
        self.expense_tree.heading('Amount', text='Amount')
        self.expense_tree.heading('Description', text='Description')
        
        # Scrollbar for the table
        scrollbar = ttk.Scrollbar(self.view_expenses_tab, orient="vertical", command=self.expense_tree.yview)
        self.expense_tree.configure(yscrollcommand=scrollbar.set)
        
        # Button to delete selected expense
        delete_btn = tk.Button(self.view_expenses_tab, text="Delete Selected", command=self.delete_expense)
        delete_btn.pack(pady=5)
        
        # Pack widgets into the tab
        self.expense_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.load_expenses()  # Load expense data


    # Budget Tab
    def setup_budget_tab(self):
        # Table to display budgets and remaining balances
        self.budget_tree = ttk.Treeview(self.budget_tab, columns=('Category', 'Budget', 'Spent', 'Remaining'))
        self.budget_tree.heading('Category', text='Category')
        self.budget_tree.heading('Budget', text='Budget')
        self.budget_tree.heading('Spent', text='Spent')
        self.budget_tree.heading('Remaining', text='Remaining')
        
        # Input fields for adding/updating a budget
        frame = ttk.Frame(self.budget_tab)
        tk.Label(frame, text="Category:").pack(side="left", padx=5)
        self.budget_category = ttk.Combobox(frame, values=self.get_categories())
        self.budget_category.pack(side="left", padx=5)
        
        tk.Label(frame, text="Budget:").pack(side="left", padx=5)
        self.budget_amount = tk.Entry(frame)
        self.budget_amount.pack(side="left", padx=5)
        
        # Button to set a new budget
        tk.Button(frame, text="Set Budget", command=self.set_budget).pack(side="left", padx=5)
        
        # Pack widgets into the tab
        self.budget_tree.pack(pady=10, fill="both", expand=True)
        frame.pack(pady=10)
        
        self.load_budgets()  # Load budget data


    # Deleting an Expense
    def delete_expense(self):
        # Get the selected expense item from the tree view
        selected_item = self.expense_tree.selection()
        
        # If no item is selected, show a warning message and exit
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
            
        # Confirm deletion with the user
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            item_id = selected_item[0]  # Retrieve the ID of the selected item
            
            # Delete the expense from the database using its ID
            self.cursor.execute('DELETE FROM expenses WHERE id = ?', (item_id,))
            self.conn.commit()  # Commit the changes
            
            # Remove the item from the tree view
            self.expense_tree.delete(item_id)
            
            # Refresh the expense table, budget table, and visualizations
            self.load_expenses()
            self.load_budgets()
            self.update_visualization('category')


    # Loading Expenses
    def load_expenses(self):
        # Clear the current expense entries from the tree view
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # Fetch all expense records from the database, joined with their categories
        self.cursor.execute('''
            SELECT expenses.id, expenses.date, categories.name, expenses.amount, expenses.description
            FROM expenses
            JOIN categories ON expenses.category_id = categories.id
            ORDER BY expenses.date DESC
        ''')
        
        # Populate the tree view with the retrieved data
        for row in self.cursor.fetchall():
            expense_id = row[0]  # Store the unique ID of the expense
            values = row[1:]  # Use the rest of the data for display
            self.expense_tree.insert('', 'end', iid=expense_id, values=values)


    # Loading Budgets
    def load_budgets(self):
        # Clear the current budget entries from the tree view
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
        
        # Query the database to calculate the spent amount per category for the current month
        self.cursor.execute('''
            SELECT 
                categories.name,  -- Category name
                categories.budget,  -- Budget allocated to the category
                COALESCE(SUM(expenses.amount), 0) as spent  -- Total spent amount (default to 0 if none)
            FROM categories
            LEFT JOIN expenses ON 
                categories.id = expenses.category_id
            GROUP BY categories.id, categories.name, categories.budget
        ''')
        
        # Populate the tree view with category, budget, spent, and remaining values
        for row in self.cursor.fetchall():
            category, budget, spent = row
            remaining = budget - spent if budget else 0  # Calculate remaining budget
            self.budget_tree.insert('', 'end', values=(
                category,
                f"${budget:.2f}",  # Format budget as currency
                f"${spent:.2f}",  # Format spent amount as currency
                f"${remaining:.2f}"  # Format remaining amount as currency
            ))


    # Visualization Tab
    def setup_visualization_tab(self):
        # Create a matplotlib figure for visualizations
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.visualization_tab)
        self.canvas.get_tk_widget().pack()
        
        # Buttons to switch between visualization types
        tk.Button(self.visualization_tab, text="Category Breakdown", 
                 command=lambda: self.update_visualization('category')).pack(pady=5)
        tk.Button(self.visualization_tab, text="Monthly Trend", 
                 command=lambda: self.update_visualization('monthly')).pack(pady=5)


    # Adding a New Expense
    def add_expense(self):
        try:
            # Get the input values from the form
            amount = float(self.amount_entry.get())  # Convert amount to float
            category = self.category_combo.get()  # Get selected category
            date = self.date_entry.get_date()  # Get selected date
            description = self.description_entry.get()  # Get description
            
            # Fetch the category ID corresponding to the selected category
            self.cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
            category_id = self.cursor.fetchone()[0]
            
            # Insert the new expense into the database
            self.cursor.execute('''
                INSERT INTO expenses (amount, category_id, date, description)
                VALUES (?, ?, ?, ?)
            ''', (amount, category_id, date, description))
            
            self.conn.commit()  # Commit the transaction
            messagebox.showinfo("Success", "Expense added successfully!")  # Success message
            
            # Clear the input fields after adding the expense
            self.amount_entry.delete(0, tk.END)
            self.category_combo.set('')
            self.description_entry.delete(0, tk.END)
            
            # Refresh the expense list, budget list, and visualization
            self.load_expenses()
            self.load_budgets()
            self.update_visualization('category')
            
        except ValueError:
            # Handle invalid input for amount
            messagebox.showerror("Error", "Please enter a valid amount")


    # Fetching Categories from Database
    def get_categories(self):
        # Query the database to retrieve all category names
        self.cursor.execute('SELECT name FROM categories')
        return [category[0] for category in self.cursor.fetchall()]  # Return the names as a list


    # Setting a Budget for a Category
    def set_budget(self):
        try:
            # Get input values from the form
            category = self.budget_category.get()  # Get selected category
            budget = float(self.budget_amount.get())  # Convert budget to float
            
            # Update the budget value for the selected category in the database
            self.cursor.execute('UPDATE categories SET budget = ? WHERE name = ?', 
                              (budget, category))
            self.conn.commit()  # Commit the transaction
            
            # Refresh the budget list
            self.load_budgets()
            messagebox.showinfo("Success", "Budget updated successfully!")  # Success message
            
            # Clear the input fields after setting the budget
            self.budget_amount.delete(0, tk.END)
            self.budget_category.set('')
            
        except ValueError:
            # Handle invalid input for budget
            messagebox.showerror("Error", "Please enter a valid budget amount")


    # Updating Visualizations
    def update_visualization(self, viz_type):
        self.ax.clear()  # Clear the current chart
        
        if viz_type == 'category':  # Visualization by category
            # Query the database for total expenses per category
            self.cursor.execute('''
                SELECT categories.name, SUM(expenses.amount)
                FROM expenses
                JOIN categories ON expenses.category_id = categories.id
                GROUP BY categories.name
            ''')
            data = self.cursor.fetchall()
            
            if data:
                labels = [row[0] for row in data]  # Extract category names
                sizes = [row[1] for row in data]  # Extract total amounts
                self.ax.pie(sizes, labels=labels, autopct='%1.1f%%')  # Create a pie chart
                self.ax.set_title('Expenses by Category')  # Set chart title
            
        elif viz_type == 'monthly':  # Visualization by monthly trend
            # Query the database for total expenses per month
            self.cursor.execute('''
                SELECT strftime('%Y-%m', date) as month, SUM(amount)
                FROM expenses
                GROUP BY month
                ORDER BY month
            ''')
            data = self.cursor.fetchall()
            
            if data:
                months = [row[0] for row in data]  # Extract months
                amounts = [row[1] for row in data]  # Extract total amounts
                self.ax.bar(months, amounts)  # Create a bar chart
                self.ax.set_title('Monthly Expense Trend')  # Set chart title
                plt.xticks(rotation=45)  # Rotate x-axis labels for readability
        
        # Redraw the canvas to display the updated chart
        self.canvas.draw()


    
    def run(self):
        # Start the main event loop of the Tkinter application
        self.root.mainloop()


if __name__ == "__main__":
    app = ExpenseTracker()  # Create an instance of the ExpenseTracker class
    app.run()  # Run the application
