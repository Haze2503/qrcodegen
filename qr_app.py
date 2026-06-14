import qrcode
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
import os

APP_NAME = "QR Studio"
APP_DATA_DIR = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "QRStudio")
os.makedirs(APP_DATA_DIR, exist_ok=True)
SETTINGS_FILE = os.path.join(APP_DATA_DIR, "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            if "theme" not in data:
                data["theme"] = "dark"
            if "last_dir" not in data:
                data["last_dir"] = ""
            return data
    return {"last_dir": "", "theme": "dark"}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

settings = load_settings()

THEMES = {
    "dark": {
        "bg": "#0f1117",
        "panel": "#171b24",
        "panel_alt": "#1d2430",
        "field": "#0f1520",
        "text": "#f4f7fb",
        "muted": "#98a2b3",
        "qr_fill": "#111827",
        "accent": "#7c5cff",
        "accent_hover": "#6950e6",
        "success": "#3bd671",
        "danger": "#ff6b7a",
        "qr_bg": "#ffffff",
        "button_text": "#ffffff",
        "input_insert": "#f4f7fb",
    },
    "light": {
        "bg": "#eef2ff",
        "panel": "#ffffff",
        "panel_alt": "#f7f8fc",
        "field": "#ffffff",
        "text": "#172033",
        "muted": "#667085",
        "qr_fill": "#172033",
        "accent": "#3f63ff",
        "accent_hover": "#2f53e6",
        "success": "#0ea65b",
        "danger": "#d92d20",
        "qr_bg": "#ffffff",
        "button_text": "#ffffff",
        "input_insert": "#172033",
    },
}


def get_theme():
    return THEMES.get(settings.get("theme", "dark"), THEMES["dark"])


def set_status(message, kind="neutral"):
    theme = get_theme()
    colors = {
        "neutral": theme["muted"],
        "success": theme["success"],
        "error": theme["danger"],
    }
    status.configure(text=message, fg=colors.get(kind, theme["muted"]))


def render_preview(img):
    preview_size = 320
    preview_img = img.resize((preview_size, preview_size))
    tk_img = ImageTk.PhotoImage(preview_img)
    qr_label.configure(image=tk_img, text="")
    qr_label.image = tk_img


def apply_theme():
    theme = get_theme()
    root.configure(bg=theme["bg"])
    canvas.configure(bg=theme["bg"], highlightthickness=0)
    canvas.itemconfigure(bg_card, fill=theme["panel"])
    canvas.itemconfigure(accent_blob, fill=theme["accent"])
    canvas.itemconfigure(accent_blob_2, fill=theme["accent_hover"])

    for widget in (title, subtitle, section_input, section_preview):
        widget.configure(bg=theme["panel"], fg=theme["text"])

    subtitle.configure(fg=theme["muted"])
    status.configure(bg=theme["panel_alt"], fg=theme["muted"])
    entry.configure(
        bg=theme["field"],
        fg=theme["text"],
        insertbackground=theme["input_insert"],
        highlightbackground=theme["accent"],
        highlightcolor=theme["accent"],
    )
    qr_frame.configure(bg=theme["panel_alt"])
    qr_label.configure(bg=theme["panel_alt"], fg=theme["muted"])
    theme_button.configure(
        bg=theme["panel_alt"],
        fg=theme["text"],
        activebackground=theme["accent_hover"],
        activeforeground=theme["button_text"],
    )
    generate_button.configure(
        bg=theme["accent"],
        fg=theme["button_text"],
        activebackground=theme["accent_hover"],
        activeforeground=theme["button_text"],
    )
    save_button.configure(
        bg=theme["success"],
        fg=theme["button_text"],
        activebackground="#28b95d",
        activeforeground=theme["button_text"],
    )
    clear_button.configure(
        bg=theme["panel_alt"],
        fg=theme["text"],
        activebackground=theme["accent_hover"],
        activeforeground=theme["button_text"],
    )


def refresh_theme_label():
    theme_button.configure(text=("☀ Light mode" if settings.get("theme", "dark") == "dark" else "☾ Dark mode"))


def toggle_theme():
    settings["theme"] = "light" if settings.get("theme", "dark") == "dark" else "dark"
    save_settings(settings)
    refresh_theme_label()
    apply_theme()
    if hasattr(root, "generated_img"):
        render_preview(root.generated_img)

def generate_qr():
    url = entry.get().strip()
    if not url:
        set_status("Please enter text or URL", "error")
        return

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    theme = get_theme()
    img = qr.make_image(fill_color=theme["qr_fill"], back_color=theme["qr_bg"]).convert("RGB")

    render_preview(img)
    set_status("QR preview generated", "success")

    root.generated_img = img


def clear_qr():
    entry.delete(0, tk.END)
    qr_label.configure(image="", text="Your QR preview will appear here")
    qr_label.image = None
    if hasattr(root, "generated_img"):
        delattr(root, "generated_img")
    set_status("Ready to generate", "neutral")

def save_qr():
    if not hasattr(root, "generated_img"):
        messagebox.showerror("Error", "Generate QR first")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        initialdir=settings["last_dir"],
        filetypes=[("PNG Image", "*.png")]
    )

    if file_path:
        root.generated_img.save(file_path)
        settings["last_dir"] = os.path.dirname(file_path)
        save_settings(settings)
        set_status("QR code saved successfully", "success")

