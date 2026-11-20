from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["auth-test"])

_PAGE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VN101 Firebase Auth Check</title>
<style>
body{font:16px system-ui,sans-serif;max-width:560px;margin:40px auto;padding:0 18px;color:#172033}
input,button{box-sizing:border-box;width:100%;padding:12px;margin:7px 0;border:1px solid #ccd3df;border-radius:8px;font:inherit}
button{background:#1d4ed8;color:white;border:0;font-weight:600}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f8;padding:14px;border-radius:8px}
small{color:#596579}
</style></head><body>
<h2>Kiểm tra đăng nhập VN101 AI Office</h2>
<p>Trang này đăng nhập trực tiếp với Firebase. Mật khẩu không được gửi đến máy chủ VN101.</p>
<form id="login">
<label>Email Firebase</label><input id="email" type="email" autocomplete="username" required>
<label>Mật khẩu Firebase</label><input id="password" type="password" autocomplete="current-password" required>
<button id="submit" type="submit">Đăng nhập và kiểm tra quyền</button>
</form>
<small>ID Token chỉ được giữ tạm trong bộ nhớ trình duyệt, gửi qua HTTPS đến API rồi bị xóa khi đăng xuất.</small>
<pre id="result">Đang chờ đăng nhập…</pre>
<script type="module">
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.2/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/11.0.2/firebase-auth.js";
const firebaseConfig = {
  apiKey: "AIzaSyBuBwadxGSIcoVoyxeo7NgMCD9hnZ1w5RE",
  authDomain: "vn101-ai-office.firebaseapp.com",
  projectId: "vn101-ai-office",
  storageBucket: "vn101-ai-office.firebasestorage.app",
  messagingSenderId: "320342680959",
  appId: "1:320342680959:web:5222cffbe859b80e9ae64a"
};
const auth = getAuth(initializeApp(firebaseConfig));
const form = document.querySelector("#login");
const result = document.querySelector("#result");
const button = document.querySelector("#submit");
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  button.disabled = true;
  result.textContent = "Đang xác thực với Firebase…";
  let credential;
  try {
    credential = await signInWithEmailAndPassword(auth,
      document.querySelector("#email").value.trim(),
      document.querySelector("#password").value);
    const idToken = await credential.user.getIdToken(true);
    result.textContent = "Firebase đăng nhập thành công. Đang kiểm tra API…";
    const response = await fetch("/api/v1/users/me", {
      headers: { Authorization: "Bearer " + idToken }
    });
    const payload = await response.json();
    if (!response.ok) throw new Error("API HTTP " + response.status + ": " + (payload.detail || JSON.stringify(payload)));
    result.textContent = JSON.stringify({
      api_status: response.status,
      firebase_uid: payload.firebase_uid,
      email: payload.email,
      email_verified: payload.email_verified,
      role: payload.role,
      owner_check: payload.role === "owner" ? "PASS — tài khoản có quyền owner" : "FAIL — chưa nhận quyền owner"
    }, null, 2);
  } catch (error) {
    result.textContent = "KIỂM TRA THẤT BẠI\n" + (error?.message || String(error));
  } finally {
    if (credential) await signOut(auth).catch(() => {});
    button.disabled = false;
  }
});
</script></body></html>"""

@router.get("/auth-test", include_in_schema=False, response_class=HTMLResponse)
async def firebase_auth_test() -> HTMLResponse:
    return HTMLResponse(_PAGE)
