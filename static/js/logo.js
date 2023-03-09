const liffId = "1657167128-RMEY8X7b";
const url_user = "https://linefresh-bot.herokuapp.com/liff/user";
const url_update = "https://linefresh-bot.herokuapp.com/liff/update";
var profile;
var logo_list;
var logo_count;

const dict = {
    "709515534097453956": "鷗咖啡",
    "486251073846121999": "烤大爺",
    "456601103492978868": "九湯屋",
    "751219810968302955": "東東市",
    "763479858557753605": "購夠台東",
    "486259086518654761": "GAYA",
    "559436735390423911": "門廷若室 鐵花秀泰館",
    "486259068957103674": "南豐鐵花棧",
    "707009872612300234": "時光車站",
    "656248336109542165": "六吋盤 早午餐",
    "508744347441697919": "多那之烘焙",
    "763456598134755967": "六扇門 時尚湯鍋",
    "486247031019411330": "客來吃樂",
    "547169009087290975": "蔬念 Vegine",
    "767896838429745071": "青澤伴手禮 鐵花館",
    "486251028371477386": "青澤伴手禮 正氣一店",
    "439005353038726604": "青澤伴手禮 正氣二店",
    "486259086564792106": "旅人驛站 鐵花文創館",
    "575384972458738796": "旅人驛站 日暮微旅",
    "486259092302600073": "台東桂田 喜來登酒店",
    "486248109765038421": "花惹蜜",
};

async function main() {
    // init liff
    if (!liff.isInClient()) return alert("請用手機版 LINE 開啟網頁");
    await liff.init({ liffId: liffId });
    profile = await liff.getProfile();

    // found logo
    await logo_hunt();

    // output html
    logo_list = await(await fetchData(`${url_user}/logo`, { "user_id": profile.userId })).logo_list;
    logo_count = logo_list.length;
    console.log(logo_list);

    document.getElementById("logo_count").innerText = logo_count.toString().padStart(2, '0');

    c0 = document.getElementById("c0");
    c1 = document.getElementById("c1");
    document.getElementById("label0").innerText = `尚未完成尋寶的店家 (${Object.keys(dict).length - logo_count})`;
    document.getElementById("label1").innerText = `已完成尋寶的店家 (${logo_count})`;

    for (let key in dict) {
        if (key == "439005353038726604") {
            s = ching2();
        } else {
            s = createShop(key, dict[key]);
        }
        if (logo_list.includes(key)) {c1.appendChild(s);
        } else {c0.appendChild(s);}
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

async function logo_hunt() {
    const shop_id = new URLSearchParams(window.location.search).get('id');
    if (!shop_id) return;
    if (!(shop_id in dict)) return alert("wrong id");

    result = await fetchData(url_update, { "user_id": profile.userId, "task_name": "logo_hunt", "detail": shop_id });
    if (!result.updated) return alert("已經找過了喔");

    // change to div
    alert(`恭喜你找到 ${dict[shop_id]}！`);
    window.location = window.location.pathname;
}

function createShop(shop_id, shop_name) {
    s = document.createElement("a");
    s.href = `https://spot.line.me/detail/${shop_id}`;
    s.innerHTML = `<div class="shop-icon" id="${shop_id}">
        <div class="uk-card uk-card-hover">
            <div class="uk-card-media-top uk-flex uk-flex-center">
                <img class="uk-border-circle" src="../static/img/shop_logo/${shop_name}.png" alt="">
            </div>
            <div class="uk-card-title uk-text-center">
                <label class="shop-name">${shop_name.replace(" ", "<br>")}</label>
            </div>
        </div>
    </div>`;
    return s;
}

function ching2() {
    s = document.createElement("a");
    s.href = `https://spot.line.me/detail/486251028371477386`;
    s.innerHTML = `<div class="shop-icon" id="439005353038726604">
        <div class="uk-card uk-card-hover">
            <div class="uk-card-media-top uk-flex uk-flex-center">
                <img class="uk-border-circle" src="../static/img/shop_logo/青澤伴手禮 正氣一店.png" alt="">
            </div>
            <div class="uk-card-title uk-text-center">
                <label class="shop-name">青澤伴手禮<br>正氣二店</label>
            </div>
        </div>
    </div>`;
    return s;
}

main();