from wxauto import *  # 导入微信自动化操作库,方便控制微信客户端
import os             # 导入操作系统模块,用于环境变量设置
import tiktoken       # 导入OpenAI的Token计数库,用于估算消息token数
from openai import OpenAI  # 导入新版OpenAI SDK客户端

# 设置HTTP和HTTPS代理,确保程序通过本地代理服务器访问网络(常用于翻墙)
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

# 初始化OpenAI客户端,api_key替换为你自己的秘钥
client = OpenAI(
    api_key=""
)

# 定义使用的模型名称,gpt-4o为示例,具体请根据账号权限选择
MODEL_NAME = "gpt-4o"

# 最大token限制,这里设为128000,实际调用中会限制max_tokens不超过4096
MAX_TOTAL_TOKENS = 128000


# 读取文本文件内容,返回字符串,encoding指定为utf-8保证中文正常读取
def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# 计算字符串所占用的token数量,便于控制请求长度,避免超过模型限制
def num_tokens_from_string(text: str, model: str = MODEL_NAME) -> int:
    encoding = tiktoken.encoding_for_model(model)  # 根据模型自动获取编码方式
    return len(encoding.encode(text))               # 编码后token列表长度即为token数


# 调用OpenAI接口进行提问并获得回答
# 参数:text_context - 角色扮演文本内容;user_question - 用户聊天内容
def ask_question(text_context, user_question):
    # 构造完整prompt,包含角色扮演说明及用户问题,保证AI扮演设定角色
    full_prompt = f"请以扮演文档中的角色:\n{text_context}\n\n并和群友聊天,所有话题进你所能的聊天,请完全代入角色而不是提及自己存在于某个作品中:\n{user_question}\n"

    # 系统角色设定,告诉模型你是"猫猫"
    system_prompt = "你是猫猫."

    # 统计系统消息和用户消息占用的token数量
    tokens_used = (
        num_tokens_from_string(system_prompt) +
        num_tokens_from_string(full_prompt)
    )

    # 计算给模型回复分配的最大token数,保证总token数不超限制
    max_tokens_reply = MAX_TOTAL_TOKENS - tokens_used

    # 限制max_tokens_reply在1到4096之间,防止请求参数非法
    max_tokens_reply = max(1, min(max_tokens_reply, 4096))

    # 调用OpenAI接口生成聊天回复
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},  # 系统提示,设置身份
            {"role": "user", "content": full_prompt}       # 用户提问及上下文
        ],
        temperature=0.3,      # 生成文本的随机程度,数值越低越确定
        max_tokens=max_tokens_reply  # 回复最大长度限制
    )
    # 返回模型回复内容,去除前后空白
    return response.choices[0].message.content.strip()


# 程序主入口
if __name__ == "__main__":
    # 读取角色扮演文档内容
    document_path = "document.txt"
    document_content = load_text(document_path)

    # 初始化微信客户端控制对象
    wx = WeChat()

    # 获取当前微信会话列表(用于后续消息获取)
    wx.GetSessionList()

    # 需要发送消息的微信群名称(请替换成实际群名)
    group = ''

    print("OpenAI加载成功\n")

    # 保存上一次处理的问题,防止重复响应
    question = "123"

    # 设定AI识别的名字关键词,用于过滤是否回复
    ai_name = "猫猫"

    # 主循环,不断检测微信消息
    while True:
        # 获取微信所有新消息,参数savepic=True表示保存图片消息
        msgs = wx.GetAllMessage(savepic=True)

        # 遍历所有消息
        for msg in msgs:
            if msg.type == 'friend':  # 判断消息是否为好友消息
                sender = msg.sender_remark  # 获取发送者备注名
                message = msg.content      # 获取消息文本内容
                # 格式化消息,备注名右对齐20位,方便输出对齐查看
                question1 = f'{sender.rjust(20)}:{message}'

        # 如果当前消息和上次相同,则跳过,避免重复处理
        if question == question1:
            continue
        else:
            question = question1  # 更新最新消息内容
            print("收到问题:", question, "\n")

            # 判断消息中是否包含AI名字关键词,只有包含时才调用接口回复
            if ai_name in question:
                content = ask_question(document_content, question)  # 调用AI接口获取回复
                wx.SendMsg(msg=content, who=group)                  # 发送回复到指定微信群
                print("回答:", content, "\n")                       # 控制台打印回复内容
