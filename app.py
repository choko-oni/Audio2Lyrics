import streamlit as st
import os
import tempfile
from start import recognize_japanese_lyrics
from pykakasi import kakasi

st.title("歌词识别工具")

language = st.selectbox(
    "请选择歌曲语言：",
    ("中文", "英文", "日语")
)

st.write(f"您选择的语言是: {language}")

st.subheader("文件上传")
uploaded_file = st.file_uploader("请选择一个文件", type=None)

if uploaded_file is not None:
    st.write("文件名:", uploaded_file.name)
    st.write("文件类型:", uploaded_file.type)
    st.write("文件大小:", uploaded_file.size, "字节")
    
    # 保存上传的文件到临时目录
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_file_path = tmp_file.name
    
    # 音频播放控件
    st.subheader("音频播放")
    st.audio(uploaded_file, format=uploaded_file.type)
    
    # 识别歌词按钮
    if st.button("识别歌词", type="secondary"):
        with st.spinner("正在识别歌词，请稍候..."):
            # 调用识别函数
            lyrics = recognize_japanese_lyrics(temp_file_path)
            
            if lyrics:
                # 保存歌词到session_state
                st.session_state.lyrics = lyrics
                st.session_state.show_romaji = False
            else:
                st.error("歌词识别失败，请检查错误信息")
    
    # 显示识别结果
    if 'lyrics' in st.session_state:
        st.subheader("识别结果")
        
        # 添加罗马音转换按钮
        if st.button("转换为罗马音"):
            st.session_state.show_romaji = True
        
        if st.session_state.get('show_romaji', False):
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
                    table_data.append({"日文原文": line, "罗马音": romaji})
            
            # 显示表格
            st.subheader("歌词罗马音对照")
            st.table(table_data)
        else:
            st.text(st.session_state.lyrics)
    
    # 清理临时文件
    if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
        os.unlink(temp_file_path)