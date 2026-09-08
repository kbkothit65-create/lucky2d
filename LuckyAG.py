import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pytz
import flet as ft
import requests
import random
import time
import json
from datetime import datetime, timedelta
from supabase import create_client, Client

def prevent_double_click(action_func):
    """ခလုတ်ကို ၁ ချက်ထက်ပိုပြီး ဆက်တိုက် နှိပ်မရအောင် ကာကွယ်ပေးသော Function"""
    def wrapper(e):
        # နှိပ်လိုက်တာနဲ့ ခလုတ်ကို ချက်ချင်း Disabled ပိတ်မည်
        e.control.disabled = True
        e.control.page.update()
        
        try:
            action_func(e)
        finally:
            # Logic ပြီးသွားပါက ခလုတ်ကို ပြန်ဖွင့်ပေးမည်
            e.control.disabled = False
            e.control.page.update()
            
    return wrapper

# Telegram ထဲသို့ စာနှင့် ပုံ ပို့ပေးမည့် Function
def send_deposit_to_telegram(phone, amount, trx_id, deposit_id, Paytp):
    BOT_TOKEN = "8680151013:AAGCgLOOKzLTm3X4PiJa8TaUVR3NUEd-S6s"
    CHAT_ID = "-1004379940626"
    
    text_msg = (
        f"📩 ( ငွေသွင်းတောင်းဆိုမှု 🟢 )\n\n"
        f"⚠️ Req ID - `{deposit_id}`\n"
        f"👤 User - `{phone}`\n"
        f"💰 ပမာဏ - {amount:,} MMK\n\n"
        f"🏧 Pay Type - `{Paytp}`\n"
        f"🆔 Trx ID - `{trx_id}`\n"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve_{deposit_id}"},
                {"text": "❌ Reject", "callback_data": f"reject_{deposit_id}"}
            ]
        ]
    }
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text_msg}"
    payload = {
        "chat_id":CHAT_ID,
        "text": text_msg,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard)
    }
    requests.get(url, json=payload)

def send_withdraw_to_telegram(phone, amount, trx_id, withdraw_id, Paytp):
    BOT_TOKEN = "8680151013:AAGCgLOOKzLTm3X4PiJa8TaUVR3NUEd-S6s"
    CHAT_ID = "-1004379940626"
    
    withdraw_text_msg = (
        f"📩 ( ငွေထုတ်တောင်းဆိုမှု 🔴 )\n\n"
        f"⚠️ Req ID - `{withdraw_id}`\n"
        f"👤 User Phone - `{phone}`\n"
        f"💰 ပမာဏ - {amount:,} MMK\n\n"
        f"🏧 Pay Type - `{Paytp}`\n"
        f"🆔 Trx ID - `{trx_id}`\n"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve_{withdraw_id}"},
                {"text": "❌ Reject", "callback_data": f"reject_{withdraw_id}"}
            ]
        ]
    }
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={withdraw_text_msg}"
    payload = {
        "chat_id":CHAT_ID,
        "text": withdraw_text_msg,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard)
    }
    requests.get(url, json=payload)

yangon_tz = pytz.timezone('Asia/Yangon')
now = datetime.now(yangon_tz)
# ----------------------------------------------------
# 🔗 SUPABASE CONNECTION SETTINGS
# ----------------------------------------------------
SUPABASE_URL = "https://xtnuvccclnezphranjer.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0bnV2Y2NjbG5lenBocmFuamVyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTE1NDUxOCwiZXhwIjoyMTAwNzMwNTE4fQ.rkJgdp7pqxFtbscBUAbphNNzxCx5nNBN1uYzpr8hMKo"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔐 ADMIN ONLY PASSCODE
ADMIN_PIN = "103006"

global user_phone_text,user_name_text,wallet_text
# Global Current User Session
current_user = {
    "phone": "",
    "name": ""
}

