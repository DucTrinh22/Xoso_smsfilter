import streamlit as st
import re
from config.constants import DAI_XO_SO, LOAI_CUOC

def highlight_syntax(text):
    """
    Hàm phân tích nhanh để tô màu HTML hiển thị cho người dùng kiểm tra
    """
    if not text: return ""
    
    # Normalize sơ bộ để tách từ
    text = text.lower()
    text = re.sub(r'[,:;]', ' ', text)
    text = re.sub(r'([a-z]+)(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-z]+)', r'\1 \2', text)
    
    tokens = text.split()
    html_out = []
    
    # Danh sách check nhanh
    all_dai = set()
    for shorts in DAI_XO_SO.values():
        for s in shorts: all_dai.add(s.lower())
        
    all_bet = set(LOAI_CUOC.keys())
    all_bet.update(['blo', 'b', 'x', 'da', 'dá'])
    
    prev_is_num = False # Để check context BD
    
    for token in tokens:
        color = "black"
        style = ""
        is_num = False
        
        # 1. Check Tiền (có đuôi n, k, tr, d)
        if re.match(r'^\d+(\.\d+)?[nkdđ(tr)]+$', token):
            color = "#d63031" # Red
            token_display = f"{token}"
            
        # 2. Check Số (thuần số)
        elif re.match(r'^\d+$', token):
            color = "#00b894" # Green
            is_num = True
            token_display = token
            
        # 3. Check Đài vs Loại cược (Xử lý BD)
        elif token in all_dai or token in all_bet:
            is_dai = False
            is_bet = False
            
            if token in all_bet:
                is_bet = True
            
            # Logic check BD
            if token == 'bd':
                if prev_is_num: is_dai = False; is_bet = True
                else: is_dai = True; is_bet = False
            elif token in all_dai:
                is_dai = True
            
            if is_dai:
                color = "#0984e3" # Blue
                style = "font-weight:bold;"
                token_display = f"{token.upper()}"
            elif is_bet:
                color = "#e17055" # Orange
                token_display = f"{token}"
            else:
                 # Trường hợp hiếm
                 token_display = token
        
        # 4. Lỗi / Không xác định
        else:
             color = "white"
             style = "background-color: #ff7675; padding: 0 4px; border-radius: 4px;"
             token_display = token

        html_out.append(f'<span style="color:{color}; {style} margin-right:4px;">{token_display}</span>')
        prev_is_num = is_num

    return " ".join(html_out)

def render_input_form():
    """
    Hiển thị vùng nhập liệu và trả về danh sách các dòng tin nhắn
    """
    st.subheader("📩 Nhập tin nhắn SMS cược xổ số")
    
    # 1. Text Area
    text_input = st.text_area(
        "Dán nhiều dòng tin nhắn (mỗi dòng 1 lệnh cược):",
        height=150,
        placeholder="Ví dụ: BD 98-97-99dau30n...",
        key="input_sms_area"
    )
    
    # 2. Live Preview Highlight
    if text_input:
        st.caption("🔍 **Kiểm tra cú pháp nhanh:** (Đài: Xanh | Số: Lục | Cược: Cam | Tiền: Đỏ)")
        preview_container = st.container()
        with preview_container:
            lines = [line.strip() for line in text_input.splitlines() if line.strip()]
            for line in lines:
                highlighted_html = highlight_syntax(line)
                st.markdown(f"<div style='background-color:#f0f2f6; padding:8px; border-radius:5px; margin-bottom:5px; font-family:monospace;'>{highlighted_html}</div>", unsafe_allow_html=True)

    return [line.strip() for line in text_input.splitlines() if line.strip()]