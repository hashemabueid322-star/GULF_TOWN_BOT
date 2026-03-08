import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio

# --- تشغيل السيرفر لبقاء البوت Live ---
app = Flask('')
@app.route('/')
def home(): return "Gulf Town RP is Online!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت والـ Intents ---
intents = discord.Intents.default()
intents.message_content = True # تأكد من تفعيلها في موقع المطورين
intents.members = True
bot = commands.Bot(command_prefix='-', intents=intents)

# --- الأيدي (IDs) الخاصة بالرتب ---
RP_ROLE_ID = 1479535297917354077     # رتبة الـ RP
STAFF_ROLE_ID = 1479535409863201014   # رتبة الإدارة

# --- [1] نظام مراجعة الهوية (قبول/رفض) ---
class IdentityReview(discord.ui.View):
    def __init__(self, applicant):
        super().__init__(timeout=None)
        self.applicant = applicant

    @discord.ui.button(label="قبول الهوية ✅", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild.get_role(STAFF_ROLE_ID) not in interaction.user.roles:
            return await interaction.response.send_message("❌ للإدارة فقط!", ephemeral=True)
        role = interaction.guild.get_role(RP_ROLE_ID)
        await self.applicant.add_roles(role)
        await interaction.message.delete()
        await interaction.channel.send(f"✅ تم قبول هوية {self.applicant.mention} ومنحه رتبة الـ RP!")

    @discord.ui.button(label="رفض ❌", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild.get_role(STAFF_ROLE_ID) not in interaction.user.roles:
            return await interaction.response.send_message("❌ للإدارة فقط!", ephemeral=True)
        await interaction.message.delete()
        await interaction.channel.send(f"❌ تم رفض طلب هوية {self.applicant.mention}.")

# --- [2] نظام الرحلات (أزرار مستقلة) ---
class TripModal(discord.ui.Modal, title="إنشاء رحلة جديدة ✈️"):
    time = discord.ui.TextInput(label="الموعد", placeholder="مثال: 10:00 مساءً")
    helper = discord.ui.TextInput(label="المساعد", placeholder="اسم المساعد")
    details = discord.ui.TextInput(label="التفاصيل", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="✈️ إعلان رحلة: مدينة الخليج", color=discord.Color.gold())
        embed.add_field(name="📅 الموعد:", value=self.time.value, inline=False)
        embed.add_field(name="👨‍✈️ المساعد:", value=self.helper.value, inline=True)
        embed.add_field(name="📝 التفاصيل:", value=self.details.value, inline=False)
        await interaction.response.send_message(content="@everyone", embed=embed)

class TripControl(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="بدأ رحلة ✈️", style=discord.ButtonStyle.success)
    async def start_trip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TripModal())
    @discord.ui.button(label="إعلان إعصار 🌪️", style=discord.ButtonStyle.danger)
    async def storm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🌪️ **تحذير! إعصار قادم لمدينة الخليج.. استعدوا!**", content="@everyone")

# --- [3] نظام التذاكر (استلام وإغلاق) ---
class TicketControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.claimed_by = None

    @discord.ui.button(label="استلام 🤝", style=discord.ButtonStyle.primary)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild.get_role(STAFF_ROLE_ID) not in interaction.user.roles:
            return await interaction.response.send_message("❌ للإدارة فقط!", ephemeral=True)
        self.claimed_by = interaction.user
        button.disabled = True
        button.label = f"استلمها: {interaction.user.name}"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="إغلاق 🔒", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.claimed_by:
            return await interaction.response.send_message("❌ فقط المستلم يغلقها!", ephemeral=True)
        await interaction.channel.delete()

# --- الأحداث ومعالجة الرسائل ---
@bot.event
async def on_ready():
    print(f'✅ {bot.user} جاهز للعمل في مدينة الخليج')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    await bot.process_commands(message) # هذا السطر ضروري لعمل الأوامر

# --- الأوامر المنفصلة ---

@bot.command()
async def سيت_اب_رحلات(ctx):
    await ctx.send("🎮 **تحكم بالرحلات والطقس**", view=TripControl())

@bot.command()
async def سيت_اب_تذاكر(ctx):
    view = discord.ui.View()
    btn = discord.ui.Button(label="فتح تذكرة 🎫", style=discord.ButtonStyle.success)
    async def tkt_c(i):
        ch = await i.guild.create_text_channel(f"تذكرة-{i.user.name}")
        await ch.send(f"مرحباً {i.user.mention}، انتظر الإدارة.", view=TicketControl())
        await i.response.send_message(f"فتحت تذكرتك: {ch.mention}", ephemeral=True)
    btn.callback = tkt_c
    view.add_item(btn)
    await ctx.send("🎫 **قسم التواصل مع الإدارة**", view=view)

@bot.command()
async def سيت_اب_هوية(ctx):
    view = discord.ui.View()
    btn_in = discord.ui.Button(label="تسجيل دخول 📥", style=discord.ButtonStyle.primary)
    async def in_c(i): await i.response.send_message(f"📥 المواطن {i.user.mention} سجل **دخول** الآن.")
    btn_in.callback = in_c
    btn_out = discord.ui.Button(label="تسجيل خروج 📤", style=discord.ButtonStyle.danger)
    async def out_c(i): await i.response.send_message(f"📤 المواطن {i.user.mention} سجل **خروج** الآن.")
    btn_out.callback = out_c
    view.add_item(btn_in); view.add_item(btn_out)
    await ctx.send("💳 **نظام الحضور والغياب للهوية**", view=view)

@bot.command()
async def انشاء_هوية(ctx):
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    await ctx.send("👤 اسمك في الـ RP؟"); name = await bot.wait_for('message', check=check)
    await ctx.send("🎂 عمرك؟"); age = await bot.wait_for('message', check=check)
    embed = discord.Embed(title="💳 طلب مراجعة هوية", description=f"المواطن: {ctx.author.mention}\nالاسم: {name.content}\nالعمر: {age.content}", color=discord.Color.blue())
    await ctx.send("✅ تم الإرسال للإدارة.")
    await ctx.send("📥 **طلب مراجعة جديد:**", embed=embed, view=IdentityReview(ctx.author))

@bot.command()
async def خط(ctx):
    await ctx.message.delete()
    await ctx.send("💜 ▬▬▬▬▬▬▬▬▬ **GULF TOWN** ▬▬▬▬▬▬▬▬▬ 💜")

# --- التشغيل ---
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))