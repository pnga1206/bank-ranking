"""Ghép output/scores.json + data/*.csv vào src/template.html -> output/dashboard.html (file đơn, mở bằng trình duyệt)."""
import csv
import json
import pathlib

from scoring import METRICS

ROOT = pathlib.Path(__file__).resolve().parent.parent


def read(p):
    with open(ROOT / "data" / p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


method = {
    "dbi": ("DBI (Bộ chỉ số đánh giá mức độ chuyển đổi số doanh nghiệp) của Bộ KH&CN/Bộ TT&TT gồm 6 trụ cột cho doanh nghiệp lớn: "
            "Khách hàng (25 tiêu chí thành phần), Chiến lược (24), Công nghệ (29), Vận hành (22), Văn hóa (22), Dữ liệu (18). "
            "DBI là bộ tự đánh giá nội bộ cần dữ liệu doanh nghiệp; bên ngoài không có điểm DBI công bố của từng ngân hàng. "
            "Dashboard này là <b>mô hình chấm điểm dựa trên dữ liệu công khai, lấy cảm hứng từ cấu trúc DBI</b>, không phải điểm DBI chính thức."),
    "rows": [
        ["Tỷ trọng giao dịch qua kênh số", "Khách hàng", 30, "80% (mục tiêu NHNN đến 2025) = 0 điểm; 100% = 100 điểm"],
        ["Người dùng số hoạt động", "Khách hàng", 25, "Số triệu người dùng ÷ 18 triệu (mức cao nhất quan sát được), tối đa 100"],
        ["Nghiệp vụ trọng yếu hoàn toàn trên kênh số", "Vận hành", 15, "Giá trị % trực tiếp"],
        ["Mốc sản phẩm/nền tảng số trong năm", "Công nghệ", 15, "Đếm mốc có nguồn, 3 mốc trở lên = 100 điểm"],
        ["Chiến lược CĐS chính thức", "Chiến lược", 10, "100 = có chương trình + sáng kiến/KPI định lượng; 70 = có chương trình chính thức, chưa thấy KPI; 40 = chỉ có định hướng chung"],
        ["Giải thưởng CĐS độc lập", "Ghi nhận bên thứ ba (đại diện thay thế)", 5, "Đếm giải, 3 giải trở lên = 100 điểm"],
    ],
    "limits": [
        "Trụ cột <b>Văn hóa</b> và <b>Dữ liệu</b> của DBI không chấm được vì không có dữ liệu công khai so sánh được; do đó đây không phải đánh giá toàn diện 6 trụ cột.",
        "Điểm năm = trung bình có trọng số của các chỉ tiêu <b>có dữ liệu</b>; chỉ tiêu thiếu không bị tính 0 nhưng làm giảm độ phủ. Với độ phủ dưới 50% hãy xem thứ hạng như tham khảo.",
        "Định nghĩa số liệu khác nhau giữa các ngân hàng và giữa các năm (giao dịch bán lẻ vs toàn hàng; khách hàng vs giao dịch; số công bố trong năm vs cuối năm). Các dòng không nhất quán rõ rệt được đánh dấu “không tính điểm”.",
        "Các chỉ tiêu “chấm theo thang” (mốc sản phẩm, chiến lược, giải thưởng) là đánh giá của người phân tích và phụ thuộc vào những gì tìm được trên báo chí; ngân hàng truyền thông nhiều có lợi thế.",
        "Phần lớn số liệu lấy từ thông cáo/báo chí về hội nghị kết quả kinh doanh và báo cáo thường niên; chưa được kiểm toán độc lập về chuyển đổi số. SHB 2024: báo cáo thường niên nêu 90% giao dịch số trong khi báo chí nêu 92–98%, mô hình dùng số thấp nhất từ nguồn chính thức.",
        "Kết quả kiểm chứng tự động (src/scrape.py) chưa được chạy trong phiên làm việc này; nguồn đã được đọc khi tìm kiếm, cần chạy lại trên máy có internet để đối chiếu từ khóa.",
    ],
    "dbi_sources": [
        ["Bộ chỉ số DBI doanh nghiệp lớn (Phụ lục II, QĐ Bộ KH&CN)", "https://storage-vnportal.vnpt.vn/gov-tha/7560/FileQuanTriTinTuc/7.QD_PHU LUC II_BO CHI SO DNL638881833500064267.pdf".replace(" ", "%20")],
        ["MISA AMIS – Bộ chỉ số DBI", "https://amis.misa.vn/54491/bo-chi-so-danh-gia-chuyen-doi-so-dbi/"],
    ],
}

scores = json.loads((ROOT / "output" / "scores.json").read_text(encoding="utf-8"))
data = {
    "scores": scores,
    "metrics": {m: {"label": v[2], "pillar": v[0], "weight": v[1]} for m, v in METRICS.items()},
    "evidence": read("evidence.csv"),
    "news": [{"bank": n["bank"], "date": n["date"], "headline": n["headline"], "note": n["note"], "url": n["url"]} for n in read("news_2026.csv")],
    "method": method,
}
js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = (ROOT / "src" / "template.html").read_text(encoding="utf-8").replace("/*DATA*/", js)
out = ROOT / "output" / "dashboard.html"
out.write_text(html, encoding="utf-8")
print("wrote", out, f"({out.stat().st_size//1024} KB)")
