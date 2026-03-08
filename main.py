import discord
from discord.ext import commands
import asyncio

# --- إعدادات مدينة الخليج GULF TOWN ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix='-', intents=intents)

# أسماء الرتب (تأكد إنها نفس اللي بسيرفرك)
STAFF_ROLE = "Support"      # رتبة الإدارة لاستلام التذاكر
MEMBER_ROLE = "Citizen"    # الرتبة اللي تنعطى وقت التفعيل

# --- نظام التذاكر (Tickets) مع حماية الإغلاق ---
class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.claimed_by = None

    @discord.ui.button(label="استلام التذكرة 🤝", style=discord.ButtonStyle.blurple, custom_id="claim_btn")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.name == STAFF_ROLE for role in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("عذراً، هذا الأمر للإدارة فقط! ❌", ephemeral=True)
        
        self.claimed_by = interaction.user
        button.disabled = True
        button.label = f"مستلمة بواسطة {interaction.user.name}"
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"✅ {interaction.user.mention} استلم التذكرة وسيقوم بمساعدتك.")

    @discord.ui.button(label="إغلاق 🔒", style=discord.ButtonStyle.red, custom_id="close_btn")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.administrator or (self.claimed_by and interaction.user.id == self.claimed_by.id):
            await interaction.response.send_message("🔒 سيتم إغلاق التذكرة خلال 5 ثوانٍ...")
            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("❌ لا يمكنك إغلاق التذكرة إلا إذا كنت أنت المستلم أو إداري!", ephemeral=True)

class OpenTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تذكرة 🎫", style=discord.ButtonStyle.green, custom_id="open_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = await interaction.guild.create_text_channel(f'ticket-{interaction.user.name}')
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await channel.send(f"مرحباً {interaction.user.mention}، انتظر رد الإدارة.", view=TicketControlView())
        await interaction.response.send_message(f"✅ تم فتح تذكرتك: {channel.mention}", ephemeral=True)

# --- الأوامر العامة لمدينة الخليج ---
@bot.command()
async def خط(ctx):
    await ctx.message.delete()
    await ctx.send("💜 ▬▬▬▬▬▬▬▬▬▬ **GT** ▬▬▬▬▬▬▬▬▬▬ 💜")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def تفعيل(ctx, member: discord.Member, *, name: str):
    role = discord.utils.get(ctx.guild.roles, name=MEMBER_ROLE)
    if role:
        await member.add_roles(role)
        await member.edit(nick=f"GT | {name}")
        await ctx.send(f"✅ تم تفعيل {member.mention} بنجاح باسم: **{name}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def تنبيه(ctx, *, text: str):
    await ctx.message.delete()
    embed = discord.Embed(title="📢 تنبيه من إدارة GULF TOWN", description=text, color=0x9b59b6)
    embed.set_footer(text=f"المرسل: {ctx.author.name}")
    await ctx.send(content="@everyone", embed=embed)

@bot.command()
async def هوية(ctx, name: str, age: str, loc: str):
    embed = discord.Embed(title="💳 بطاقة هوية مدينة الخليج", color=0x9b59b6)
    embed.add_field(name="الاسم:", value=name, inline=True)
    embed.add_field(name="العمر:", value=age, inline=True)
    embed.add_field(name="المنطقة:", value=loc, inline=True)
    embed.set_thumbnail(url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def سيت_اب(ctx):
    await ctx.send("🌴 **لوحة تحكم مدينة الخليج (GULF TOWN)** 🌴", view=OpenTicketView())

@bot.event
async def on_ready():
    bot.add_view(OpenTicketView())
    bot.add_view(TicketControlView())
    print(f"✅ {bot.user} جاهز للعمل في مدينة الخليج!")

# التوكن حقك
bot.run('MTQ3OTA5NTMxMDA1OTA0NDk1NA.GZvNlW.yfC7s-gfCI8ioZvFcpz0lnDU0wz2q1jCteHhcE')
@bot.command()
@commands.has_permissions(manage_messages=True)
async def مسح(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'✅ تم مسح {amount} رسالة بنجاح في مدينة الخليج!', delete_after=5)