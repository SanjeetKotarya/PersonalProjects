import customtkinter as ctk
from customtkinter import CTkTextbox, CTkScrollbar
import threading
import subprocess
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# === CONFIGURATION ===
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_DRIVER_PATH = os.path.join(os.getcwd(), "chromedriver.exe")
USER_DATA_DIR = r"C:\chrome_debug"
DEBUG_PORT = "9222"

# Globals
driver = None
download_thread_running = False

# === FUNCTIONS ===
def launch_chrome():
    global driver
    url = url_entry.get().strip()
    # Ensure URL starts with http/https
    if url and not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    if not url:
        status_label.configure(text="Please enter a valid URL.", text_color="red")
        return

    print(f"[DEBUG] Navigating to URL: {url}")  # Debug output

    try:
        chrome_cmd = f'"{CHROME_PATH}" --remote-debugging-port={DEBUG_PORT} --user-data-dir="{USER_DATA_DIR}"'
        subprocess.Popen(chrome_cmd, shell=True)
        # Wait for Chrome to be ready (retry loop)
        max_retries = 5
        for attempt in range(max_retries):
            try:
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", f"localhost:{DEBUG_PORT}")
                service = Service(CHROME_DRIVER_PATH)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                break
            except Exception as e:
                print(f"[DEBUG] Waiting for Chrome to be ready... ({attempt+1}/{max_retries})")
                time.sleep(2)
        else:
            status_label.configure(text="Failed to connect to Chrome after several attempts.", text_color="red")
            return

        driver.get(url)
        time.sleep(3)

        link_elements = driver.find_elements(By.TAG_NAME, "a")
        download_links = [
            link.get_attribute("href")
            for link in link_elements
            if link.get_attribute("href") and ".rar" in link.get_attribute("href").lower()
        ]

        link_display.configure(state='normal')
        link_display.delete("1.0", "end")
        for i, link in enumerate(download_links, 1):
            part_name = os.path.basename(link)
            link_display.insert("end", f"{i}. {part_name}\n")
        link_display.configure(state='disabled')

        start_download.links = download_links
        status_label.configure(text=f"Found {len(download_links)} .rar files.", text_color="green")

    except Exception as e:
        status_label.configure(text=f"Error launching Chrome: {e}", text_color="red")

def start_download():
    global download_thread_running
    download_thread_running = True
    threading.Thread(target=download_links, daemon=True).start()

def download_links():
    global driver, download_thread_running
    links = getattr(start_download, 'links', [])

    if not links:
        status_label.configure(text="No links to download.", text_color="red")
        return

    try:
        for i, link in enumerate(links, 1):
            if not download_thread_running:
                status_label.configure(text="Download canceled.", text_color="orange")
                return

            try:
                print(f"[DEBUG] Opening link {i}: {link}")
                
                # Navigate directly to the link instead of opening new tab
                driver.get(link)
                time.sleep(3)  # Give page time to load

                # Click download button directly without waiting
                print("[DEBUG] Clicking DOWNLOAD button...")
                
                # Try multiple ways to find the download button
                download_btn = None
                try:
                    # Try different button selectors - starting with the most specific ones
                    selectors = [
                        "//button[@class='link-button text-5xl gay-button']",
                        "//button[contains(@class,'link-button')]",
                        "//button[contains(@class,'gay-button')]",
                        "//button[contains(text(),'DOWNLOAD')]",
                        "//button[contains(text(),'Download')]",
                        "//button[contains(text(),'download')]",
                        "//button[contains(@class,'download')]",
                        "//a[contains(text(),'DOWNLOAD')]",
                        "//a[contains(text(),'Download')]",
                        "//a[contains(@class,'download')]"
                    ]
                    
                    for selector in selectors:
                        try:
                            download_btn = driver.find_element(By.XPATH, selector)
                            print(f"[DEBUG] Found download button with selector: {selector}")
                            break
                        except:
                            continue
                    
                    if download_btn:
                        driver.execute_script("arguments[0].click();", download_btn)
                        time.sleep(2)
                    else:
                        print("[ERROR] No download button found with any selector")
                        continue
                        
                except Exception as e:
                    print(f"[ERROR] Error finding download button: {e}")
                    continue

                # Check if a new tab opened (ad popup)
                if len(driver.window_handles) > 1:
                    print("[DEBUG] Ad popup detected, closing and returning...")
                    try:
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(1)
                    except Exception as e:
                        print(f"[ERROR] Error handling popup: {e}")
                        # If popup handling fails, just continue
                        pass

                    # Click download button again (second time)
                    print("[DEBUG] Clicking DOWNLOAD button again...")
                    # Try to find the download button again for the second click
                    download_btn = None
                    for selector in selectors:
                        try:
                            download_btn = driver.find_element(By.XPATH, selector)
                            break
                        except:
                            continue
                    
                    if download_btn:
                        driver.execute_script("arguments[0].click();", download_btn)
                        time.sleep(2)
                    else:
                        print("[ERROR] Could not find download button for second click")

                status_label.configure(text=f"Downloaded {i}/{len(links)}", text_color="blue")

            except Exception as e:
                print(f"Error processing link {i}: {e}")
                continue

        status_label.configure(text="All downloads complete ✅", text_color="green")

    except Exception as e:
        print(f"Unexpected download error: {e}")
        status_label.configure(text="Download stopped.", text_color="orange")


