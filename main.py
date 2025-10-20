import customtkinter as ctk
from tkinter import messagebox
import os
import json
from datetime import datetime as dt
import base64
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import ctypes

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
        self.masterPass = "password123"
        self.is_authenticated = False
        self.encryptionKey = None

        # Configure main window grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Create main container
        self.mainContainer = ctk.CTkFrame(self.root)
        self.mainContainer.grid(
            row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.mainContainer.grid_columnconfigure(0, weight=1)
        self.mainContainer.grid_rowconfigure(0, weight=1)

        # Password entries and data file
        self.passData = {}
        self.dataFile = 'files//passwords.dat'
        self.saltFile = 'files//salt.dat'
        self.masterFile = 'files//master.dat'

        # Search functionalities
        self.loadOrCreateSalt()

        # Search functionalities
        self.filterData = {}
        self.isSearchActive = False

        # Create the two pages
        self.setupLoginPage()
        self.setupMainPage()

        # Show login page initially
        self.showLoginPage()

    def loadOrCreateSalt(self):
        """Load existing salt or create new one for key derivation"""
        if os.path.exists(self.saltFile):
            with open(self.saltFile, 'rb') as f:
                self.salt = f.read()
        else:
            # Create new salt
            self.salt = os.urandom(16)
            os.makedirs(os.path.dirname(self.saltFile), exist_ok=True)
            with open(self.saltFile, 'wb') as f:
                f.write(self.salt)

    def deriveKey(self, password):
        """Derive encryption key from master password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

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

        # Load stored master password or use default
        storedMasterPass = self.loadMasterPass()
        if storedMasterPass is None:
            storedMasterPass = self.masterPass
            self.saveMasterPass(self.masterPass)

        if enteredPass == storedMasterPass:
            # Generate encryption key from the entered password
            self.encryptionKey = self.deriveKey(enteredPass)

            if self.encryptionKey is None:
                messagebox.showerror(
                    "Error", "Failed to initialize encryption!")
                return

            self.loadPass()
            self.is_authenticated = True
            self.currentMasterPass = enteredPass
            self.passEntry.delete(0, 'end')
            self.showMainPage()
            CustomDialog.showinfo(
                "Success", "Welcome! Vault unlocked, Milord", parent=self.root)
        else:
            messagebox.showerror("Error", "Incorrect password! Try again.")
            self.passEntry.delete(0, 'end')
            self.passEntry.focus()

    def loadMasterPass(self):
        """Load master password from encrypted file"""
        if not os.path.exists(self.masterFile):
            return None

        with open(self.masterFile, 'rb') as f:
            encryptedMasterPass = f.read()

        if not encryptedMasterPass:
            return None

        # Use a simpel key derived from the salt for master pass storage
        saltPadded = self.salt + b'\x00' * (32 - len(self.salt))
        simpleKey = base64.urlsafe_b64encode(saltPadded)
        fernet = Fernet(simpleKey)
        decryptedMasterPass = fernet.decrypt(encryptedMasterPass)
        return decryptedMasterPass.decode()

    def saveMasterPass(self, newMasterPass):
        """Save master password to encrypted file"""
        os.makedirs(os.path.dirname(self.masterFile), exist_ok=True)

        # FIX: Use proper salt padding to ensure 32 bytes
        saltPadded = self.salt + b'\x00' * (32 - len(self.salt))
        simpleKey = base64.urlsafe_b64encode(saltPadded)
        fernet = Fernet(simpleKey)
        encryptedMasterPass = fernet.encrypt(newMasterPass.encode())

        with open(self.masterFile, 'wb') as f:
            f.write(encryptedMasterPass)

        return True

    def setupMainPage(self):
        """Create the main page"""
        self.mainFrame = ctk.CTkFrame(self.mainContainer)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.mainFrame.grid_rowconfigure(0, weight=1)

        # Left Sidebar
        bottombar = ctk.CTkFrame(self.mainFrame, height=60)
        bottombar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        bottombar.grid_propagate(False)

        for i in range(6):
            bottombar.grid_columnconfigure(i, weight=1)

        # Menu buttons
        menuButtons = [
            "📝 Add Password",
            "🔑 Change Masterpass",
            "📤 Export Data"
        ]

        for i, buttonText in enumerate(menuButtons):
            button = ctk.CTkButton(
                bottombar,
                text=buttonText,
                height=40,
                font=ctk.CTkFont(size=14),
                command=lambda text=buttonText: self.bottomBarBtns(text)
            )
            button.grid(row=0, column=i+1, padx=15, pady=10, sticky="ew")

        # Lock button at bottom
        lockButton = ctk.CTkButton(
            bottombar,
            text="🔒 Lock Vault",
            command=self.logout,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="red",
            hover_color="darkred"
        )
        lockButton.grid(row=0, column=5, padx=15, pady=10, sticky="ew")

        # Main content area
        contentArea = ctk.CTkFrame(self.mainFrame)
        contentArea.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        contentArea.grid_columnconfigure(0, weight=1)
        contentArea.grid_rowconfigure(1, weight=1)

        # Header frame with title and search bar
        headerFrame = ctk.CTkFrame(contentArea, fg_color="transparent")
        headerFrame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        headerFrame.grid_columnconfigure(1, weight=1)

        # Content header
        contentHeader = ctk.CTkLabel(
            headerFrame,
            text="🎉 Welcome to SecureVault!",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        contentHeader.grid(row=0, column=0, sticky="w")

        # Search frame
        searchFrame = ctk.CTkFrame(headerFrame, fg_color="transparent")
        searchFrame.grid(row=0, column=2, sticky="e")

        # Search dropdown
        self.searchDropdown = ctk.CTkComboBox(
            searchFrame,
            values=["site", "username"],
            width=100,
            height=30
        )
        self.searchDropdown.grid(row=0, column=0, padx=(0, 5))
        self.searchDropdown.set("site")

        # Search entry
        self.searchEntry = ctk.CTkEntry(
            searchFrame,
            placeholder_text="Search ...",
            width=150,
            height=30
        )
        self.searchEntry.grid(row=0, column=1, padx=(0, 5))

        # Search button
        searchBtn = ctk.CTkButton(
            searchFrame,
            text="🔍",
            width=40,
            height=30,
            command=self.performSearch
        )
        searchBtn.grid(row=0, column=2)

        # Key bindings for search bar
        self.searchEntry.bind('<Return>', lambda event: self.performSearch())

        # Content body
        self.contentBody = ctk.CTkFrame(contentArea)
        self.contentBody.grid(
            row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.contentBody.grid_columnconfigure(0, weight=1)
        self.contentBody.grid_rowconfigure(0, weight=1)

        # Show existing pass
        self.displayPass()

    def logout(self):
        """Handle logout and clears encryption key"""
        result = messagebox.askyesno(
            "Confirm", "Are you sure you want to lock the Vault, Milord?")
        if result:
            self.is_authenticated = False
            self.encryptionKey = None
            self.passData = {}
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
        self.mainFrame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    def bottomBarBtns(self, buttonText):
        """Handle sidebar button clicks"""
        if buttonText == "📝 Add Password":
            self.showAddPassDialog()
        elif buttonText == "🔑 Change Masterpass":
            self.changeMasterPass()
        elif buttonText == "📤 Export Data":
            self.exportPass()
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

    def changeMasterPass(self):
        """Change master password"""
        dialog = ChangeMasterPasswordDialog(
            self.root, self.handleMasterPassChange)

    def handleMasterPassChange(self, currentPass, newPass):
        """Handle master password change"""
        # Verify current password
        storedMasterPass = self.loadMasterPass()
        if storedMasterPass is None:
            storedMasterPass = self.masterPass

        if currentPass != storedMasterPass:
            messagebox.showerror("Error", "Current password is incorrect!")
            return False

        # Derive new encryption key
        newEncryptionKey = self.deriveKey(newPass)

        # Save data with new encryption key
        jsonData = json.dumps(self.passData, indent=2)
        fernet = Fernet(newEncryptionKey)
        encryptedData = fernet.encrypt(jsonData.encode())

        # Save to file
        with open(self.dataFile, 'wb') as f:
            f.write(encryptedData)

        # Save new master password
        if self.saveMasterPass(newPass):
            # Update current session
            self.encryptionKey = newEncryptionKey
            self.currentMasterPass = newPass

            messagebox.showinfo(
                "Success", "Master password changed successfully!\nAll data has been re-encrypted with the new password.")
            return True
        else:
            return False

    def exportPass(self):
        """Export Passkeys in JSON file"""
        # Ask user confirmation
        result = messagebox.askyesno(
            "📤 Export Data", "Export all Passkeys to 'files/passwords.json'?")

        # Save to JSON file
        if result:
            with open('files/passwords.json', 'w') as j:
                json.dump(self.passData, j, indent=2)
            messagebox.showinfo(
                "Success", "All Pass Keys saved to 'files/passwords.json'")

    def addPassEntry(self, site, username, password, notes=""):
        """Add a new password entry and save to encrypted file"""
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
        """Load passwords from .dat file"""
        if not os.path.exists(self.dataFile):
            # print(f"{self.dataFile} not found. Initiating empty Dict...")
            self.passData = {}
            return

        with open(self.dataFile, 'rb') as f:
            encryptedData = f.read()

        if not encryptedData:
            # print(f"No encrypted data")
            self.passData = {}
            return

        # print(f"Encrypted Data: {encryptedData}")
        # Decrypt data
        fernet = Fernet(self.encryptionKey)
        decryptedData = fernet.decrypt(encryptedData)

        # Convert back to dictionary
        self.passData = json.loads(decryptedData.decode())

    def savePass(self):
        """Save passwords to JSON file"""
        # Create JSON file if it isn't created
        os.makedirs(os.path.dirname(self.dataFile), exist_ok=True)

        # Convert dictionary to JSON string
        jsonData = json.dumps(self.passData, indent=2)

        # Encrypt the JSON data
        fernet = Fernet(self.encryptionKey)
        encryptedData = fernet.encrypt(jsonData.encode())

        # Overwrite JSON with current data
        with open(self.dataFile, 'wb') as f:
            f.write(encryptedData)

    def displayPass(self):
        """Display stored passwords in the main content area"""
        # Clear current content
        for widget in self.contentBody.winfo_children():
            widget.destroy()

        # Determine which data to display
        self.dataToShow = self.filterData if self.isSearchActive else self.passData

        if not self.dataToShow:
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
        scrollableFrame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        scrollableFrame.grid_columnconfigure(0, weight=1)

        # Add header
        headerLabel = ctk.CTkLabel(
            scrollableFrame,
            text=f"Your Passwords ({len(self.dataToShow)} entries)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        headerLabel.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        for i, (entryID, data) in enumerate(self.dataToShow.items()):
            self.createPassItem(scrollableFrame, i+1, entryID, data)

    def createPassItem(self, parent, row, entryID, data):
        """Create a password item display"""
        # Main item frame
        itemFrame = ctk.CTkFrame(parent)
        itemFrame.grid(row=row, column=0, sticky="ew", padx=10, pady=3)
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
        usernameLabel.grid(row=1, column=1, sticky="ew",
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

        # UPDATE BUTTON - NEW
        updateBtn = ctk.CTkButton(
            buttonFrame,
            text="✏️ Update",
            width=70,
            height=30,
            command=lambda: self.updatePass(entryID, data),
            font=ctk.CTkFont(size=12),
            fg_color="orange",
            hover_color="darkorange"
        )
        updateBtn.pack(side="left", padx=2)

        # Delete button (to delete password)
        delBtn = ctk.CTkButton(
            buttonFrame,
            text="🗑️ Delete",
            width=80,
            height=30,
            command=lambda: self.delPass(entryID, data['site']),
            font=ctk.CTkFont(size=12),
            fg_color="red",
            hover_color="darkred"
        )
        delBtn.pack(side="left", padx=2)

    def viewPass(self, data):
        """Show password details"""
        details = f"Site: {data['site']}\n"
        details += f"Username: {data['username']}\n"
        details += f"Password: {data['password']}\n"
        if data.get('notes'):
            details += f"Notes: {data['notes']}\n"
        details += f"Created: {data['created'][:19]}"

        messagebox.showinfo("Password Details", details)

    def updatePass(self, entryID, currentData):
        """Update an existing password entry"""
        dialog = AddPasswordDialog(self.root, lambda site, username, password, notes: self.handlePassUpdate(
            entryID, site, username, password, notes), currentData)

    def handlePassUpdate(self, entryID, site, username, password, notes):
        """Handle the password update"""
        if entryID in self.passData:
            # Update the entry with new data
            self.passData[entryID].update({
                'site': site,
                'username': username,
                'password': password,
                'notes': notes,
                'modified': dt.now().isoformat()
            })

            # Save to encrypted file
            self.savePass()

            # Update the display
            self.displayPass()

            # Show success message
            messagebox.showinfo(
                "Success", f"Password for {site} updated successfully!")

    def delPass(self, entryID, siteName):
        """Delete a password entry"""
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the password for {siteName}?\n\nThis action cannot be undone!"
        )

        if result:
            # Remove from dictionary
            if entryID in self.passData:
                del self.passData[entryID]

                # Save updated data to encrypted file
                self.savePass()

                # Update the display
                self.displayPass()

                # Show success message
                messagebox.showinfo(
                    "Success", f"Password for {siteName} deleted successfully!")

    def performSearch(self):
        """Filter password data based on search criteria"""
        searchTerm = self.searchEntry.get().strip().lower()
        searchField = self.searchDropdown.get()

        if not searchTerm:
            # Empty search - show all data
            self.filterData = {}
            self.isSearchActive = False
            self.displayPass()
            return

        # Filter the data
        self.filterData = {}
        for entryID, data in self.passData.items():
            fieldValue = data.get(searchField, "").lower()
            if searchTerm in fieldValue:
                # print(f"Adding {entryID} to Filter Data")
                self.filterData[entryID] = data

        self.isSearchActive = True
        self.displayPass()

    def run(self):
        """Start the application"""
        self.root.mainloop()


class AddPasswordDialog:
    def __init__(self, parent, callBack, existingData=None):
        self.callBack = callBack
        self.existingData = existingData

        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)

        # Set title based on whether we're adding or updating
        if existingData:
            self.dialog.title("Update Password")
            dialogTitle = "✏️ Update Password"
        else:
            self.dialog.title("Add New Password")
            dialogTitle = "📝 Add New Password"

        self.dialog.geometry("450x550")
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry(
            "+%d+%d" % (parent.winfo_rootx()+175, parent.winfo_rooty()+100))

        # Main frame
        mainFrame = ctk.CTkFrame(self.dialog)
        mainFrame.pack(fill="both", expand=True, padx=5, pady=5)
        mainFrame.grid_columnconfigure(0, weight=1)

        # Title
        titleLabel = ctk.CTkLabel(
            mainFrame,
            text=dialogTitle,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titleLabel.grid(row=0, column=0, pady=(20, 30))

        # Site/Service field
        siteLabel = ctk.CTkLabel(
            mainFrame, text="Site/Service:", font=ctk.CTkFont(size=14, weight="bold"))
        siteLabel.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 5))

        self.siteEntry = ctk.CTkEntry(
            mainFrame,
            placeholder_text="e.g. Google, Facebook, GitHub",
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.siteEntry.grid(row=2, column=0, sticky="ew",
                            padx=20, pady=(0, 15))

        # Username field
        usernameLabel = ctk.CTkLabel(
            mainFrame, text="Username/Email:", font=ctk.CTkFont(size=14, weight="bold"))
        usernameLabel.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 5))

        self.usernameEntry = ctk.CTkEntry(
            mainFrame,
            placeholder_text="your.email@example.com",
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.usernameEntry.grid(
            row=4, column=0, sticky="ew", padx=20, pady=(0, 15))

        # Password field
        passwordLabel = ctk.CTkLabel(
            mainFrame, text="Password:", font=ctk.CTkFont(size=14, weight="bold"))
        passwordLabel.grid(row=5, column=0, sticky="w", padx=20, pady=(0, 5))

        self.passEntry = ctk.CTkEntry(
            mainFrame,
            placeholder_text="Enter password",
            show="*",
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.passEntry.grid(
            row=6, column=0, sticky="ew", padx=20, pady=(0, 15))

        # Notes field (optional)
        notesLabel = ctk.CTkLabel(
            mainFrame, text="Notes (Optional):", font=ctk.CTkFont(size=14, weight="bold"))
        notesLabel.grid(row=7, column=0, sticky="w", padx=20, pady=(0, 5))

        self.notesTextbox = ctk.CTkTextbox(
            mainFrame,
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.notesTextbox.grid(
            row=8, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Populate fields if updating existing entry
        if existingData:
            self.siteEntry.insert(0, existingData.get('site', ''))
            self.usernameEntry.insert(0, existingData.get('username', ''))
            self.passEntry.insert(0, existingData.get('password', ''))
            if existingData.get('notes'):
                self.notesTextbox.insert('1.0', existingData.get('notes', ''))

        # Buttons
        buttonFrame = ctk.CTkFrame(mainFrame, fg_color="transparent")
        buttonFrame.grid(row=9, column=0, pady=20)

        # Dynamic button text
        saveButtonText = "💾 Update Password" if existingData else "💾 Save Password"

        saveBtn = ctk.CTkButton(
            buttonFrame,
            text=saveButtonText,
            command=self.savePass,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        saveBtn.pack(side="left", padx=10)

        cancelBtn = ctk.CTkButton(
            buttonFrame,
            text="❌ Cancel",
            command=self.dialog.destroy,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray",
            hover_color="gray30"
        )
        cancelBtn.pack(side="left", padx=10)

        # Focus on first field
        self.siteEntry.focus()

    def savePass(self):
        """Save the password entry"""
        site = self.siteEntry.get().strip()
        username = self.usernameEntry.get().strip()
        password = self.passEntry.get().strip()
        notes = self.notesTextbox.get('1.0', 'end').strip()

        # Validation
        if not site or not username or not password:
            messagebox.showwarning(
                "Validation Error", "Please fill in the required fields!")
            return

        # Call the callback function
        self.callBack(site, username, password, notes)

        # Close dialog
        self.dialog.destroy()


class ChangeMasterPasswordDialog:
    def __init__(self, parent, callback):
        self.callback = callback

        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Change Master Password")
        self.dialog.geometry("450x480")
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry(
            "+%d+%d" % (parent.winfo_rootx()+175, parent.winfo_rooty()+150))

        # Main frame
        mainFrame = ctk.CTkFrame(self.dialog)
        mainFrame.pack(fill="both", expand=True, padx=10, pady=10)
        mainFrame.grid_columnconfigure(0, weight=1)

        # Title
        titleLabel = ctk.CTkLabel(
            mainFrame,
            text="🔑 Change Master Password",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titleLabel.grid(row=0, column=0, pady=(20, 30))

        # Warning message
        warningLabel = ctk.CTkLabel(
            mainFrame,
            text="⚠️ Warning: Changing your master password will re-encrypt all data.\nMake sure you remember the new password!",
            font=ctk.CTkFont(size=12),
            text_color=("orange", "yellow"),
            justify="center"
        )
        warningLabel.grid(row=1, column=0, pady=(0, 20))

        # Current password field
        currentLabel = ctk.CTkLabel(
            mainFrame,
            text="Current Master Password:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        currentLabel.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 5))

        self.currentEntry = ctk.CTkEntry(
            mainFrame,
            placeholder_text="Enter current password",
            show="*",
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.currentEntry.grid(
            row=3, column=0, sticky="ew", padx=20, pady=(0, 15))

        # New password field
        newLabel = ctk.CTkLabel(
            mainFrame,
            text="New Master password:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        newLabel.grid(row=4, column=0, sticky="w", padx=20, pady=(0, 5))

        self.newEntry = ctk.CTkEntry(
            mainFrame,
            placeholder_text="Enter new password",
            show="*",
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.newEntry.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 15))

        # Confirm new password field
        confirmLabel = ctk.CTkLabel(
            mainFrame,
            text="Confirm New Password:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        confirmLabel.grid(row=6, column=0, sticky="w", padx=20, pady=(0, 5))

        self.confirmEntry = ctk.CTkEntry(
            mainFrame,
            placeholder_text="Confirm new password",
            show="*",
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.confirmEntry.grid(
            row=7, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Buttons
        buttonFrame = ctk.CTkFrame(mainFrame, fg_color="transparent")
        buttonFrame.grid(row=8, column=0, pady=20)

        changeBtn = ctk.CTkButton(
            buttonFrame,
            text="🔑 Change Password",
            command=self.changePass,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        changeBtn.pack(side="left", padx=10)

        cancelBtn = ctk.CTkButton(
            buttonFrame,
            text="❌ Cancel",
            command=self.dialog.destroy,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray",
            hover_color="gray30"
        )
        cancelBtn.pack(side="left", padx=10)

        # Focus on first field
        self.currentEntry.focus()

    def changePass(self):
        """Validate and change password"""
        currentPass = self.currentEntry.get().strip()
        newPass = self.newEntry.get().strip()
        confirmPass = self.confirmEntry.get().strip()

        # Validation
        if not currentPass:
            messagebox.showwarning(
                "Validation Error", "Please enter your current password!")
            return

        if not newPass:
            messagebox.showwarning(
                "Validation Error", "Please enter a new password!")
            return

        if len(newPass) < 6:
            messagebox.showwarning(
                "Validation Error", "New password must be at least 6 characters long!")
            return

        if newPass != confirmPass:
            messagebox.showerror("Validation Error",
                                 "New passwords don't match!")
            return

        if currentPass == newPass:
            messagebox.showwarning(
                "Validation Error", "New password must be different from current password!")
            return

        # Attempt to change password
        if self.callback(currentPass, newPass):
            self.dialog.destroy()


class CustomDialog:
    """Custom CTkinter dialog"""

    @staticmethod
    def _apply_theme(dialog):
        """Apply dark theme to dialog title bar (Windows only)"""
        try:
            # Try to apply dark theme to title bar on Windows
            HWND = ctypes.windll.user32.GetParent(dialog.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                HWND,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int)
            )
        except:
            pass  # Silently fail on non-Windows or if API unavailable

    @staticmethod
    def _calculate_height(message, baseHeight=140, lineHeight=25):
        """Calculate dialog height based on message length"""
        # Estimate lines (assuming ~50 chars per line with wrapping)
        estimatedLines = max(1, len(message) // 50 + message.count('\n'))
        # Add height for each line beyond the first
        additionalHeight = max(0, (estimatedLines - 1) * lineHeight)
        return min(baseHeight + additionalHeight, 400)  # Cap at 400px

    @staticmethod
    def showinfo(title, message, parent=None):
        pass

    @staticmethod
    def showwarning(title, message, parent=None):
        pass

    @staticmethod
    def showerror(title, message, parent=None):
        pass

    @staticmethod
    def askyesno(title, message, parent=None):
        pass


def main():
    """Main function to run the password manager"""
    # Create and run the application
    app = BasicPasswordManager()
    app.run()


if __name__ == '__main__':
    main()
