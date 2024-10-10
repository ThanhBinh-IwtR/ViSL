// document.getElementById("start-button").addEventListener("click", function() {
//     const video = document.getElementById('camera-stream');
//     const overlay = document.getElementById('overlay');

//     // Yêu cầu quyền truy cập camera của người dùng
//     navigator.mediaDevices.getUserMedia({ video: true })
//         .then(function(stream) {
//             // Đặt stream vào thẻ video để hiển thị
//             video.srcObject = stream;
//             video.style.display = 'block'; // Hiển thị video
//             overlay.style.display = 'none'; // Ẩn lớp phủ và nút "Bắt đầu"
//         })
//         .catch(function(err) {
//             console.log("Lỗi khi truy cập camera: ", err);
//         });
// });

document.getElementById("start-button").addEventListener("click", function() {
    const video = document.getElementById('camera-stream');
    const overlay = document.getElementById('overlay');
    const resultBox = document.querySelector('textarea[name="resultbox"]');

    // Yêu cầu quyền truy cập camera của người dùng
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            // Đặt stream vào thẻ video để hiển thị
            video.srcObject = stream;
            video.style.display = 'block'; // Hiển thị video
            overlay.style.display = 'none'; // Ẩn lớp phủ và nút "Bắt đầu"

            // Bắt đầu gửi frame liên tục
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');

            // Thiết lập canvas với kích thước giống video khi video đã sẵn sàng
            video.addEventListener('loadedmetadata', () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            });

            // Hàm để gửi frame đến server
            function sendFrame() {
                // Kiểm tra nếu video có stream thì vẽ lên canvas
                if (video.readyState === 4) { // 4 = HAVE_ENOUGH_DATA
                    context.drawImage(video, 0, 0, canvas.width, canvas.height);

                    // Lấy dữ liệu hình ảnh từ canvas dưới dạng base64 (chỉ lấy phần sau 'data:image/jpeg;base64,')
                    const imageData = canvas.toDataURL('image/jpeg').split(',')[1];

                    // Log lại chuỗi base64 để kiểm tra
                    console.log('Base64 Image Data:', imageData);

                    if (imageData) {
                        // Gửi frame tới backend
                        fetch('/process-frame', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                frame: imageData  // Gửi chỉ phần dữ liệu base64 mà không có header
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            // Cập nhật kết quả vào textarea
                            resultBox.value = data.result;
                        })
                        .catch(err => console.log('Lỗi khi gửi frame: ', err));
                    } else {
                        console.error('No base64 data generated');
                    }
                } else {
                    console.error('Video is not ready for capturing frames');
                }

                // Tiếp tục gửi frame sau 100ms (10 frame mỗi giây)
                setTimeout(sendFrame, 100);
            }

            // Bắt đầu gửi frame đầu tiên
            sendFrame();
        })
        .catch(function(err) {
            console.log("Lỗi khi truy cập camera: ", err);
        });
});