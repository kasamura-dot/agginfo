# Aggregated JP Gov Stats Viewer

日本政府・省庁公開統計を「選択的に」表示するための最小プロトタイプです。

## 構成
- `backend`: FastAPI で統計データ取得・整形APIを提供
- `frontend`: シンプルな静的UI（絞り込み・表示）

## 対応テーマ
- `population` 人口
- `employment` 雇用
- `households` 世帯
- `cpi` 消費者物価
- `tourism` 観光
- `wage` 賃金

`GET /api/themes` でテーマ一覧を取得でき、フロントのセレクトはこのAPIから自動生成されます。

## 使い方
1. 仮想環境を作成し依存関係をインストール
   - `python -m venv .venv`
   - `.\\.venv\\Scripts\\python -m pip install -r requirements.txt`
2. （任意）e-Stat APIキーを設定
   - `.env` に `ESTAT_APP_ID=あなたのAPIキー`
3. サーバー起動
   - `.\\.venv\\Scripts\\python -m uvicorn backend.app.main:app --reload --port 8000`
4. ブラウザで確認
   - テーマ一覧: `http://127.0.0.1:8000/api/themes`
   - 統計API: `http://127.0.0.1:8000/api/stats?theme=population&pref=13`
   - UI: `http://127.0.0.1:8000/`

## MVP公開（Render）
1. このリポジトリを GitHub に push
2. Render で `New +` -> `Blueprint` を選択し、当該リポジトリを接続
3. `render.yaml` が検出されるので作成を進める
4. Render 管理画面の Environment で `ESTAT_APP_ID` を設定（任意）
5. デプロイ完了後、発行された URL にアクセス

`ESTAT_APP_ID` 未設定時はモックデータで動作します。

## 注意
- このプロトタイプはまず操作性を確認するための最小実装です。
- `population` と `employment` 以外は現在モックデータで表示します（テーマ定義は拡張済み）。
- 本番ではキャッシュ・監視・利用規約対応・障害時リトライを追加してください。
