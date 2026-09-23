"""登录 + 详细诊断"""
import os, time
from playwright.sync_api import sync_playwright

# 路径全部用 raw string
WORK = r"C:\Users\shenghua\Desktop\新建文件夹"
CHROME = r"C:\Users\shenghua\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe"
SCREEN_DIR = WORK

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=False, slow_mo=300)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    # 监听所有响应（必须在 goto 之前注册）
    api_responses = []
    responses_with_body = []
    def on_response(resp):
        try:
            if "baovbao" in resp.url and resp.url.startswith("http"):
                api_responses.append({"url": resp.url, "status": resp.status, "method": resp.request.method})
                if ("/Login/" in resp.url or "adminLogin" in resp.url or "captcha" in resp.url):
                    try:
                        body = resp.text()
                        responses_with_body.append({"url": resp.url, "status": resp.status, "body": body[:1500]})
                    except Exception:
                        pass
        except Exception:
            pass
    page.on("response", on_response)

    print("→ 打开登录页")
    page.goto("https://mall.baovbao.com/admin/index.html", wait_until="networkidle", timeout=60000)
    time.sleep(2)

    # 抓验证码算式
    captcha = page.evaluate("""
        () => {
            const all = document.querySelectorAll('*');
            for (const el of all) {
                if (el.children.length === 0) {
                    const t = (el.innerText || '').trim();
                    if (/^\\d+\\s*\\+\\s*\\d+\\s*=\\s*\\?$/.test(t)) return t;
                }
            }
            return null;
        }
    """)
    print("  验证码算式:", captcha)
    answer = None
    if captcha:
        m = captcha.replace(" ", "").replace("?", "").split("+")
        if len(m) == 2 and m[0].isdigit() and m[1].isdigit():
            answer = str(int(m[0]) + int(m[1]))
    if not answer:
        # 抓不到算式时，看看 captcha API 返回的 cookie 或 session
        answer = "0"
    print("  算式答案:", answer)

    # 填表单
    page.fill("input[placeholder='请输入账号名称']", "18557207352")
    page.fill("input[placeholder='请输入账号登录密码']", "abc123456")
    page.fill("input[placeholder='请输入验证码']", answer)

    # 点击登录
    print("→ 点击登录")
    clicked = page.evaluate("""
        () => {
            const all = document.querySelectorAll('button, span, div, a');
            for (const el of all) {
                const t = (el.innerText || '').replace(/\\s+/g, '');
                if (t === '立即登录' && el.tagName === 'BUTTON') { el.click(); return 'clicked'; }
            }
            return 'not-found';
        }
    """)
    print("  ", clicked)
    time.sleep(8)

    print("URL:", page.url)
    try:
        page.screenshot(path=os.path.join(SCREEN_DIR, "_p2_after_login.png"), full_page=True)
    except Exception as e:
        print("  screenshot err:", e)

    text = page.evaluate("document.body.innerText")
    print("--- body text (前 1500 字符) ---")
    print(text[:1500])

    print("\n--- API 响应 /api/ ---")
    for r in responses_with_body:
        print(f"  [{r['status']}] {r['url']}")
        print(f"      {r['body'][:400]}")

    print("\n--- 所有 baovbao 域响应 ---")
    seen = set()
    for r in api_responses:
        if r['url'] not in seen:
            print(f"  [{r['status']}] {r['method']} {r['url']}")
            seen.add(r['url'])

    browser.close()
print("done.")
