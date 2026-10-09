import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pytz
import flet as ft
import requests
import json
from datetime import datetime, timedelta
from supabase import create_client, Client

yangon_tz = pytz.timezone('Asia/Yangon')
now = datetime.now(yangon_tz)
# ----------------------------------------------------
# 🔗 SUPABASE CONNECTION SETTINGS
# ----------------------------------------------------
SUPABASE_URL = "https://xtnuvccclnezphranjer.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0bnV2Y2NjbG5lenBocmFuamVyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTE1NDUxOCwiZXhwIjoyMTAwNzMwNTE4fQ.rkJgdp7pqxFtbscBUAbphNNzxCx5nNBN1uYzpr8hMKo"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


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

    def go_back(e=None):
        if len(page.views) > 1:
            page.views.pop()
            page.update()

    # ----------------------------------------------------
    # 👑 ADMIN SETTLE DIALOG
    # ----------------------------------------------------
    def open_settle_dialog():
        win_num_input = ft.TextField(label="ထွက်ဂဏန်း (ဥပမာ - 00)", keyboard_type=ft.KeyboardType.NUMBER, max_length=2)
        session_dropdown = ft.Dropdown(
            label="ပွဲချိန် ရွေးပါ",
            options=[ft.dropdown.Option("12:01 PM"), ft.dropdown.Option("04:30 PM")],
            value="12:01 PM"
        )

        def confirm_settle(e):
            w_num = win_num_input.value.strip() if win_num_input.value else ""
            s_val = session_dropdown.value
            if len(w_num) != 2:
                page.open(ft.SnackBar(ft.Text("🛑 ၂ လုံးဂဏန်း အတိအကျ ထည့်ပါ (ဥပမာ 05)"), bgcolor=ft.Colors.RED_800))
                return

            try:
                today_date_str = datetime.now().strftime("%d.%m.%Y")

                existing_res = supabase.table("win_results").select("*").eq("date", today_date_str).eq("session", s_val).execute()
                
                if existing_res.data and existing_res.data[0].get("win_num"):
                    page.close(settle_dialog)
                    page.open(ft.SnackBar(ft.Text(f"🛑 Error: ({today_date_str}) - {s_val} အတွက် ပေါက်ဂဏန်း ထည့်ပြီးဖြစ်၍ ထပ်မံပြင်ဆင်၍ မရတော့ပါ။"), bgcolor=ft.Colors.RED_800))
                    return

                bets_res = supabase.table("bets").select("*").eq("session", s_val).eq("settled", False).execute()
                bets = bets_res.data if bets_res.data else []

                for bet in bets:
                    b_id = bet["id"]
                    u_id = bet["user_id"]
                    numbers_list = [n.strip() for n in bet["numbers"].split(",")]
                    unit_price = bet["unit_price"]

                    if w_num in numbers_list:
                        won_amount = unit_price * 90
                        u_res = supabase.table("users").select("balance").eq("id", u_id).execute()
                        if u_res.data:
                            cur_bal = u_res.data[0]["balance"]
                            supabase.table("users").update({"balance": cur_bal + won_amount}).eq("id", u_id).execute()

                    supabase.table("bets").update({"settled": True, "win_num": w_num}).eq("id", b_id).execute()

                if existing_res.data:
                    r_id = existing_res.data[0]["id"]
                    supabase.table("win_results").update({"win_num": w_num}).eq("id", r_id).execute()
                else:
                    supabase.table("win_results").insert({
                        "date": today_date_str,
                        "session": s_val,
                        "win_num": w_num
                    }).execute()

                page.close(settle_dialog)
                page.open(ft.SnackBar(ft.Text(f"✅ ပေါက်ဂဏန်း ({w_num}) ဖြင့် လျော်ပေးမှုနှင့် မှတ်တမ်းတင်ခြင်း ပြီးစီးပါပြီ!"), bgcolor=ft.Colors.GREEN_800))
            except Exception as ex:
                page.open(ft.SnackBar(ft.Text(f"Settle Error: {ex}"), bgcolor=ft.Colors.RED_800))

        settle_dialog = ft.AlertDialog(
            title=ft.Text("🏆 2D ပေါက်ဂဏန်း ထည့်သွင်းရန်", weight=ft.FontWeight.BOLD),
            content=ft.Column([session_dropdown, win_num_input], tight=True, spacing=10),
            actions=[
                ft.TextButton("မလုပ်တော့ပါ", on_click=lambda _: page.close(settle_dialog)),
                ft.ElevatedButton("လျော်မည် (Settle)", bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE, on_click=confirm_settle)
            ]
        )
        page.open(settle_dialog)

    def open_wallet():
        tx_list = ft.ListView(expand=True, spacing=10)

        def load_pending_transactions():
            tx_list.controls.clear()
            try:
                res = supabase.table("transactions").select("*").eq("status", "Pending").order("id", desc=True).execute()
                pending_txs = res.data if res.data else []
            except Exception as ex:
                pending_txs = []

            if not pending_txs:
                tx_list.controls.append(
                    ft.Container(
                        content=ft.Text("စောင့်ဆိုင်းဆဲ ငွေသွင်း/ငွေထုတ် တောင်းဆိုချက် မရှိပါ။", color=ft.Colors.GREY_400, size=13),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                )
            else:
                for tx in pending_txs:
                    tx_id = tx["id"]
                    u_id = tx["user_id"]
                    tx_type = tx["type"]
                    amt = tx["amount"]
                    p_type = tx["pay_type"]
                    ref = tx["trans_id_or_acc"]

                    def approve_tx(e, tid=tx_id, uid=u_id, ttype=tx_type, tamt=amt):
                        try:
                            if ttype == "deposit":
                                u_res = supabase.table("users").select("balance").eq("id", uid).execute()
                                if u_res.data:
                                    c_bal = u_res.data[0]["balance"]
                                    supabase.table("users").update({"balance": c_bal + tamt}).eq("id", uid).execute()

                            supabase.table("transactions").update({"status": "Approved"}).eq("id", tid).execute()
                            page.open(ft.SnackBar(ft.Text("✅ တောင်းဆိုချက်ကို အတည်ပြုလိုက်ပါပြီ။"), bgcolor=ft.Colors.GREEN_800))
                            load_pending_transactions()
                        except Exception as ex:
                            page.open(ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_800))

                    def reject_tx(e, tid=tx_id, uid=u_id, ttype=tx_type, tamt=amt):
                        try:
                            if ttype == "withdraw":
                                u_res = supabase.table("users").select("balance").eq("id", uid).execute()
                                if u_res.data:
                                    c_bal = u_res.data[0]["balance"]
                                    supabase.table("users").update({"balance": c_bal + tamt}).eq("id", uid).execute()

                            supabase.table("transactions").update({"status": "Rejected"}).eq("id", tid).execute()
                            page.open(ft.SnackBar(ft.Text("❌ တောင်းဆိုချက်ကို ငြင်းပယ်လိုက်ပါပြီ။"), bgcolor=ft.Colors.RED_800))
                            load_pending_transactions()
                        except Exception as ex:
                            page.open(ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_800))

                    title_str = "📥 ငွေသွင်းရန်" if tx_type == "deposit" else "📤 ငွေထုတ်ရန်"
                    color_str = ft.Colors.GREEN_400 if tx_type == "deposit" else ft.Colors.RED_400

                    # 💡 အချက် (၄) - Admin panel ထဲက withdraw တောင်းဆိုမှုများတွင် ဖုန်းနံပါတ်သက်သက်ကိုသာ Copy ကူးခြင်း
                    copy_action_btn = ft.Container()
                    if tx_type == "withdraw":
                        # ref တွင် "အမည် - ဖုန်းနံပါတ်" ပုံစံ သိမ်းထားသဖြင့် ဖုန်းနံပါတ်ကို သီးသန့်ခွဲထုတ်ယူခြင်း
                        raw_ref = ref
                        if " - " in raw_ref:
                            phone_val = raw_ref.split(" - ")[-1].strip()
                        else:
                            phone_val = raw_ref.strip()

                        def copy_withdraw_phone(e, phone_val=phone_val):
                            try:
                                page.set_clipboard(phone_val)
                            except:
                                try:
                                    pyperclip.copy(phone_val)
                                except:
                                    pass
                            page.open(ft.SnackBar(ft.Text(f"📋 ဖုန်းနံပါတ် ({phone_val}) ကို Copy ကူးပြီးပါပြီ!"), bgcolor=ft.Colors.BLUE_800))

                        copy_action_btn = ft.IconButton(
                            icon=ft.Icons.COPY,
                            icon_size=16,
                            tooltip="ဖုန်းနံပါတ် Copy ကူးရန်",
                            on_click=copy_withdraw_phone
                        )
                    card = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"{title_str} ({p_type})", size=13, weight=ft.FontWeight.BOLD, color=color_str),
                                ft.Text(f"{amt:,} Ks", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"• User ဖုန်း: {u_id}", size=12),
                            ft.Row([
                                ft.Text(f"• Ref / ဖုန်း: {ref}", size=12, color=ft.Colors.CYAN_300),
                                copy_action_btn
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.ElevatedButton("Approve", bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, height=35, on_click=approve_tx),
                                ft.ElevatedButton("Reject", bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, height=35, on_click=reject_tx)
                            ], alignment=ft.MainAxisAlignment.END, spacing=10)
                        ], spacing=5),
                        padding=12,
                        bgcolor=ft.Colors.WHITE10,
                        border_radius=8
                    )
                    tx_list.controls.append(card)
            page.update()

        load_pending_transactions()

        return ft.View(
            route="/admin_panel",
            controls=[
                ft.AppBar(
                    title=ft.Text("👑 Admin Management Panel", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back)
                ),
                ft.Container(content=tx_list, padding=10, expand=True)
            ]
        )
    # ----------------------------------------------------
    # 🏠 MAIN HOME VIEW
    # ----------------------------------------------------
    def get_main_home_view():

        banner_image = ft.Container(
            content=ft.Image(
                src="icon.png",
                width=200,
                height=200,
                fit=ft.ImageFit.COVER,
            ),
            alignment=ft.alignment.center,
            width=300,
            margin=ft.margin.only(bottom=15)
        )

        btn_2d = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CASINO, size=28),
                ft.Text("2D ထွက်ဂဏန်း", size=20, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12)),
            width=280, height=55,
            on_click=lambda _: (page.views.append(open_settle_dialog()), page.update())
        )

        btn_wallet = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SWAP_HORIZ, size=28),
                ft.Text("ငွေသွင်း - ငွေထုတ်", size=18, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            style=ft.ButtonStyle(bgcolor=ft.Colors.TEAL_700, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12)),
            width=280, height=55,
            on_click=lambda _: (page.views.append(open_wallet()), page.update())
        )

        return ft.View(
            route="/home",
            controls=[
                ft.AppBar(
                    title=ft.Text("Lucky 2D", color="Yellow", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    automatically_imply_leading=False,
                ),
                ft.Column([
                    ft.Container(
                        content=ft.Column([banner_image, btn_2d, btn_wallet], 
                        spacing=15, 
                        alignment=ft.MainAxisAlignment.CENTER
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