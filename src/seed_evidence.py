"""Tạo data/evidence.csv và data/news_2026.csv từ các số liệu đã thu thập (kèm nguồn).

Mỗi dòng = 1 số liệu / 1 nhận định có link nguồn. Cột:
  kind     = reported (số công bố) | rubric (điểm/đếm do nhóm phân tích chấm theo thang trong README)
  scored   = 1 tính vào điểm, 0 chỉ hiển thị (định nghĩa không nhất quán với năm khác)
  keyword  = chuỗi dùng để kiểm chứng lại trên trang nguồn (scrape.py)
"""
import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
H = ["bank", "year", "metric", "value", "unit", "as_of", "scored", "kind", "note", "source_title", "url", "keyword"]

TTC = "https://thitruongtaichinhtiente.vn/"
U = {
    "vcb23": "https://nhadautu.vn/chia-khoa-chinh-phuc-dinh-cao-d75503.html",
    "vcb_strat": TTC + "vietcombank-chuyen-minh-manh-me-voi-thanh-toan-so-44555.html",
    "vcb24q2": TTC + "di-dau-trong-tien-trinh-chuyen-doi-so-cac-ngan-hang-va-doanh-nghiep-da-dat-duoc-ket-qua-gi-63749.html",
    "vcb24new": TTC + "print/59638.html",
    "vcb25": "https://tapchikinhtetaichinh.vn/song-tren-nhung-cu-cham-so-cua-ngan-hang-hien-dai-157012.html",
    "vtb23": "https://vnba.org.vn/vi/vietinbank-cap-nhat-ket-qua-kinh-doanh--voi-tang-truong-an-toan-va-ben-vung-12319.htm",
    "vtb23ops": "https://www.sggp.org.vn/vietinbank-voi-chien-luoc-chuyen-doi-so-dinh-vi-va-tao-da-but-pha-post690373.html",
    "vtb23strat": TTC + "print/46788.html",
    "vtb23award": TTC + "ngan-hang-so-cho-doanh-nghiep-cua-vietinbank-duoc-vinh-danh-sao-khue-2023-46525.html",
    "vtb24": "https://tapchitoaan.vn/vietinbank-nam-2024-chay-da-hieu-qua-but-pha-thanh-cong12976.html",
    "vtb24strat": "https://daibieunhandan.vn/tang-truong-manh-me-hieu-qua-ben-vung-10352121.html",
    "vtb25": "https://viettimes.vn/vietinbank-dot-pha-so-suc-manh-moi-post195181.html",
    "vtb25app": "https://vnbusiness.vn/vietinbank-ipay-mobile-nhan-giai-thuong-ung-dung-ngan-hang-so-sang-tao-nhat-viet-nam-2025.html",
    "shb23": "https://tapchicongthuong.vn/nam-2023--shb-tiep-tuc-chuyen-doi-manh-me-va-toan-dien-117537.htm",
    "shb24bctn": "https://www.shb.com.vn/BCTN2024/pdf/Chuong-3-BCTN-SHB-2024.pdf",
    "shb24vs": "https://en.vietstock.vn/2024/12/shb-promotes-digital-solutions-for-corporate-customers-37-593551.htm",
    "shb24strat": TTC + "ket-thuc-2024-nam-ban-le-cua-chien-luoc-chuyen-doi-shb-ghi-nhan-ket-qua-kinh-doanh-but-pha-65417.html",
    "shb25saha": TTC + "shb-ra-mat-ung-dung-ngan-hang-so-the-he-moi-shb-saha-an-tam-trong-moi-giao-dich-68388.html",
    "shb25res": "https://lsvn.vn/shb-lai-truoc-thue-hon-15-000-ti-dong-tang-30-huong-den-muc-tieu-tong-tai-san-1-trieu-ti-dong-a169078.html",
    "shb25q1": "https://vnba.org.vn/vi/shb-lai-gan-4-400-ty-dong-quy-i-va-du-kien-chia-co-tuc-len-toi-36-17382.htm",
    "shb25banker": TTC + "the-banker-vinh-danh-shb-la-ngan-hang-cua-nam-2025-74238.html",
    "stb23": "https://vnexpress.net/sacombank-day-manh-chuyen-doi-so-4598067.html",
    "stb23prod": TTC + "print/55432.html",
    "stb23award": TTC + "sacombank-nhan-2-giai-thuong-quoc-te-ve-chuyen-doi-so-va-ban-le-47481.html",
    "stb24": TTC + "sacombank-day-manh-chuyen-doi-so-gop-phan-tao-dong-luc-tang-truong-moi-cho-tp-ho-chi-minh-63547.html",
    "stb24vis": TTC + "sacombank-nhan-2-giai-thuong-trong-linh-vuc-ngan-hang-so-va-ban-le-sang-tao-59355.html",
    "stb25": TTC + "sacombank-dong-hanh-cung-ngay-khong-tien-mat-2025-gop-phan-thuc-day-kinh-te-so-68238.html",
    "stb25prod": "https://vnba.org.vn/vi/sacombank-14-nam-lien-giu-vung-danh-hieu-thuong-hieu-manh-viet-nam-19178.htm",
    "stb25award": TTC + "5-nam-lien-tiep-sacombank-khang-dinh-vi-the-tai-giai-thuong-sao-khue-67127.html",
    "nab23": "https://vneconomy.vn/chuyen-doi-so-nganh-ngan-hang-2023-nam-a-bank-tien-phong-voi-he-sinh-thai-ngan-hang-so-mot-cham-moi-trai-nghiem.htm",
    "nab23award": "https://www.sggp.org.vn/nam-a-bank-ngan-hang-chuyen-doi-so-cua-nam-post722526.html",
    "nab_tap": "https://www.sggp.org.vn/nam-a-bank-ngan-hang-dau-tien-phoi-hop-napas-trien-khai-dich-vu-thanh-toan-di-dong-tap-pay-post774659.html",
    "nab24card": TTC + "print/63405.html",
    "nab24award": "https://thoibaotaichinhvietnam.vn/onebank-cua-nam-a-bank-xuat-sac-nhan-giai-thuong-chuyen-doi-so-viet-nam-2024-161155.html",
    "nab25": "https://daibieunhandan.vn/nam-a-bank-nhan-cu-dup-giai-thuong-tai-le-trao-giai-ngan-hang-viet-nam-tieu-bieu-2025-10387257.html",
    "nab25agm": "https://namabank.com.vn/Data/Sites/1/userfiles/34/2026/vankien01_27022026.pdf",
}

