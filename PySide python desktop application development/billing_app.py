import sys
import mysql.connector
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QMessageBox
)
from datetime import date


# ---------------------- DB CONNECTION ----------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Use your own password if needed
        database="billing_app"
    )


# ---------------------- MAIN WINDOW ----------------------
class BillingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billing Form")

        # Form fields
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.details_input = QTextEdit()

        # Buttons
        self.submit_button = QPushButton("Add Bill")
        self.view_button = QPushButton("View Bills")

        # Connect buttons
        self.submit_button.clicked.connect(self.add_bill)
        self.view_button.clicked.connect(self.view_bills)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Customer Name"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Phone"))
        layout.addWidget(self.phone_input)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Amount"))
        layout.addWidget(self.amount_input)
        layout.addWidget(QLabel("Bill Details"))
        layout.addWidget(self.details_input)

        layout.addWidget(self.submit_button)
        layout.addWidget(self.view_button)

        self.setLayout(layout)

    def add_bill(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        amount = self.amount_input.text()
        details = self.details_input.toPlainText()

        if not (name and phone and email and amount):
            QMessageBox.warning(self, "Missing Info", "Please fill in all required fields.")
            return

        try:
            db = get_db_connection()
            cursor = db.cursor()

            # Check if customer exists
            cursor.execute("SELECT id FROM customers WHERE phone = %s", (phone,))
            result = cursor.fetchone()
            if result:
                customer_id = result[0]
            else:
                # Insert new customer
                cursor.execute("INSERT INTO customers (name, phone, email) VALUES (%s, %s, %s)",
                               (name, phone, email))
                customer_id = cursor.lastrowid

            # Insert bill
            cursor.execute("INSERT INTO bills (customer_id, date, amount, details) VALUES (%s, %s, %s, %s)",
                           (customer_id, date.today(), amount, details))

            db.commit()
            cursor.close()
            db.close()

            QMessageBox.information(self, "Success", "Bill added successfully.")
            self.clear_fields()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def view_bills(self):
        self.viewer = BillViewer()
        self.viewer.show()

    def clear_fields(self):
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.amount_input.clear()
        self.details_input.clear()


# ---------------------- BILL VIEWER ----------------------
class BillViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("View Bills")
        self.resize(700, 400)

        self.table = QTableWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        try:
            db = get_db_connection()
            cursor = db.cursor()

            cursor.execute("""
                SELECT b.id, c.name, c.phone, b.date, b.amount, b.details
                FROM bills b
                JOIN customers c ON b.customer_id = c.id
                ORDER BY b.date DESC
            """)
            records = cursor.fetchall()
            self.table.setRowCount(len(records))
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(["Bill ID", "Customer", "Phone", "Date", "Amount", "Details"])

            for row_idx, row_data in enumerate(records):
                for col_idx, item in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

            cursor.close()
            db.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ---------------------- APP START ----------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillingApp()
    window.show()
    sys.exit(app.exec())
s   