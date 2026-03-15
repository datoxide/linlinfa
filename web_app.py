"""
法律智能助手 Web 应用
基于 Streamlit 的法律问答、内容生成和文档分析平台
"""
import streamlit as st
import tempfile
import os
from typing import Optional

# 导入 agent 模块
from agent.chat import LegalChatAgent
from agent.generator import LegalContentGenerator, ContentType
from agent.analyzer import LegalDocumentAnalyzer


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="邻临法",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== API Key 检查 ====================
from config import Config

def check_api_key():
    """检查 API Key 是否已配置"""
    api_key = Config.OPENROUTER_API_KEY
    if not api_key:
        st.error("⚠️ 请配置 OPENROUTER_API_KEY")
        st.markdown("""
        **配置方法 (二选一)：**

        1. **Streamlit Cloud**: 在 Streamlit 应用的 Settings → Secrets 中添加：
           ```toml
           OPENROUTER_API_KEY = "your-api-key-here"
           ```

        2. **本地运行**: 创建 `.env` 文件：
           ```bash
           OPENROUTER_API_KEY=your-api-key-here
           ```
        """)
        st.stop()

# 在页面加载时检查 API Key
check_api_key()


# ==================== 自定义样式 ====================
def apply_custom_styles():
    """应用自定义样式"""
    st.markdown("""
    <style>
    /* 主色调 - 专业蓝色 */
    :root {
        --primary-color: #1e3a5f;
        --secondary-color: #2c5282;
        --accent-color: #3182ce;
        --background-color: #f7fafc;
        --text-color: #2d3748;
    }

    /* 侧边栏样式 - 固定底部布局 */
    [data-testid="stSidebar"] {
        background-color: #1e3a5f !important;
        display: flex;
        flex-direction: column;
        height: 100vh !important;
        position: relative !important;
    }

    /* 侧边栏内部内容区域 */
    [data-testid="stSidebar"] > div:first-child {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
    }

    /* 底部版权区域固定 */
    .sidebar-footer {
        margin-top: auto;
        flex-shrink: 0;
        background-color: #1e3a5f;
    }

    /* 确保 radio 按钮区域有正确的背景 */
    [data-testid="stSidebar"] .stRadio {
        background-color: transparent;
    }

    [data-testid="stSidebar"] .stRadio > div {
        background-color: transparent;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        margin: 6px 0 !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* 选中项高亮 */
    [data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%) !important;
        box-shadow: 0 2px 8px rgba(49, 130, 206, 0.4);
    }

    /* radio 按钮本身隐藏，用样式替代 */
    [data-testid="stSidebar"] .stRadio input[type="radio"] {
        display: none;
    }

    /* Logo 区域样式 */
    .logo-container {
        text-align: center;
        padding: 24px 0 16px 0;
    }

    .logo-text {
        font-size: 48px;
        font-weight: 700;
        color: white;
        letter-spacing: 8px;
        margin: 0;
    }

    /* 蓝色渐变分割线 */
    .gradient-divider {
        height: 3px;
        background: linear-gradient(90deg, transparent, #3182ce, #63b3ed, #3182ce, transparent);
        margin: 12px 20px 0 20px;
        border-radius: 2px;
    }

    /* 导航按钮区域 */
    .nav-container {
        padding: 16px 12px;
    }

    /* 自定义 radio 按钮高亮样式 */
    .nav-radio label {
        background-color: transparent !important;
    }

    /* 选中项高亮背景 */
    div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%) !important;
        border-radius: 8px !important;
    }

    /* 使用说明区域 */
    .instruction-container {
        padding: 12px;
    }

    /* 免责声明卡片样式 */
    .disclaimer-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 12px 14px;
        margin: 0 12px 12px 12px;
        border-left: 3px solid #ed8936;
    }

    .disclaimer-title {
        color: #ed8936;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .disclaimer-text {
        color: #a0aec0;
        font-size: 11px;
        line-height: 1.5;
        margin: 0;
    }

    /* 版权区域样式 */
    .copyright-container {
        text-align: center;
        padding: 16px 0;
    }

    .copyright-line1 {
        color: white;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 4px;
    }

    .copyright-line2, .copyright-line3 {
        color: #718096;
        font-size: 12px;
        line-height: 1.4;
    }

    /* 分割线样式 */
    .custom-divider {
        border: none;
        border-top: 1px solid #4a5568;
        margin: 0 12px;
    }

    /* 聊天气泡样式 - 用户 */
    .chat-user {
        background: linear-gradient(135deg, #2c5282 0%, #3182ce 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* 聊天气泡样式 - 助手 */
    .chat-assistant {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%);
        color: #2d3748;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 80%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* 标题样式 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        text-align: center;
        padding: 20px 0;
        border-bottom: 3px solid #3182ce;
        margin-bottom: 30px;
    }

    /* 功能卡片样式 */
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #3182ce;
        margin: 10px 0;
    }

    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(135deg, #2c5282 0%, #3182ce 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
    }

    /* 输入框样式 */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #cbd5e0;
    }

    .stTextInput>div>div>input:focus {
        border-color: #3182ce;
    }

    /* 选择框样式 */
    .stSelectbox>div>div>div {
        border-radius: 8px;
    }

    /* 文件上传样式 */
    .stFileUploader>div>div>div {
        border-radius: 12px;
        border: 2px dashed #cbd5e0;
    }

    /* 响应式调整 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
        .chat-user, .chat-assistant {
            max-width: 95%;
        }
    }

    /* 加载动画 */
    .loading-spinner {
        text-align: center;
        padding: 20px;
        color: #718096;
    }

    /* 提示信息样式 */
    .info-box {
        background: #ebf8ff;
        border-left: 4px solid #3182ce;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 10px 0;
    }

    .warning-box {
        background: #fffaf0;
        border-left: 4px solid #ed8936;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== 侧边栏 ====================
def render_sidebar():
    """渲染侧边栏导航"""
    with st.sidebar:
        # Logo 区域
        st.markdown("""
        <div class="logo-container">
            <h1 class="logo-text">邻临法</h1>
        </div>
        <div class="gradient-divider"></div>
        """, unsafe_allow_html=True)

        # 导航功能按钮
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        page = st.radio(
            "功能导航",
            ["💬 法律问答", "📝 内容生成", "📄 文档分析"],
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 使用说明
        with st.expander("📖 使用说明", expanded=False):
            st.markdown("""
            **法律问答**
            - 支持多轮对话
            - 可选择法律领域
            - 获得专业法律解答

            **内容生成**
            - 多种文章类型
            - 可自定义主题和长度
            - 生成专业法律内容

            **文档分析**
            - 支持 PDF/DOCX/TXT
            - 多种分析模式
            - 快速提取关键信息
            """)

        # 免责声明 - 优化后的卡片样式
        st.markdown("""
        <div class="disclaimer-card">
            <div class="disclaimer-title">⚠️ 免责声明</div>
            <p class="disclaimer-text">
                本应用提供的内容仅供参考，不构成法律意见。具体法律问题请咨询专业律师。
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 底部版权区域 - 固定在底部
        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
        st.markdown("""
        <div class="sidebar-footer">
            <div class="copyright-container">
                <div class="copyright-line1">@Gengxis Lab</div>
                <div class="copyright-line2">华东政法大学韬奋新闻传播学院</div>
                <div class="copyright-line3">金庚星研究组</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return page


# ==================== 页面1: 法律问答 ====================
def render_chat_page():
    """渲染法律问答页面"""

    # 页面标题
    st.markdown('<h1 class="main-title">💬 法律问答对话</h1>', unsafe_allow_html=True)

    # 初始化会话状态
    if "chat_agent" not in st.session_state:
        st.session_state.chat_agent = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "prompt_type" not in st.session_state:
        st.session_state.prompt_type = "default"

    # 侧边栏配置
    with st.expander("⚙️ 对话设置", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            prompt_type = st.selectbox(
                "法律领域",
                ["default", "criminal", "civil", "labor"],
                format_func=lambda x: {
                    "default": "通用法律",
                    "criminal": "刑事法律",
                    "civil": "民事法律",
                    "labor": "劳动法律"
                }.get(x, x),
                index=0
            )
        with col2:
            if st.button("🔄 新建对话", use_container_width=True):
                st.session_state.chat_agent = LegalChatAgent(prompt_type=prompt_type)
                st.session_state.chat_history = []
                st.session_state.prompt_type = prompt_type
                st.rerun()

    # 初始化聊天代理
    if st.session_state.chat_agent is None:
        st.session_state.chat_agent = LegalChatAgent(prompt_type=prompt_type)
        st.session_state.prompt_type = prompt_type

    # 显示聊天历史
    st.markdown("### 对话历史")
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <strong>您：</strong>{msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-assistant">
                    <strong>⚖️ 法律助手：</strong><br><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)

    # 提示框
    if not st.session_state.chat_history:
        st.info("👋 您好！我是法律智能助手，您可以向我咨询任何法律问题。")

    st.markdown("---")

    # 输入区域
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "请输入您的问题：",
                placeholder="例如：签订劳动合同时需要注意什么？",
                label_visibility="collapsed",
                key="chat_input"
            )
        with col2:
            submit_button = st.form_submit_button("发送", use_container_width=True)

    if submit_button and user_input.strip():
        # 添加用户消息
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        # 获取助手回复
        with st.spinner("🤔 思考中，请稍候..."):
            try:
                response = st.session_state.chat_agent.chat(user_input)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"抱歉，发生了一些问题: {str(e)}"
                })

        st.rerun()

    # 清空对话按钮
    if st.session_state.chat_history:
        if st.button("🗑️ 清空对话记录"):
            st.session_state.chat_agent.reset_conversation()
            st.session_state.chat_history = []
            st.rerun()


# ==================== 页面2: 内容生成 ====================
def render_generator_page():
    """渲染法律内容生成页面"""

    # 页面标题
    st.markdown('<h1 class="main-title">📝 法律内容生成</h1>', unsafe_allow_html=True)

    # 初始化会话状态
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = None

    # 参数配置
    with st.expander("⚙️ 生成设置", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            content_type = st.selectbox(
                "文章类型",
                [ct.value for ct in ContentType],
                format_func=lambda x: {
                    "article": "法律文章",
                    "case": "案例分析",
                    "popular": "科普文章",
                    "faq": "问答解析",
                    "summary": "法规摘要"
                }.get(x, x),
                index=0
            )

        with col2:
            length = st.selectbox(
                "文章长度",
                ["short", "medium", "long"],
                format_func=lambda x: {
                    "short": "短篇 (500-800字)",
                    "medium": "中篇 (1000-1500字)",
                    "long": "长篇 (2000-3000字)"
                }.get(x, x),
                index=1
            )

        with col3:
            style = st.selectbox(
                "文章风格",
                ["formal", "casual", "academic"],
                format_func=lambda x: {
                    "formal": "正式专业",
                    "casual": "轻松易读",
                    "academic": "学术严谨"
                }.get(x, x),
                index=0
            )

    # 主题输入
    st.markdown("### 📋 生成内容")
    topic = st.text_area(
        "请输入主题或内容要点：",
        placeholder="例如：劳动合同法中关于试用期的规定",
        height=100,
        key="topic_input"
    )

    # 生成按钮
    col1, col2 = st.columns([1, 4])
    with col1:
        generate_btn = st.button("🚀 生成内容", use_container_width=True)
    with col2:
        if st.button("🔄 重新生成"):
            st.session_state.generated_content = None
            st.rerun()

    # 执行生成
    if generate_btn and topic.strip():
        with st.spinner("✍️ 正在生成内容，请稍候..."):
            try:
                generator = LegalContentGenerator()
                result = generator.generate(
                    topic=topic,
                    content_type=ContentType(content_type),
                    length=length,
                    style=style
                )
                st.session_state.generated_content = result
            except Exception as e:
                st.error(f"生成失败: {str(e)}")

    # 显示生成结果
    if st.session_state.generated_content:
        st.markdown("---")
        st.markdown("### 📄 生成结果")

        # 复制按钮
        col1, col2 = st.columns([6, 1])
        with col1:
            st.info("📌 生成的内容仅供参考")
        with col2:
            st.code(st.session_state.generated_content, language=None)

        st.markdown(st.session_state.generated_content)

    # 示例提示
    if not st.session_state.generated_content:
        st.markdown("""
        <div class="info-box">
            <strong>💡 生成示例：</strong>
            <ul style="margin-top: 8px;">
                <li>法律文章：解读《民法典》合同编亮点</li>
                <li>案例分析：某商品房买卖合同纠纷案例</li>
                <li>科普文章：什么是知识产权保护？</li>
                <li>问答解析：工伤认定标准是什么？</li>
                <li>法规摘要：《劳动合同法》核心条款</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ==================== 页面3: 文档分析 ====================
def render_analyzer_page():
    """渲染法律文档分析页面"""

    # 页面标题
    st.markdown('<h1 class="main-title">📄 法律文档分析</h1>', unsafe_allow_html=True)

    # 初始化会话状态
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None

    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None

    # 参数配置
    with st.expander("⚙️ 分析设置", expanded=True):
        analysis_type = st.selectbox(
            "分析类型",
            ["summary", "risk", "compliance", "full"],
            format_func=lambda x: {
                "summary": "文档摘要",
                "risk": "风险分析",
                "compliance": "合规审查",
                "full": "全面分析"
            }.get(x, x),
            index=0
        )

    # 文件上传
    st.markdown("### 📤 上传文档")
    uploaded_file = st.file_uploader(
        "支持 PDF、Word (.docx)、文本 (.txt) 文件",
        type=["pdf", "docx", "txt"],
        help="上传需要分析的法律文档"
    )

    # 处理文件上传
    if uploaded_file is not None:
        # 检查文件是否变化
        if st.session_state.uploaded_file != uploaded_file.name:
            st.session_state.uploaded_file = uploaded_file.name
            st.session_state.analysis_result = None

        st.success(f"✅ 已上传: {uploaded_file.name}")

        # 保存上传的文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # 分析按钮
        col1, col2 = st.columns([1, 4])
        with col1:
            analyze_btn = st.button("🔍 开始分析", use_container_width=True)

        with col2:
            if st.button("🗑️ 清除结果"):
                st.session_state.analysis_result = None
                st.session_state.uploaded_file = None
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                st.rerun()

        # 执行分析
        if analyze_btn:
            with st.spinner("📊 正在分析文档，请稍候..."):
                try:
                    analyzer = LegalDocumentAnalyzer()
                    result = analyzer.analyze(tmp_path, analysis_type=analysis_type)
                    st.session_state.analysis_result = result
                except Exception as e:
                    st.error(f"分析失败: {str(e)}")
                finally:
                    # 清理临时文件
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

    # 显示分析结果
    if st.session_state.analysis_result:
        st.markdown("---")
        st.markdown("### 📋 分析结果")

        col1, col2 = st.columns([6, 1])
        with col1:
            st.info("📌 分析结果仅供参考，具体法律意见请咨询专业律师")
        with col2:
            st.code(st.session_state.analysis_result, language=None)

        st.markdown(st.session_state.analysis_result)

    # 使用提示
    if not uploaded_file:
        st.markdown("""
        <div class="info-box">
            <strong>💡 使用说明：</strong>
            <ul style="margin-top: 8px;">
                <li>上传法律文档（合同、协议、起诉书等）</li>
                <li>选择分析类型：摘要、风险、合规或全面分析</li>
                <li>点击"开始分析"获取分析结果</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ==================== 主函数 ====================
def main():
    """主函数"""
    # 应用自定义样式
    apply_custom_styles()

    # 渲染侧边栏并获取当前页面
    page = render_sidebar()

    # 根据页面选择渲染对应内容
    if page == "💬 法律问答":
        render_chat_page()
    elif page == "📝 内容生成":
        render_generator_page()
    elif page == "📄 文档分析":
        render_analyzer_page()


if __name__ == "__main__":
    main()