R = []


def add(bank, year, metric, value, unit, as_of, scored, kind, note, title, key, kw):
    R.append([bank, year, metric, value, unit, as_of, scored, kind, note, title, U[key], kw])


# ---------------- VCB ----------------
add("VCB", 2023, "tx_share", 98, "%", "2023-04", 1, "reported", "98% giao dịch của khách hàng thực hiện trên kênh số", "Chìa khóa chinh phục đỉnh cao (nhadautu.vn, 10/04/2023)", "vcb23", "98%")
add("VCB", 2023, "users_m", 10, "triệu", "2023-04", 1, "reported", "Gần 10 triệu khách hàng thường xuyên giao dịch kênh số", "Chìa khóa chinh phục đỉnh cao (nhadautu.vn, 10/04/2023)", "vcb23", "10 triệu")
add("VCB", 2023, "strategy", 70, "điểm", "2023-03", 1, "rubric", "Có Nghị quyết 2021 & kế hoạch hành động CĐS đến 2025 (mục tiêu ngân hàng số đứng đầu); chưa thấy KPI định lượng công bố", "Vietcombank chuyển mình mạnh mẽ với 'Thanh toán số' (03/03/2023)", "vcb_strat", "2025")
add("VCB", 2024, "tx_share", 92, "%", "2024-Q2", 1, "reported", "92% tỷ trọng giao dịch xử lý trên kênh số quý II/2024 (so mục tiêu NHNN 80% đến 2025). Lưu ý: định nghĩa khác số 2023", "Đi đầu trong tiến trình chuyển đổi số (thitruongtaichinhtiente.vn)", "vcb24q2", "92%")
add("VCB", 2024, "users_m", 13, "triệu", "2024-06", 1, "reported", "Gần 13 triệu khách hàng thường xuyên VCB Digibank, >6 triệu giao dịch/ngày", "Vietcombank ra mắt ngân hàng số thế hệ mới (18/6/2024)", "vcb24new", "13 triệu")
add("VCB", 2024, "milestones", 2, "số mốc", "2024", 1, "rubric", "(1) Ra mắt VCB Digibank thế hệ mới 18/6/2024; (2) xác thực sinh trắc học giao dịch online từ 1/7/2024", "Vietcombank ra mắt ngân hàng số thế hệ mới (18/6/2024)", "vcb24new", "18/6/2024")
add("VCB", 2024, "strategy", 70, "điểm", "2024", 1, "rubric", "Chương trình CĐS đến 2025; chưa thấy KPI định lượng công bố ngoài mục tiêu ngành", "Đi đầu trong tiến trình chuyển đổi số (thitruongtaichinhtiente.vn)", "vcb24q2", "Vietcombank")
add("VCB", 2025, "tx_share", 99, "%", "2025-12", 1, "reported", "Gần 99% giao dịch bán lẻ qua kênh số; ~1,17 tỷ giao dịch, ~14,7 triệu tỷ đồng", "Sống trên những cú chạm số (Tạp chí Kinh tế - Tài chính)", "vcb25", "99%")
add("VCB", 2025, "users_m", 18, "triệu", "2025-12", 1, "reported", "Gần 18 triệu khách hàng hoạt động trên VCB Digibank", "Sống trên những cú chạm số (Tạp chí Kinh tế - Tài chính)", "vcb25", "18 triệu")
add("VCB", 2025, "milestones", 2, "số mốc", "2025", 1, "rubric", "(1) Gói VCB DigiShop (Q3/2025); (2) thu thập sinh trắc học >15 triệu KH, ~2,5 triệu TK liên kết an sinh qua VNeID", "Sống trên những cú chạm số (Tạp chí Kinh tế - Tài chính)", "vcb25", "15 triệu")
add("VCB", 2025, "strategy", 70, "điểm", "2025", 1, "rubric", "Chương trình CĐS đến 2025; chưa thấy KPI định lượng công bố", "Sống trên những cú chạm số (Tạp chí Kinh tế - Tài chính)", "vcb25", "VCB")

