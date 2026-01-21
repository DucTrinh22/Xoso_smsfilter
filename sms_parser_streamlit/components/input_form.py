# File: components/input_form.py
import streamlit as st
import re
from config.constants import DAI_XO_SO, LOAI_CUOC

def highlight_syntax(text):
    """
    Hàm phân tích nhanh để tô màu HTML (Giữ nguyên logic cũ)
    """
    if not text: return ""
    
    text = text.lower()
    text = re.sub(r'[,:;]', ' ', text)
    text = re.sub(r'([a-z]+)(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-z]+)', r'\1 \2', text)
    
    tokens = text.split()
    html_out = []
    
    all_dai = set()
    for shorts in DAI_XO_SO.values():
        for s in shorts: all_dai.add(s.lower())
        
    all_bet = set(LOAI_CUOC.keys())
    all_bet.update(['blo', 'b', 'x', 'da', 'dá'])
    
    prev_is_num = False 
    
    for token in tokens:
        color = "black"
        style = ""
        is_num = False
        
        if re.match(r'^\d+(\.\d+)?[nkdđ(tr)]+$', token):
            color = "#d63031" # Red
            token_display = f"{token}"
        elif re.match(r'^\d+$', token):
            color = "#10d8b0" # Green
            is_num = True
            token_display = token
        elif token in all_dai or token in all_bet:
            is_dai = False
            is_bet = False
            if token in all_bet: is_bet = True
            
            if token == 'bd':
                if prev_is_num: is_dai = False; is_bet = True
                else: is_dai = True; is_bet = False
            elif token in all_dai:
                is_dai = True
            
            if is_dai:
                color = "#0931e3"; style = "font-weight:bold;"; token_display = f"{token.upper()}"
            elif is_bet:
                color = "#d83911"; token_display = f"{token}"
            else: token_display = token
        else:
             color = "white"; style = "background-color: #ff7675; padding: 0 4px; border-radius: 4px;"; token_display = token

        html_out.append(f'<span style="color:{color}; {style} margin-right:4px;">{token_display}</span>')
        prev_is_num = is_num

    return " ".join(html_out)

def render_input_form():
    """
    Hiển thị vùng nhập liệu và style viền (stroke)
    """
    st.subheader("📩 Nhập tin nhắn SMS cược xổ số")
    
    # CSS tạo viền và chỉnh font
    st.markdown("""
        <style>
        .stTextArea textarea {
            font-size: 25px !important; 
            font-family: 'Courier New', monospace;
            line-height: 1.5 !important;
            border: 2px solid #4b7bec !important; 
            border-radius: 8px !important;
            padding: 10px !important;
        }
        .stTextArea textarea:focus {
            border-color: #eb3b5a !important;
            box-shadow: 0 0 5px rgba(235, 59, 90, 0.5);
        }
        </style>
    """, unsafe_allow_html=True)
    
    text_input = st.text_area(
        "Label ẩn",
        height=150,
        placeholder="Ví dụ: BD 98-97-99dau30n...",
        label_visibility="collapsed",
        key="input_sms_area"
    )
    
    return [line.strip() for line in text_input.splitlines() if line.strip()]

def render_syntax_check(lines):
    """
    Hàm hiển thị phần kiểm tra cú pháp (Riêng biệt)
    """
    if lines:
        with st.expander("🔍 Xem kiểm tra cú pháp nhanh (Bấm để mở)", expanded=False):
            st.caption("Quy ước: (Đài: Xanh | Số: Lục | Cược: Cam | Tiền: Đỏ)")
            preview_container = st.container()
            with preview_container:
                for line in lines:
                    highlighted_html = highlight_syntax(line)
                    st.markdown(f"<div style='background-color:#f0f2f6; padding:8px; border-radius:5px; margin-bottom:5px; font-family:monospace;'>{highlighted_html}</div>", unsafe_allow_html=True)
