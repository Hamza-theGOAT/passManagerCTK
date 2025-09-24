import customtkinter as ctk
from tkinter import messagebox

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BasicPasswordManager:
    def __init__(self):
        # Create main window
        self.root = ctk.CTk()
        self.root.title("🔐 SecureVault - Password Manager")
        self.root.geometry("800x600")

        # Using hardcoded pass initially
        self.correctPass = "password123"
        self.is_authenticated = False

        # Configure main window grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Create main container
        self.mainContainer = ctk.CTkFrame(self.root)
        self.mainContainer.grid(
            row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.mainContainer.grid_columnconfigure(0, weight=1)
        self.mainContainer.grid_rowconfigure(0, weight=1)

        # Create the two pages
        self.setupLoginPage()
        self.setupMainPage()

        # Show login page initially
        self.showLoginPage()

    def setupLoginPage(self):
        pass

    def setupMainPage(self):
        pass

    def showLoginPage(self):
        pass

    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main function to run the password manager"""
    # Create and run the application
    app = BasicPasswordManager()
    app.run()


if __name__ == '__main__':
    main()
