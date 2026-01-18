# App.py
from datetime import datetime
import requests
import streamlit as st
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

# Import core modules
from core.bet_checker import BetChecker
from core.comparator import SMSComparator
from core.lottery_fetcher import MinhNgocFetcher
from core.parser import SMSParser
from components.input_form import render_input_form
from components.result_display import render_results

# Config trang
st.set_page_config(page_title="SMS Cược XS", layout="wide")
st.title("📟 Hệ thống Phân Tích & Dò Số")

@st.cache_data(ttl=3600, show_spinner=False)
def get_cached_lottery_data(date_str, region_slug):
    """
    Hàm này giúp Streamlit ghi nhớ kết quả.
    Nếu ngày này đã tải rồi -> Trả về ngay lập tức.
    Nếu chưa -> Gọi Fetcher đi tải -> Lưu vào RAM -> Trả về.
    """
    fetcher_instance = MinhNgocFetcher()
    return fetcher_instance.fetch_data(date_str, region_slug)

# --- 1. CẤU HÌNH (SIDEBAR HOẶC TOP) ---
with st.expander("📆 Lịch Xổ Số", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        selected_date = st.date_input("Chọn ngày:", datetime.now())
        date_str_api = selected_date.strftime("%d-%m-%Y")
    
    with c2:
        khu_vuc = st.selectbox(
            "Chọn Miền:",
            options=["Miền Nam", "Miền Trung", "Miền Bắc"],
            index=0
        )
        # Mapping tên miền sang slug dùng cho URL và Fetcher
        slug_map = {
            "Miền Nam": "mien-nam",
            "Miền Trung": "mien-trung",
            "Miền Bắc": "mien-bac"
        }
        region_slug = slug_map[khu_vuc]

    # THÊM ĐOẠN NÀY VÀO DƯỚI st.selectbox ---
    st.markdown("---")
    if st.button("🗑️ Xóa bộ nhớ tạm (Tải lại)"):
        st.cache_data.clear()
        st.toast("Đã xóa cache! Dữ liệu sẽ được tải mới.", icon="✅")        

# Khởi tạo classes
comparator = SMSComparator()
parser = SMSParser()
fetcher = MinhNgocFetcher()

# --- 2. HIỂN THỊ KẾT QUẢ XỔ SỐ TỪ WEB ---
st.info(f"Đang xem: **{khu_vuc}** - Ngày: **{date_str_api}**")

# URL để hiển thị (Embed view)
url_embed = f"https://www.minhngoc.net.vn/ket-qua-xo-so/{region_slug}/{date_str_api}.html"

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    # Request nhẹ để lấy HTML bảng kết quả
    resp = requests.get(url_embed, headers=headers, timeout=10)
    
    if resp.status_code == 200:
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Lấy bảng kết quả (box_kqxs)
        content_div = soup.find('div', class_='box_kqxs')
        
        if content_div:
            # CSS tối giản để hiển thị gọn
            css = """
            <style>
                body { font-family: sans-serif; margin: 0; padding: 0; }
                .box_kqxs { border: 1px solid #ddd; }
                table { width: 100%; border-collapse: collapse; font-size: 14px; }
                td, th { border: 1px solid #eee; padding: 4px; text-align: center; }
                .tinh { color: #d32f2f; font-weight: bold; }
                .giai_db { color: red; font-weight: bold; font-size: 16px; }
                /* Ẩn các thành phần thừa */
                .opt_date, .buttons-wrapper, .box_kqxs_tructiep { display: none !important; }
            </style>
            """
            html_show = f'<base href="https://www.minhngoc.net.vn/" target="_blank">{css}{str(content_div)}'
            components.html(html_show, height=500, scrolling=True)
        else:
            st.warning("Chưa tìm thấy bảng kết quả (hoặc web thay đổi cấu trúc).")
    else:
        st.error("Không tải được trang Minh Ngọc.")

except Exception as e:
    st.error(f"Lỗi tải bảng KQ: {e}")

st.divider()

# --- 3. KHUNG NHẬP LIỆU ---
lines = render_input_form()
col_act1, col_act2 = st.columns([1, 4])

with col_act1:
    btn_run = st.button("Phân tích sms", type="primary")
with col_act2:
    if st.button("Làm mới"):
        if "input_sms_area" in st.session_state:
            st.session_state.input_sms_area = ""
        st.rerun()

# --- 4. XỬ LÝ LOGIC CHÍNH ---
if "results" not in st.session_state:
    st.session_state.results = []

if btn_run:
    if not lines:
        st.warning("Vui lòng nhập tin nhắn cược!")
    else:
        # A. TẢI DỮ LIỆU SỐ (Quan trọng: Truyền region_slug)
        kqxs_data = {}
        with st.spinner(f"Đang đồng bộ dữ liệu {khu_vuc} ({date_str_api})..."):
            # --- SỬA THÀNH GỌI HÀM CACHE ---
            kqxs_data = get_cached_lottery_data(date_str_api, region_slug)
        
        has_data = bool(kqxs_data)

        if has_data:
            with st.expander("🔍 Soi dữ liệu thô (Dữ liệu máy dùng để chấm)", expanded=False):
                st.write("Dưới đây là danh sách các số máy đã tải về. Hãy tìm số bạn đánh ở đây:")
                st.json(kqxs_data)
                
        if not has_data:
            st.error(f"⚠️ Không tìm thấy dữ liệu xổ số cho {khu_vuc} ngày {date_str_api}. Chỉ phân tích cú pháp.")

        # B. PHÂN TÍCH VÀ DÒ
        checker = BetChecker(kqxs_data)
        final_results = []

        for line in lines:
            # 1. So sánh cú pháp
            res_ss = comparator.compare(line)
            
            # 2. Parse lại để lấy object xử lý
            res_parse = None
            list_check = []
            
            if res_ss.hop_le:
                res_parse = parser.parse(res_ss.tin_nhan_sau_sua)
                
                # 3. Dò kết quả (Nếu có data xổ số)
                if has_data and res_parse.hop_le:
                    for cuoc in res_parse.danh_sach_cuoc:
                        # Logic Dò từng cược
                        kq_check = checker.check_cuoc(cuoc)
                        list_check.append(kq_check)

            final_results.append({
                "ss": res_ss,
                "parse": res_parse,
                "check_results": list_check # List kết quả thắng/thua
            })
        
        st.session_state.results = final_results

# --- 5. RENDER KẾT QUẢ ---
if st.session_state.results:
    # Kiểm tra xem có kết quả dò nào không để bật chế độ tô màu
    has_check_data = any(len(r["check_results"]) > 0 for r in st.session_state.results)
    
    render_results(st.session_state.results, has_data=has_check_data)
