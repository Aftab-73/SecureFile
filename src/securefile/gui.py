import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import platform

# Import logic from same package
from securefile.crypto import encrypt_bytes, decrypt_bytes
from securefile.steg import embed_bytes_into_png, extract_bytes_from_png

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_BG = "#0f172a"
COLOR_PANEL = "#1e293b"
COLOR_ACCENT = "#3b82f6"
COLOR_TEXT = "#f8fafc"

class EncodeView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLOR_BG)
        
        self.enc_in = ctk.StringVar()
        self.enc_cover = ctk.StringVar()
        self.enc_out = ctk.StringVar()
        self.enc_pass = ctk.StringVar()
        
        self.var_del = ctk.BooleanVar(value=False)
        self.var_hide = ctk.BooleanVar(value=False)

        # File Selectors
        self._make_row("1. Secret File:", self.enc_in, self._browse_in, 0)
        self._make_row("2. Cover Image (PNG):", self.enc_cover, self._browse_cover, 1)
        self._make_row("3. Output Image (PNG):", self.enc_out, self._browse_out, 2, is_save=True)

        # Password
        lbl = ctk.CTkLabel(self, text="4. Password:", font=("Inter", 14, "bold"), text_color=COLOR_TEXT)
        lbl.grid(row=3, column=0, padx=(20, 10), pady=(15, 5), sticky="e")
        ent = ctk.CTkEntry(self, textvariable=self.enc_pass, show="*", width=300, 
                           font=("Inter", 14), fg_color=COLOR_PANEL, border_color="#334155")
        ent.grid(row=3, column=1, padx=(0, 20), pady=(15, 5), sticky="w")

        # Options
        opt_frame = ctk.CTkFrame(self, fg_color="transparent")
        opt_frame.grid(row=4, column=0, columnspan=3, pady=(20, 10))
        ctk.CTkCheckBox(opt_frame, text="Delete original file", variable=self.var_del, text_color=COLOR_TEXT).pack(side="left", padx=10)
        ctk.CTkCheckBox(opt_frame, text="Hide output file (Win)", variable=self.var_hide, text_color=COLOR_TEXT).pack(side="left", padx=10)

        # Run Button
        self.btn_run = ctk.CTkButton(self, text="START ENCRYPTION", font=("Inter", 15, "bold"),
                                     fg_color=COLOR_ACCENT, hover_color="#2563eb", height=45,
                                     command=self.run_encode)
        self.btn_run.grid(row=5, column=0, columnspan=3, pady=(30, 20))

    def _make_row(self, label_text, var, cmd, row, is_save=False):
        lbl = ctk.CTkLabel(self, text=label_text, font=("Inter", 14, "bold"), text_color=COLOR_TEXT)
        lbl.grid(row=row, column=0, padx=(20, 10), pady=(15, 5), sticky="e")
        
        ent = ctk.CTkEntry(self, textvariable=var, width=300, font=("Inter", 12), 
                           fg_color=COLOR_PANEL, border_color="#334155")
        ent.grid(row=row, column=1, padx=(0, 10), pady=(15, 5), sticky="we")
        
        btn = ctk.CTkButton(self, text="Browse", width=80, fg_color="#334155", hover_color="#475569", command=cmd)
        btn.grid(row=row, column=2, padx=(0, 20), pady=(15, 5))

    def _browse_in(self):
        f = filedialog.askopenfilename()
        if f: self.enc_in.set(f)

    def _browse_cover(self):
        f = filedialog.askopenfilename(filetypes=[("PNG Images", "*.png")])
        if f: self.enc_cover.set(f)

    def _browse_out(self):
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Images", "*.png")])
        if f: self.enc_out.set(f)

    def run_encode(self):
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        f = self.enc_in.get()
        c = self.enc_cover.get()
        o = self.enc_out.get()
        p = self.enc_pass.get()
        
        if not all([f, c, o, p]):
            self.after(0, lambda: messagebox.showerror("Error", "All fields are required!"))
            return
            
        if not o.lower().endswith(".png"):
            self.after(0, lambda: messagebox.showerror("Error", "Output file must be a .png"))
            return
            
        self.after(0, lambda: self.btn_run.configure(state="disabled", text="PROCESSING...", fg_color="#475569"))
        try:
            with open(f, "rb") as file:
                data = file.read()
            encrypted = encrypt_bytes(data, p)
            embed_bytes_into_png(encrypted, c, o)
            
            if self.var_del.get():
                os.remove(f)
            if self.var_hide.get() and platform.system() == "Windows":
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(o, 0x02)
                
            self.after(0, lambda: messagebox.showinfo("Success", "File hidden securely!"))
            self.after(0, lambda: self.enc_pass.set(""))
        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror("Error", f"Encryption failed:\n{err}"))
        finally:
            self.after(0, lambda: self.btn_run.configure(state="normal", text="START ENCRYPTION", fg_color=COLOR_ACCENT))

