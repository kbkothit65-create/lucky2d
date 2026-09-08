import flet as ft
from supabase import create_client, Client

SUPABASE_URL = "https://xtnuvccclnezphranjer.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0bnV2Y2NjbG5lenBocmFuamVyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTE1NDUxOCwiZXhwIjoyMTAwNzMwNTE4fQ.rkJgdp7pqxFtbscBUAbphNNzxCx5nNBN1uYzpr8hMKo"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Lucky 2D Agent App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # ဖုန်း Screen Size နှင့် Resize လုပ်မရအောင် ပိတ်ထားခြင်း
    page.window.width = 390
    page.window.height = 800
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.DARK

    def show_snackbar(message, color=ft.Colors.GREEN):
        snack = ft.SnackBar(ft.Text(message, color=ft.Colors.WHITE), bgcolor=color)
        page.open(snack)
        page.update()

    # --- 2. MENU PAGE ---
    def load_menu_page(agent_data):
        page.clean()

        balance_text = ft.Text(f"Balance: {agent_data.get('balance', 0):,} ကျပ်", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        agent_info = ft.Text(f"{agent_data.get('name')} ({agent_data.get('phone')})", size=13, weight=ft.FontWeight.W_500)

        def handle_logout(e):
            page.client_storage.remove("agent_phone")
            page.client_storage.remove("agent_name")
            load_login_page()

        logout_btn = ft.IconButton(icon=ft.Icons.LOGOUT, icon_color=ft.Colors.RED, tooltip="Logout", on_click=handle_logout)

        top_bar = ft.Row(
            [ft.Column([balance_text, agent_info], spacing=2), logout_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Deposit Section
        dep_amount_field = ft.TextField(label="ထည့်မည့် ငွေပမာဏ (Amount)", keyboard_type=ft.KeyboardType.NUMBER)
        dep_phone_field = ft.TextField(label="User ၏ ဖုန်းနံပါတ်", keyboard_type=ft.KeyboardType.PHONE)

        def transfer_money(e):
            try:
                amt_str = dep_amount_field.value.strip() if dep_amount_field.value else ""
                target_phone = dep_phone_field.value.strip() if dep_phone_field.value else ""

                if not amt_str or not target_phone or not amt_str.isdigit():
                    show_snackbar("အချက်အလက်များကို မှန်ကန်စွာ ထည့်ပါ။", ft.Colors.RED)
                    return

                amount = int(amt_str)
                if amount <= 0 or agent_data['balance'] < amount:
                    show_snackbar("လက်ကျန်ငွေ မလုံလောက်ပါ (သို့) ငွေပမာဏ မှားယွင်းနေပါသည်။", ft.Colors.RED)
                    return

                user_res = supabase.table('users').select('*').eq('id', target_phone).execute()
                if not user_res.data:
                    show_snackbar("ဤဖုန်းနံပါတ်ဖြင့် User အကောင့် မရှိပါ။", ft.Colors.RED)
                    return

                new_user_bal = user_res.data[0]['balance'] + amount
                supabase.table('users').update({'balance': new_user_bal}).eq('id', target_phone).execute()

                new_agent_bal = agent_data['balance'] - amount
                supabase.table('agents').update({'balance': new_agent_bal}).eq('phone', agent_data['phone']).execute()

                agent_data['balance'] = new_agent_bal
                balance_text.value = f"Balance: {agent_data['balance']:,} ကျပ်"
                dep_amount_field.value = ""
                dep_phone_field.value = ""
                
                show_snackbar("ငွေပေးပို့ခြင်း အောင်မြင်ပါသည်။", ft.Colors.GREEN)
                page.update()
            except Exception as ex:
                show_snackbar(f"အမှား: {str(ex)}", ft.Colors.RED)

        transfer_btn = ft.ElevatedButton(text="ငွေပေးပို့မည်", on_click=transfer_money, color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE)
        
        deposit_box = ft.Container(
            content=ft.Column([
                ft.Text("User အကောင့်သို့ ငွေထည့်ရန်", size=15, weight=ft.FontWeight.BOLD),
                dep_amount_field,
                dep_phone_field,
                transfer_btn
            ], spacing=10),
            padding=15,
            bgcolor=ft.Colors.GREY_900,
            border_radius=10
        )

        # Withdraw Section
        with_amount_field = ft.TextField(label="ထုတ်မည့် ငွေပမာဏ (Amount)", keyboard_type=ft.KeyboardType.NUMBER)
        with_phone_field = ft.TextField(label="User ၏ ဖုန်းနံပါတ်", keyboard_type=ft.KeyboardType.PHONE)

        def withdraw_money(e):
            try:
                amt_str = with_amount_field.value.strip() if with_amount_field.value else ""
                target_phone = with_phone_field.value.strip() if with_phone_field.value else ""

                if not amt_str or not target_phone or not amt_str.isdigit():
                    show_snackbar("အချက်အလက်များကို မှန်ကန်စွာ ထည့်ပါ။", ft.Colors.RED)
                    return
                amount = int(amt_str)
                if amount <= 0:
                    show_snackbar("ငွေပမာဏ မှားယွင်းနေပါသည်။", ft.Colors.RED)
                    return

                user_res = supabase.table('users').select('*').eq('id', target_phone).execute()
                if not user_res.data:
                    show_snackbar("ဤဖုန်းနံပါတ်ဖြင့် User အကောင့် မရှိပါ။", ft.Colors.RED)
                    return

                if user_res.data[0]['balance'] < amount:
                    show_snackbar("User ၏ လက်ကျန်ငွေ မလုံလောက်ပါ။ (ငွေပိုထုတ်၍မရပါ)", ft.Colors.RED)
                    return

                new_user_bal = user_res.data[0]['balance'] - amount
                supabase.table('users').update({'balance': new_user_bal}).eq('id', target_phone).execute()

                new_agent_bal = agent_data['balance'] + amount
                supabase.table('agents').update({'balance': new_agent_bal}).eq('phone', agent_data['phone']).execute()

                agent_data['balance'] = new_agent_bal
                balance_text.value = f"Balance: {agent_data['balance']:,} ကျပ်"
                with_amount_field.value = ""
                with_phone_field.value = ""

                
                show_snackbar("ငွေထုတ်ယူခြင်း အောင်မြင်ပါသည်။", ft.Colors.GREEN)
                page.update()
            except Exception as ex:
                show_snackbar(f"အမှား: {str(ex)}", ft.Colors.RED)

        withdraw_btn = ft.ElevatedButton(text="ငွေထုတ်မည်", on_click=withdraw_money, color=ft.Colors.WHITE, bgcolor=ft.Colors.ORANGE_800)

        withdraw_box = ft.Container(
            content=ft.Column([
                ft.Text("User အကောင့်မှ ငွေထုတ်ရန်", size=15, weight=ft.FontWeight.BOLD),
                with_amount_field,
                with_phone_field,
                withdraw_btn
            ], spacing=10),
            padding=15,
            bgcolor=ft.Colors.GREY_900,
            border_radius=10
        )

        # Page ပေါ်သို့ တိုက်ရိုက် ထည့်သွင်းခြင်း
        page.add(
            ft.Container(
                content=ft.Column([
                    top_bar,
                    ft.Divider(),
                    deposit_box,
                    withdraw_box
                ], spacing=15, scroll=ft.ScrollMode.AUTO),
                width=370,
                height=780,
                padding=10
            )
        )
        page.update()

    # --- 1. LOGIN PAGE ---
    def load_login_page():
        page.clean()

        saved_phone = page.client_storage.get("agent_phone")
        saved_name = page.client_storage.get("agent_name")

        if saved_phone and saved_name:
            try:
                res = supabase.table('agents').select('*').eq('phone', saved_phone).eq('name', saved_name).eq('role', 'agent').execute()
                if res.data:
                    load_menu_page(res.data[0])
                    return
            except:
                pass

        phone_field = ft.TextField(label="ဖုန်းနံပါတ်", keyboard_type=ft.KeyboardType.PHONE)
        name_field = ft.TextField(label="အမည် (Name)")

        def handle_login(e):
            phone = phone_field.value.strip() if phone_field.value else ""
            name = name_field.value.strip() if name_field.value else ""
            if not phone or not name:
                show_snackbar("ဖုန်းနံပါတ်နှင့် အမည်ကို ဖြည့်ပါ", ft.Colors.RED)
                return

            try:
                response = supabase.table('agents').select('*').eq('phone', phone).eq('name', name).execute()
                
                if response.data and len(response.data) > 0:
                    page.client_storage.set("agent_phone", phone)
                    page.client_storage.set("agent_name", name)
                    load_menu_page(response.data[0])
                else:
                    show_snackbar("ဖုန်းနံပါတ် (သို့) အမည် မှားယွင်းနေပါသည်။", ft.Colors.RED)
            except Exception as ex:
                show_snackbar(f"ချိတ်ဆက်မှု အမှား: {str(ex)}", ft.Colors.RED)

        login_btn = ft.ElevatedButton(text="Login ဝင်မည်", on_click=handle_login, color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN)

        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Agent Login", size=20, weight=ft.FontWeight.BOLD),
                    phone_field,
                    name_field,
                    login_btn
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                padding=25,
                bgcolor=ft.Colors.GREY_900,
                border_radius=10,
                width=330
            )
        )
        page.update()

    load_login_page()

ft.app(target=main, assets_dir="assets")