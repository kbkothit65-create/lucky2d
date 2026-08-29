import time
import requests
from supabase import create_client

# Supabase URL နှင့် KEY
SUPABASE_URL = "https://xtnuvccclnezphranjer.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0bnV2Y2NjbG5lenBocmFuamVyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTE1NDUxOCwiZXhwIjoyMTAwNzMwNTE4fQ.rkJgdp7pqxFtbscBUAbphNNzxCx5nNBN1uYzpr8hMKo"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BOT_TOKEN = "8680151013:AAGCgLOOKzLTm3X4PiJa8TaUVR3NUEd-S6s"
offset = 0

def process_telegram_clicks():
    global offset
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=10"
    
    try:
        response = requests.get(url).json()
        
        if "result" in response:
            for update in response["result"]:
                offset = update["update_id"] + 1
                
                if "callback_query" in update:
                    query = update["callback_query"]
                    query_id = query["id"]
                    data = query["data"]
                    message_id = query["message"]["message_id"]
                    chat_id = query["message"]["chat"]["id"]
                    
                    print(f"\n[CLICKED]: {data}")
                    action, deposit_id = data.split("_")
                    
                    # 1. Transactions table ထဲမှ Transaction ID ဖြင့် ရှာမည်
                    dep_res = supabase.table("transactions").select("*").eq("id", deposit_id).execute()
                    
                    if dep_res.data:
                        deposit = dep_res.data[0]
                        user_phone = deposit.get("phone") or deposit.get("user_id") or deposit.get("id")
                        amount = deposit.get("amount", 0)
                        current_status = deposit.get("status", "Pending")
                        
                        # Transaction အမျိုးအစား ခွဲခြားခြင်း (deposit သို့မဟုတ် withdraw)
                        tx_type = str(deposit.get("type", "deposit")).lower()
                        
                        if str(current_status).lower() == "pending":
                            # 2. Users Table ထဲမှ User ကို ရှာမည်
                            user_res = supabase.table("users").select("*").eq("id", user_phone).execute()
                            if not user_res.data:
                                user_res = supabase.table("users").select("*").eq("id", user_phone).execute()

                            if user_res.data:
                                user_info = user_res.data[0]
                                current_bal = user_info.get("balance", 0) or 0
                                
                                # --- (A) Approve နှိပ်သည့်အခါ ---
                                if action == "approve":
                                    if "withdraw" in tx_type:
                                        # ငွေထုတ် - App ဘက်က Balance နှုတ်ပြီးသားဖြစ်၍ Status သာ ပြောင်းမည်
                                        alert_msg = f"✅ ဖုန်း {user_phone} ၏ ငွေထုတ်ယူမှု {amount:,} MMK ကို အတည်ပြုလိုက်ပါပြီ။"
                                    else:
                                        # ငွေသွင်း - User Balance ထဲ ငွေသွားပေါင်းမည်
                                        new_bal = current_bal + int(amount)
                                        supabase.table("users").update({"balance": new_bal}).eq("id", user_info["id"]).execute()
                                        alert_msg = f"✅ ဖုန်း {user_phone} ထံသို့ {amount:,} MMK ထည့်ပေးလိုက်ပါပြီ။"

                                    supabase.table("transactions").update({"status": "Approved"}).eq("id", deposit_id).execute()
                                    status_text = "✅ APPROVED"
                                    print(f"SUCCESS: Transaction #{deposit_id} Approved!")
                                
                                # --- (B) Reject နှိပ်သည့်အခါ ---
                                elif action == "reject":
                                    if "withdraw" in tx_type:
                                        # ငွေထုတ် Reject - အကောင့်ထဲ ငွေပြန်ပေါင်းပေးမည် (Refund)
                                        new_bal = current_bal + int(amount)
                                        supabase.table("users").update({"balance": new_bal}).eq("id", user_info["id"]).execute()
                                        alert_msg = f"❌ ငွေထုတ်လွှာ #{deposit_id} ကို ပယ်ဖျက်ပြီး {amount:,} MMK အကောင့်ထဲ ပြန်ထည့်ပေးလိုက်ပါပြီ။"
                                    else:
                                        # ငွေသွင်း Reject - Status ပဲ ငြင်းမည်
                                        alert_msg = f"❌ ငွေသွင်းလွှာ #{deposit_id} ကို ပယ်ဖျက်လိုက်ပါပြီ။"

                                    supabase.table("transactions").update({"status": "Rejected"}).eq("id", deposit_id).execute()
                                    status_text = "❌ REJECTED"
                                    print(f"SUCCESS: Transaction #{deposit_id} Rejected!")
                                    
                            else:
                                alert_msg = f"❌ User {user_phone} ကို users table ထဲမှာ မတွေ့ပါ!"
                                status_text = "❌ USER NOT FOUND"
                                print("FAILED: User not found!")
                                
                            # Admin ဖုန်းတွင် Alert Pop-up ပြပေးမည်
                            requests.post(
                                f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                                json={"callback_query_id": query_id, "text": alert_msg, "show_alert": True}
                            )
                            
                            # Telegram Message တွင် Status စာသား ပြောင်းပေးမည်
                            orig_text = query["message"]["text"]
                            requests.post(
                                f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                                json={
                                    "chat_id": chat_id,
                                    "message_id": message_id,
                                    "text": f"{orig_text}\n\n**Status: {status_text}**"
                                }
                            )
                        else:
                            print(f"INFO: Transaction #{deposit_id} က status: '{current_status}' ဖြစ်ပြီးသားပါ။")
                    else:
                        print(f"FAILED: Transaction ID #{deposit_id} ကို transactions table ထဲမှာ မတွေ့ပါ။")
    except Exception as e:
        print("Error occurred:", e)

print("🚀 Telegram Bot Listener Started...")
while True:
    process_telegram_clicks()
    time.sleep(1)
