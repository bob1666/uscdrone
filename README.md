# uscdrone 🚁

**uscdrone** 是一個專為無人機程式教學設計的 Python 函式庫（源自實踐大學資通系的教學實作）。
它將底層複雜的 MQTT 通訊與 MAVLink 封包完美封裝，讓 Python 初學者與學生能夠以最直覺、最簡單的英文指令來撰寫無人機自動飛行腳本。

## ✨ 核心特色 (Features)

* **🎯 極簡 API**：告別複雜的通訊協定，只需呼叫 `take_off(5)` 或 `move_forward(3)` 即可控制飛行。
* **⏳ 智慧等待 (Auto-Wait) 防呆機制**：內建距離與角度的物理時間估算。發送移動指令後，程式會自動暫停等待無人機飛到定位，徹底解決「瞬間塞爆飛控通訊埠 (Multiple access on port)」的致命當機問題。
* **📊 即時遙測 (Telemetry)**：在背景自動更新無人機的姿態、GPS、電池與 WiFi 訊號，隨時可用 `get_status()` 等指令安全讀取。
* **🧑‍🤝‍🧑 多機陣列支援**：支援自訂 MQTT Topic，方便多組學生在同一堂課、同一個網域下同時操作多台無人機（例如 1 號機、2 號機）而不互相干擾。

---

## 📦 安裝與使用方式 (Installation)

目前為輕量化教學版本，無需透過 pip 安裝：

1. 點擊本專案上方的 **Code** -> **Download ZIP** 下載檔案。
2. 將解壓縮後的 `uscdrone.py` 檔案，放到你準備撰寫程式的**同一個資料夾**內。
3. 在你的 Python 檔案開頭引入：
   ```python
   from uscdrone import UscDrone


