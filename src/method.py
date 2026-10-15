"""Research scoring methodology and limitations."""

method = {
    "dbi": (
        "DBI doanh nghiệp lớn là khung tham khảo về các trụ cột chuyển đổi số. "
        "Bảng này là mô hình nghiên cứu riêng cho ngân hàng dựa trên dữ liệu công khai, "
        "không phải điểm DBI chính thức và không thay thế tự đánh giá nội bộ của ngân hàng."
    ),
    "rows": [
        ["Tỷ trọng giao dịch qua kênh số", "Khách hàng", 30, "Chỉ so sánh khi nguồn công bố cùng định nghĩa và phạm vi."],
        ["Người dùng số hoạt động", "Khách hàng", 25, "Ghi rõ kỳ đo, định nghĩa người dùng và phạm vi khách hàng."],
        ["Nghiệp vụ trên kênh số", "Vận hành", 15, "Tỷ lệ công bố trực tiếp; không thay thế số liệu thiếu."],
        ["Mốc sản phẩm/nền tảng số", "Công nghệ", 15, "Đếm mốc có nguồn, kèm quy tắc tránh đếm trùng."],
        ["Chiến lược chuyển đổi số", "Chiến lược", 10, "Rubric cần công bố tiêu chí và bằng chứng."],
        ["Ghi nhận bên thứ ba", "Tham khảo", 5, "Chỉ dùng giải thưởng chuyên biệt về số hóa."],
    ],
    "limits": [
        "Các chỉ số được công bố không đồng nhất giữa ngân hàng và năm; điểm tổng hợp cần được xem cùng độ phủ dữ liệu.",
        "Mốc sản phẩm, chiến lược và giải thưởng có yếu tố mã hóa thủ công, cần lưu bằng chứng và áp dụng cùng rubric.",
        "BCTN là nguồn để khai phá nội dung và tìm bằng chứng; tần suất từ khóa không tự nó chứng minh mức độ chuyển đổi số.",
        "Chỉ xếp hạng các ngân hàng-năm có dữ liệu; không gán 0 cho dữ liệu thiếu. Công bố cả số năm có dữ liệu và độ phủ.",
    ],
    "dbi_sources": [
        ["DBI – Bộ KH&CN", "https://mst.gov.vn/"],
        ["Repo tham khảo BCTN", "https://github.com/Tumiqa/vn-annual-report-miner"],
    ],
}