def main(page: ft.Page):
    page.title = "Lucky 2D"
    page.window.width = 390
    page.window.height = 800
    page.window.resizable = False
    page.padding = 15
    page.theme_mode = ft.ThemeMode.DARK

    selected_numbers = []
    # HTML/CSS ဖြင့် ပြုလုပ်ထားသော Smooth Marquee Component
    marquee_container = ft.Container(
        content=ft.WebView(
            url="data:text/html;charset=utf-8," + """
            <html>
            <head>
                <style>
                    body {
                        margin: 0;
                        background-color: #111419 ;
                        overflow: hidden;
                        display: flex;
                        align-items: center;
                    }
                    .marquee {
                        white-space: nowrap;
                        font-family: sans-serif;
                        font-weight: bold;
                        font-size: 13px;
                        color: #FFC107;
                        animation: marquee 12s linear infinite;
                    }
                    @keyframes marquee {
                        0%   { transform: translateX(150%); }
                        100% { transform: translateX(-100%); }
                    }
                </style>
            </head>
            <body>
                <div class="marquee">
                    📢 ဒီမနက် ၁၀၀၀၀ ဖိုးပေါက်ရင် ညနေ ဖုန်းအသစ်ဝယ်လိုက်🤭
                </div>
            </body>
            </html>
            """,
            expand=True,
        ),
        height=35,
        border_radius=8,
    )

    def go_back(e=None):
        if len(page.views) > 1:
            page.views.pop()
            page.update()

    # ----------------------------------------------------
    # 💰 FETCH USER BALANCE
    # ----------------------------------------------------
    def get_user_balance():

        phone = user_phone_text.value if user_phone_text and user_phone_text.value else page.client_storage.get("saved_phone")

        if not phone :
            return 0
        try:
            res = supabase.table("users").select("balance").eq("id",phone).execute()
            if res.data:
                return res.data[0]["balance"]
        except Exception as ex:
            print("Database Balance Error:", ex)
        return 0

    wallet_text = ft.Text("0 Ks", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
    user_name_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    user_phone_text = ft.Text("", size=10, color=ft.Colors.GREY_400)

    def refresh_wallet_ui(e=None):
        phone = user_phone_text.value if user_phone_text and user_phone_text.value else page.client_storage.get("saved_phone")
        if not phone :
            print("Error: No phone number found to refresh.")
            return
        try:
            res = supabase.table("users").select("name, balance, id").eq("id",phone).execute()
            if res.data:
                data = res.data[0]
            wallet_text.value = f"{data['balance']:,} Ks"
            user_name_text.value = data['name']
            user_phone_text.value = data['id']

            current_user["name"] = data['name']
            current_user["phone"] = data['id']
            
            page.update()
            if e:
                page.open(ft.SnackBar(ft.Text("🔄 လက်ကျန်ငွေ အသစ်ဖြစ်သွားပါပြီ။"), bgcolor=ft.Colors.BLUE_800))
        except Exception as ex:
            print("Refresh Error:", ex)

    # ----------------------------------------------------
    # 🔑 AUTHENTICATION VIEW
    # ----------------------------------------------------
    def show_login_signup_view():
        phone_input = ft.TextField(
            label="ဖုန်းနံပါတ်",
            hint_text="09xxxxxxxxx",
            keyboard_type=ft.KeyboardType.PHONE,
            autofocus=True
        )
        
        name_input = ft.TextField(
            label="အမည် (Name)",
            hint_text="အမည်မှန်ထည့်ပါ"
        )

        is_signup_mode = False
        mode_title = ft.Text("🔑 အကောင့်သို့ ဝင်ရောက်ရန်", size=18, weight=ft.FontWeight.BOLD)
        action_btn = ft.ElevatedButton("Login ဝင်မည်", bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, width=280, height=45)
        toggle_link = ft.TextButton("အကောင့်မရှိသေးပါက Signup လုပ်ရန် နှိပ်ပါ")

        def toggle_mode(e):
            nonlocal is_signup_mode
            is_signup_mode = not is_signup_mode
            if is_signup_mode:
                mode_title.value = "📝 အကောင့်သစ် ဖွင့်ရန်"
                name_input.label = "အမည် (Signup လုပ်ရန်အတွက်သာ)"
                action_btn.text = "Account ဖွင့်မည်"
                action_btn.bgcolor = ft.Colors.GREEN_600
                toggle_link.text = "အကောင့်ရှိပြီးသားဆိုပါက Login သို့ ပြန်သွားရန်"
            else:
                mode_title.value = "🔑 အကောင့်သို့ ဝင်ရောက်ရန်"
                name_input.label = "အမည် (Name)"
                action_btn.text = "Login ဝင်မည်"
                action_btn.bgcolor = ft.Colors.BLUE_600
                toggle_link.text = "အကောင့်မရှိသေးပါက Signup လုပ်ရန် နှိပ်ပါ"
            page.update()

        def handle_auth(e):
            phone = phone_input.value.strip() if phone_input.value else ""
            name = name_input.value.strip() if name_input.value else ""

            if not phone or len(phone) < 8:
                page.open(ft.SnackBar(ft.Text("🛑 ဖုန်းနံပါတ် မှန်ကန်စွာ ရိုက်ထည့်ပါ!"), bgcolor=ft.Colors.RED_800))
                return
            
            if not name:
                page.open(ft.SnackBar(ft.Text("🛑 အမည် (Name) ထည့်ရန် လိုအပ်ပါသည်။"), bgcolor=ft.Colors.RED_800))
                return

            try:
                if is_signup_mode:
                    check_u = supabase.table("users").select("*").eq("id", phone).execute()
                    if check_u.data:
                        page.open(ft.SnackBar(ft.Text("🛑 ဒီဖုန်းနံပါတ်ဖြင့် အကောင့်ပွင့်ပြီးသား ဖြစ်ပါသည်။ Login ဝင်ပေးပါ။"), bgcolor=ft.Colors.RED_800))
                        return
                    
                    supabase.table("users").insert({"id": phone, "name": name, "balance": 0}).execute()

                    page.client_storage.set("saved_phone", phone)
                    page.client_storage.set("saved_name", name)

                    user_phone_text.value = phone
                    user_name_text.value = name

                    refresh_wallet_ui()
                    page.views.clear()
                    page.views.append(get_main_home_view())
                    page.update()

                else:
                    res = supabase.table("users").select("*").eq("id", phone).execute()
                    if not res.data:
                        page.open(ft.SnackBar(ft.Text("🛑 အကောင့် မရှိသေးပါ။ ကျေးဇူးပြု၍ Signup လုပ်ပေးပါ။"), bgcolor=ft.Colors.RED_800))
                        return
                    
                    db_user = res.data[0]
                    if db_user["name"].strip() != name:
                        page.open(ft.SnackBar(ft.Text("🛑 ဖုန်းနံပါတ် သို့မဟုတ် အမည် (Name) မှားယွင်းနေပါသည်။"), bgcolor=ft.Colors.RED_800))
                        return

                    page.client_storage.set("saved_phone", phone)
                    page.client_storage.set("saved_name", db_user["name"])

                    user_phone_text.value = phone
                    user_name_text.value = db_user["name"]

                    refresh_wallet_ui()
                    page.views.clear()
                    page.views.append(get_main_home_view())
                    page.update()

            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Connection Error: {ex}"), bgcolor=ft.Colors.RED_800))

        action_btn.on_click = handle_auth
        toggle_link.on_click = toggle_mode

        return ft.View(
            route="/auth",
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CASINO, size=60, color=ft.Colors.AMBER_400),
                        mode_title,
                        ft.Container(height=10),
                        phone_input,
                        name_input,
                        ft.Container(height=10),
                        action_btn,
                        toggle_link
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=20
                )
            ]
        )
        
    # ----------------------------------------------------
    # 📊 2D WINNING RESULTS PAGE
    # ----------------------------------------------------
    def get_results_page():
        results_list = ft.ListView(expand=True, spacing=12)

        try:
            res = supabase.table("win_results").select("*").order("id", desc=True).execute()
            all_results = res.data if res.data else []
        except Exception as ex:
            all_results = []

        if not all_results:
            results_list.controls.append(
                ft.Container(
                    content=ft.Text("ထွက်ဂဏန်း မှတ်တမ်း မရှိသေးပါ", color=ft.Colors.GREY_400, size=14),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            grouped_data = {}
            for item in all_results:
                date_key = item["date"]
                if date_key not in grouped_data:
                    grouped_data[date_key] = {"12:01 PM": "--", "04:30 PM": "--"}
                grouped_data[date_key][item["session"]] = item["win_num"]

            for date_val, sessions in grouped_data.items():
                card = ft.Container(
                    content=ft.Column([
                        ft.Text(f"📅 {date_val}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                        ft.Divider(height=1, color=ft.Colors.WHITE10),
                        ft.Row([
                            ft.Text("12:01 PM", size=13, color=ft.Colors.WHITE70),
                            ft.Text(f"{sessions.get('12:01 PM', '--')}", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Text("4:30 PM", size=13, color=ft.Colors.WHITE70),
                            ft.Text(f"{sessions.get('04:30 PM', '--')}", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], spacing=6),
                    padding=15,
                    bgcolor=ft.Colors.WHITE10,
                    border_radius=10
                )
                results_list.controls.append(card)

        return ft.View(
            route="/results",
            controls=[
                ft.AppBar(
                    title=ft.Text("2D ထွက်ဂဏန်းများ", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back)
                ),
                ft.Container(content=results_list, padding=10, expand=True)
            ]
        )

    # ----------------------------------------------------
    # 📜 HISTORY PAGE
    # ----------------------------------------------------
    def get_history_page():
        history_list = ft.ListView(expand=True, spacing=10)

        try:
            res = supabase.table("bets").select("*").eq("user_id", page.client_storage.get("saved_phone")).order("id", desc=True).execute()
            bet_history = res.data if res.data else []
        except Exception as ex:
            bet_history = []

        if not bet_history:
            history_list.controls.append(
                ft.Container(
                    content=ft.Text("ထိုးထားသော စာရင်း မရှိသေးပါ", color=ft.Colors.GREY_400, size=14),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            for item in bet_history:
                is_settled = item.get("settled", False)
                win_num = item.get("win_num", None)
                
                status_text = "⏳ စောင့်ဆိုင်းဆဲ"
                status_color = ft.Colors.AMBER_400

                if is_settled:
                    num_list = [n.strip() for n in item["numbers"].split(",")]
                    if win_num and win_num in num_list:
                        won_amt = item["unit_price"] * 90
                        status_text = f"🎉 ပေါက်ပါသည် (+{won_amt:,} Ks)"
                        status_color = ft.Colors.GREEN_400
                    else:
                        status_text = f"❌ မပေါက်ပါ (ထွက်: {win_num})"
                        status_color = ft.Colors.RED_400

                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"📅 {item['bet_date']} ({item['session']})", size=12, color=ft.Colors.CYAN_300, weight=ft.FontWeight.BOLD),
                            ft.Text(status_text, size=12, weight=ft.FontWeight.BOLD, color=status_color)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(height=1, color=ft.Colors.WHITE10),
                        ft.Text(f"ဂဏန်းများ: {item['numbers']}", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Text(f"အကွက်ရေ: {item['count']} ကွက်", size=11, color=ft.Colors.WHITE70),
                            ft.Text(f"စုစုပေါင်း: {item['total_cost']:,} Ks", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], spacing=5),
                    padding=12,
                    bgcolor=ft.Colors.WHITE10,
                    border_radius=10
                )
                history_list.controls.append(card)

        return ft.View(
            route="/history",
            controls=[
                ft.AppBar(
                    title=ft.Text("ထိုးထားသော စာရင်းများ", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back)
                ),
                ft.Container(content=history_list, padding=10, expand=True)
            ]
        )

    # ----------------------------------------------------
    # 🎯 2D PAGE UI BUILDER
    # ----------------------------------------------------
    def get_2d_page():
        now = datetime.now(yangon_tz)
        current_time_val = now.time()

        t_12pm = datetime.strptime("12:00:00", "%H:%M:%S").time()
        t_430pm = datetime.strptime("16:30:00", "%H:%M:%S").time()

        target_date = now.date()

        if current_time_val >= t_430pm:
            target_date = now.date() + timedelta(days=1)
            disable_12pm = False
            disable_4pm = False
            default_session = "12:01 PM"
        else:
            disable_12pm = current_time_val >= t_12pm
            disable_4pm = False
            default_session = "04:30 PM" if disable_12pm else "12:01 PM"

        if target_date.weekday() in [5, 6]:
            return ft.View(
                route="/page_1",
                controls=[
                    ft.AppBar(
                        title=ft.Text("2D ထိုးမည့် စာမျက်နှာ", size=18, weight=ft.FontWeight.BOLD),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back)
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.EVENT_BUSY, size=70, color=ft.Colors.RED_400),
                            ft.Text("⚠️ စနေ/တနင်္ဂနွေ ပိတ်ရက်ဖြစ်ပါသည်!", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True, alignment=ft.alignment.center
                    )
                ]
            )

        date_str_formatted = target_date.strftime("%d.%m.%Y")
        day_str_formatted = target_date.strftime("%A")
        date_display_text = ft.Text(
            f"📅 ထိုးမည့်ရက်စွဲ: {date_str_formatted} ({day_str_formatted})",
            size=13,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.CYAN_300
        )

        radio_12pm = ft.Radio(value="12:01 PM", label="12:01 PM (မနက်)", disabled=disable_12pm)
        radio_4pm = ft.Radio(value="04:30 PM", label="04:30 PM (ညနေ)", disabled=disable_4pm)

        session_radio = ft.RadioGroup(
            content=ft.Row([radio_12pm, radio_4pm], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            value=default_session
        )

        amount_input = ft.TextField(
            label="ထိုးကြေး (ကျပ်)",
            hint_text="100",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=115,
            height=45,
            text_size=13,
            label_style=ft.TextStyle(size=12)
        )

        def update_grid_ui():
            for btn in grid_buttons:
                num = btn.data
                if num in selected_numbers:
                    btn.bgcolor = ft.Colors.AMBER_600
                    btn.content.color = ft.Colors.BLACK
                else:
                    btn.bgcolor = ft.Colors.BLUE_GREY_900
                    btn.content.color = ft.Colors.WHITE
            page.update()

        def toggle_number(e, num_str):
            if num_str in selected_numbers:
                selected_numbers.remove(num_str)
            else:
                selected_numbers.append(num_str)
            update_grid_ui()

        def apply_quick_select(category, digit=None):
            selected_numbers.clear()
            
            if category == "စုံစုံ":
                for i in range(100):
                    num = f"{i:02d}"
                    if int(num[0]) % 2 == 0 and int(num[1]) % 2 == 0:
                        selected_numbers.append(num)
            elif category == "မမ":
                for i in range(100):
                    num = f"{i:02d}"
                    if int(num[0]) % 2 != 0 and int(num[1]) % 2 != 0:
                        selected_numbers.append(num)
            elif category == "အပူး":
                for i in range(10):
                    selected_numbers.append(f"{i}{i}")
            elif category == "ပါဝါ":
                selected_numbers.extend(["05", "50", "16", "61", "27", "72", "38", "83", "49", "94"])
            elif category == "နက္ခတ်":
                selected_numbers.extend(["07", "70", "18", "81", "24", "42", "35", "53", "69", "96"])
            elif category == "ပတ်သီး" and digit is not None:
                for i in range(100):
                    num = f"{i:02d}"
                    if digit in num:
                        selected_numbers.append(num)

            page.close(quick_select_dialog)
            update_grid_ui()

        patthit_input = ft.TextField(label="ပတ်သီး (0-9)", keyboard_type=ft.KeyboardType.NUMBER, max_length=1, width=150)

        def on_patthit_click(e):
            d = patthit_input.value.strip() if patthit_input.value else ""
            if not d.isdigit():
                page.open(ft.SnackBar(ft.Text("🛑 0 နှင့် 9 ကြား ဂဏန်းတစ်ခု ထည့်ပါ"), bgcolor=ft.Colors.RED_800))
                return
            apply_quick_select("ပတ်သီး", digit=d)

        quick_select_dialog = ft.AlertDialog(
            title=ft.Text("⚡ အမြန်ရွေးမည် / ပတ်သီး", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton("စုံစုံ", on_click=lambda _: apply_quick_select("စုံစုံ")),
                    ft.ElevatedButton("မမ", on_click=lambda _: apply_quick_select("မမ")),
                    ft.ElevatedButton("အပူး", on_click=lambda _: apply_quick_select("အပူး")),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Row([
                    ft.ElevatedButton("ပါဝါ", on_click=lambda _: apply_quick_select("ပါဝါ")),
                    ft.ElevatedButton("နက္ခတ်", on_click=lambda _: apply_quick_select("နက္ခတ်")),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Divider(),
                ft.Row([patthit_input, ft.ElevatedButton("ပတ်သီးယူ", bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE, on_click=on_patthit_click)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], tight=True, spacing=10),
            actions=[ft.TextButton("ပိတ်မည်", on_click=lambda _: page.close(quick_select_dialog))]
        )

        btn_quick_select = ft.OutlinedButton(
            text="အမြန်ရွေး",
            icon=ft.Icons.FLASH_ON,
            style=ft.ButtonStyle(color=ft.Colors.AMBER_400),
            on_click=lambda _: page.open(quick_select_dialog)
        )

        grid_buttons = []
        for i in range(100):
            num_str = f"{i:02d}"
            btn = ft.Container(
                content=ft.Text(num_str, weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.WHITE),
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=8,
                data=num_str,
                on_click=lambda e, n=num_str: toggle_number(e, n)
            )
            grid_buttons.append(btn)

        number_grid = ft.GridView(
            controls=grid_buttons,
            runs_count=5,
            max_extent=60,
            spacing=8,
            run_spacing=8,
            expand=True,
        )

        def process_final_bet(unit_price, total_cost, target_session, confirm_dialog):
            page.close(confirm_dialog)

            active_user_phone = page.client_storage.get("saved_phone")
            curr_bal = get_user_balance()
            new_bal = curr_bal - total_cost
            formatted_date = target_date.strftime("%d.%m.%Y")

            try:
                supabase.table("users").update({"balance": new_bal}).eq("id", active_user_phone).execute()

                supabase.table("bets").insert({
                    "user_id": active_user_phone,
                    "bet_date": formatted_date,
                    "session": target_session,
                    "numbers": ', '.join(sorted(selected_numbers)),
                    "count": len(selected_numbers),
                    "unit_price": unit_price,
                    "total_cost": total_cost,
                    "settled": False
                }).execute()

                refresh_wallet_ui()
                selected_numbers.clear()
                amount_input.value = ""
                update_grid_ui()

                page.open(
                    ft.SnackBar(
                        ft.Text(f"✅ ထိုးစာရင်း အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!"),
                        bgcolor=ft.Colors.GREEN_800
                    )
                )

            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Bet Error: {ex}"), bgcolor=ft.Colors.RED_800))

        def submit_bet(e):
            val_str = amount_input.value
            target_session = session_radio.value

            # 💡 အချက် (၁) - အချိန်ကန့်သတ်ချက် စစ်ဆေးခြင်း
            current_dt = datetime.now(yangon_tz)
            # ယနေ့ရက်စွဲနှင့် ရွေးချယ်ထားသော ပွဲချိန်ကို စစ်ဆေးခြင်း
            if target_date == current_dt.date():
                t_now = current_dt.time()
                if target_session == "12:01 PM":
                    limit_time_12 = datetime.strptime("11:55:00", "%H:%M:%S").time()
                    if t_now >= limit_time_12:
                        page.open(ft.SnackBar(ft.Text("🛑 ထိုးချိန်မမှီတော့ပါ (မနက် ၁၁:၅၅ ကျော်သွားပါပြီ)"), bgcolor=ft.Colors.RED_800))
                        return
                elif target_session == "04:30 PM":
                    limit_time_4 = datetime.strptime("15:50:00", "%H:%M:%S").time()
                    if t_now >= limit_time_4:
                        page.open(ft.SnackBar(ft.Text("🛑 ထိုးချိန်မမှီတော့ပါ (ညနေ ၃:၅၀ ကျော်သွားပါပြီ)"), bgcolor=ft.Colors.RED_800))
                        return

            if not selected_numbers:
                page.open(ft.SnackBar(ft.Text("ကျေးဇူးပြု၍ ဂဏန်းအနည်းဆုံး တစ်လုံး ရွေးပါ!")))
                return

            if not val_str or not val_str.isdigit():
                page.open(ft.SnackBar(ft.Text("ကျေးဇူးပြု၍ ထိုးကြေးပမာဏ မှန်ကန်စွာ ရိုက်ထည့်ပါ!")))
                return

            unit_price = int(val_str)
            if unit_price < 100:
                page.open(ft.SnackBar(ft.Text("🛑 အနည်းဆုံး ၁၀၀ ကျပ်မှစ၍ ထိုးရပါမည်။"), bgcolor=ft.Colors.RED_800))
                return

            total_cost = unit_price * len(selected_numbers)
            current_bal = get_user_balance()

            if total_cost > current_bal:
                page.open(ft.SnackBar(ft.Text(f"🛑 လက်ကျန်ငွေ မလုံလောက်ပါ။ (လိုအပ်ငွေ: {total_cost:,} Ks)"), bgcolor=ft.Colors.RED_800))
                return

            sorted_nums = ', '.join(sorted(selected_numbers))

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("📌 ထိုးစာရင်း အတည်ပြုရန်", weight=ft.FontWeight.BOLD),
                content=ft.Column([
                    ft.Text(f"• ရက်စွဲ/ချိန်: {target_date.strftime('%d.%m.%Y')} ({target_session})", size=13, color=ft.Colors.CYAN_300),
                    ft.Text(f"• ဂဏန်းများ: {sorted_nums}", size=13, color=ft.Colors.AMBER_300),
                    ft.Text(f"• အကွက်ရေ: {len(selected_numbers)} ကွက်", size=13),
                    ft.Text(f"• စုစုပေါင်း: {total_cost:,} ကျပ်", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                ], tight=True, spacing=8),
                actions=[
                    ft.TextButton("မဟုတ်ပါ", on_click=lambda _: page.close(confirm_dialog)),
                    ft.ElevatedButton(
                        "သေချာပြီ", 
                        bgcolor=ft.Colors.GREEN_600, 
                        color=ft.Colors.WHITE,
                        on_click=prevent_double_click(
                            lambda _: process_final_bet(unit_price, total_cost, target_session, confirm_dialog)
                        )
                    ),
                ]
            )

            page.open(confirm_dialog)

        submit_btn = ft.ElevatedButton("ထိုးမည်", bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, height=45, width=80)
        submit_btn.on_click = submit_bet

        return ft.View(
            route="/page_1",
            controls=[
                ft.AppBar(
                    title=ft.Text("2D ထိုးမည့် စာမျက်နှာ", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back),
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.RECEIPT_LONG, 
                            tooltip="ထိုးထားသော စာရင်းများ",
                            on_click=lambda _: (page.views.append(get_history_page()), page.update())
                        )
                    ]
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([date_display_text], alignment=ft.MainAxisAlignment.CENTER),
                        session_radio,
                        ft.Container(content=number_grid, expand=True),
                        ft.Row([amount_input, btn_quick_select, submit_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]),
                    expand=True, padding=10
                )
            ]
        )

    # ----------------------------------------------------
    # 📞 CUSTOMER SERVICE DIALOG
    # ----------------------------------------------------
    def open_help_dialog(e):
        help_dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.SUPPORT_AGENT, color=ft.Colors.AMBER_400, size=24),
                ft.Text("အကူအညီ ရယူရန်", weight=ft.FontWeight.BOLD, size=18)
            ], spacing=10),
            content=ft.Column([
                ft.Text("အကူအညီ ရယူလိုပါက အောက်ပါ လူမှုကွန်ရက်များမှတစ်ဆင့် ဆက်သွယ်နိုင်ပါသည် -", size=13, color=ft.Colors.GREY_300),
                ft.Container(height=5),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.TELEGRAM, color=ft.Colors.BLUE_400, size=22),
                        ft.Column([
                            ft.Text("Telegram", size=11, color=ft.Colors.GREY_400),
                            ft.Text("@MgLucky7", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                        ], spacing=1)
                    ], spacing=12),
                    padding=12, bgcolor=ft.Colors.WHITE10, border_radius=8
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PHONE, color=ft.Colors.PURPLE_400, size=22),
                        ft.Column([
                            ft.Text("Viber", size=11, color=ft.Colors.GREY_400),
                            ft.Text("+959984960264", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
                        ], spacing=1)
                    ], spacing=12),
                    padding=12, bgcolor=ft.Colors.WHITE10, border_radius=8
                ),
            ], tight=True, spacing=10),
            actions=[
                ft.ElevatedButton("ပိတ်မည်", bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE, on_click=lambda _: page.close(help_dialog))
            ]
        )
        page.open(help_dialog)

    def card_flip_page():
    # ==========================================
    # Game Config & States
    # ==========================================
        ENTRY_FEE = 1000
        PRIZES = {"🎁": 1000, "🏆": 2000, "💵": 3000, "💰": 5000, "💎": 10000, "🔴": 0}
    
    # Session / State Variables
        flipped_cards = []  # ရွေးချယ်ထားသော ကတ် Index များ
        card_data = []      # Random ကျထားသော ကတ် values များ (ဥပမာ ['A', 'C', 'A', ...])
        card_buttons = []   # UI Button Objects
        is_playing = False

        # Client Storage မှ User Data များယူခြင်း
        user_name = page.client_storage.get("saved_name") or "Player"
        user_phone = page.client_storage.get("saved_phone") or ""

        # Current Balance ယူခြင်း
        user_res = supabase.table("users").select("balance").eq("id", user_phone).execute()
        current_balance = user_res.data[0]["balance"] if user_res.data else 0

        # ==========================================
        # UI Components (Header & Status)
        # ==========================================
        balance_text = ft.Text(f"{current_balance:,} Ks", size=16, weight=ft.FontWeight.BOLD, color="yellow")
        status_text = ft.Text("ကတ်လှန်ရန် ၁၀၀၀ ကျပ်ဖြင့်စတင်ပါ", size=14, color="white", weight=ft.FontWeight.BOLD)

        grid_container = ft.GridView(
            expand=True,
            runs_count=5,
            max_extent=80,
            child_aspect_ratio=0.9,
            spacing=6,
            run_spacing=6,
        )

        init_cards = ["💎"]*5 + ["💰"]*5 + ["💵"]*5 + ["🏆"]*5
        # UI Grid Rebuild
        grid_container.controls.clear()
            
        for val in init_cards:
            btn = ft.Container(
                content=ft.Text(val,size=20, color="black", weight=ft.FontWeight.BOLD),
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.WHITE, border_radius=8
            )
            grid_container.controls.append(btn)

        # ==========================================
        # Logic Functions
        # ==========================================
        def update_balance_ui(new_balance):
            nonlocal current_balance
            current_balance = new_balance
            balance_text.value = f"{current_balance:,} Ks"
            page.update()

        def auto_reveal_all():
            """ဂိမ်းအနိုင်/အရှုံး ပေါ်ပါက ကျန်သော ကတ်များကို ပွင့်ပြပေးခြင်း"""
            for idx, btn in enumerate(card_buttons):
                val = card_data[idx]
                btn.content = ft.Text(f"{val}", size=20, weight=ft.FontWeight.BOLD, color="black", text_align=ft.TextAlign.CENTER)
                btn.bgcolor = ft.Colors.BLUE_GREY_100
                btn.disabled = True
            page.update()

        def on_card_click(e, index):
            nonlocal flipped_cards
    
            # နှိပ်ပြီးသား သို့မဟုတ် ၃ ကြိမ်ပြည့်နေပါက အလုပ်မလုပ်ပါ
            if index in flipped_cards or len(flipped_cards) >= 3:
                return
            # ကတ်လှန်ခြင်း UI Update
            val = card_data[index]
            e.control.content = ft.Text(val, size=22, weight=ft.FontWeight.BOLD, color="black")
            e.control.bgcolor = ft.Colors.WHITE
            page.update()
            flipped_cards.append(index)
            # လှန်ထားသော ကတ်များထဲမှ Values များကို ယူခြင်း
            opened_values = [card_data[i] for i in flipped_cards]
            # ၁။ လှန်ထားသော ကတ်များထဲတွင် မည်သည့် ကတ် ၂ ခု မဆို တူသွားပါက (အနိုင်)
            matched_val = None
            for v in set(opened_values):
                if v != "🔴" and opened_values.count(v) >= 2:
                    matched_val = v
                    break
            if matched_val:
                time.sleep(0.3)
                win_amount = PRIZES[matched_val]
                new_bal = current_balance + win_amount
                # Supabase Balance & Transaction Update
                supabase.table("users").update({"balance": new_bal}).eq("id", user_phone).execute()
        
                update_balance_ui(new_bal)
                refresh_wallet_ui()
                status_text.value = f"🎉 ဂုဏ်ယူပါသည်! {matched_val} တူညီ၍ {win_amount:,} ကျပ် နိုင်ပါသည်!"
                status_text.color = "green"
        
                auto_reveal_all()
                play_btn.disabled = False
                page.update()
                return
            # ၂။ ၄ ကတ် လှန်ပြီးသော်လည်း တူသည့်ကတ် မရှိပါက (အရှုံး)
            if len(flipped_cards) == 3:
                time.sleep(0.3)
                status_text.value = "❌ ၃ ကတ်လုံး မတူပါ! နောက်တစ်ကြိမ် ပြန်လည်ကြိုးစားပါ။"
                status_text.color = "red"
                auto_reveal_all()
                play_btn.disabled = False
                page.update()

        def start_game(e):
            nonlocal card_data, flipped_cards, is_playing

            # Balance စစ်ခြင်း
            if current_balance < ENTRY_FEE:
                page.open(ft.SnackBar(ft.Text("❌ လက်ကျန်ငွေ မလုံလောက်ပါ!"), bgcolor=ft.Colors.RED_800))
                return

            # ၁,၀၀၀ ကျပ် နှုတ်ခြင်း
            new_bal = current_balance - ENTRY_FEE
            supabase.table("users").update({"balance": new_bal}).eq("id", user_phone).execute()
            update_balance_ui(new_bal)
            refresh_wallet_ui()

            # ကတ် ၅ မျိုးကို ၃ စုံစီ Random မွှေခြင်း (စုစုပေါင်း ၁၅ ကတ်)
            cards = ["🏆", "💵", "💰"] * 3 + ["🔴"] * 5 + ["💎"] * 2 + ["🎁"] * 4
            random.shuffle(cards)
            card_data = cards
            flipped_cards = []

            grid_container.controls.clear()
            card_buttons.clear()

            for i in range(20):
                btn = ft.Container(
                    content=ft.Icon(ft.Icons.QUESTION_MARK, color="white", size=18),
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.BLUE_800, border_radius=8,
                    on_click=lambda e, idx=i: on_card_click(e, idx)
                )
                card_buttons.append(btn)
                grid_container.controls.append(btn)

            play_btn.disabled = True
            status_text.value = "ကတ် ၃ ခု ရွေးချယ်လှန်ပါ..."
            status_text.color = "white"
            page.update()

    # ==    ========================================
    # UI     Layout Construction
    # ==========================================
        play_btn = ft.ElevatedButton("ဆော့မည်", on_click=prevent_double_click(start_game), style=ft.ButtonStyle(bgcolor="orange", color="black"))

        # Top Bar: Back Button, User Name, Balance
        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back),
                ft.Text(user_name, size=16, weight=ft.FontWeight.BOLD),
                balance_text
            ]
        )

        # Prize Table (ဆုကြေးဇယား)
        prize_info = ft.Column([
            ft.Row([
                ft.Container(content=ft.Text("🎁 = 1000", color="black", weight="bold"), bgcolor="white", padding=5, border_radius=5),
                ft.Container(content=ft.Text("🏆 = 2000", color="black", weight="bold"), bgcolor="white", padding=5, border_radius=5),
                ft.Container(content=ft.Text("💵 = 3000", color="black", weight="bold"), bgcolor="white", padding=5, border_radius=5),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Container(content=ft.Text("💰 = 5000", color="black", weight="bold"), bgcolor="white", padding=5, border_radius=5),
                ft.Container(content=ft.Text("💎 = 10000", color="black", weight="bold"), bgcolor="white", padding=5, border_radius=5),
                ft.Container(content=ft.Text("🔴 = XXXX", color="black", weight="bold"), bgcolor="white", padding=5, border_radius=5),
            ], alignment=ft.MainAxisAlignment.CENTER),
        ])

        return ft.View(
            "/card_flip",
            controls=[
                header,
                ft.Divider(),
                prize_info,
                ft.Container(content=grid_container, height=340, padding=10),
                ft.Container(height=10),
                ft.Container(content=status_text,alignment=ft.alignment.center),
                ft.Container(content=play_btn, alignment=ft.alignment.center)
                
            ]
        )

    # ----------------------------------------------------
    # 🏠 MAIN HOME VIEW
    # ----------------------------------------------------
    def get_main_home_view():
        user_wallet = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=ft.Colors.GREEN_400, size=20),
                ft.Column([
                    ft.Text("လက်ကျန်ငွေ", size=10, color=ft.Colors.GREY_400),
                    wallet_text,
                ], spacing=1)
            ]),
            padding=10, bgcolor=ft.Colors.WHITE10, border_radius=10
        )

        user_info = ft.Container(
            content=ft.Row([
                ft.Column([user_name_text, user_phone_text], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=1),
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=ft.Colors.AMBER_400, size=28),
            ]),
            padding=10, bgcolor=ft.Colors.WHITE10, border_radius=10
        )

        header_section = ft.Row([user_wallet, user_info], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        banner_image = ft.Container(
            content=ft.Image(
                src="icon.png",
                width=200,
                height=200,
                fit=ft.ImageFit.COVER,
            ),
            alignment=ft.alignment.center,
            width=300,
            margin=ft.margin.only(bottom=10)
        )

        btn_slot = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CASINO, size=28),
                ft.Text("ကတ်လှန်ဂိမ်းဆော့မယ်", size=18, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12)),
            width=280, height=50,
            on_click=lambda _: (page.views.append(card_flip_page()), page.update())
        )

        btn_2d = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CASINO, size=28),
                ft.Text("2D ထိုးမည်", size=20, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12)),
            width=280, height=50,
            on_click=lambda _: (page.views.append(get_2d_page()), page.update())
        )

        btn_history = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.RECEIPT_LONG, size=28),
                ft.Text("ထိုးထားသော စာရင်းများ", size=18, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12)),
            width=280, height=50,
            on_click=lambda _: (page.views.append(get_history_page()), page.update())
        )

        btn_results = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.LOOKS_TWO, size=28),
                ft.Text("2D ထွက်ဂဏန်းများကြည့်မည်", size=16, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE_700, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12)),
            width=280, height=50,
            on_click=lambda _: (page.views.append(get_results_page()), page.update())
        )

        return ft.View(
            route="/home",
            controls=[
                ft.AppBar(
                    title=ft.Text("Lucky 2D users", color="Yellow", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    automatically_imply_leading=False,
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Refresh Balance",
                            on_click=refresh_wallet_ui
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SUPPORT_AGENT,
                            tooltip="Help",
                            on_click=open_help_dialog
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            tooltip="Log out",
                            on_click=lambda _: (
                                page.client_storage.remove("saved_phone"),
                                page.client_storage.remove("saved_name"),
                                page.views.clear(), 
                                page.views.append(show_login_signup_view()), 
                                page.update()
                            )
                        )
                    ]
                ),
                ft.Column([
                    header_section,
                    marquee_container,
                    ft.Container(
                        content=ft.Column([banner_image,btn_slot, btn_2d, btn_history, btn_results], 
                        spacing=10, 
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO
                        ),
                        expand=True,
                        alignment=ft.alignment.center
                    )
                ], expand=True)
            ],
            padding=15
        )

    page.on_view_pop = lambda e: go_back()

    # ----------------------------------------------------
    # 🚀 APP STARTUP
    # ----------------------------------------------------
    saved_phone = page.client_storage.get("saved_phone")
    saved_name = page.client_storage.get("saved_name")

    user_phone_text=ft.Text(saved_phone if saved_phone else "")
    user_name_text=ft.Text(saved_name if saved_name else "")
    wallet_text=ft.Text("0 ks")

    page.views.clear()
    
    if saved_phone:
        current_user["phone"] = saved_phone
        current_user["name"] = saved_name if saved_name else ""
        
        page.views.append(get_main_home_view())
        page.update()
        
        try:
            refresh_wallet_ui()
        except:
            pass
    else:
        page.views.append(show_login_signup_view())
        page.update()

import os

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=int(os.environ.get("PORT", 8080)), assets_dir="assets")
