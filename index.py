import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen

def connect_db():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    return conn, cursor

def create_tables():
    conn, cursor = connect_db()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY,
            name TEXT,
            business_type TEXT,
            address TEXT,
            phone TEXT,
            email TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            budget DECIMAL,
            status TEXT DEFAULT 'pending'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY,
            invoice_number TEXT UNIQUE,
            amount DECIMAL,
            status TEXT DEFAULT 'unpaid'
        )
    ''')

    conn.commit()
    conn.close()

create_tables()


class BaseModel:
    table_name = ""
    
    @classmethod
    def get_all(cls):
        conn, cursor = connect_db()
        cursor.execute(f"SELECT * FROM {cls.table_name}")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @classmethod
    def create(cls, **kwargs):
        conn, cursor = connect_db()
        columns = ', '.join(kwargs.keys())
        values = ', '.join(f"'{v}'" for v in kwargs.values())
        cursor.execute(f"INSERT INTO {cls.table_name} ({columns}) VALUES ({values})")
        conn.commit()
        conn.close()
    
    @classmethod
    def delete(cls, id):
        conn, cursor = connect_db()
        cursor.execute(f"DELETE FROM {cls.table_name} WHERE id = {id}")
        conn.commit()
        conn.close()

class Client(BaseModel):
    table_name = "clients"
    
    def __init__(self, name, business_type, address=None, phone=None, email=None):
        self.name = name
        self.business_type = business_type
        self.address = address
        self.phone = phone
        self.email = email
    
    def save(self):
        self.create(name=self.name, business_type=self.business_type, address=self.address, phone=self.phone, email=self.email)

class Project(BaseModel):
    table_name = "projects"
    
    def __init__(self, name, description, budget, status="pending"):
        self.name = name
        self.description = description
        self.budget = budget
        self.status = status
    
    def save(self):
        self.create(name=self.name, description=self.description, budget=self.budget, status=self.status)

class Invoice(BaseModel):
    table_name = "invoices"
    
    def __init__(self, invoice_number, amount, status="unpaid"):
        self.invoice_number = invoice_number
        self.amount = amount
        self.status = status
    
    def save(self):
        self.create(invoice_number=self.invoice_number, amount=self.amount, status=self.status)


class ClientScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10)
        
        back_button = Button(text="Back to Menu", size_hint=(1, None), height=40)
        back_button.bind(on_press=self.go_to_menu)
        layout.add_widget(back_button)

        self.name_input = TextInput(hint_text="Enter Name", size_hint=(1, None), height=50)
        self.business_type_input = TextInput(hint_text="Enter Business Type", size_hint=(1, None), height=50)
        layout.add_widget(self.name_input)
        layout.add_widget(self.business_type_input)
        
        add_button = Button(text="Add Client", size_hint=(1, None), height=40)
        add_button.bind(on_press=self.add_client)
        layout.add_widget(add_button)
        
        self.client_list = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.client_list.add_widget(self.grid)
        layout.add_widget(self.client_list)
        
        self.load_clients()
        
        self.add_widget(layout)
    
    def add_client(self, instance):
        name = self.name_input.text
        business_type = self.business_type_input.text
        if name and business_type:
            client = Client(name, business_type)
            client.save()
            self.name_input.text = ""
            self.business_type_input.text = ""
            self.load_clients()
    
    def load_clients(self):
        self.grid.clear_widgets()
        clients = Client.get_all()
        for client in clients:
            client_widget = BoxLayout(size_hint_y=None, height=40)
            client_widget.add_widget(Label(text=client[1]))
            client_widget.add_widget(Label(text=client[2]))
            delete_button = Button(text="Delete", size_hint_x=None, width=100)
            delete_button.bind(on_press=lambda btn, client_id=client[0]: self.delete_client(client_id))
            client_widget.add_widget(delete_button)
            self.grid.add_widget(client_widget)
    
    def delete_client(self, client_id):
        Client.delete(client_id)
        self.load_clients()

    def go_to_menu(self, instance):
        self.manager.current = "menu_screen"


class ProjectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10)
        
        back_button = Button(text="Back to Menu", size_hint=(1, None), height=40)
        back_button.bind(on_press=self.go_to_menu)
        layout.add_widget(back_button)
        
        self.name_input = TextInput(hint_text="Enter Project Name", size_hint=(1, None), height=50)
        self.description_input = TextInput(hint_text="Enter Project Description", size_hint=(1, None), height=50)
        self.budget_input = TextInput(hint_text="Enter Budget", size_hint=(1, None), height=50)
        self.status_input = TextInput(hint_text="Enter Status", size_hint=(1, None), height=50) 
        
        layout.add_widget(self.name_input)
        layout.add_widget(self.description_input)
        layout.add_widget(self.budget_input)
        layout.add_widget(self.status_input) 
        
        add_button = Button(text="Add Project", size_hint=(1, None), height=40)
        add_button.bind(on_press=self.add_project)
        layout.add_widget(add_button)
        
        self.project_list = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.project_list.add_widget(self.grid)
        layout.add_widget(self.project_list)
        
        self.load_projects()
        
        self.add_widget(layout)
    
    def add_project(self, instance):

        name = self.name_input.text
        description = self.description_input.text
        budget = self.budget_input.text
        status = self.status_input.text 
        
        if name and description and budget and status:
            try:
                project = Project(name=name, description=description, budget=float(budget), status=status)
                project.save()

                self.name_input.text = ""
                self.description_input.text = ""
                self.budget_input.text = ""
                self.status_input.text = "" 
                self.load_projects()
            except ValueError:
                print("Invalid budget value")
    
    def load_projects(self):
        self.grid.clear_widgets()
        projects = Project.get_all()

        for project in projects:
            print("Project Data:", project)
            
            project_name = str(project[2]) if project[2] is not None and project[2] != '' else "No Name"
            project_description = str(project[3]) if project[3] is not None else "No Description"
            
            print("Project Name:", project_name)
            print("Project Description:", project_description)
            
            try:
                project_budget = f"{float(project[4]):.2f}" if project[4] is not None else "0.00"
            except ValueError:
                project_budget = "0.00" 
            
            print("Project Budget:", project_budget)
            
            project_status = str(project[5]) if project[5] is not None else "No Status"
            
            print("Project Status:", project_status)
            
            project_widget = BoxLayout(size_hint_y=None, height=40)

            project_widget.add_widget(Label(text=project_name))
            project_widget.add_widget(Label(text=project_description))
            project_widget.add_widget(Label(text=project_budget))
            project_widget.add_widget(Label(text=project_status))
            
            delete_button = Button(text="Delete", size_hint_x=None, width=100)
            delete_button.bind(on_press=lambda btn, project_id=project[0]: self.delete_project(project_id))
            project_widget.add_widget(delete_button)
            
            self.grid.add_widget(project_widget)

    def delete_project(self, project_id):
        Project.delete(project_id)
        self.load_projects()

    def go_to_menu(self, instance):
        self.manager.current = "menu_screen"

class InvoiceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10)
        
        back_button = Button(text="Back to Menu", size_hint=(1, None), height=40)
        back_button.bind(on_press=self.go_to_menu)
        layout.add_widget(back_button)
        
        self.invoice_number_input = TextInput(hint_text="Enter Invoice Number", size_hint=(1, None), height=50)
        self.amount_input = TextInput(hint_text="Enter Amount", size_hint=(1, None), height=50)
        self.status_input = TextInput(hint_text="Enter Status", size_hint=(1, None), height=50)
        
        layout.add_widget(self.invoice_number_input)
        layout.add_widget(self.amount_input)
        layout.add_widget(self.status_input)  
        
        add_button = Button(text="Add Invoice", size_hint=(1, None), height=40)
        add_button.bind(on_press=self.add_invoice)
        layout.add_widget(add_button)
        
        self.invoice_list = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.invoice_list.add_widget(self.grid)
        layout.add_widget(self.invoice_list)
        
        self.load_invoices()
        
        self.add_widget(layout)
    
    def add_invoice(self, instance):
        invoice_number = self.invoice_number_input.text
        amount = self.amount_input.text
        status = self.status_input.text 
        if invoice_number and amount and status:
            try:
                invoice = Invoice(invoice_number=invoice_number, amount=float(amount), status=status)
                invoice.save()
                self.invoice_number_input.text = ""
                self.amount_input.text = ""
                self.status_input.text = ""
                self.load_invoices()
            except ValueError:
                print("Invalid amount value")
    
    def load_invoices(self):
        self.grid.clear_widgets()
        invoices = Invoice.get_all()
        
        for invoice in invoices:
            invoice_widget = BoxLayout(size_hint_y=None, height=40)
            
            invoice_number = str(invoice[3]) if invoice[3] is not None else "No Invoice Number"
            invoice_amount = f"{invoice[4]:.2f}" if invoice[4] is not None else "0.00"
            invoice_status = str(invoice[5]) if invoice[5] is not None else "Unknown"
            
            print("Invoice Number:", invoice_number)
            print("Invoice Amount:", invoice_amount)
            print("Invoice Status:", invoice_status)
            
            invoice_widget.add_widget(Label(text=invoice_number))
            invoice_widget.add_widget(Label(text=invoice_amount))
            invoice_widget.add_widget(Label(text=invoice_status))
            
            delete_button = Button(text="Delete", size_hint_x=None, width=100)
            delete_button.bind(on_press=lambda btn, invoice_id=invoice[0]: self.delete_invoice(invoice_id))
            invoice_widget.add_widget(delete_button)
            
            self.grid.add_widget(invoice_widget)


    
    def delete_invoice(self, invoice_id):
        Invoice.delete(invoice_id)
        self.load_invoices()

    def go_to_menu(self, instance):
        self.manager.current = "menu_screen"


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10)
        
        header_layout = BoxLayout(size_hint=(1, 0.7), padding=10)
        
        welcome_label = Label(text="Selamat Datang", size_hint=(1, 1), color=(1, 1, 1, 1), font_size=80, halign="center", valign="middle")
        header_layout.add_widget(welcome_label)
        
        layout.add_widget(header_layout)
        
        clients_button = Button(text="Clients", size_hint=(1, None), height=40)
        clients_button.bind(on_press=self.go_to_clients)
        layout.add_widget(clients_button)
        
        projects_button = Button(text="Projects", size_hint=(1, None), height=40)
        projects_button.bind(on_press=self.go_to_projects)
        layout.add_widget(projects_button)
        
        invoices_button = Button(text="Invoices", size_hint=(1, None), height=40)
        invoices_button.bind(on_press=self.go_to_invoices)
        layout.add_widget(invoices_button)
        
        self.add_widget(layout)
    
    def go_to_clients(self, instance):
        self.manager.current = "client_screen"
    
    def go_to_projects(self, instance):
        self.manager.current = "project_screen"
    
    def go_to_invoices(self, instance):
        self.manager.current = "invoice_screen"



class CRUDApp(App):
    def build(self):
        sm = ScreenManager()
        
        sm.add_widget(MenuScreen(name="menu_screen"))
        sm.add_widget(ClientScreen(name="client_screen"))
        sm.add_widget(ProjectScreen(name="project_screen"))
        sm.add_widget(InvoiceScreen(name="invoice_screen"))
        
        return sm

if __name__ == "__main__":
    CRUDApp().run()
