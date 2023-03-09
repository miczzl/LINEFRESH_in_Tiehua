const liffId = "1657167128-RMEY8X7b";
const url_user = "https://linefresh-bot.herokuapp.com/liff/user";
const url_raffle = "https://linefresh-bot.herokuapp.com/liff/raffle";
const url_push_message = "https://linefresh-bot.herokuapp.com/liff/push_message";
var profile;
var raffle_num;

async function main() {
    // init liff
    if (!liff.isInClient()) return alert("請用手機版 LINE 開啟網頁");
    await liff.init({ liffId: liffId });
    profile = await liff.getProfile();

    raffle_num = await (await fetchData(`${url_user}/raffle`, { "user_id": profile.userId })).raffle_num;

    // output html
    $("nav").on('click', '#nav2', () => { window.location = "https://linefresh-bot.herokuapp.com/liff/coupon"; });
    $('#modal_btn').click(() => { window.location.reload(); });
    document.getElementById("num_of_coupon").innerText = raffle_num;
    document.getElementById("remain_raffle_num").innerText = raffle_num;
    document.getElementById("spin").addEventListener('click', raffle);
}

async function fetchData(url, data) {
    result = await fetch(url, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return result.json();
}

async function raffle() {
    if (raffle_num == 0) return alert("快去完成任務，獲得抽獎機會吧！");

    document.getElementById("spin").removeEventListener('click', raffle);
    result = await fetchData(url_raffle, { "user_id": profile.userId });
    if (result.updated) {
        document.getElementById("num_of_coupon").innerText = raffle_num - 1;
        document.getElementById("remain_raffle_num").innerHTML = `還剩餘 <b> ${raffle_num - 1} </b> 次抽獎機會`;
        return spin(result.coupon_name, result.spin_deg, result.detail);
    }
}

// TODO change spin
function spin(coupon_name, spin_deg, detail) {
    if (coupon_name == "line_point") {
        document.getElementById("result_coupon_name").innerText = `恭喜你抽中 LINE POINTS 點數！\n點擊官方帳號推播的訊息連結領取吧～`;
    } else {
        document.getElementById("result_coupon_name").innerText = `「${coupon_name}！」`;
    }

    console.log("Rotate" + spin_deg);

    document.querySelector(".container1").style.transform = "rotate(" + spin_deg + "deg)";
    setTimeout(function () {
        $('#modal').css('display', 'flex');
        if (coupon_name == "line_point") fetchData(url_push_message, { "user_id": profile.userId, "guid": detail });
    }, 4500);

}

main();