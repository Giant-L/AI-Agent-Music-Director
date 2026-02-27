import streamlit as st
import os
from pathlib import Path

# 导入我们的终极大脑
from agent.core import run_agent_workflow

# ==========================================
# 1. 页面与环境配置
# ==========================================
st.set_page_config(page_title="Agent 音乐工作站", page_icon="🎵", layout="wide")

st.title("🎵 AI Agent 音乐创意工作站")
st.markdown("上传一首歌，让大模型帮你分析旋律、提取伴奏，并生成一首全新风格的 Remix！")

INPUT_DIR = Path("workspace/inputs")
INPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. 侧边栏：文件上传
# ==========================================
with st.sidebar:
    st.header("📁 上传原始音频")
    uploaded_file = st.file_uploader("支持 MP3/WAV 格式", type=["mp3", "wav"])
    
    current_file_path = None
    if uploaded_file is not None:
        file_path = INPUT_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"上传成功: {uploaded_file.name}")
        current_file_path = str(file_path.absolute())
        st.audio(current_file_path)

# ==========================================
# 3. 核心聊天与 Agent 执行区
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天输入框
if prompt := st.chat_input("例如：帮我把这首歌的伴奏提取出来，并生成一首赛博朋克风格的Remix"):
    
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 触发 Agent 大脑
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.info("🧠 Agent 正在思考并执行链式任务... (本地推理可能需要几分钟，请耐心等待)")
        
        # 🌟 核心黑魔法：上下文注入
        agent_prompt = prompt
        if current_file_path:
            agent_prompt += f"\n\n[System Context: The user has uploaded an audio file located at '{current_file_path}'. Use this exact path.]"
        
        try:
            # 运行我们写好的极其稳定的 core.py
            response_text = run_agent_workflow(agent_prompt)
            
            # 清理状态提示，显示最终结果
            status_placeholder.empty()
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            # 🌟 动态 音频控制台 (Audio Console) 🌟
            st.markdown("---")
            st.subheader("🎛️ 智能音频控制台")
            
            # 1. 动态展示所有分离出的独立音轨
            if uploaded_file:
                stem_name = Path(uploaded_file.name).stem
                sep_dir = Path(f"workspace/separated/htdemucs/{stem_name}")
                
                if sep_dir.exists():
                    st.markdown("#### 🎧 提取的独立音轨 (Stems)")
                    col1, col2 = st.columns(2)
                    
                    vocals_path = sep_dir / "vocals.wav"
                    if vocals_path.exists():
                        with col1:
                            st.info("🎤 人声 / 清唱 (Vocals)")
                            st.audio(str(vocals_path))
                            
                    other_path = sep_dir / "other.wav"
                    if other_path.exists():
                        with col2:
                            st.success("🎹 纯伴奏 (Accompaniment)")
                            st.audio(str(other_path))
                            
                    drums_path = sep_dir / "drums.wav"
                    if drums_path.exists():
                        with col1:
                            st.warning("🥁 鼓点 (Drums)")
                            st.audio(str(drums_path))
                            
                    bass_path = sep_dir / "bass.wav"
                    if bass_path.exists():
                        with col2:
                            st.error("🎸 贝斯 (Bass)")
                            st.audio(str(bass_path))
            
            # 2. 意图识别防呆设计：只有大模型明确生成了东西，才展示播放器
            if "generated_music.wav" in response_text or "generate_music" in response_text or "Remix" in response_text:
                gen_path = Path("workspace/outputs/generated_music.wav")
                if gen_path.exists():
                    st.markdown("#### 🚀 AI 全新生成的 Remix")
                    st.audio(str(gen_path))

        except Exception as e:
            status_placeholder.error(f"❌ Agent 运行崩溃: {str(e)}")