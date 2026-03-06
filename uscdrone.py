import paho.mqtt.client as mqtt
import time
import threading

class UscDrone:
    def __init__(self, ip="192.168.5.104", port=1883, qos=2, username="drone1", password="drone1",
                 cmd_topic="drone/1/pi4/execute", data_topic="drone/1/pi4/data"):
        """初始化 uscdrone 設定"""
        self.ip = ip
        self.port = port
        self.qos = qos
        self.cmd_topic = cmd_topic
        self.data_topic = data_topic
        
        # 儲存即時感測器資料
        self.telemetry = {
            "ATTITUDE": {}, "FLIGHT_STATUS": {}, "BATTERY": {}, "BATTERY_DETAIL": {},    
            "GPS": {}, "GLOBAL_POSITION": {}, "LOCAL_POSITION": {}, "FLIGHT_DATA": {},       
            "ALTITUDE_SOURCES": {}, "DISTANCE_SENSOR": {}, "WIFI": {},              
            "HEARTBEAT_STATUS": {}, "MESSAGE": {}            
        }

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.username_pw_set(username, password)
        self.client.on_message = self._on_message

    def connect(self):
        print(f"[USC Drone] 正在連線至 Broker ({self.ip})...")
        try:
            self.client.connect(self.ip, self.port, 60)
            self.client.subscribe(self.data_topic, qos=self.qos)
            self.client.loop_start() 
            time.sleep(1.5) 
            print(f"[USC Drone] 連線成功！已準備好接收指令。")
        except Exception as e:
            print(f"[USC Drone] 連線失敗: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("[USC Drone] 已斷開連線。")

    def _on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            parts = payload.split(',')
            if len(parts) > 0:
                data_type = parts[0]
                data_dict = {}
                for item in parts[1:]:
                    if '=' in item:
                        k, v = item.split('=', 1)
                        try:
                            data_dict[k] = float(v) 
                        except ValueError:
                            data_dict[k] = v 
                self.telemetry[data_type] = data_dict
        except Exception:
            pass 

    def _send(self, cmd_string):
        formatted_cmd = f"({cmd_string})"
        self.client.publish(self.cmd_topic, formatted_cmd, qos=self.qos)

    # ==========================================
    # ✈️ 飛行控制指令 (含自動智慧等待邏輯)
    # ==========================================
    
    def change_mode(self, mode_name):
        self._send(f"mode:{mode_name}")
        print(f"[USC Drone] 請求切換至 {mode_name} 模式，等待 2 秒確保系統確認...")
        time.sleep(2)

    def take_off(self, altitude):
        self._send(f"take_off:{altitude}")
        # 估算起飛時間：高度 / (假設爬升速度 2m/s) + 3秒緩衝
        wait_t = (altitude / 2.0) + 3.0
        print(f"[USC Drone] 發比起飛指令 ({altitude}m)，自動等待 {wait_t:.1f} 秒讓無人機到位...")
        time.sleep(wait_t)

    def _move_with_wait(self, action, distance):
        """內部共用移動方法，自動計算等待時間"""
        self._send(f"{action}:{distance}")
        # 估算移動時間：距離 / (假設水平速度 2m/s) + 2秒緩衝
        wait_t = (distance / 2.0) + 2.0
        direction_tw = action.replace("move_", "").replace("forward", "向前").replace("backward", "向後").replace("left", "向左").replace("right", "向右").replace("up", "向上").replace("down", "向下")
        print(f"[USC Drone] {direction_tw}移動 {distance} 公尺，自動等待 {wait_t:.1f} 秒...")
        time.sleep(wait_t)

    def move_forward(self, distance): self._move_with_wait("move_forward", distance)
    def move_backward(self, distance): self._move_with_wait("move_backward", distance)
    def move_left(self, distance): self._move_with_wait("move_left", distance)
    def move_right(self, distance): self._move_with_wait("move_right", distance)
    def move_up(self, distance): self._move_with_wait("move_up", distance)
    def move_down(self, distance): self._move_with_wait("move_down", distance)

    def _yaw_with_wait(self, action, angle):
        """內部共用旋轉方法，自動計算等待時間"""
        self._send(f"{action}:{angle}")
        # 估算旋轉時間：角度 / (假設旋轉速度 30度/s) + 1.5秒緩衝
        wait_t = (angle / 30.0) + 1.5
        dir_str = "向左" if "left" in action else "向右"
        print(f"[USC Drone] 機頭{dir_str}偏航 {angle} 度，自動等待 {wait_t:.1f} 秒...")
        time.sleep(wait_t)

    def yaw_left(self, angle): self._yaw_with_wait("yaw_left", angle)
    def yaw_right(self, angle): self._yaw_with_wait("yaw_right", angle)

    def set_servo(self, angle):
        self._send(f"servo:{angle}")
        print(f"[USC Drone] 觸發伺服馬達至 {angle} 度，等待 1 秒...")
        time.sleep(1)

    def wait(self, seconds):
        """讓學生可以手動要求程式額外暫停"""
        print(f"[USC Drone] 手動懸停等待 {seconds} 秒...")
        time.sleep(seconds)

    # ==========================================
    # 📊 資料讀取指令 (保持不變)
    # ==========================================
    def get_status(self): return self.telemetry.get("FLIGHT_STATUS", {})
    def get_attitude(self): return self.telemetry.get("ATTITUDE", {})
    def get_battery(self): return self.telemetry.get("BATTERY_DETAIL", {})
    def get_location(self): return self.telemetry.get("GLOBAL_POSITION", {})
    def get_speed(self): return self.telemetry.get("FLIGHT_DATA", {})
    def get_distance_sensor(self): return self.telemetry.get("DISTANCE_SENSOR", {})
    def get_wifi_rssi(self):
        return self.telemetry.get("WIFI", {}).get("rssi", -99)