# ---------------- VietinBank ----------------
add("VietinBank", 2023, "tx_share", 90.5, "%", "2023-09", 1, "reported", "Tỷ trọng giao dịch KHCN qua iPay 90,5% (9T/2023); eFAST 82%", "VietinBank cập nhật kết quả kinh doanh (VNBA, 15/11/2023)", "vtb23", "90,5%")
add("VietinBank", 2023, "users_m", 7.4, "triệu", "2023-09", 1, "reported", "Gần 7,4 triệu KH dùng iPay Mobile; 786 triệu giao dịch 9T/2023", "VietinBank cập nhật kết quả kinh doanh (VNBA, 15/11/2023)", "vtb23", "7,4 triệu")
add("VietinBank", 2023, "ops_pct", 65, "%", "2023", 1, "reported", "65% sản phẩm, dịch vụ thực hiện hoàn toàn trên kênh số", "VietinBank với chiến lược chuyển đổi số (SGGP)", "vtb23ops", "65%")
add("VietinBank", 2023, "strategy", 85, "điểm", "2023-05", 1, "rubric", "Chiến lược CĐS 2023–2025, tầm nhìn 2030; 'đại dự án thứ 3' do Chủ tịch HĐQT chỉ đạo; chưa thấy KPI công bố", "VietinBank xây dựng chiến lược chuyển đổi số 2023–2025", "vtb23strat", "2023")
add("VietinBank", 2023, "recognition", 1, "giải", "2023-05", 1, "rubric", "VietinBank eFAST – Sao Khuê 2023 (lần thứ 5)", "Ngân hàng số cho DN của VietinBank được vinh danh Sao Khuê 2023", "vtb23award", "Sao Khuê")
add("VietinBank", 2024, "tx_share", 92.9, "%", "2024-12", 1, "reported", "Tỷ trọng giao dịch KHCN qua iPay 92,9%; eFAST 84%", "VietinBank năm 2024: Chạy đà hiệu quả (Tạp chí Toàn Án)", "vtb24", "92,9%")
add("VietinBank", 2024, "users_m", 9.0, "triệu", "2024-12", 1, "reported", "Hơn 9 triệu KH iPay Mobile, 1.960 triệu giao dịch (+66% so 2023)", "VietinBank năm 2024: Chạy đà hiệu quả (Tạp chí Toàn Án)", "vtb24", "9 triệu")
add("VietinBank", 2024, "milestones", 1, "số mốc", "2024-06", 1, "rubric", "Ra mắt Nhà máy số (6/2024)", "VietinBank năm 2024: Chạy đà hiệu quả (Tạp chí Toàn Án)", "vtb24", "Nhà máy số")
add("VietinBank", 2024, "strategy", 100, "điểm", "2024", 1, "rubric", "Chương trình CĐS 2024–2028: 108 sáng kiến/29 nhóm; theo dõi định lượng (17/45 sáng kiến 2024 triển khai đến Q3)", "Tăng trưởng mạnh mẽ, hiệu quả, bền vững (Báo Đại biểu Nhân dân)", "vtb24strat", "108")
add("VietinBank", 2025, "tx_share", 94, "%", "2025-12", 1, "reported", "Tỷ lệ chuyển dịch giao dịch lên kênh số >94% (kênh số 95,3%); giải ngân online Q4 >500.000 tỷ", "VietinBank đột phá số, sức mạnh mới (Viettimes)", "vtb25", "94%")
add("VietinBank", 2025, "users_m", 14, "triệu", "2025-06", 0, "reported", ">14 triệu KH thường xuyên iPay Mobile (H1/2025). KHÔNG tính điểm: nhảy từ 9 triệu (cuối 2024) có thể do khác định nghĩa", "VietinBank iPay Mobile nhận giải thưởng (VnBusiness)", "vtb25app", "14 triệu")
add("VietinBank", 2025, "milestones", 1, "số mốc", "2025", 1, "rubric", "Hoàn thiện hệ sinh thái số KHDN quanh eFAST; cổng API >300 triệu giao dịch/năm", "VietinBank đột phá số, sức mạnh mới (Viettimes)", "vtb25", "300 triệu")
add("VietinBank", 2025, "strategy", 100, "điểm", "2025", 1, "rubric", "Đang thực thi chương trình CĐS 2024–2028 (108 sáng kiến)", "Tăng trưởng mạnh mẽ, hiệu quả, bền vững (Báo Đại biểu Nhân dân)", "vtb24strat", "108")
add("VietinBank", 2025, "recognition", 1, "giải", "2025", 1, "rubric", "iPay Mobile – Ứng dụng Ngân hàng số sáng tạo nhất VN 2025 (Global Banking & Finance Review)", "VietinBank iPay Mobile nhận giải thưởng (VnBusiness)", "vtb25app", "2025")

