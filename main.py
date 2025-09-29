import customtkinter as ctk
from tkinter import messagebox
import os
import json
from datetime import datetime as dt

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BasicPasswordManager:
    def __init__(self):
        # Create main window
        self.root = ctk.CTk()
        self.root.title("🔐 SecureVault - Password Manager")
        self.root.geometry("800x700")

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

        # Password entries and data file
        self.passData = {}
        self.dataFile = 'files//passwords.json'
        self.loadPass()

    def setupLoginPage(self):
        """Create the login page"""
        self.loginFrame = ctk.CTkFrame(self.mainContainer)
        self.loginFrame.grid_columnconfigure(0, weight=1)
        self.loginFrame.grid_rowconfigure(0, weight=1)

        # Center contianer for login elements
        loginContainer = ctk.CTkFrame(self.loginFrame, width=400, height=350)
        loginContainer.grid(row=0, column=0)
        loginContainer.grid_propagate(False)
        loginContainer.grid_columnconfigure(0, weight=1)

        # App title
        titleLabel = ctk.CTkLabel(
            loginContainer,
            text="🔐 SecureVault",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        titleLabel.grid(row=0, column=0, pady=(40, 10))

        # Subtitle
        subtitleLabel = ctk.CTkLabel(
            loginContainer,
            text="Your Personal Password Manager, MiLord",
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray40")
        )
        subtitleLabel.grid(row=1, column=0, pady=(0, 30))

        # Login instruction
        instructionLabel = ctk.CTkLabel(
            loginContainer,
            text="Enter your master password to continue",
            font=ctk.CTkFont(size=14)
        )
        instructionLabel.grid(row=2, column=0, pady=(0, 20))

        # Password entry
        self.passEntry = ctk.CTkEntry(
            loginContainer,
            placeholder_text="Master Password",
            show="*",
            width=280,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.passEntry.grid(row=3, column=0, pady=(0, 20))

        # Login button
        loginButton = ctk.CTkButton(
            loginContainer,
            text="🔓 Unlock Vault",
            command=self.login,
            width=280,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        loginButton.grid(row=4, column=0, pady=(0, 20))

        # Bind Enter key to login
        self.passEntry.bind('<Return>', lambda event: self.login())

    def login(self):
        """Handle login attempt"""
        enteredPass = self.passEntry.get()

        if not enteredPass:
            messagebox.showwarning("Warning", "Please enter a password!")
            return

        if enteredPass == self.correctPass:
            self.is_authenticated = True
            self.passEntry.delete(0, 'end')
            self.showMainPage()
            messagebox.showinfo("Success", "Welcome! Vault unlocked, Milord")
        else:
            messagebox.showerror("Error", "Incorrect password! Try again.")
            self.passEntry.delete(0, 'end')
            self.passEntry.focus()

    def setupMainPage(self):
        """Create the main page"""
        self.mainFrame = ctk.CTkFrame(self.mainContainer)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.grid_rowconfigure(0, weight=1)

        # Left Sidebar
        sidebar = ctk.CTkFrame(self.mainFrame, width=250)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)

        # Sidebar Label
        sidebarLabel = ctk.CTkLabel(
            sidebar,
            text="🔐 SecureVault",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        sidebarLabel.grid(row=0, column=0, padx=20, pady=(20, 20))

        # Welcome message
        welcomeLabel = ctk.CTkLabel(
            sidebar,
            text="Welcome! Vault is unlocked, MiLord!",
            font=ctk.CTkFont(size=14),
            text_color=("green", "lightgreen")
        )
        welcomeLabel.grid(row=1, column=0, padx=20, pady=(0, 30))

        # Menu buttons
        menuButtons = [
            "📝 Add Password",
            "🔍 Search Passwords",
            "🎲 Generate Password",
            "📊 Password Health",
            "📤 Export Data",
            "⚙️ Settings"
        ]

        for i, buttonText in enumerate(menuButtons):
            button = ctk.CTkButton(
                sidebar,
                text=buttonText,
                height=40,
                font=ctk.CTkFont(size=14),
                command=lambda text=buttonText: self.sideBarBtns(text)
            )
            button.grid(row=2+i, column=0, padx=20, pady=5, sticky="ew")

        # Lock button at bottom
        lockButton = ctk.CTkButton(
            sidebar,
            text="🔒 Lock Vault",
            command=self.logout,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="red",
            hover_color="darkred"
        )
        lockButton.grid(row=10, column=0, padx=20, pady=(30, 20), sticky="ew")

        # Main content area
        contentArea = ctk.CTkFrame(self.mainFrame)
        contentArea.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        contentArea.grid_columnconfigure(0, weight=1)
        contentArea.grid_rowconfigure(1, weight=1)

        # Content header
        contentHeader = ctk.CTkLabel(
            contentArea,
            text="🎉 Welcome to SecureVault!",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        contentHeader.grid(row=0, column=0, padx=30, pady=(30, 20))

        # Content body
        self.contentBody = ctk.CTkFrame(contentArea)
        self.contentBody.grid(
            row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        self.contentBody.grid_columnconfigure(0, weight=1)
        self.contentBody.grid_rowconfigure(0, weight=1)

        # Show existing pass
        self.displayPass()

    def logout(self):
        """Handle logout"""
        result = messagebox.askyesno(
            "Confirm", "Are you sure you want to lock the Vault, Milord?")
        if result:
            self.is_authenticated = False
            self.showLoginPage()
            messagebox.showinfo("Locked", "Vault has been locked, Milord!")

    def showLoginPage(self):
        """Display the login page"""
        # Hide main page
        if hasattr(self, 'mainFrame'):
            self.mainFrame.grid_remove()

        # Show login page
        self.loginFrame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Focus on password entry
        self.passEntry.focus()

    def showMainPage(self):
        """Display the main page"""
        # Hide login page
        self.loginFrame.grid_remove()

        # Show main page
        self.mainFrame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    def sideBarBtns(self, buttonText):
        """Handle sidebar button clicks"""
        if buttonText == "📝 Add Password":
            self.showAddPassDialog()
        else:
            # Clear current content
            for widget in self.contentBody.winfo_children():
                widget.destroy()

            # Show placeholder for other features
            placeholderLabel = ctk.CTkLabel(
                self.contentBody,
                text=f"🚧 {buttonText}\n\nThis feature will be implemented soon!",
                font=ctk.CTkFont(size=16),
                justify="center"
            )
            placeholderLabel.grid(row=0, column=0, padx=40, pady=40)

    def showAddPassDialog(self):
        """Show add password dialog"""
        dialog = AddPasswordDialog(self.root, self.addPassEntry)

    def addPassEntry(self, site, username, password, notes=""):
        """Add a new password entry"""
        entryID = f"pwd_{len(self.passData)+1}"

        # Create password entry
        passEntry = {
            'site': site,
            'username': username,
            'password': password,
            'notes': notes,
            'created': dt.now().isoformat(),
            'modified': dt.now().isoformat()
        }

        # Add to data
        self.passData[entryID] = passEntry

        # Save to file
        self.savePass()

        # Show success message
        messagebox.showinfo(
            "Success", f"Password for {site} added successfully!")

        # Update the main display
        self.displayPass()

    def loadPass(self):
        """Load passwords from JSON file"""
        if os.path.exists(self.dataFile):
            with open(self.dataFile, 'r') as j:
                self.passData = json.load(j)
        else:
            self.passData = {}

    def savePass(self):
        """Save passwords to JSON file"""
        with open(self.dataFile, 'w') as f:
            json.dump(self.passData, f, indent=2)

    def displayPass(self):
        """Display stored passwords in the main content area"""
        # Clear current content
        for widget in self.contentBody.winfo_children():
            widget.destroy()

        if not self.passData:
            # Show empty state
            emptyLabel = ctk.CTkLabel(
                self.contentBody,
                text="No passwords stored yet.\n\nChlick 'Add Password' to get started!",
                font=ctk.CTkFont(size=16),
                text_color=("gray60", "gray40")
            )
            emptyLabel.grid(row=0, column=0, padx=40, pady=40)
            return

        # Create scrollable frame for password list
        scrollableFrame = ctk.CTkScrollableFrame(self.contentBody)
        scrollableFrame.grid(row=0, column=0, padx=40, pady=40)
        scrollableFrame.grid_columnconfigure(0, weight=1)

        # Add header
        headerLabel = ctk.CTkLabel(
            scrollableFrame,
            text=f"Your Passwords ({len(self.passData)} entries)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        headerLabel.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        for i, (entryID, data) in enumerate(self.passData.items()):
            self.createPassItem(scrollableFrame, i+1, entryID, data)

    def createPassItem(self, parent, row, entryID, data):
        """Create a password item display"""
        # Main item frame
        itemFrame = ctk.CTkFrame(parent)
        itemFrame.grid(row=row, column=0, sticky="ew", padx=20, pady=5)
        itemFrame.grid_columnconfigure(1, weight=1)

        # Site icon
        iconLabel = ctk.CTkLabel(
            itemFrame, text="🌐", font=ctk.CTkFont(size=20))
        iconLabel.grid(row=0, column=0, rowspan=2, padx=15, pady=10)

        # Site name
        siteLabel = ctk.CTkLabel(
            itemFrame,
            text=data['site'],
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        siteLabel.grid(row=0, column=1, sticky="ew",
                       padx=(0, 10), pady=(10, 0))

        # Username
        usernameLabel = ctk.CTkLabel(
            itemFrame,
            text=data['username'],
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40"),
            anchor="w"
        )
        usernameLabel.grid(row=1, column=1, stick="ew",
                           padx=(0, 10), pady=(10, 0))

        # Action buttons
        buttonFrame = ctk.CTkFrame(itemFrame, fg_color="transparent")
        buttonFrame.grid(row=0, column=2, rowspan=2, padx=10, pady=10)

        # View button (to show password)
        viewBtn = ctk.CTkButton(
            buttonFrame,
            text="👁️ View",
            width=80,
            height=30,
            command=lambda: self.viewPass(data),
            font=ctk.CTkFont(size=12)
        )
        viewBtn.pack(side="left", padx=2)

    def viewPass(self, data):
        """Show password details"""
        details = f"Site: {data['state']}\n"
        details += f"Username: {data['username']}\n"
        details += f"Password: {data['password']}\n"
        if data.get('notes'):
            details += f"Notes: {data['notes']}\n"
        details += f"Created: {data['created'][:19]}"

        messagebox.showinfo("Password Details", details)

    def run(self):
        """Start the application"""
        self.root.mainloop()


class AddPasswordDialog:
    def __init__(self):
        pass


def main():
    """Main function to run the password manager"""
    # Create and run the application
    app = BasicPasswordManager()
    app.run()


if __name__ == '__main__':
    main()
