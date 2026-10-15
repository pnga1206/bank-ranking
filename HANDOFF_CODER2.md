# Handoff cho coder 2: xây dashboard

## Chạy và cấu trúc

- Cài dependency: `pip install -r requirements.txt`
- Chạy app hiện có: `python -m streamlit run src/app.py`
- Entry point: `src/app.py`. Hàm chuẩn hóa, ngân hàng, năm và trọng số: `src/scoring.py`. Mô tả DBI: `src/method.py`.
- `src/app.py` đọc hai CSV dưới `data/`; không cần `output/` hay chạy script tạo HTML.

## Dữ liệu và cách dùng

### `data/evidence.csv` — nguồn điểm chính

Mỗi dòng là một quan sát theo ngân hàng, năm, tiêu chí. Cột chính:

- `bank`, `year`, `metric`: khóa quan sát.
- `value`, `unit`, `as_of`: giá trị, đơn vị và kỳ/thời điểm công bố.
- `scored`: `1` được tính; `0` loại mặc định vì định nghĩa/đơn vị chưa so sánh được.
- `kind`: `reported` là số do nguồn công bố; `rubric` là điểm mã hóa theo quy tắc nghiên cứu.
- `note`: giải thích điều số liệu đo và các cảnh báo cần hiện trong dashboard.
- `source_title`, `url`: nguồn để người xem mở và kiểm chứng.

Tiêu chí/trọng số hiện tại trong `src/scoring.py`: tỷ trọng giao dịch số 30; người dùng số 25; nghiệp vụ số hóa 15; mốc sản phẩm 15; chiến lược 10; giải thưởng 5. Điểm năm lấy trung bình có trọng số của các tiêu chí có dữ liệu và chuẩn hóa lại trọng số; điểm toàn kỳ lấy trung bình các năm có điểm. Độ phủ là tổng trọng số tiêu chí có dữ liệu. Hiển thị độ phủ cạnh điểm để người xem biết mức thiếu dữ liệu.

### `data/news_2026.csv` — tin tham khảo

Cột `bank,date,headline,note,url`. Dùng làm mục tin riêng, **không** đưa vào điểm 2023–2025. Đây là danh sách biên tập tĩnh; không phải crawler live. Cần ưu tiên bài trực tiếp từ ngân hàng/NHNN/hiệp hội hoặc báo chí uy tín, dùng URL bài cụ thể thay cho trang tag/chuyên mục.

## Trạng thái chất lượng — không trình bày quá mức dữ liệu

- Có 58 dòng evidence, trong đó 56 dòng được tính điểm và 2 dòng đang bị loại mặc định. Các dòng chấm có URL nguồn.
- Chưa đạt yêu cầu 2–3 minh chứng độc lập cho từng tiêu chí. Hiện một dòng điểm chỉ có một URL. Khi hoàn thiện, tạo `data/evidence_sources.csv` với khóa `bank,year,metric` và nhiều nguồn cho mỗi khóa; thêm trích dẫn ngắn, số trang/ngày xuất bản, định nghĩa, phạm vi đo và trạng thái kiểm tra.
- `data/news_2026.csv` chỉ có một số tin đã sưu tầm, không đầy đủ và không tự cập nhật. Cần thêm lọc ngân hàng/ngày, thời điểm cập nhật, và kiểm tra nguồn/link.
- Một số chỉ tiêu có phạm vi khác nhau (ví dụ giao dịch toàn ngân hàng so với bán lẻ, khách hàng hoạt động so với lượt tải app). Không gộp nếu định nghĩa khác; ghi chú và loại khỏi điểm khi chưa so sánh được.
- Điểm chiến lược/mốc/giải thưởng có yếu tố rubric và cần quy tắc mã hóa nhất quán. Trọng số/ngưỡng hiện tại là thiết kế nghiên cứu, không phải công thức DBI chính thức.
- Nam A Bank có độ phủ thấp; mọi biểu đồ/xếp hạng cần cho thấy độ phủ, và tránh diễn giải hạng như kết luận chắc chắn.

## Phần dashboard cần bàn giao

1. BXH tổng kỳ và theo năm; cho thấy điểm, hạng, độ phủ và kỳ dữ liệu.
2. So sánh theo từng metric giữa 5 ngân hàng và xu hướng qua năm.
3. Bảng minh chứng có bộ lọc bank/năm/metric, URL mở được, ghi rõ `scored` và `kind`; khi có evidence_sources thì hiển thị 2–3 nguồn, không tạo nguồn giả để đủ số lượng.
4. Trang tin riêng: cập nhật theo ngày, lọc ngân hàng, chỉ lấy URL bài viết trực tiếp và tách tin dự báo/mục tiêu khỏi kết quả đã đạt; không dùng tin 2026 để chấm điểm 2023–2025.
5. Giữ trang phương pháp và giải thích giới hạn; không gọi đây là BXH chính thức của NHNN.
6. Nên cho tải CSV/ảnh hoặc báo cáo, và lưu được bộ trọng số mặc định để người khác tái lập kết quả.