# ---------------- SHB ----------------
add("SHB", 2023, "tx_share", 90, "%", "2023", 1, "reported", "90% số lượng giao dịch KH DN & cá nhân hoàn toàn qua kênh số", "Năm 2023, SHB tiếp tục chuyển đổi mạnh mẽ (Tạp chí Công Thương)", "shb23", "90%")
add("SHB", 2023, "ops_pct", 90, "%", "2023", 1, "reported", "90% nghiệp vụ trọng yếu thực hiện hoàn toàn trên kênh số", "Năm 2023, SHB tiếp tục chuyển đổi mạnh mẽ (Tạp chí Công Thương)", "shb23", "90%")
add("SHB", 2024, "tx_share", 90, "%", "2024", 1, "reported", "90% (BCTN 2024). Báo chí nêu 92%–98%: dùng số thấp nhất từ báo cáo chính thức", "BCTN SHB 2024 – Chương 3", "shb24bctn", "90%")
add("SHB", 2024, "ops_pct", 90, "%", "2024-12", 1, "reported", "90% nghiệp vụ trọng yếu thực hiện số (báo chí khác nêu >95%)", "SHB promotes digital solutions for corporate customers (Vietstock)", "shb24vs", "90 per cent")
add("SHB", 2024, "milestones", 1, "số mốc", "2024-12", 1, "rubric", "Triển khai SHB Corporate Mobile cho KH doanh nghiệp", "SHB promotes digital solutions for corporate customers (Vietstock)", "shb24vs", "Corporate Mobile")
add("SHB", 2024, "strategy", 70, "điểm", "2024", 1, "rubric", "Chiến lược Chuyển đổi 2024–2028 với 4 trụ cột (có trụ cột hiện đại hóa CNTT & CĐS); chưa thấy KPI số hóa định lượng", "Kết thúc 2024 – năm bản lề của Chiến lược Chuyển đổi, SHB", "shb24strat", "4 trụ cột")
add("SHB", 2025, "milestones", 2, "số mốc", "2025-06", 1, "rubric", "(1) Ra mắt SHB SAHA 18/6/2025; (2) giải pháp tài chính số cho bệnh viện, trường học (2025)", "SHB ra mắt ứng dụng ngân hàng số thế hệ mới SHB SAHA", "shb25saha", "18/6/2025")
add("SHB", 2025, "strategy", 70, "điểm", "2025", 1, "rubric", "Chiến lược 4 trụ cột, CĐS là đòn bẩy tăng trưởng; chưa thấy KPI số hóa công bố", "SHB lãi gần 4.400 tỷ quý I (VNBA)", "shb25q1", "4 trụ cột")
add("SHB", 2025, "recognition", 1, "giải", "2025-12", 1, "rubric", "The Banker – Ngân hàng của năm 2025 tại VN (tiêu chí gồm cả chuyển đổi số, không thuần số)", "The Banker vinh danh SHB là Ngân hàng của năm 2025", "shb25banker", "Ngân hàng của năm 2025")

