fetch("/api/weather/latest")
  .then(response => response.json())
  .then(result => {
    console.log("API 回傳資料：", result);

    const container = document.getElementById("latest-weather");

    if (result.status === "success") {
      let html = "";

      result.data.forEach(item => {
        html += `
          <div style="border:1px solid #ccc; margin:10px; padding:10px;">
            <p><strong>城市：</strong>${item.location_name}</p>
            <p><strong>時間：</strong>${item.recorded_at}</p>
            <p><strong>溫度：</strong>${item.temperature_celsius} °C</p>
            <p><strong>濕度：</strong>${item.humidity} %</p>
          </div>
        `;
      });

      container.innerHTML = html;
    } else {
      container.innerHTML = `<p>資料讀取失敗：${result.message}</p>`;
    }
  })
  .catch(error => {
    console.error("API 錯誤:", error);
    document.getElementById("latest-weather").innerHTML = "<p>發生錯誤，無法載入資料。</p>";
  });