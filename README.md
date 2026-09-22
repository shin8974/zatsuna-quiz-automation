# ざつなクイズ 自動化

毎日 08:00 / 17:00（日本時間）に、白と青の棒人間クイズ動画を生成して YouTube に**非公開**でアップロードするための土台です。

## いまの安全な動き

Google の未監査 API プロジェクトは、API 経由のアップロードが非公開に制限されるため、この仕組みは公開を自動実行しません。動画は YouTube Studio で内容を確認して公開します。監査後に公開フローを見直します。

## GitHub Secrets（次の設定で追加）

- `YT_CLIENT_ID`
- `YT_CLIENT_SECRET`
- `YT_REFRESH_TOKEN`

これらをコード、Issue、コミット、チャットに貼らないでください。

## 初回の接続

1. ダウンロード済みの OAuth クライアント JSON を、このPCだけで使う。
2. `python scripts/authorize.py <JSONのパス>` を実行し、Google の同意画面で「Zatsuna Quiz Automation」の YouTube アップロード権限を承認する。
3. 表示された更新トークンと、JSON内の client ID / client secret を GitHub Secrets に一つずつ保存する。

トークンの生成後は、JSONをリポジトリに入れず、PCからも安全な場所に保管または削除する。

