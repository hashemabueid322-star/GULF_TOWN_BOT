import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- تشغيل السيرفر لبقاء البوت Live ---
app = Flask('')
@app.route('/')
def home(): return "Gulf Town RP is Live!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت والـ Intents ---
intents = discord.Intents.all() # استخدمنا الكل لضمان تخطي أي قيود
bot = commands.Bot(command_prefix='-', intents=intents, help_command=None)

# --- الأيدي (IDs) الخاصة بالرتب ---
RP_ROLE_ID = 1479535297917354077     
STAFF_ROLE_ID = 1479535409863201014   

# --- [1] نظام مراجعة الهوية ---
class IdentityReview(discord.ui.View):
    def __init__(self, applicant):
        super().__init__(timeout=None)
        self.applicant = applicant

    @discord.ui.button(label="قبول الهوية ✅", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role not in interaction.user.roles:
            return await interaction.response.send_message("❌ للإدارة فقط!", ephemeral=True)
        role = interaction.guild.get_role(RP_ROLE_ID)
        await self.applicant.add_roles(role)
        await interaction.message.delete()
        await interaction.channel.send(f"✅ تم قبول هوية {self.applicant.mention} ومنحه رتبة الـ RP!")

# --- [2] نظام الرحلات ---
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

# --- الأحداث ومعالجة الرسائل ---
@bot.event
async def on_ready():
    print(f'✅ {bot.user} متصل وجاهز لاستلام الأوامر!')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    # طباعة الرسالة في الكونسول للتأكد أن البوت يراها
    print(f"رسالة جديدة: {message.content}") 
    await bot.process_commands(message)

# --- الأوامر المباشرة ---

@bot.command()
async def سيت_اب_رحلات(ctx):
    view = discord.ui.View()
    btn = discord.ui.Button(label="بدأ رحلة ✈️", style=discord.ButtonStyle.success)
    async def trip_c(i): await i.response.send_modal(TripModal())
    btn.callback = trip_c
    view.add_item(btn)
    await ctx.send("🎮 **تحكم بالرحلات - مدينة الخليج**", view=view)

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
    await ctx.send("💳 **نظام الحضور والغياب**", view=view)

@bot.command()
async def انشاء_هوية(ctx):
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    await ctx.send("👤 اسمك في الـ RP؟")
    name = await bot.wait_for('message', check=check)
    await ctx.send("🎂 عمرك؟")
    age = await bot.wait_for('message', check=check)
    embed = discord.Embed(title="💳 طلب مراجعة هوية", description=f"المواطن: {ctx.author.mention}\nالاسم: {name.content}\nالعمر: {age.content}", color=discord.Color.blue())
    await ctx.send("📥 **طلب جديد:**", embed=embed, view=IdentityReview(ctx.author))

@bot.command()
async def خط(ctx):
    await ctx.message.delete()
    await ctx.send("💜 ▬▬▬▬▬▬▬▬▬ **GULF TOWN** ▬▬▬▬▬▬▬▬▬ 💜")

# --- التشغيل ---
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))