# ---------------- Sacombank ----------------
add("Sacombank", 2023, "tx_share", 97, "%", "2022", 1, "reported", "97% giao dịch là giao dịch số (số năm 2022, công bố tại ĐHĐCĐ 2023)", "Sacombank đẩy mạnh chuyển đổi số (VnExpress)", "stb23", "97%")
add("Sacombank", 2023, "users_m", 7.5, "triệu", "2023-04", 1, "reported", "15 triệu KH, 50% là người dùng số (≈7,5 triệu)", "Sacombank đẩy mạnh chuyển đổi số (VnExpress)", "stb23", "50%")
add("Sacombank", 2023, "milestones", 2, "số mốc", "2023", 1, "rubric", "(1) Sacombank Pay kết nối Apple Pay; (2) rút tiền mặt qua VietQR tại ATM ngân hàng khác", "Sacombank Pay nhận giải sản phẩm, dịch vụ tin dùng (09/01/2024)", "stb23prod", "Apple Pay")
add("Sacombank", 2023, "strategy", 70, "điểm", "2023-06", 1, "rubric", "Trung tâm CĐS từ 2021, 4 trụ cột (hạ tầng, số hóa, sản phẩm, con người); chưa thấy KPI công bố", "Sacombank nhận 2 giải thưởng quốc tế về chuyển đổi số và bán lẻ", "stb23award", "Trung tâm Chuyển đổi số")
add("Sacombank", 2023, "recognition", 3, "giải", "2023", 1, "rubric", "IBM 'Ngân hàng CĐS tốt nhất VN 2023'; ABF 'Công nghệ & vận hành tốt nhất 2023'; 'Sản phẩm dịch vụ tiêu biểu TP.HCM 2023'", "Sacombank nhận 2 giải thưởng quốc tế về chuyển đổi số và bán lẻ", "stb23award", "2023")
add("Sacombank", 2024, "users_m", 12.7, "triệu", "2024-10", 1, "reported", "Gần 19 triệu KH, 67% trên kênh số (≈12,7 triệu); 508 triệu giao dịch kênh số năm 2023", "Sacombank đẩy mạnh chuyển đổi số, góp phần tạo động lực (10/2024)", "stb24", "67%")
add("Sacombank", 2024, "milestones", 1, "số mốc", "2024-10", 1, "rubric", "Triển khai xác thực sinh trắc học & chữ ký số giao dịch trực tuyến; hoàn thiện dự án omnichannel", "Sacombank đẩy mạnh chuyển đổi số, góp phần tạo động lực (10/2024)", "stb24", "sinh trắc học")
add("Sacombank", 2024, "strategy", 70, "điểm", "2024", 1, "rubric", "Mục tiêu 2030: TOP 3 ngân hàng số hóa & bán lẻ (định lượng theo thứ hạng)", "Sacombank nhận 2 giải thưởng ngân hàng số và bán lẻ sáng tạo", "stb24vis", "2030")
add("Sacombank", 2024, "recognition", 1, "giải", "2024", 1, "rubric", "IBM – Ngân hàng số & bán lẻ sáng tạo (năm thứ 4)", "Sacombank nhận 2 giải thưởng ngân hàng số và bán lẻ sáng tạo", "stb24vis", "IBM")
add("Sacombank", 2025, "tx_share", 96, "%", "2025-05", 1, "reported", "Gần 96% giao dịch qua kênh số (hết 5/2025)", "Sacombank đồng hành 'Ngày không tiền mặt 2025'", "stb25", "96%")
add("Sacombank", 2025, "users_m", 6.8, "triệu", "2025-05", 0, "reported", "6,8 triệu lượt tải & sử dụng Sacombank Pay. KHÔNG tính điểm: định nghĩa khác (một app) so với số KH số 2024", "Sacombank đồng hành 'Ngày không tiền mặt 2025'", "stb25", "6,8 triệu")
add("Sacombank", 2025, "milestones", 2, "số mốc", "2025", 1, "rubric", "(1) Loa thanh toán thông minh cho hộ kinh doanh; (2) thanh toán giao thông công cộng Mastercard MultiPass/Metro Pass", "Sacombank 14 năm giữ danh hiệu Thương hiệu mạnh VN (VNBA)", "stb25prod", "Loa thanh toán")
add("Sacombank", 2025, "recognition", 1, "giải", "2025-04", 1, "rubric", "Sao Khuê 2025 – 5 sao cho Sacombank Pay (năm thứ 5 liên tiếp)", "5 năm liên tiếp Sacombank tại Giải thưởng Sao Khuê", "stb25award", "Sao Khuê")

