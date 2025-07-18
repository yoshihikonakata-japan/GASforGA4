/**
 * 月次データ取得＋サンプリング・クォータ監視アラート
 */
function exportMonthlyGa4DataGenAll() {
  // ────────────────────────────────
  // １．設定
  // ────────────────────────────────
  const propertyId        = '123456789';         // ← 数字のみの GA4 Property ID
  const alertTo           = 'alert@example.com'; // ← 通知先メールアドレス
  const quotaThreshold    = 1000;                // ← クォータ警告の閾値

  // ────────────────────────────────
  // 通知設定フラグ（ユーザーが Yes/No で切り替え）
  // ────────────────────────────────
  const notifyOnNoSampling = true;  // サンプリング未検出時にもメール通知する？ (Yes / No)
  const notifyOnQuotaOk    = true;  // クォータに余裕あり時にもメール通知する？ (Yes / No)

  // ────────────────────────────────
  // ２．スプレッドシート取得
  // ────────────────────────────────
  const ss       = SpreadsheetApp.getActiveSpreadsheet();
  const sheet    = ss.getSheetByName('月次_gen_全体');
  const dateSh   = ss.getSheetByName('Date');
  const startDate = dateSh.getRange('B1').getDisplayValue();  // YYYY-MM-DD
  const endDate   = dateSh.getRange('C1').getDisplayValue();  // YYYY-MM-DD

  // ────────────────────────────────
  // ３．APIリクエスト生成
  // ────────────────────────────────
  const request = {
    dimensions: [{ name: 'yearMonth' }],
    metrics: [
      { name: 'sessions' },
      { name: 'bounceRate' },
      { name: 'totalUsers' },
      { name: 'purchaseRevenue' }
    ],
    dateRanges: [{ startDate, endDate }],
    returnPropertyQuota: true
  };

  try {
    // ────────────────────────────────
    // ４．レポート取得
    // ────────────────────────────────
    const response = AnalyticsData.Properties.runReport(request, `properties/${propertyId}`);

    // ────────────────────────────────
    // ５．サンプリング検出
    // ────────────────────────────────
    if (response.metadata && response.metadata.samplesReadCounts) {
      // 5-(b) 検出された場合
      MailApp.sendEmail(
        alertTo,
        '【GA4アラート】サンプリング検出',
        `プロパティ ${propertyId} のレポートでサンプリングが検出されました。\n` +
        `期間：${startDate} ～ ${endDate}\n` +
        `・読み込まれたサンプル数: ${response.metadata.samplesReadCounts.join(', ')}\n` +
        `・サンプリング対象の件数: ${response.metadata.samplingSpaceSizes.join(', ')}`
      );
    } else if (notifyOnNoSampling) {
      // 5-(a) 検出されない場合
      MailApp.sendEmail(
        alertTo,
        '【GA4通知】サンプリング未検出',
        `プロパティ ${propertyId} のレポートでサンプリングは検出されませんでした。\n` +
        `期間：${startDate} ～ ${endDate}`
      );
    }

    // ────────────────────────────────
    // ６．クォータ残量チェック
    // ────────────────────────────────
    if (response.propertyQuota) {
      const dailyRem  = response.propertyQuota.tokensPerDay.remaining;
      const hourlyRem = response.propertyQuota.tokensPerHour.remaining;

      if (dailyRem < quotaThreshold || hourlyRem < quotaThreshold) {
        // 6-(b) 閾値以下（検出された場合）
        MailApp.sendEmail(
          alertTo,
          '【GA4アラート】APIクォータ逼迫',
          `プロパティ ${propertyId} の残クォータが閾値以下です。\n` +
          `本日残トークン：${dailyRem}\n` +
          `1時間残トークン：${hourlyRem}`
        );
      } else if (notifyOnQuotaOk) {
        // 6-(a) まだ余裕あり（検出されない場合）
        MailApp.sendEmail(
          alertTo,
          '【GA4通知】APIクォータ余裕あり',
          `プロパティ ${propertyId} の残クォータはまだ閾値に余裕がありますが、念のため送信しました。\n` +
          `本日残トークン：${dailyRem}\n` +
          `1時間残トークン：${hourlyRem}`
        );
      }
    }

    // ────────────────────────────────
    // ７．シート書き出し（既存ロジック）
    // ────────────────────────────────
    if (!response.rows) return;

    // ヘッダー
    const headers = ["月", "セッション", "直帰率", "総ユーザー数", "購入による総収益"];
    sheet.getRange(2, 1, 1, headers.length).setValues([headers]);

    // 本体データ
    const rows = response.rows.map(r => {
      let ym = r.dimensionValues[0].value;  // YYYYMM
      ym = ym.slice(0,4) + "-" + ym.slice(4);

      const sessions   = Number(r.metricValues[0].value);
      let bounceRate   = Number(r.metricValues[1].value);
      const totalUsers = Number(r.metricValues[2].value);
      const revenue    = Number(r.metricValues[3].value);
      if (bounceRate < 1) bounceRate *= 100;

      return [
        ym,
        sessions,
        bounceRate.toFixed(1) + "%",
        totalUsers,
        "$" + revenue.toFixed(2)
      ];
    });
    sheet.getRange(3, 1, rows.length, headers.length).setValues(rows);

  } catch (e) {
    // エラー時にも通知
    MailApp.sendEmail(
      alertTo,
      '【GA4アラート】スクリプト実行エラー',
      `エラー内容:\n${e.message}`
    );
  }
}
