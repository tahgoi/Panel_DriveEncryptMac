import panel as pn
from utils import encrypt

pn.extension()

# --- Initial Data Fetch ---
phys_drives, apfs_vols = encrypt.get_parsed_drives()

# --- UI Components ---
title = pn.pane.Markdown("# 🔒 macOS APFS Encryption Manager")
refresh_btn = pn.widgets.Button(name="Refresh Drive Lists", button_type="primary")
console_output = pn.widgets.TextAreaInput(name="Console Output", height=200, disabled=True)

# 1. Lock/Unlock Tab Widgets (Dedicated Instances)
lock_volume_dropdown = pn.widgets.Select(name="APFS Volume", options=apfs_vols)
lock_password_input = pn.widgets.PasswordInput(name="Password", placeholder="Enter password")
unlock_btn = pn.widgets.Button(name="Unlock Volume", button_type="success")
lock_btn = pn.widgets.Button(name="Lock Volume", button_type="warning")

# 2. Manage Password Tab Widgets (Dedicated Instances)
manage_volume_dropdown = pn.widgets.Select(name="APFS Volume", options=apfs_vols)
manage_password_input = pn.widgets.PasswordInput(name="Current Password", placeholder="Enter password")
new_password_input = pn.widgets.PasswordInput(name="New Password", placeholder="Enter new password")
change_pass_btn = pn.widgets.Button(name="Change Password", button_type="primary")
delete_pass_btn = pn.widgets.Button(name="Remove Encryption", button_type="danger")

# 3. Format Tab Widgets (Dedicated Instances)
physical_dropdown = pn.widgets.Select(name="Physical Disk (For Formatting)", options=phys_drives)
format_name = pn.widgets.TextInput(name="New Volume Name", placeholder="SecretDrive")
format_password_input = pn.widgets.PasswordInput(name="Encryption Password", placeholder="Enter password")
format_btn = pn.widgets.Button(name="Format & Encrypt", button_type="danger")

# --- Callbacks ---
def update_console(success, msg):
    status = "✅ SUCCESS" if success else "❌ ERROR"
    console_output.value = f"{status}:\n{msg}\n\n{console_output.value}"

def on_refresh(event):
    p_drives, a_vols = encrypt.get_parsed_drives()
    
    # Update ALL dropdowns across all tabs
    physical_dropdown.options = p_drives
    lock_volume_dropdown.options = a_vols
    manage_volume_dropdown.options = a_vols

def on_format(event):
    success, msg = encrypt.format_and_encrypt(physical_dropdown.value, format_name.value, format_password_input.value)
    update_console(success, msg)
    on_refresh(None) # Auto-refresh lists after formatting

def on_unlock(event):
    success, msg = encrypt.unlock_drive(lock_volume_dropdown.value, lock_password_input.value)
    update_console(success, msg)

def on_lock(event):
    success, msg = encrypt.lock_drive(lock_volume_dropdown.value)
    update_console(success, msg)

def on_change_pass(event):
    success, msg = encrypt.change_password(manage_volume_dropdown.value, manage_password_input.value, new_password_input.value)
    update_console(success, msg)

def on_delete_pass(event):
    success, msg = encrypt.decrypt_drive(manage_volume_dropdown.value, manage_password_input.value)
    update_console(success, msg)

# --- Bind Callbacks ---
refresh_btn.on_click(on_refresh)
format_btn.on_click(on_format)
unlock_btn.on_click(on_unlock)
lock_btn.on_click(on_lock)
change_pass_btn.on_click(on_change_pass)
delete_pass_btn.on_click(on_delete_pass)

# --- Layout ---
layout = pn.Column(
    title,
    refresh_btn,
    pn.layout.Divider(),
    pn.Tabs(
        ("Lock / Unlock", pn.Column(
            lock_volume_dropdown, lock_password_input,
            pn.Row(unlock_btn, lock_btn)
        )),
        ("Manage Password", pn.Column(
            manage_volume_dropdown, manage_password_input, new_password_input,
            pn.Row(change_pass_btn, delete_pass_btn)
        )),
        ("Format & Provision", pn.Column(
            pn.pane.Markdown("**WARNING**: This wipes the entire physical drive selected."),
            physical_dropdown, format_name, format_password_input,
            format_btn
        ))
    ),
    pn.layout.Divider(),
    console_output
)

layout.servable()