# ---------------- Nam A Bank ----------------
add("Nam A Bank", 2023, "tx_share", 92, "%", "2023-05", 1, "reported", "92% KH giao dịch qua kênh số (đo theo KH, khác định nghĩa theo giao dịch)", "Chuyển đổi số ngành Ngân hàng 2023: Nam A Bank tiên phong (VnEconomy)", "nab23", "92%")
add("Nam A Bank", 2023, "milestones", 1, "số mốc", "2023", 1, "rubric", "Triển khai soft POS (Tap to Phone) cùng NAPAS trong năm 2023", "Nam A Bank – NH đầu tiên phối hợp NAPAS triển khai Tap & Pay (SGGP)", "nab_tap", "soft POS")
add("Nam A Bank", 2023, "recognition", 3, "giải", "2023-01", 1, "rubric", "Vietnam Digital Awards 2023; ABF 'Hệ sinh thái NH số sáng tạo nhất 2023'; bằng khen Bộ TT&TT về CĐS ngân hàng", "Nam A Bank – ngân hàng chuyển đổi số của năm (SGGP)", "nab23award", "2023")
add("Nam A Bank", 2024, "milestones", 2, "số mốc", "2024", 1, "rubric", "(1) Tap & Pay NAPAS 24/12/2024 (NH đầu tiên); (2) MoU thẻ đồng thương hiệu NAPAS–Mastercard 15/10/2024", "Nam A Bank – NH đầu tiên phối hợp NAPAS triển khai Tap & Pay (SGGP)", "nab_tap", "24-12-2024")
add("Nam A Bank", 2024, "strategy", 40, "điểm", "2024-12", 1, "rubric", "Định hướng 'số hóa và xanh hóa' là cốt lõi chiến lược; chưa thấy chương trình/KPI CĐS định lượng", "Nam A Bank – NH đầu tiên phối hợp NAPAS triển khai Tap & Pay (SGGP)", "nab_tap", "số hóa và xanh hóa")
add("Nam A Bank", 2024, "recognition", 2, "giải", "2024-10", 1, "rubric", "Giải thưởng CĐS Việt Nam 2024 (ONEBANK 365+); ABF Hệ sinh thái sáng tạo nhất 2024", "ONEBANK của Nam A Bank nhận Giải thưởng CĐS Việt Nam 2024", "nab24award", "2024")
add("Nam A Bank", 2025, "tx_share", 97, "%", "2025-09", 1, "reported", ">97% giao dịch chuyển khoản, thanh toán thực hiện online", "Nam A Bank nhận cú đúp giải thưởng Ngân hàng VN tiêu biểu 2025", "nab25", "97%")
add("Nam A Bank", 2025, "milestones", 1, "số mốc", "2025-12", 1, "rubric", "Mở rộng ONEBANK lên 137 điểm giao dịch số (31/12/2025)", "Văn kiện ĐHĐCĐ 2026 – Nam A Bank", "nab25agm", "137")
add("Nam A Bank", 2025, "recognition", 1, "giải", "2025-09", 1, "rubric", "Vietnam Outstanding Banking Awards 2025 – Ngân hàng Số tiêu biểu", "Nam A Bank nhận cú đúp giải thưởng Ngân hàng VN tiêu biểu 2025", "nab25", "Ngân hàng Số tiêu biểu")

