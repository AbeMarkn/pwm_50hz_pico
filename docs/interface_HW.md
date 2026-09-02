# ハードウェア インターフェース設計

## 1. ピン配置

| 設計ID | Raspberry Pi Pico端子 | 方向 | 接続先 | 電気設定 | 論理・用途 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| DESN-HW-001 | GP0 | 出力 | PWM接続先 | 3.3 V CMOS、PWM | 50 Hz、0～100% |
| DESN-HW-002 | GP1 | 入力 | DIP bit 0 | 内部プルアップ | ON=Low、重み1 |
| DESN-HW-002 | GP2 | 入力 | DIP bit 1 | 内部プルアップ | ON=Low、重み2 |
| DESN-HW-002 | GP3 | 入力 | DIP bit 2 | 内部プルアップ | ON=Low、重み4 |
| DESN-HW-002 | GP4 | 入力 | DIP bit 3 | 内部プルアップ | ON=Low、重み8 |
| DESN-HW-003 | GP25 | 出力 | Raspberry Pi Pico内蔵LED | GPIO出力 | High=点灯、Low=消灯 |
| DESN-HW-002 | GND | 電源 | DIP共通端子 | 0 V | 各スイッチON時に対応入力へ接続 |

Raspberry Pi Picoの内蔵LEDはGP25へ接続されているため、ファームウェアではGPIO番号`25`を指定する。

## 2. インターフェース一覧

| インターフェース | 使用 | 設計内容 |
| :--- | :---: | :--- |
| GPIO | 使用 | GP1～GP4のDIP入力、内蔵LED制御 |
| PWM | 使用 | GP0から50 Hzを出力 |
| USB | 使用 | 給電、MicroPython書込み、`mpremote`によるファイル転送、REPL |
| UART | 不使用 | 本機能では使用しない |
| I2C | 不使用 | 本機能では使用しない |
| SPI | 不使用 | 本機能では使用しない |
| ADC | 不使用 | 本機能では使用しない |
| CAN | 不使用 | Raspberry Pi Picoに標準CANコントローラはなく、本機能でも使用しない |
| Ethernet | 不使用 | 本機能では使用しない |
| Wi-Fi | 不使用 | Raspberry Pi Picoは搭載しない |
| Bluetooth | 不使用 | Raspberry Pi Picoは搭載しない |

## 3. 電気的制約

- GP0にはオシロスコープ等の計測機器だけを接続し、モータ等の負荷を接続しない。
- DIPスイッチは起動時に1回だけ読み取り、チャタリング対策を行わない。
- USBから給電し、電池および充電回路を使用しない。
- 試作品のため、過電圧、過電流および逆接に対する追加保護回路を設けない。
- 使用するUSB給電元と計測機器は、それぞれの機器の定格および取扱説明に従う。
