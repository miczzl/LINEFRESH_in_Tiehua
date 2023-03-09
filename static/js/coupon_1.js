const liffId = "1657167128-RMEY8X7b";
const url_user = "https://linefresh-bot.herokuapp.com/liff/user";
const url_check_coupon = "https://linefresh-bot.herokuapp.com/liff/check_coupon";
const url_verify = "https://linefresh-bot.herokuapp.com/liff/verify";
var profile;
var coupon_id;

async function main() {
    // init liff
    if (!liff.isInClient()) return alert("請用手機版 LINE 開啟網頁");
    await liff.init({ liffId: liffId });
    profile = await liff.getProfile();

    // found logo
    coupon_id = new URLSearchParams(window.location.search).get('id');
    if (!coupon_id) return;
    if (!await check_coupon()) return;

    // output html
    document.getElementById("redeem-btn").addEventListener('click', verify_coupon);
}

async function fetchData(url, data) {
    result = await fetch(url, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return result.json();
}

async function check_coupon() {
    result = await fetchData(url_check_coupon, { "id": coupon_id, "user_id": profile.userId });
    if (!result.result) return false;

    if (result.desc) {
        document.getElementById("desc").innerHTML = result.desc;
    }
    if (result.notice) {
        document.getElementById("notice-text").innerHTML = result.notice;
    }
    console.log("update desc & notice");
    return true;
}

async function verify_coupon() {
    var confirm = window.confirm('確定兌換此優惠券？（請交由店員核銷）');
    if (!confirm) return

    result = await fetchData(url_verify, { "id": coupon_id, "user_id": profile.userId });
    if (result.result) {
        alert("兌換成功！");
        document.getElementById("redeem-btn").removeEventListener('click', verify_coupon);
        document.getElementById("redeem-btn").innerHTML = "已&emsp;兌&emsp;換";
        document.getElementById("redeem-btn").style.backgroundColor = "#c3aa41";
    }
}

main();