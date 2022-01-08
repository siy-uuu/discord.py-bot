import discord, sqlite3, time
from discord.ext import commands
bot = commands.Bot(command_prefix='#')

client = discord.Client()
riot_token = ""
    
@client.event
async def on_connect():
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
        name TEXT,
        id TEXT,
        yn TEXT,
        stime TEXT
        )
    ''')
    print("출퇴근봇 ONLINE")
    game = discord.Game('League of Legends')
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.content.startswith('!위성'):
        url = 'https://www.weather.go.kr/weather/images/satellite_service.jsp'
        res = urllib.request.urlopen(url).read()

        soup = BeautifulSoup(res, 'html.parser')
        soup = soup.find("div", class_="image-player-slide")
        imgUrl = 'https://www.weather.go.kr' + soup.find("img")["src"]

        typoonEmbed = discord.Embed(title='천리안 2A호 위성사진', description='제공: 기상청', colour=discord.Colour.dark_grey())
        typoonEmbed.set_image(url=imgUrl)
        await message.channel.send(embed=typoonEmbed)


    if "시발" in message.content:
        await message.delete()
        await message.channel.send(f"{message.author.mention} 님이 비속어를 사용하였습니다.")

    if "ㅅㅂ" in message.content:
        await message.delete()
        await message.channel.send(f"{message.author.mention} 님이 비속어를 사용하였습니다.")

    if message.content.startswith('!한강온도'):
        json = requests.get('http://hangang.dkserver.wo.tc/').json()
        temp = json.get("temp") # 한강온도
        time = json.get("time") # 측정시간

        embed = discord.Embed(title='💧 한강온도', description=f'{temp}°C', colour=discord.Colour.blue())
        embed.set_footer(text=f'{time}에 측정됨')

        await message.channel.send(embed=embed)
        
    if message.guild is None:
        if message.author.bot:
            return
        else:
            embed = discord.Embed(colour=discord.Colour.blue(), timestamp=message.created_at)
            embed.add_field(name='전송자', value=message.author, inline=False)
            embed.add_field(name='내용', value=message.content, inline=False)
            embed.set_footer(text=f'!디엠 <@{message.author.id}> [할말] 을 통해 답장을 보내주세요!')
            await client.get_channel(862625590897147944).send(f"`{message.author.name}({message.author.id})`", embed=embed)

    if message.content.startswith('!디엠'):
        if message.author.guild_permissions.manage_messages:
            msg = message.content[26:]
            await message.mentions[0].send(f"**{message.author.name}** 님의 답장: {msg}")
            await message.channel.send(f'`{message.mentions[0]}`에게 DM을 보냈습니다')
        else:
            return
     
    if isinstance(message.channel,
                  discord.abc.PrivateChannel) and message.author.id != "862625590897147944":
        await client.get_user("353382954577297408").send(message.author.name + "(" + str(message.author.id) + "): " + message.content)

    if message.content == "#adddfswDM":
        await message.author.send(".")

    if message.content.startswith("#검색 "):
        UserName = message.content.replace("#검색 ", "")
        UserInfoUrl = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + UserName
        res = requests.get(UserInfoUrl, headers={"X-Riot-Token": riot_token})
        resjs = json.loads(res.text)

        if res.status_code == 200:
            UserIconUrl = "http://ddragon.leagueoflegends.com/cdn/11.3.1/img/profileicon/{}.png"
            embed = discord.Embed(title=f"{resjs['name']} 님의 플레이어 정보",
                                  description=f"**{resjs['summonerLevel']} LEVEL**", color=0xFF9900)

            UserInfoUrl_2 = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/" + resjs["id"]
            res_2 = requests.get(UserInfoUrl_2, headers={"X-Riot-Token": riot_token})
            res_2js = json.loads(res_2.text)

            if res_2js == []:  
                embed.add_field(name=f"{resjs['name']} 님은 언랭크입니다.", value="**언랭크 유저의 정보는 출력하지 않습니다.**", inline=False)

            else:  
                for rank in res_2js:
                    if rank["queueType"] == "RANKED_SOLO_5x5":
                        embed.add_field(name="솔로랭크",
                                        value=f"**티어 : {rank['tier']} {rank['rank']} - {rank['leaguePoints']} LP**\n"
                                              f"**승 / 패 : {rank['wins']} 승 {rank['losses']} 패**", inline=True)

                    else:
                        embed.add_field(name="자유랭크",
                                        value=f"**티어 : {rank['tier']} {rank['rank']} - {rank['leaguePoints']} LP**\n"
                                              f"**승 / 패 : {rank['wins']} 승 {rank['losses']} 패**", inline=True)

            embed.set_author(name=resjs['name'], url=f"http://fow.kr/find/{UserName.replace(' ', '')}",
                             icon_url=UserIconUrl.format(resjs['profileIconId']))
            await message.channel.send(embed=embed)

        else:  
            error = discord.Embed(title="존재하지 않는 소환사명입니다.\n다시 한번 확인해주세요.", color=0xFF9900)
            await message.channel.send(embed=error)

        
    if message.content.startswith("#청소"):
        i = (message.author.guild_permissions.administrator)

        if i is True:
            amount = message.content[4:]
            await message.channel.purge(limit=1)
            await message.channel.purge(limit=int(amount))

            embed = discord.Embed(title="메시지 삭제 알림",
                                  description="최근 디스코드 채팅 {}개가\n관리자 {} 님의 요청으로 인해 정상 삭제 조치 되었습니다.".format(amount,
                                                                                                          message.author),
                                  color=0x000000)
            embed.set_footer(text="",
                             icon_url="")
            await message.channel.send(embed=embed)

        if i is False:
            await message.channel.purge(limit=1)
            await message.channel.send("{}, 당신은 명령어를 사용할 수 있는 권한이 없습니다".format(message.author.mention))
            
        achannel = 807807756853051394


    if message.content == '!명령어':
        embed = discord.Embed(title='명령어', description='!출근\n!퇴근\n!등록여부\n!등록 @유저')
        await message.channel.send(embed=embed)
        
    if message.content.startswith("!등록") and not message.content == '!등록여부':
        if message.author.guild_permissions.administrator:
            try:
                target = message.mentions[0]
            except:
                await message.channel.send('유저가 지정되지 않았습니다')

            try:
                db = sqlite3.connect('main.db')
                cursor = db.cursor()
                cursor.execute(f'SELECT yn FROM main WHERE id = {target.id}')
                result = cursor.fetchone()
                if result is None:
                    sql = 'INSERT INTO main(name, id, yn, stime) VALUES(?,?,?,?)'
                    val = (str(target), str(target.id), str('0'), str('0'))
                else:
                    embed = discord.Embed(title='❌  등록 실패', description='이미 등록된 유저입니다', color=0xFF0000)
                    await message.channel.send(embed=embed)
                    return
                cursor.execute(sql, val)
                db.commit()
                db.close()

                embed = discord.Embed(title='✅  등록 성공', description=f'등록을 성공하였습니다', colour=discord.Colour.green())
                embed.set_author(name=target, icon_url=target.avatar_url)
                await message.channel.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(title='❌  오류', description=f'오류가 발생하였습니다\n`{str(e)}`', color=0xFF0000)
                await message.channel.send(embed=embed)
        else:
            await message.channel.send(f'{message.author.mention} 권한이 부족합니다')

    if message.content == '!등록여부':
        db = sqlite3.connect('main.db')
        cursor = db.cursor()
        cursor.execute(f'SELECT yn FROM main WHERE id = {message.author.id}')
        result = cursor.fetchone()
        if result is None:
            await message.channel.send(f'**{message.author}**님은 등록되지 않았습니다')
        else:
            await message.channel.send(f'**{message.author}**님은 등록되어 있습니다')

    if message.content == "!출근":
        try:
            db = sqlite3.connect('main.db')
            cursor = db.cursor()
            cursor.execute(f'SELECT yn FROM main WHERE id = {message.author.id}')
            result = cursor.fetchone()
            if result is None:
                await message.channel.send(f'{message.author.mention} 등록되지 않은 유저입니다')
                return
            if "y" in result:
                await message.channel.send(f'{message.author.mention} 이미 출근 상태입니다')
                return
            else:
                sql = f'UPDATE main SET yn = ? WHERE id = {message.author.id}'
                val = (str('y'),)
                cursor.execute(sql, val)
                sql = f'UPDATE main SET stime = ? WHERE id = {message.author.id}'
                val = (str(time.time()),)
                cursor.execute(sql, val)
            db.commit()
            db.close()

            embed = discord.Embed(title='', description=f'**{message.author.mention}** 님이 출근하였습니다',
                                  color=discord.Colour.green())
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            embed.set_footer(text='출근시간: ' + time.strftime('%m-%d %H:%M'))
            await client.get_channel(int(achannel)).send(embed=embed)
            await message.channel.send(f'{message.author.mention} 출근완료')
        except Exception as e:
            embed = discord.Embed(title='❌  오류', description=f'오류가 발생하였습니다\n`{str(e)}`', color=0xFF0000)
            await message.channel.send(embed=embed)

    if message.content == "!퇴근":
        try:
            db = sqlite3.connect('main.db')
            cursor = db.cursor()
            cursor.execute(f'SELECT yn FROM main WHERE id = {message.author.id}')
            result = cursor.fetchone()
            if result is None:
                await message.channel.send(f'{message.author.mention} 등록되지 않은 유저입니다')
                return
            else:
                if not "y" in result:
                    await message.channel.send(f'{message.author.mention} 출근상태가 아닙니다')
                    return
                elif "y" in result:
                    sql = f'UPDATE main SET yn = ? WHERE id = {message.author.id}'
                    val = (str('n'),)
                    cursor.execute(sql, val)

                    cursor.execute(f'SELECT stime FROM main WHERE id = {message.author.id}')
                    result = cursor.fetchone()
                    result = str(result).replace('(', '').replace(')', '').replace(',', '').replace("'", "")
                    result = result.split(".")[0]
                    result = int(result)

                    cctime = round(time.time()) - result
            db.commit()
            db.close()

            if cctime >= 3600:
                worktime = round(cctime / 3600)
                danwe = '시간'
            elif cctime < 3600:
                worktime = round(cctime / 60)
                danwe = '분'

            embed = discord.Embed(title='', description=f'**{message.author.mention}** 님이 퇴근하였습니다',
                                  color=discord.Colour.red())
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            embed.set_footer(text='퇴근시간: ' + time.strftime('%m-%d %H:%M') + '\n' + '근무시간: ' + str(worktime) + str(danwe))
            await client.get_channel(int(achannel)).send(embed=embed)
            await message.channel.send(f'{message.author.mention} 퇴근완료')
        except Exception as e:
                embed = discord.Embed(title='❌  오류', description=f'오류가 발생하였습니다\n`{str(e)}`', color=0xFF0000)
                await message.channel.send(embed=embed)
 
client.run("ODE5NTAwODE3MjQ1NjY3MzI5.YEnhnA.nEvpzJKaAVONMRldYLYt48sg1ac")