# ---------------- UI ----------------
root = tk.Tk()
root.title(APP_NAME)
root.geometry("620x720")
root.minsize(620, 720)
root.resizable(False, False)

theme = get_theme()

canvas = tk.Canvas(root, width=620, height=720, highlightthickness=0, bg=theme["bg"])
canvas.pack(fill="both", expand=True)

canvas.create_oval(-120, -80, 220, 260, fill=theme["accent"], outline="")
canvas.create_oval(430, 560, 760, 880, fill=theme["accent_hover"], outline="")
bg_card = canvas.create_rectangle(28, 28, 592, 692, fill=theme["panel"], outline="")
accent_blob = canvas.create_oval(38, 38, 120, 120, fill=theme["accent"], outline="")
accent_blob_2 = canvas.create_oval(514, 40, 580, 106, fill=theme["accent_hover"], outline="")

card = tk.Frame(root, bg=theme["panel"])
canvas.create_window(310, 360, window=card, width=520, height=620)

header = tk.Frame(card, bg=theme["panel"])
header.pack(fill="x", padx=8, pady=(6, 18))

title = tk.Label(header, text="QR Studio", font=("Segoe UI", 24, "bold"), bg=theme["panel"], fg=theme["text"])
title.pack(anchor="w")

subtitle = tk.Label(
    header,
    text="Generate clean QR codes with a polished preview and instant theme switching.",
    font=("Segoe UI", 10),
    bg=theme["panel"],
    fg=theme["muted"],
    wraplength=470,
    justify="left",
)
subtitle.pack(anchor="w", pady=(6, 0))

theme_button = tk.Button(card, text="", command=toggle_theme, font=("Segoe UI", 10, "bold"), bd=0, relief="flat", padx=14, pady=10, cursor="hand2")
theme_button.pack(anchor="e", padx=8, pady=(0, 8))

section_input = tk.Label(card, text="Text or URL", font=("Segoe UI", 11, "bold"), bg=theme["panel"], fg=theme["text"])
section_input.pack(anchor="w", padx=8)

entry = tk.Entry(card, font=("Segoe UI", 12), width=42, bd=0, relief="flat", highlightthickness=1)
entry.pack(fill="x", padx=8, pady=(8, 18))
entry.insert(0, "https://example.com")

actions_row = tk.Frame(card, bg=theme["panel"])
actions_row.pack(fill="x", padx=8, pady=(0, 18))

generate_button = tk.Button(actions_row, text="Generate Preview", command=generate_qr, font=("Segoe UI", 11, "bold"), bd=0, relief="flat", padx=18, pady=12, cursor="hand2")
generate_button.pack(side="left", expand=True, fill="x", padx=(0, 8))

clear_button = tk.Button(actions_row, text="Clear", command=clear_qr, font=("Segoe UI", 11, "bold"), bd=0, relief="flat", padx=18, pady=12, cursor="hand2")
clear_button.pack(side="left", padx=(8, 8))

save_button = tk.Button(actions_row, text="Download QR Code", command=save_qr, font=("Segoe UI", 11, "bold"), bd=0, relief="flat", padx=18, pady=12, cursor="hand2")
save_button.pack(side="left")

section_preview = tk.Label(card, text="Preview", font=("Segoe UI", 11, "bold"), bg=theme["panel"], fg=theme["text"])
section_preview.pack(anchor="w", padx=8)

qr_frame = tk.Frame(card, bg=theme["panel_alt"], highlightthickness=1)
qr_frame.pack(fill="x", padx=8, pady=(8, 18))
qr_frame.configure(width=360, height=360)
qr_frame.pack_propagate(False)
qr_label = tk.Label(qr_frame, text="Your QR preview will appear here", font=("Segoe UI", 11), bg=theme["panel_alt"], fg=theme["muted"], justify="center")
qr_label.place(relx=0.5, rely=0.5, anchor="center")

status = tk.Label(card, text="Ready to generate", font=("Segoe UI", 10), bg=theme["panel_alt"], fg=theme["muted"], anchor="w", padx=14, pady=10)
status.pack(fill="x", padx=8, pady=(6, 0))

refresh_theme_label()
apply_theme()

root.mainloop()
