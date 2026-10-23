"""Nickles setup wizard: one window, Next / Back, does everything (the work itself is in setup_engine.py).

    python setup_wizard.py                       # the wizard
    python setup_wizard.py --unattended file.json  # no window: the settings come from the file (keys as in setup_engine.DEFAULT_SETTINGS)
"""
import json
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import setup_engine as se


def choose_defaults():
    x = se.find_xampp() or r"C:\xampp"
    s = dict(se.DEFAULT_SETTINGS)
    s.update({"xampp_dir": se.find_xampp(), "web_dir": os.path.join(x, "htdocs", "nickles"), "public_url": "http://localhost/nickles",
              "btcshop_dir": os.path.join(x, "htdocs", "btcshop") if os.path.isdir(os.path.join(x, "htdocs", "btcshop")) else ""})
    if os.path.exists(os.path.join(se.HERE, "wallet.json")):
        s["wallet_mode"] = "keep"      # never replace a wallet by default
    return s


class Wizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nickles Setup")
        self.geometry("720x560")
        self.minsize(640, 520)
        self.vars = {}
        self.settings = choose_defaults()
        self.page_index = 0
        self.running = False
        self.result = None

        self.header = tk.Label(self, text="", font=("Segoe UI", 15, "bold"), anchor="w", padx=20, pady=12)
        self.header.pack(fill="x")
        ttk.Separator(self).pack(fill="x")
        self.body = tk.Frame(self, padx=20, pady=10)
        self.body.pack(fill="both", expand=True)
        ttk.Separator(self).pack(fill="x")
        bar = tk.Frame(self, padx=20, pady=10)
        bar.pack(fill="x")
        self.cancel_btn = ttk.Button(bar, text="Cancel", command=self.on_cancel)
        self.cancel_btn.pack(side="left")
        self.next_btn = ttk.Button(bar, text="Next >", command=self.next)
        self.next_btn.pack(side="right")
        self.back_btn = ttk.Button(bar, text="< Back", command=self.back)
        self.back_btn.pack(side="right", padx=6)

        self.pages = [("Welcome", self.p_welcome), ("System check", self.p_system), ("Database", self.p_database),
                      ("You and your wallet", self.p_people), ("Your company and the advertiser contract", self.p_operator),
                      ("Where to publish", self.p_publish), ("Ready to install", self.p_summary), ("Installing", self.p_install),
                      ("All done", self.p_done)]
        self.show(0)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    # ---------------------------------------------------------------- plumbing
    def var(self, key, kind="str"):
        if key not in self.vars:
            value = self.settings.get(key, "")
            self.vars[key] = tk.BooleanVar(value=bool(value)) if kind == "bool" else tk.StringVar(value=str(value))
        return self.vars[key]

    def collect(self):
        for key, v in self.vars.items():
            val = v.get()
            if key in ("db_port",):
                try:
                    val = int(val)
                except ValueError:
                    raise se.SetupError("The database port must be a number.")
            self.settings[key] = val

    def clear(self):
        for w in self.body.winfo_children():
            w.destroy()

    def label(self, text, **kw):
        lab = tk.Label(self.body, text=text, justify="left", anchor="w", wraplength=660, **kw)
        lab.pack(fill="x", pady=(0, 6))
        return lab

    def field(self, text, key, show=None, browse=False, width=44):
        row = tk.Frame(self.body)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=text, width=26, anchor="w").pack(side="left")
        ttk.Entry(row, textvariable=self.var(key), show=show or "", width=width).pack(side="left")
        if browse:
            ttk.Button(row, text="Browse...", command=lambda: self.var(key).set(os.path.normpath(filedialog.askdirectory() or self.var(key).get()))).pack(side="left", padx=6)

    def check(self, text, key):
        ttk.Checkbutton(self.body, text=text, variable=self.var(key, "bool")).pack(anchor="w", pady=2)

    def show(self, index):
        self.page_index = index
        title, builder = self.pages[index]
        self.header.config(text=title)
        self.clear()
        builder()
        last = index == len(self.pages) - 1
        self.back_btn.config(state="disabled" if index in (0, 7, 8) else "normal")
        self.next_btn.config(text="Install" if index == 6 else ("Finish" if last else "Next >"), state="disabled" if index == 7 else "normal")
        self.cancel_btn.config(state="disabled" if index in (7, 8) else "normal")

    def next(self):
        try:
            self.collect()
            self.validate(self.page_index)
        except se.SetupError as e:
            messagebox.showwarning("Please check", str(e))
            return
        if self.page_index == 8:
            self.destroy()
            return
        if self.page_index == 6:
            self.show(7)
            self.start_install()
            return
        self.show(self.page_index + 1)

    def back(self):
        self.collect_quiet()
        self.show(self.page_index - 1)

    def collect_quiet(self):
        try:
            self.collect()
        except se.SetupError:
            pass

    def on_cancel(self):
        if self.running:
            return
        if messagebox.askyesno("Cancel setup", "Leave the setup without finishing?"):
            self.destroy()

    def validate(self, index):
        s = self.settings
        if index == 2:
            for k, label in (("db_name", "database name"), ("db_app_user", "database user")):
                se._ident(s[k])
        if index == 3 and s["wallet_mode"] == "import" and len(s["wallet_private_key"].strip()) != 64:
            raise se.SetupError("Paste the 64-character private key, or choose a different wallet option.")
        if index == 4:
            if not s["operator_name"].strip() or not s["operator_contact"].strip() or not s["governing_law"].strip():
                raise se.SetupError("The advertiser contract needs your company name, a contact address and the country whose law applies.")
        if index == 5:
            if not s["web_dir"].strip():
                raise se.SetupError("Choose the website folder.")
            if not s["public_url"].startswith(("http://", "https://")):
                raise se.SetupError("The website address must start with http:// or https://")

    # ---------------------------------------------------------------- pages
    def p_welcome(self):
        self.label("This wizard sets up a complete Nickles ad network on this PC:", font=("Segoe UI", 10, "bold"))
        self.label("  -  checks Python and installs what is missing\n"
                   "  -  finds XAMPP (MariaDB + Apache) or installs it for you\n"
                   "  -  creates the database with its own login and all tables\n"
                   "  -  creates your wallet, the chain and the encryption keys\n"
                   "  -  publishes the dashboard and the advertiser contract to your website folder")
        self.label("Nothing is changed until you press Install on the last page. Ports used by the network: 8332 (ads/portal) and 8333 (peers).")

    def p_system(self):
        rows, missing = se.system_check(self.settings)
        for label, ok, detail in rows:
            line = tk.Frame(self.body)
            line.pack(fill="x", pady=2)
            tk.Label(line, text="OK" if ok else "!!", fg="#14803c" if ok else "#b3261e", width=3, font=("Segoe UI", 10, "bold")).pack(side="left")
            tk.Label(line, text="%s  -  %s" % (label, detail), anchor="w", justify="left", wraplength=620).pack(side="left")
        if not se.find_xampp(self.settings.get("xampp_dir", "")):
            self.label("\nXAMPP (the free package that provides MariaDB and the Apache web server) was not found.", font=("Segoe UI", 10, "bold"))
            self.check("Install XAMPP for me (uses Windows' winget; about 150 MB)", "install_xampp")
            self.label("Or install it yourself from %s and click Back, then Next." % se.XAMPP_DOWNLOAD_PAGE)
        self.check("Start MariaDB and Apache if they are not running (a running one is never restarted)", "start_services")

    def p_database(self):
        self.label("The wizard creates a database and a separate login that can only use that database. To do that it needs one-time administrator access to MariaDB (on a fresh XAMPP the user is root with an empty password).")
        self.field("MariaDB address", "db_host")
        self.field("MariaDB port", "db_port", width=10)
        self.field("Administrator user", "db_admin_user")
        self.field("Administrator password", "db_admin_password", show="*")
        self.label("")
        self.field("New database name", "db_name")
        self.field("New database user", "db_app_user")
        self.label("The password for the new user is generated and stored only in dbconfig.json, which the web server refuses to serve.")

    def p_people(self):
        self.label("Wallet", font=("Segoe UI", 10, "bold"))
        for value, text in (("new", "Create a new wallet"), ("keep", "Keep the wallet.json that is already in this folder"),
                            ("import", "Import an existing wallet (paste its private key)")):
            ttk.Radiobutton(self.body, text=text, value=value, variable=self.var("wallet_mode")).pack(anchor="w")
        self.field("Private key (import only)", "wallet_private_key", show="*")
        self.label("\nFirst publisher account (the person whose websites show ads and earn from clicks)", font=("Segoe UI", 10, "bold"))
        self.field("Username", "developer_username")
        self.field("E-mail (optional)", "developer_email")
        self.label("There is no password login: earnings go to the wallet address above.")

    def p_operator(self):
        self.label("Anyone who submits ads has to accept an Advertiser Agreement first. These details are filled into it.")
        self.field("Your name or company", "operator_name")
        self.field("Contact e-mail or address", "operator_contact")
        self.field("Governing law (country)", "governing_law")
        self.label("\nUpload fee (mandatory service)", font=("Segoe UI", 10, "bold"))
        self.check("Advertisers must pay an upload fee in my btcshop before an ad is accepted", "ad_upload_fee_required")
        self.field("btcshop folder", "btcshop_dir", browse=True)
        self.field("Public address of the shop", "btcshop_url")
        self.label("The contract text (terms/advertiser_agreement.txt) is a template, not legal advice - have a lawyer in your country review it before you take ads from the public.", fg="#b3261e")

    def p_publish(self):
        self.label("The dashboard, the API and the advertiser contract page are copied to a website folder. Everything secret (wallet, keys, database login) stays out of public reach.")
        self.field("Website folder", "web_dir", browse=True)
        self.field("Its public address", "public_url")
        self.field("Key folder (outside the site)", "key_dir", browse=True)
        self.check("Start the wallet automatically when Windows starts", "startup_shortcut")
        self.label("Leave the key folder empty to use <XAMPP>\\pyc_keys.")

    def summary_text(self):
        s = self.settings
        lines = ["XAMPP: %s" % (s["xampp_dir"] or ("will be installed" if s["install_xampp"] else "NOT FOUND")),
                 "Database: %s on %s:%s as %s" % (s["db_name"], s["db_host"], s["db_port"], s["db_app_user"]),
                 "Wallet: %s" % {"new": "new", "keep": "keep existing", "import": "import"}[s["wallet_mode"]],
                 "Publisher: %s" % (s["developer_username"] or "(none yet)"),
                 "Operator: %s, %s, law of %s" % (s["operator_name"], s["operator_contact"], s["governing_law"]),
                 "Upload fee: %s" % ("required (btcshop: %s)" % (s["btcshop_dir"] or "not set") if s["ad_upload_fee_required"] else "off"),
                 "Website folder: %s  ->  %s" % (s["web_dir"], s["public_url"]),
                 "Start with Windows: %s" % ("yes" if s["startup_shortcut"] else "no")]
        return "\n".join(lines)

    def p_summary(self):
        self.label("Press Install to do the following:")
        self.label(self.summary_text(), font=("Consolas", 10))

    def p_install(self):
        self.progress = ttk.Progressbar(self.body, maximum=100)
        self.progress.pack(fill="x", pady=6)
        self.log_box = tk.Text(self.body, height=18, state="disabled", font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True)

    def p_done(self):
        r = self.result or {}
        self.label("Nickles is installed.", font=("Segoe UI", 12, "bold"))
        self.label("Your wallet address:  %s\nWebsite folder:  %s\nEncryption keys:  %s" % (r.get("address", ""), r.get("web_dir", ""), r.get("key_dir", "")))
        self.label("Start the wallet with run.bat. Advertisers accept the contract at:\n%s/advertiser_terms.php" % self.settings["public_url"].rstrip("/"))
        if not r.get("site_reachable"):
            self.label("The website address did not answer yet - that is normal if it is not online yet.")
        self.label("Back up the key folder and wallet.json: they cannot be recovered if lost.", fg="#b3261e")

    # ---------------------------------------------------------------- install
    def log(self, text):
        self.after(0, self._log, text)

    def _log(self, text):
        self.log_box.config(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def start_install(self):
        self.running = True

        def work():
            try:
                self.result = se.run_all(self.settings, log=self.log, progress=lambda f, t: self.after(0, lambda: self.progress.config(value=f * 100)))
                self.after(0, self.finished, None)
            except Exception as e:
                self.after(0, self.finished, e)
        threading.Thread(target=work, daemon=True).start()

    def finished(self, error):
        self.running = False
        if error:
            self._log("\nSTOPPED: %s" % error)
            self.next_btn.config(text="Close", state="normal", command=self.destroy)
            self.back_btn.config(state="normal", command=lambda: self.show(6) or self.next_btn.config(command=self.next))
            messagebox.showerror("Setup stopped", str(error))
        else:
            self.show(8)


def main():
    if "--unattended" in sys.argv:
        path = sys.argv[sys.argv.index("--unattended") + 1]
        settings = json.load(open(path, encoding="utf-8"))
        result = se.run_all(settings, log=print, progress=lambda f, t: None)
        print(json.dumps(result, indent=2))
        return
    Wizard().mainloop()


if __name__ == "__main__":
    try:
        main()
    except se.SetupError as e:
        print("Setup stopped: %s" % e)
        sys.exit(1)
