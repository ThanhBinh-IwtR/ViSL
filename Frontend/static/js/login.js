/* 10. loginform */
const registerButton = document.getElementById('register');
const loginButton = document.getElementById('login');
const container = document.getElementById('container');

registerButton.addEventListener('click', () => {
    container.classList.add('right-panel-active');
});

loginButton.addEventListener('click', () => {
    container.classList.remove('right-panel-active');
});

/* 11. register */

// Sự kiện đăng ký
async function handleRegister(event) {
    event.preventDefault(); 

    const form = document.getElementById("registerForm");
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();  
        console.log("Server response:", result);

        if (result.status === "success") {
            // Hiển thị thông báo thành công
            showPopup('success');
        } else if (result.status === "error") {
            // Hiển thị thông báo lỗi
            showPopup('invaliduseremail');
        } else {
            alert("Đăng ký không thành công. Vui lòng thử lại.");
        }
    } catch (error) {
        console.error("Lỗi:", error);
        alert("Đã xảy ra lỗi. Vui lòng thử lại.");
    }
}


// Hàm để đọc cookie
function getCookie(name) {
    let cookieArr = document.cookie.split(";");
    for (let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if (name === cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }
    return null;
}

// Khi trang được tải, kiểm tra token trong cookie và lấy thông tin người dùng
document.addEventListener("DOMContentLoaded", function() {
    const token = getCookie("access_token");  // Lấy token từ cookie
    console.log("Token:", token);
    
    if (token) {
        // Nếu token tồn tại, xóa tiền tố "Bearer " trước khi thêm vào header
        const cleanToken = token.replace("Bearer ", "");
        
        // Gửi yêu cầu để lấy thông tin người dùng
        fetch("/user-info", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${cleanToken}`  // Gửi token xác thực
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.username) {
                // Cập nhật giao diện với thông tin người dùng
                document.getElementById("username-display").textContent = data.username;
                document.getElementById("user-info").style.display = "block";
                document.getElementById("user-info-box").style.display = "none";
            }
        })
        .catch(err => {
            console.error("Có lỗi khi lấy thông tin người dùng", err);
        });
    }
});

// Hàm để xử lý đăng nhập
document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("loginForm");
    
    // Lắng nghe sự kiện submit của form đăng nhập
    loginForm.addEventListener("submit", function(event) {
        event.preventDefault();  // Ngăn chặn hành vi mặc định (submit form)
        
        const formData = new FormData(loginForm);  // Thu thập dữ liệu từ form
        
        // Gửi yêu cầu đăng nhập
        fetch("/login", {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (response.redirected) {
                // Nếu đăng nhập thành công, chuyển hướng về trang chủ
                window.location.href = response.url;
            } else {
                return response.json();  // Nếu không, xử lý lỗi
            }
        })
        .then(data => {
            if (data && data.error) {
                console.error("Có lỗi khi đăng nhập:", data.error);
            }
        })
        .catch(error => {
            console.error("Có lỗi khi đăng nhập", error);
        });
    });
});

// // Xử lý đăng nhập
// async function handleLogin(event) {
//     event.preventDefault();
//     const form = document.getElementById("loginForm");
//     const formData = new FormData(form);

//     try {
//         const response = await fetch('/login', {
//             method: 'POST',
//             body: formData
//         });

//         if (response.ok) {
//             // Nếu đăng nhập thành công, chuyển hướng về trang chủ
//             window.location.href = "/";
//         } else {
//             const result = await response.json();
//             alert(result.error || "Đăng nhập thất bại.");
//         }
//     } catch (error) {
//         console.error("Lỗi:", error);
//         alert("Đã xảy ra lỗi. Vui lòng thử lại.");
//     }
// }

// Xử lý đăng xuất
function logout() {
    // Xóa cookie access_token
    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.href = "/";
}

// Hiển thị popup
function showPopup(type) {
    document.getElementById("popup-box").style.display = "block";
    
    if (type === 'success') {
        document.querySelector(".success").style.display = "block";
    } else if (type === 'invaliduseremail') {
        document.querySelector(".invaliduseremail").style.display = "block";
    }

    // Ẩn popup sau 5 giây
    setTimeout(() => {
        document.getElementById("popup-box").style.display = "none";
        document.querySelector(".success").style.display = "none";
        document.querySelector(".invaliduseremail").style.display = "none";
    }, 5000); 
}