import subprocess
import os
import csv
import re
from datetime import datetime

LOG_DIR = "logs"

def log_action(action, disk, status):
    """Logs actions to a daily CSV."""
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime('%y%m%d')
    filepath = os.path.join(LOG_DIR, f"logs-{date_str}.csv")
    
    file_exists = os.path.isfile(filepath)
    with open(filepath, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Action", "Target", "Status"])
        writer.writerow([datetime.now().isoformat(), action, disk, status])

def run_cmd(cmd_list):
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError:
        return False, "Command 'diskutil' not found. Ensure you are running natively on macOS, not in a Linux Docker container."

def get_parsed_drives():
    """Returns separate lists for physical drives (formatting) and volumes (locking)."""
    success, output = run_cmd(["diskutil", "list", "external"])
    if not success:
        return ["Error fetching drives"], ["Error fetching volumes"]
    
    physical_drives = []
    apfs_volumes = []
    
    # Simple regex to grab lines that define a disk or volume
    lines = output.split('\n')
    for line in lines:
        if "/dev/disk" in line and "(external, physical)" in line:
            disk_id = re.search(r'/dev/disk\d+', line)
            if disk_id: physical_drives.append(disk_id.group())
        elif "Apple_APFS" in line or "APFS Volume" in line:
            # Look for synthesized volume IDs like disk3s1
            vol_id = re.search(r'disk\d+s\d+', line)
            if vol_id: apfs_volumes.append(f"/dev/{vol_id.group()}")
            
    if not physical_drives: physical_drives = ["No external physical drives found"]
    if not apfs_volumes: apfs_volumes = ["No external APFS volumes found"]
            
    return physical_drives, apfs_volumes

def format_and_encrypt(disk_id, volume_name, password):
    if not disk_id or "No" in disk_id: return False, "Invalid disk selected."
    
    # STEP 1: Format the physical drive to standard APFS
    # The macOS CLI requires "APFS" as the format personality string
    erase_cmd = ["diskutil", "eraseDisk", "APFS", volume_name, disk_id]
    success_erase, msg_erase = run_cmd(erase_cmd)
    
    if not success_erase:
        return False, f"Format Failed:\n{msg_erase}"
        
    # STEP 2: Extract the newly synthesized APFS volume ID (e.g., disk3s1) from the output
    # This prevents edge-case errors if you have two drives with the same name
    import re # Ensure this is at the top of your file
    match = re.search(r'Created new APFS Volume (disk\d+s\d+)', msg_erase)
    
    # Fallback to the mount path if regex misses for any reason
    target_volume = f"/dev/{match.group(1)}" if match else f"/Volumes/{volume_name}"
        
    # STEP 3: Apply military-grade AES encryption to the new volume
    encrypt_cmd = ["diskutil", "apfs", "encryptVolume", target_volume, "-user", "disk", "-passphrase", password]
    success_enc, msg_enc = run_cmd(encrypt_cmd)
    
    if not success_enc:
        log_action("Format & Encrypt", disk_id, "Partial Fail (Encryption step)")
        return False, f"Formatted to APFS, but encryption failed:\n{msg_enc}"
        
    log_action("Format & Encrypt", disk_id, "Success")
    return True, f"Success! Drive formatted and encrypted.\n\n[Erase Details]:\n{msg_erase}\n\n[Encryption Details]:\n{msg_enc}"

def lock_drive(volume_id):
    if not volume_id or "No" in volume_id: return False, "Invalid volume selected."
    cmd = ["diskutil", "unmount", volume_id]
    success, msg = run_cmd(cmd)
    log_action("Lock", volume_id, "Success" if success else "Failed")
    return success, msg

def unlock_drive(volume_id, password):
    if not volume_id or "No" in volume_id: return False, "Invalid volume selected."
    cmd = ["diskutil", "apfs", "unlockVolume", volume_id, "-passphrase", password]
    success, msg = run_cmd(cmd)
    log_action("Unlock", volume_id, "Success" if success else "Failed")
    return success, msg

def change_password(volume_id, old_password, new_password):
    if not volume_id or "No" in volume_id: return False, "Invalid volume selected."
    cmd = ["diskutil", "apfs", "changePassphrase", volume_id, "-oldpassphrase", old_password, "-newpassphrase", new_password]
    success, msg = run_cmd(cmd)
    log_action("Change Password", volume_id, "Success" if success else "Failed")
    return success, msg

def decrypt_drive(volume_id, current_password):
    if not volume_id or "No" in volume_id: return False, "Invalid volume selected."
    cmd = ["diskutil", "apfs", "decryptVolume", volume_id, "-passphrase", current_password]
    success, msg = run_cmd(cmd)
    log_action("Decrypt", volume_id, "Started" if success else "Failed")
    return success, msg