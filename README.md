# DownloadMaid

ダウンロードフォルダを監視して、ファイルを自動で仕分けするツールです。  
macOS / Windows 対応。システムトレイに常駐して動作します。

## 機能

- ダウンロードフォルダを監視し、ファイルを拡張子ごとに自動移動
- デフォルトで 7 カテゴリに対応（カスタマイズ可能）

| カテゴリ | 対象拡張子（例） |
|---------|----------------|
| 画像 | .jpg .png .gif .webp .heic |
| 動画 | .mp4 .mov .avi .mkv |
| 音楽 | .mp3 .flac .wav .aac |
| ドキュメント | .pdf .docx .xlsx .pptx .txt |
| 圧縮ファイル | .zip .rar .7z .tar.gz |
| インストーラ | .dmg .pkg .exe .msi |
| コード | .py .js .ts .html .json |

- システムトレイから監視の開始 / 一時停止
- ログイン時の自動起動（macOS launchd / Windows レジストリ）
- 設定ファイル（YAML）でルールをカスタマイズ可能

## インストール

### macOS

1. [Releases](https://github.com/yanoco13/downloadmaid/releases/latest) から `DownloadMaid-mac.zip` をダウンロード
2. zip を展開して `DownloadMaid.app` を `/Applications` にドラッグ
3. 起動する

> **「開発元を確認できません」と表示された場合**
>
> システム設定 → プライバシーとセキュリティ → 「このまま開く」をクリックしてください。
>
> またはターミナルで以下を実行:
> ```bash
> xattr -cr /Applications/DownloadMaid.app
> ```

### Windows

1. [Releases](https://github.com/yanoco13/downloadmaid/releases/latest) から `DownloadMaid.exe` をダウンロード
2. 任意の場所に置いて実行する

> **「Windows によって PC が保護されました」と表示された場合**
>
> 「詳細情報」→「実行」をクリックしてください。

## 設定のカスタマイズ

設定ファイルは `~/.downloadmaid/config.yaml` にあります。  
システムトレイのメニュー → 「設定ファイルを開く」からも開けます。

```yaml
watch_folder: ~/Downloads

rules:
  画像:
    extensions: [.jpg, .jpeg, .png, .gif, .webp]
    destination: ~/Downloads/画像
  # 好きなカテゴリを追加・編集できます
```

## ライセンス

MIT
