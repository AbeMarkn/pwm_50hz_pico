# TEST-DESN-001 テスト結果 001

| 項目 | 記録内容 |
| :--- | :--- |
| Test ID | TEST-DESN-001 |
| 実施日時 | 2026-09-02 10:36:13 JST |
| Firmware Version | v0.2.0 |
| Hardware Version | 実機なし |
| Gitのcommit ID | 取得不可（Gitリポジトリ未初期化） |
| Test Environment | macOS、Python 3.9.6、pytest 8.4.2 |
| Tester | GitHub Copilot |
| Actual Result | 16通りの負論理入力が0～15へ変換され、各入力の読取りは1回だった。 |
| Pass / Fail | Pass |
| Evidence | `pytest -q`の最終結果: 96 passed in 0.05s |
| Failure analysis | 該当なし |
| 備考 | テストダブルを使用した実機なし自動テスト |