with open(ROOT / "data" / "evidence.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(H)
    w.writerows(R)

NEWS_H = ["bank", "date", "headline", "note", "url"]
N = [
    ["VCB", "2026-05-23", "Giải Đặc biệt Hội thi 'Chuyển đổi số ngành ngân hàng' 2026 (32 đội thi)", "", "https://daibieunhandan.vn/vietcombank-tien-phong-tren-hanh-trinh-chuyen-doi-so-10418079.html"],
    ["VCB", "2026-09-05", "Nhà đồng hành Vàng sự kiện Chuyển đổi số ngành ngân hàng 2026, giới thiệu hệ sinh thái tài chính số", "", "https://daibieunhandan.vn/print/10429532.html"],
    ["VietinBank", "2026-08-18", "Chiến lược CĐS 2026–2028: mục tiêu CĐS đóng góp 30–35% tổng thu nhập hoạt động (TOI)", "Mục tiêu công bố, chưa phải kết quả", "https://thitruongtaichinhtiente.vn/vietinbank-du-lieu-lam-nen-tang-ai-lam-dong-luc-chuyen-doi-so-84986.html"],
    ["VietinBank", "2026-05-28", "'Hành trình vay mua nhà trên kênh số' đạt Sao Khuê 2026", "", "https://thitruongtaichinhtiente.vn/ipay-ptag.html"],
    ["VietinBank", "2026", "Ra mắt Digital L/C trên eFAST; Asian Banker: Ngân hàng SME tốt nhất VN 2026", "Ngày chính xác chưa xác minh", "https://congthuong.vn/tai-chinh"],
    ["SHB", "2026", "Ra mắt tính năng 'Sinh lời nhàn tênh' trên SHB SAHA; thêm sinh trắc học VNeID, phát hành thẻ & giải ngân online trên app DN", "Ngày chính xác chưa xác minh", "https://diendandoanhnghiep.vn/ngan-hang-so-ptag.html"],
    ["Sacombank", "2026", "Đồng hành Ngày Tài chính số 2026", "", "https://vnba.org.vn/vi/hashtag/tai-chinh-so-viet-nam-43244"],
    ["Sacombank", "2026", "Báo lỗ hơn 3.360 tỷ đồng quý IV/2025 (khoản lỗ quý đầu tiên sau 9 năm)", "Tin tài chính, không liên quan trực tiếp CĐS", "https://vnexpress.net/chu-de/sacombank-1596-p2"],
    ["Nam A Bank", "2026-02-27", "Văn kiện ĐHĐCĐ 2026: 148 điểm truyền thống + 137 điểm ONEBANK tại 31/12/2025", "Số liệu 2025 (đã dùng ở phần chấm điểm 2025)", "https://namabank.com.vn/Data/Sites/1/userfiles/34/2026/vankien01_27022026.pdf"],
]
with open(ROOT / "data" / "news_2026.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(NEWS_H)
    w.writerows(N)

print(f"evidence rows: {len(R)}, news rows: {len(N)}")
