import streamlit as st
import os
import tempfile
from start import recognize_lyrics
from pykakasi import kakasi

# 翻译字典
translations = {
    "zh": {
        "title": "歌词识别工具",
        "language_select": "请选择歌曲语言：",
        "languages": ["中文", "英文", "日语", "俄语"],
        "file_upload": "文件上传",
        "select_file": "请选择一个文件",
        "file_name": "文件名:",
        "file_type": "文件类型:",
        "file_size": "文件大小:",
        "audio_player": "音频播放",
        "recognize_button": "识别歌词",
        "recognizing": "正在识别歌词，请稍候...",
        "recognition_failed": "歌词识别失败，请检查错误信息",
        "recognition_result": "识别结果",
        "romaji_conversion": "歌词罗马音对照",
        "japanese_original": "日文原文",
        "romaji": "罗马音"
    },
    "en": {
        "title": "Lyrics Recognition Tool",
        "language_select": "Please select song language:",
        "languages": ["Chinese", "English", "Japanese", "Russian"],
        "file_upload": "File Upload",
        "select_file": "Please select a file",
        "file_name": "File name:",
        "file_type": "File type:",
        "file_size": "File size:",
        "audio_player": "Audio Playback",
        "recognize_button": "Recognize Lyrics",
        "recognizing": "Recognizing lyrics, please wait...",
        "recognition_failed": "Lyrics recognition failed, please check error message",
        "recognition_result": "Recognition Result",
        "romaji_conversion": "Lyrics Romaji Comparison",
        "japanese_original": "Japanese Original",
        "romaji": "Romaji"
    },
    "ja": {
        "title": "歌詞認識ツール",
        "language_select": "曲の言語を選択してください:",
        "languages": ["中国語", "英語", "日本語", "ロシア語"],
        "file_upload": "ファイルアップロード",
        "select_file": "ファイルを選択してください",
        "file_name": "ファイル名:",
        "file_type": "ファイルタイプ:",
        "file_size": "ファイルサイズ:",
        "audio_player": "オーディオ再生",
        "recognize_button": "歌詞を認識",
        "recognizing": "歌詞を認識中、お待ちください...",
        "recognition_failed": "歌詞の認識に失敗しました。エラーメッセージを確認してください",
        "recognition_result": "認識結果",
        "romaji_conversion": "歌詞ローマ字対照",
        "japanese_original": "日本語原文",
        "romaji": "ローマ字"
    }
}

# 页面语言选择
page_language = st.sidebar.selectbox(
    "Select Page Language / 选择页面语言 / ページ言語を選択",
    ("中文", "English", "日本語"),
    index=0
)

# 根据选择的语言设置翻译
if page_language == "中文":
    lang_key = "zh"
elif page_language == "English":
    lang_key = "en"
else:  # 日本語
    lang_key = "ja"

t = translations[lang_key]

# 显示标题
st.title(t["title"])

# 歌曲语言选择
song_language = st.selectbox(
    t["language_select"],
    t["languages"]
)

# 语言代码映射
language_code_map = {
    "中文": "zh",
    "English": "en",
    "Japanese": "ja",
    "俄语": "ru",
    "Russian": "ru",
    "日语": "ja",
    "中国語": "zh",
    "英語": "en",
    "日本語": "ja",
    "ロシア語": "ru"
}

st.subheader(t["file_upload"])
uploaded_file = st.file_uploader(t["select_file"], type=None)

if uploaded_file is not None:
    st.write(t["file_name"], uploaded_file.name)
    st.write(t["file_type"], uploaded_file.type)
    st.write(t["file_size"], round(uploaded_file.size / 1024 / 1024, 2), "MB")
    # 保存上传的文件到临时目录
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_file_path = tmp_file.name
    
    # 音频播放控件
    st.subheader(t["audio_player"])
    st.audio(uploaded_file, format=uploaded_file.type)
    
    # 识别歌词按钮
    if st.button(t["recognize_button"], type="secondary"):
        with st.spinner(t["recognizing"]):
            # 获取语言代码
            lang_code = language_code_map.get(song_language, "ja")
            
            # 调用识别函数
            lyrics = recognize_lyrics(temp_file_path, language=lang_code)
            
            if lyrics:
                # 保存歌词到session_state
                st.session_state.lyrics = lyrics
                st.session_state.lang_code = lang_code
                st.session_state.show_romaji = False
            else:
                st.error(t["recognition_failed"])
    
    # 显示识别结果
    if 'lyrics' in st.session_state:
        st.subheader(t["recognition_result"])
        
        # 检查是否是日语，若是则自动转换为罗马音
        if st.session_state.get('lang_code') == "ja":
            st.session_state.show_romaji = True
        else:
            st.session_state.show_romaji = False
        
        if st.session_state.get('show_romaji', False) and st.session_state.get('lang_code') == "ja":
            # 初始化kakasi
            kks = kakasi()
            kks.setMode("J", "a")  # 日语转罗马音
            kks.setMode("H", "a")  # 平假名转罗马音
            kks.setMode("K", "a")  # 片假名转罗马音
            conv = kks.getConverter()
            
            # 逐行转换歌词
            lyrics_lines = st.session_state.lyrics.split("\n")
            
            # 创建对照表格数据
            table_data = []
            for line in lyrics_lines:
                if line.strip():  # 跳过空行
                    romaji = conv.do(line)
                    table_data.append({t["japanese_original"]: line, t["romaji"]: romaji})
            
            # 显示表格
            st.subheader(t["romaji_conversion"])
            st.table(table_data)
        else:
            st.text(st.session_state.lyrics)
    
    # 清理临时文件
    if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
        os.unlink(temp_file_path)