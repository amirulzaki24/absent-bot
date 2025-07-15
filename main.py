import os
import json
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

# Load .env
load_dotenv()
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

absentees = defaultdict(list)  # date -> list of {name, reason}

# Clean up potential Lark mentions like <@None>
def strip_mentions(text):
    return text.replace("<@None>", "").strip()

def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    res_content = ""
    if data.event.message.message_type == "text":
        text = json.loads(data.event.message.content).get("text", "").strip()
        today = datetime.now().strftime("%Y-%m-%d")

        if text.lower().startswith("leave:"):
            body = text[7:].strip()
            body = strip_mentions(body)

            if " - " in body:
                name, reason = body.split(" - ", 1)
                name = strip_mentions(name)
                reason = strip_mentions(reason)
                absentees[today].append({"name": name.strip(), "reason": reason.strip()})
                res_content = f"✅ Got it. You are marked absent today.\n📝 Reason: {reason.strip()}"
            else:
                res_content = "⚠️ Format error.\nUse: `absent: Your Name - Reason`"

        elif "leave list" in text.lower():
            today_list = absentees.get(today, [])
            if not today_list:
                res_content = "✅ No one has reported absent today."
            else:
                lines = ["📋 Absentees today:"]
                for i, entry in enumerate(today_list, 1):
                    name = strip_mentions(entry['name'])
                    reason = strip_mentions(entry['reason'])
                    lines.append(f"{i}. {name} – {reason}")
                res_content = "\n".join(lines)
        else:
            res_content = (
                "❓ I didn't understand. To report leave, try (no bracket):\n"
                "leave: <Your Name> - <Reason>\n"
            )

    content = json.dumps({"text": res_content})

    if data.event.message.chat_type == "p2p":
        request = CreateMessageRequest.builder()\
            .receive_id_type("chat_id")\
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(data.event.message.chat_id)
                .msg_type("text")
                .content(content)
                .build()
            ).build()
        response = client.im.v1.chat.create(request)
    else:
        request = ReplyMessageRequest.builder()\
            .message_id(data.event.message.message_id)\
            .request_body(
                ReplyMessageRequestBody.builder()
                .content(content)
                .msg_type("text")
                .build()
            ).build()
        response = client.im.v1.message.reply(request)

    if not response.success():
        raise Exception(
            f"❌ Failed to reply: {response.code} | {response.msg} | Log ID: {response.get_log_id()}"
        )

# Event and client setup
event_handler = lark.EventDispatcherHandler.builder("", "")\
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)\
    .build()

client = lark.Client.builder()\
    .app_id(APP_ID)\
    .app_secret(APP_SECRET)\
    .log_level(lark.LogLevel.DEBUG)\
    .build()

wsClient = lark.ws.Client(APP_ID, APP_SECRET, event_handler=event_handler)

def main():
    print("👀 Absence bot running (mention-safe)...")
    wsClient.start()

if __name__ == "__main__":
    main()