def terminate_app():
    global driver, download_thread_running
    download_thread_running = False
    url_entry.delete(0, "end")
    link_display.configure(state='normal')
    link_display.delete("1.0", "end")
    link_display.configure(state='disabled')
    status_label.configure(text="Terminated and cleared input.", text_color="orange")

    if driver:
        handles = driver.window_handles
        if len(handles) > 1:
            main_handle = handles[0]
            for h in handles[1:]:
                driver.switch_to.window(h)
                driver.close()
            driver.switch_to.window(main_handle)

# === GUI ===
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title("FitGrab")
root.geometry("600x400")
root.resizable(False, False) 

ctk.CTkLabel(root, text="Works only for FuckingFast link page of FitGirl.", font=("Segoe UI", 14)).pack(pady=(15, 5))

# --- Top row: URL entry + Launch button side by side, full width ---
top_row = ctk.CTkFrame(root, fg_color="transparent")
top_row.pack(pady=10, padx=20, fill="x")

url_entry = ctk.CTkEntry(
    top_row,
    width=450,
    height=30,
    placeholder_text="Enter link of the page...",
    border_color="#3B82F6",      # e.g., soft blue
    border_width=1  
    )
url_entry.pack(side="left", padx=(0, 10))

launch_btn = ctk.CTkButton(
    top_row,
    text="Fetch Links",
    command=launch_chrome,
    width=150,
    height=30,
    fg_color="#3B82F6",
    hover_color="#2563EB",
    text_color="white"
    )
launch_btn.pack(side="left")

# --- Full width link display ---
textbox_frame = ctk.CTkFrame(root, fg_color="transparent")
textbox_frame.pack(padx=20, pady=10, fill="both", expand=True)

link_display = CTkTextbox(textbox_frame, height=100, width=560, corner_radius=10, font=("Consolas", 10))
link_display.pack(side="left", fill="both", expand=True)

scrollbar = CTkScrollbar(textbox_frame, command=link_display.yview)
scrollbar.pack(side="right", fill="y")

link_display.configure(yscrollcommand=scrollbar.set)
link_display.configure(state="disabled")  # Make it read-only

# Add placeholder text manually
link_display.configure(state="normal")  # Temporarily make it editable
link_display.insert("1.0", "Links will appear here after fetching...")
link_display.configure(state="disabled")  # Make it read-only again



# --- Middle row: Status and Start/Stop buttons side by side ---
middle_row = ctk.CTkFrame(root, fg_color="transparent")
middle_row.pack(pady=5, padx=20, fill="x")

status_label = ctk.CTkLabel(middle_row, text="", font=("Segoe UI", 12))
status_label.pack(side="left", padx=(0, 10), fill="x", expand=True)

start_btn = ctk.CTkButton(
    middle_row,
    text="Start Download",
    command=start_download,
    width=160, height=35,
    fg_color="#3B82F6",
    hover_color="#2563EB",
    text_color="white"
    )
start_btn.pack(side="left", padx=10)

terminate_btn = ctk.CTkButton(
    middle_row,
    text="Stop & Reset",
    command=terminate_app,
    width=160,
    height=35,
    fg_color="#3B82F6",
    hover_color="#2563EB",
    text_color="white"
    )
terminate_btn.pack(side="left")

root.mainloop()
