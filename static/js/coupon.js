const liffId = "1657167128-RMEY8X7b";
const url_user = "https://linefresh-bot.herokuapp.com/liff/user";
const url_update = "https://linefresh-bot.herokuapp.com/liff/update";
var profile;
var coupon_list;

async function main() {
    // // init liff
    if (!liff.isInClient()) return alert("請用手機版 LINE 開啟網頁");
    await liff.init({ liffId: liffId });
    profile = await liff.getProfile();

    // output html
    $("nav").on('click', '#nav1', () => { window.location = "https://linefresh-bot.herokuapp.com/liff/spin"; });
    coupons = await fetchData(`${url_user}/coupon`, { "user_id": profile.userId });

    available = document.getElementById("available");
    for (let coupon of coupons.available_coupon) {
        c = createAvailableCoupon(coupon.id, coupon.img);
        available.appendChild(c);
    }
    used_coupon = document.getElementById("used_coupon");
    for (let coupon of coupons.used_coupon) {
        c = createInavailableCoupon(coupon.id, coupon.img, "已使用");
        used_coupon.appendChild(c);
    }
    no_remain = document.getElementById("no_remain");
    for (let coupon of coupons.no_remain) {
        c = createInavailableCoupon(coupon.id, coupon.img, "已兌換完畢");
        no_remain.appendChild(c);
    }
}

async function fetchData(url, data) {
    result = await fetch(url, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return result.json();
}

function createAvailableCoupon(coupon_id, img_src) {
    c = document.createElement("div");
    c.className = "coupon";
    c.id = coupon_id;
    c.innerHTML = `
    <span class="redeem-progress">此優惠券還剩下 ${10} 張🔥</span>
    <a href="https://linefresh-bot.herokuapp.com/liff/coupon_1?id=${coupon_id}">
        <div class="coupon-img text-center" style="background-image: url('../static/img/coupon/${"LINE_ALBUM_220624_1.jpg"}');">
        </div>
    </a>`;
    return c;
}

function createInavailableCoupon(coupon_id, img_src, status) {
    c = document.createElement("div");
    c.className = "coupon";
    c.id = coupon_id;
    c.innerHTML = `
    <span class="redeem-progress"></span>
    <div class="coupon-img text-center" style="background-image: url('../static/img/coupon/${"LINE_ALBUM_220624_7.jpg"}');">
        <div class="hover-on-img">${status}</div>
    </div>`;
    return c;
}

main();