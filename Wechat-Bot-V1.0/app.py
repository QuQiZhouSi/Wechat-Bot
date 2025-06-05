from wxauto import *
import os
import openai
from openai import OpenAI


# 设置本地代理
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

# 初始化 OpenAI 客户端(新版 SDK)
client = OpenAI(
    api_key=""  # 替换为你的 API Key
)

# 从文本文件中读取内容
def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# 获取当前微信客户端
wx = WeChat()


# 获取会话列表
wx.GetSessionList()

# 使用 OpenAI 接口提问
def ask_question(text_context, user_question):
    full_prompt = f"请以扮演文档中的角色\n{text_context}\n\n并和群友聊天,所有话题进你所能的聊天,请完全代入角色而不是提及自己存在于某个作品中\n{user_question}\n"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # 可替换模型
        messages=[
            {"role": "system", "content": "你是猫猫."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.3, # 设置生成回答的随机性,越低越稳定
        max_tokens=512 # 最大tokens数
    )

    return response.choices[0].message.content.strip()

# 主程序入口
if __name__ == "__main__":
    document_path = "document.txt"
    document_content = load_text(document_path)
    group = '' # 群名或者好友名
    print("OpenAI加载成功\n")
    question = "123"
    while True:
        while True:
            msgs = wx.GetAllMessage(savepic=True)
            for msg in msgs:
                if msg.type == 'friend':
                    sender = msg.sender_remark
                    question1 = f'{sender.rjust(20)}:{msg.content}'
                    print(question,"!11")
            if question == question1:
                continue
            else:
                question = question1
                ai_name = "猫猫" # 当群友或好友在刚刚指定的聊天中提到这个就会触发回复
                if ai_name in question:
                    content = ask_question(document_content, question)
                    break
        wx.SendMsg(msg = content, who = group) 
        print("回答:", content, "\n")
