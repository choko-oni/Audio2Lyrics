import whisper
import os
import re
import tempfile

def clean_and_format_lyrics(text, language):
    """
    清理歌词：根据语言进行不同的清理和格式化
    """
    # 1. 清理特定语言的关键词
    if language == "ja":
        # 去掉"歌詞"二字
        cleaned = re.sub(r'歌詞・|歌詞、|歌詞|かし', '', text)
        # 按日语标点（顿号、逗号、句号）拆分句子并换行
        sentences = re.split(r'[，、。]', cleaned)
    elif language == "zh":
        # 去掉"歌词"二字
        cleaned = re.sub(r'歌词', '', text)
        # 按中文标点（逗号、句号）拆分句子并换行
        sentences = re.split(r'[，。]', cleaned)
    elif language == "en":
        # 按英文标点（句号、问号、感叹号）拆分句子并换行
        sentences = re.split(r'[.!?]', text)
    elif language == "ru":
        # 按俄语标点（句号、问号、感叹号）拆分句子并换行
        sentences = re.split(r'[.!?]', text)
    else:
        # 默认按通用标点拆分
        sentences = re.split(r'[，。.!?]', text)
    
    # 2. 过滤空行、纯标点行、多余空格
    formatted = []
    for sent in sentences:
        sent = sent.strip()
        if sent and not re.match(r'^[・、，。.!?\s]+$', sent):
            formatted.append(sent)
    
    # 3. 逐句换行输出
    return "\n".join(formatted)

def recognize_lyrics(audio_path, language="ja"):
    """
    识别歌词的通用函数
    :param audio_path: 音频文件路径
    :param language: 语言代码，支持 "zh"（中文）、"en"（英文）、"ja"（日语）
    :return: 格式化后的歌词文本
    """
    # ========== 1. 配置参数 ==========
    output_file = f"最终歌词_{language}_换行版.txt"

    # ========== 2. 环境/文件检查 ==========
    # 检查FFmpeg
    ffmpeg_check = os.system("ffmpeg -version > nul 2>&1" if os.name == "nt" else "ffmpeg -version > /dev/null 2>&1")
    if ffmpeg_check != 0:
        print("❌ 错误：未检测到FFmpeg，请先安装并配置到环境变量！")
        return None
    # 检查音频文件
    if not os.path.exists(audio_path):
        print(f"❌ 错误：未找到音频文件 {audio_path}")
        return None

    # ========== 3. 加载模型（避免重复生成） ==========
    print("🔍 加载Whisper多语言模型...")
    model = whisper.load_model("small", device="cpu")  # CPU用small，GPU用medium

    # ========== 4. 转录（避免提示词干扰） ==========
    print(f"🎙️ 正在识别音频：{audio_path}")
    result = model.transcribe(
        audio_path,
        language=language,
        verbose=False,
        fp16=False,
        # 核心参数：避免重复+精准识别
        temperature=0.7,
        beam_size=3,
        best_of=3,
        initial_prompt="",  # 清空提示词，避免干扰
        condition_on_previous_text=False,
        no_speech_threshold=0.6,
        logprob_threshold=-1.0,
        carry_initial_prompt=False,
    )

    # ========== 5. 清理+格式化歌词 ==========
    raw_lyrics = result["text"].strip()
    formatted_lyrics = clean_and_format_lyrics(raw_lyrics, language)

    # ========== 6. 输出+保存 ==========
    print(f"\n✅ 最终识别结果（{language}）：")
    print("-" * 50)
    print(formatted_lyrics)
    print("-" * 50)

    # 保存到文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(formatted_lyrics)
    print(f"\n📄 结果已保存到：{output_file}")

    return formatted_lyrics

# 保持向后兼容
def recognize_japanese_lyrics(audio_path):
    return recognize_lyrics(audio_path, language="ja")

# ========== 执行识别 ==========
if __name__ == "__main__":
    # 默认路径，仅在直接运行时使用
    default_path = os.path.abspath("./audio_dir/test.mp3")
    recognize_lyrics(default_path, language="ja")