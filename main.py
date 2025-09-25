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
        pass

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

        # Initial welcome (If need be)

    def logout(self):
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
