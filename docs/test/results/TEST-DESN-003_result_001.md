# TEST-DESN-003 テスト結果 001

| 項目 | 記録内容 |
| :--- | :--- |
| Test ID | TEST-DESN-003 |
| 実施日時 | 2026-09-02 10:36:13 JST |
| Firmware Version | v0.2.0 |
| Hardware Version | 実機なし |
| Gitのcommit ID | 取得不可（Gitリポジトリ未初期化） |
| Test Environment | macOS、Python 3.9.6、pytest 8.4.2 |
| Tester | GitHub Copilot |
| Actual Result | 設定値0～15の全値で、指定回数の点灯・消灯、各0.25秒の待機、終了時消灯が期待値に一致した。 |
| Pass / Fail | Pass |
| Evidence | `pytest -q`の最終結果: 96 passed in 0.05s |
| Failure analysis | 該当なし |
| 備考 | テストダブルを使用した実機なし自動テスト |
