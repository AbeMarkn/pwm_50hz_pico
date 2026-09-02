# PWM出力

文書バージョン: v1.0.0（正式初版）

> Raspberry Pi Picoで基本動作を実機確認済みです。製品用ファームウェアと実機なし自動テストを実装しています。

## 利用者向け

### 概要

Raspberry Pi Picoの電源投入時に内蔵LED、4極ディップスイッチおよびPWM出力を初期化します。初期化成功後、内蔵LEDを0.5秒点灯して消灯し、1秒待機します。その後にディップスイッチの設定を読み取り、設定値を内蔵LEDの点滅回数で通知します。通知完了後に1秒待機してから、GP0から50 HzのPWMを出力します。PWM出力中は内蔵LEDを点灯し、停止時はPWM出力を0%にして内蔵LEDを消灯します。

設定値0～10はデューティ比0～100%へ10%刻みで対応します。設定値11～15は異常値として扱い、値と同じ回数のLED通知後、出力を0%に固定します。

### 必要環境

- Raspberry Pi Pico
- 4極ディップスイッチ
- Raspberry Pi Picoへ給電できるUSB電源
- GP0の3.3 V系PWM信号を測定できるオシロスコープ等の計測機器
- Raspberry Pi Pico対応MicroPythonファームウェアと本プロジェクトのファームウェア

本装置は屋内用の試作品です。電池、充電回路、追加保護回路およびモータ等の負荷は使用しません。最大連続運転時間は24時間です。

### ディップスイッチ設定

各スイッチはONで対応入力をGNDへ接続します。

| スイッチ入力 | 重み | ON時 |
| :--- | :---: | :--- |
| GP1 | 1 | 設定値へ1を加算 |
| GP2 | 2 | 設定値へ2を加算 |
| GP3 | 4 | 設定値へ4を加算 |
| GP4 | 8 | 設定値へ8を加算 |

| 設定値 | LED点滅回数 | PWMデューティ比 |
| :---: | :---: | :---: |
| 0 | 0回 | 0% |
| 1 | 1回 | 10% |
| 2 | 2回 | 20% |
| 3 | 3回 | 30% |
| 4 | 4回 | 40% |
| 5 | 5回 | 50% |
| 6 | 6回 | 60% |
| 7 | 7回 | 70% |
| 8 | 8回 | 80% |
| 9 | 9回 | 90% |
| 10 | 10回 | 100% |
| 11～15 | 設定値と同じ回数 | 0%（異常設定） |

### 使い方

1. 電源を切った状態でディップスイッチを目的の設定値に合わせます。
2. GP0の接続先とGNDを正しく接続します。
3. Raspberry Pi Picoへ電源を投入します。
4. 内蔵LEDが0.5秒点灯して消灯し、1秒待機することを確認します。
5. 内蔵LEDの点滅回数が設定値と一致することを確認します。点灯0.25秒と消灯0.25秒で1周期です。
6. LED通知完了後に1秒待機します。その後、内蔵LEDが点灯し、GP0から選択したデューティ比の50 Hz PWMが継続して出力されます。PWM出力中はREPLへ戻りません。
7. 停止するときは`Ctrl+C`を入力します。PWM出力は0%になり、内蔵LEDは消灯します。
7. 設定を変更する場合は、電源を切ってスイッチを変更し、再度電源を投入します。

### 注意事項

- 動作中にディップスイッチを変更しても出力へ反映されません。
- 設定値11～15は異常設定であり、PWM出力は0%になります。
- GP0へ5 Vを印加しないでください。オシロスコープ等の計測機器だけを接続し、モータ等の負荷を接続しないでください。
- USBから給電し、屋内の管理された試作環境で使用してください。
- 試作品のため、過電圧、過電流および逆接に対する追加保護回路はありません。
- 連続運転は24時間以内としてください。
- 100%設定ではPWMを使用せず、GP0を約3.3 Vの固定High出力にします。接続先が想定する「PWM 100%」の電気的意味を確認してください。

## 開発者向け

### 開発概要

MicroPythonでRaspberry Pi Picoの起動処理、ディップスイッチ読取り、LED通知、PWM設定を実装しています。要求、設計、インターフェース、テストは次の文書で管理します。

- [仕様書](docs/Specification.md)
- [設計書](docs/Design.md)
- [ハードウェアインターフェース](docs/interface_HW.md)
- [ソフトウェアインターフェース](docs/interface_SW.md)
- [テスト文書](docs/test/Traceability_Matrix.md)
- [未決事項](docs/open_item.md)

### 開発環境

- Raspberry Pi Pico
- Raspberry Pi Pico対応MicroPython。版は固定しない。
- Python 3と`mpremote`
- VS CodeとMicroPico拡張、または同等のファイル転送・REPL環境
- 実機なしテスト用のpytest
- 静的解析・整形用のRuff

