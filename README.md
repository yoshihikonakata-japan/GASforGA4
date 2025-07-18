# GA4 月次レポート自動化スクリプト

Google Apps Script（GAS）を使い、GA4 Data API から月次データを取得し、  
- レポート書き込み  
- サンプリング検出／未検出の通知  
- APIクォータ逼迫／余裕ありの通知  

を一本化したサンプルスクリプトです。

---

## 📋 目次

1. [前提条件](#前提条件)  
2. [セットアップ](#セットアップ)  
3. [シート構成](#シート構成)  
4. [設定項目](#設定項目)  
5. [使い方](#使い方)  
6. [定期実行トリガー設定](#定期実行トリガー設定)  
7. [コード概要](#コード概要)  
8. [注意事項](#注意事項)  
9. [ライセンス](#ライセンス)  
10. [参考資料](#参考資料)  

---

## 前提条件

- Google Apps Script プロジェクトを作成済み  
- **Advanced Google サービス** の「Analytics Data API」を有効化  
- GCP コンソール側でも「Analytics Data API」を有効化  
- 実行ユーザーに GA4 プロパティへの「アナリスト以上」権限  
- メール送信に使用するアカウントで `MailApp.sendEmail` が使用可能  

---

## セットアップ

1. リポジトリをクローンまたは ZIP 展開  
2. GAS エディタで新規プロジェクトを作成し、`Code.gs` にスクリプトを貼り付け  
3. メニュー → **サービス** → **Advanced Google サービス** から「Analytics Data API」を ON  
4. スクリプトの最上部にある設定項目を編集  

---

## シート構成

- **月次_gen_全体**  
  - レポート結果を書き込むシート  
- **Date**  
  - B1: レポート開始日（`YYYY-MM-DD`形式）  
  - C1: レポート終了日（`YYYY-MM-DD`形式）  

---

## 設定項目

`Code.gs` の先頭にある以下の変数を編集してください：

| 変数名                  | 説明                                                              | 例              |
|-------------------------|-------------------------------------------------------------------|-----------------|
| `propertyId`            | GA4 の **数字のみ** の Property ID                                 | `123456789`     |
| `alertTo`               | 通知先メールアドレス                                               | `me@example.com`|
| `quotaThreshold`        | クォータ警告の閾値（残りトークン数がこの値未満で「逼迫」と判定）      | `1000`          |
| `notifyOnNoSampling`    | サンプリング未検出時にも通知する？（`true`=通知する, `false`=通知しない） | `true`          |
| `notifyOnQuotaOk`       | クォータ余裕時にも通知する？（`true`=通知する, `false`=通知しない）     | `true`          |

---

## 使い方

1. 手動実行  
   - GAS エディタ上で関数 `exportMonthlyGa4DataGenAll()` を実行  
2. 自動実行  
   - トリガー設定により、指定スケジュールで自動実行  
   - 実行内容：  
     1. GA4 から月次レポートを取得しシートに書き込む  
     2. サンプリングの検出・未検出をメール通知  
     3. APIクォータの逼迫・余裕をメール通知  

---

## 定期実行トリガー設定

1. GAS エディタ → **トリガー**  
2. 関数：`exportMonthlyGa4DataGenAll`  
3. イベント：**時間主導型** → **日付ベースのタイマー**  
4. 任意の実行タイミングを設定（例：毎月1日 09:00）  

---

## コード概要

- **設定フェーズ**：Property ID、通知先、閾値、通知フラグを定義  
- **データ取得**：`AnalyticsData.Properties.runReport` で月次データを取得  
- **サンプリング検出**  
  - 検出あり → 検出内容（サンプル数／母集団サイズ）を通知  
  - 検出なし → `notifyOnNoSampling` が `true` の場合に通知  
- **クォータ監視**  
  - 閾値以下 → 「逼迫」メールを通知  
  - 余裕あり → `notifyOnQuotaOk` が `true` の場合に「余裕あり」メールを通知  
- **シート書き込み**：取得した行データをシートに出力  
- **例外ハンドリング**：APIエラー発生時もメール通知  

---

## 注意事項

- 通知フラグを誤って `true` のまま本番運用すると、不要なメールが大量に送信される可能性があります。  
- `quotaThreshold` は運用量に合わせて適切に設定してください。  
- GA4 Measurement ID（`G-xxxx`）ではなく、**数字のみの Property ID** を使用してください。  

---

## ライセンス

MIT License  

---

## 参考資料

- [Analytics Data API — サンプリング検出](https://developers.google.com/analytics/devguides/reporting/data/v1)  
- [RunReportRequest — returnPropertyQuota](https://developers.google.com/analytics/devguides/reporting/data/v1/reference/rest/v1beta/RunReportRequest)  

