const OA_LINK = "https://lin.ee/RRW07VV";
const share_link = "https://liff.line.me/1657167128-RMEY8X7b/music";
const liffId = "1657167128-RMEY8X7b";
const url_user = "https://linefresh-bot.herokuapp.com/liff/user";
const url_update = "https://linefresh-bot.herokuapp.com/liff/update";
var profile;
var singer_list;
var singer_count;

async function main() {
    // init liff
    if (!liff.isInClient()) return alert("請用手機版 LINE 開啟網頁");
    await liff.init({ liffId: liffId });
    profile = await liff.getProfile();

    // output html
    singer_list = await(await fetchData(`${url_user}/singer`, { "user_id": profile.userId })).singer_list;

    console.log(singer_list)
    if (!singer_list) singer_list = [];
    singer_count = singer_list.length

    console.log(singer_list);

    document.getElementById("js-progressbar").value = (singer_count % 2) * 50;
    document.getElementById("progress").innerText = `${(singer_count % 2) * 50}%`;

    document.getElementById("nav2").addEventListener('click', () => {window.location = "https://linefresh-bot.herokuapp.com/liff/live";});
    document.getElementById("share_song_list").addEventListener('click', share_song_list);
    // TODO loop through singers' btn
    document.getElementById("singer_btn_1").addEventListener('click', singer_info);
    document.getElementById("singer_btn_2").addEventListener('click', singer_info);
    document.getElementById("singer_btn_3").addEventListener('click', singer_info);
    document.getElementById("singer_btn_4").addEventListener('click', singer_info);
    document.getElementById("singer_btn_5").addEventListener('click', singer_info);
    document.getElementById("singer_btn_6").addEventListener('click', singer_info);
    document.getElementById("singer_btn_7").addEventListener('click', singer_info);
    document.getElementById("singer_btn_8").addEventListener('click', singer_info);
    document.getElementById("singer_btn_9").addEventListener('click', singer_info);
    document.getElementById("singer_btn_10").addEventListener('click', singer_info);
}

async function fetchData(url, data) {
    result = await fetch(url, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return result.json();
}

async function share_song_list() {
    r = await liff.shareTargetPicker([{ type: "text", text: `${profile.displayName} 分享了連結，快來看看吧！\n${share_link}` }]);
    if (!r) return

    result = await fetchData(url_update, { "user_id": profile.userId, "task_name": "share_song_list", "detail": "" });
    if (result.updated) return alert("分享完成！");
    else return alert("今天已經分享過囉！");
}

async function singer_info(e) {
    singer_val = e.currentTarget.value;
    console.log(singer_val)
    if (!singer_list.includes(singer_val)) {
        result = await fetchData(url_update, { "user_id": profile.userId, "task_name": "singer_info", "detail": singer_val });
        console.log(result.updated);
    }
    console.log("redirect");
    window.location = `https://linefresh-bot.herokuapp.com/liff/singer/singer-${singer_val}`;
}

main();