ツールの版は固定せず、テスト実施時の版を結果ファイルへ記録します。

### セットアップ

1. Raspberry Pi PicoのBOOTSELボタンを押しながらUSB接続します。
2. Raspberry Pi Pico対応MicroPython UF2をUSBマスストレージへ書き込みます。
3. 再接続後、REPLへ接続できることを確認します。
4. ホスト側に仮想環境を作り、依存関係を導入します。

```console
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

実機なしテストにはpytestとRuff、Raspberry Pi Picoへの転送にはmpremoteを使用します。

### ビルド方法

MicroPythonソースに専用コンパイル工程はありません。ホスト側で次の静的解析を通過したソースを配置対象とします。

```console
.venv/bin/python -m ruff check main.py pwm_controller.py tests
```

### Flash方法

MicroPython本体はBOOTSELモードでUF2を書き込みます。次のアプリケーションファイルをRaspberry Pi Picoへ転送します。

```text
main.py
pwm_controller.py
```

転送にはMicroPicoまたは次の`mpremote`コマンドを使用します。

```console
.venv/bin/python -m mpremote fs cp pwm_controller.py :pwm_controller.py
.venv/bin/python -m mpremote fs cp main.py :main.py
.venv/bin/python -m mpremote reset
```

### 起動方法

Raspberry Pi Picoへ電源を投入するかソフトリセットすると、MicroPythonが`main.py`を自動実行します。USB REPLからのソフトリセットは`Ctrl+D`です。

### CLIオプション

運用時のCLIオプションはありません。設定は起動前のディップスイッチで行います。

### 設定ファイル

設定ファイルは使用しません。永続設定も保存しません。

### ログ

試作品のため永続ログは実装しません。未処理例外は開発時のUSB REPLへ表示します。

### デバッグ方法

- USB REPLで例外とスタックトレースを確認します。
- GP0はオシロスコープまたはロジックアナライザで周波数とデューティ比を測定します。
- GP1～GP4はREPL上の診断またはテスト用ファームウェアで論理値を確認します。
- 異常時はGP0が0%、内蔵LEDが消灯していることを最初に確認します。

### テスト実行方法

実機なし自動テストは次のコマンドで実行します。その後、テスト文書に従って実機あり自動テスト、実機あり手動テストの順に実施します。

```console
.venv/bin/python -m pytest -q
```

- [仕様テスト（正常系）](docs/test/Test_for_Specification.md)
- [仕様テスト（正常系以外）](docs/test/Test_for_Specification_non_normal.md)
- [設計テスト（正常系）](docs/test/Test_for_Design.md)
- [設計テスト（正常系以外）](docs/test/Test_for_Design_non_normal.md)

実施結果は[結果テンプレート](docs/test/results/TEST-SPEC_result_template.md)の項目を用い、Test IDごと、実施回ごとの連番ファイルへ記録します。未実施の試験にPass / Failを記録しません。

### Firmware更新方法

1. 対象版の仕様、設計、決定事項、テスト結果を確認します。
2. 更新前のGit commit IDとFirmware Versionを記録します。
3. 製品用ファイルをRaspberry Pi Picoへ転送します。
4. ソフトリセットまたは電源再投入を行います。
5. LED通知とPWM出力の受入試験を実施し、結果を記録します。

### バージョニング

Semantic Versioningの`X.Y.Z`を使用し、GitコミットはConventional Commitsに従います。

| 変更 | 接頭語 | 更新 |
| :--- | :--- | :--- |
| 非互換変更、正式な初版 | `feat!:`または`BREAKING CHANGE:` | Major |
| 後方互換の新機能 | `feat:` | Minor |
| バグ修正 | `fix:` | Patch |
| 文書、テスト、設定、整理 | `docs:`、`test:`、`chore:`、`refactor:`、`style:` | Patch |

v1.0.0は、基本機能、実機なし自動テスト、およびRaspberry Pi Picoでの基本動作確認を完了した最初の正式版です。割り当て済みの仕様・設計・テストIDは文書更新時も再利用しません。

### トラブルシューティング

| 症状 | 確認事項 |
| :--- | :--- |
| LEDが点滅しない | 設定値0では正常です。電源、MicroPython、`main.py`配置を確認します。 |
| 点滅回数が違う | DIPのONがGND接続になっていること、GP1～GP4のビット重みを確認します。 |
| PWMが0%になる | 設定値0または11～15でないか確認します。 |
| PWM周波数が違う | MicroPython版、GP0設定、測定器の入力条件を確認します。 |
| 設定変更が反映されない | 仕様どおり起動時だけ読み取ります。電源再投入またはソフトリセットを行います。 |
| REPLへ接続できない | USBケーブルのデータ通信対応、シリアルポート、MicroPython書込み状態を確認します。 |
# pwm_50hz