class DecodeView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLOR_BG)

        self.dec_in = ctk.StringVar()
        self.dec_out = ctk.StringVar()
        self.dec_pass = ctk.StringVar()

        lbl = ctk.CTkLabel(self, text="1. Stego Image (PNG):", font=("Inter", 14, "bold"), text_color=COLOR_TEXT)
        lbl.grid(row=0, column=0, padx=(20, 10), pady=(30, 5), sticky="e")
        ctk.CTkEntry(self, textvariable=self.dec_in, width=300, font=("Inter", 12), fg_color=COLOR_PANEL, border_color="#334155").grid(row=0, column=1, padx=(0, 10), pady=(30, 5))
        ctk.CTkButton(self, text="Browse", width=80, fg_color="#334155", hover_color="#475569", command=self._browse_in).grid(row=0, column=2, padx=(0, 20), pady=(30, 5))

        lbl2 = ctk.CTkLabel(self, text="2. Save Recovered File As:", font=("Inter", 14, "bold"), text_color=COLOR_TEXT)
        lbl2.grid(row=1, column=0, padx=(20, 10), pady=(15, 5), sticky="e")
        ctk.CTkEntry(self, textvariable=self.dec_out, width=300, font=("Inter", 12), fg_color=COLOR_PANEL, border_color="#334155").grid(row=1, column=1, padx=(0, 10), pady=(15, 5))
        ctk.CTkButton(self, text="Browse", width=80, fg_color="#334155", hover_color="#475569", command=self._browse_out).grid(row=1, column=2, padx=(0, 20), pady=(15, 5))

        lbl3 = ctk.CTkLabel(self, text="3. Password:", font=("Inter", 14, "bold"), text_color=COLOR_TEXT)
        lbl3.grid(row=2, column=0, padx=(20, 10), pady=(15, 5), sticky="e")
        ctk.CTkEntry(self, textvariable=self.dec_pass, show="*", width=300, font=("Inter", 14), fg_color=COLOR_PANEL, border_color="#334155").grid(row=2, column=1, padx=(0, 20), pady=(15, 5), sticky="w")

        self.btn = ctk.CTkButton(self, text="DECRYPT NOW", font=("Inter", 15, "bold"), fg_color=COLOR_ACCENT, hover_color="#2563eb", height=45, command=self.run_decode)
        self.btn.grid(row=3, column=0, columnspan=3, pady=(40, 20))

    def _browse_in(self):
        f = filedialog.askopenfilename(filetypes=[("PNG Images", "*.png")])
        if f: self.dec_in.set(f)

    def _browse_out(self):
        f = filedialog.asksaveasfilename()
        if f: self.dec_out.set(f)

    def run_decode(self):
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        i = self.dec_in.get()
        o = self.dec_out.get()
        p = self.dec_pass.get()

        if not all([i, o, p]):
            self.after(0, lambda: messagebox.showerror("Error", "All fields are required!"))
            return
            
        self.after(0, lambda: self.btn.configure(state="disabled", text="WORKING...", fg_color="#475569"))
        try:
            data = extract_bytes_from_png(i)
            plaintext = decrypt_bytes(data, p)
            with open(o, "wb") as f:
                f.write(plaintext)
            self.after(0, lambda: messagebox.showinfo("Success", "File recovered successfully!"))
            self.after(0, lambda: self.dec_pass.set(""))
        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror("Error", f"Decryption failed:\n{err}"))
        finally:
            self.after(0, lambda: self.btn.configure(state="normal", text="DECRYPT NOW", fg_color=COLOR_ACCENT))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SecureFile - Steganography & Encryption")
        self.geometry("700x550")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)

        # Header
        hdr = ctk.CTkFrame(self, fg_color=COLOR_PANEL, height=80, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        title = ctk.CTkLabel(hdr, text="SecureFile Web Edition", font=("Inter", 24, "bold"), text_color=COLOR_TEXT)
        title.pack(side="left", padx=30, pady=20)

        # Tabs
        self.tabview = ctk.CTkTabview(self, fg_color=COLOR_BG, segmented_button_fg_color=COLOR_PANEL, 
                                      segmented_button_selected_color=COLOR_ACCENT,
                                      text_color=COLOR_TEXT,
                                      segmented_button_unselected_hover_color="#334155")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.tabview.add("ENCRYPT & HIDE")
        self.tabview.add("EXTRACT & DECRYPT")

        # Add Views
        self.view_enc = EncodeView(self.tabview.tab("ENCRYPT & HIDE"))
        self.view_enc.pack(fill="both", expand=True, pady=20)

        self.view_dec = DecodeView(self.tabview.tab("EXTRACT & DECRYPT"))
        self.view_dec.pack(fill="both", expand=True, pady=20)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()