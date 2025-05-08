# ChatGPT JSON to Markdown Converter

ChatGPTとの会話ログ（JSON形式）をMarkdownファイルに変換するPythonスクリプトです。会話の内容を構造化し、タグ付けや統計情報の追加、コードブロックの分析などを行います。

## 特徴

- 会話ログの構造化されたMarkdown形式への変換
- 自動タグ生成（キーワード抽出、コード言語、カスタムタグ）
- 会話の統計情報の表示（メッセージ数、文字数、会話時間など）
- コードブロックの分析と言語の自動検出
- リンク一覧の自動生成
- 目次の自動生成（設定可能な閾値）
- 設定のカスタマイズ（config.json）
- スタンドアロン実行ファイル（Windows用）
- デフォルト設定のサポート（config.jsonが不要）

## 必要条件

### Pythonスクリプトとして実行する場合
- Python 3.6以上
- janome（日本語形態素解析用）
- unidic-lite（janomeの辞書）

### 実行ファイルを使用する場合
- Windows 10/11
- 追加のインストール不要

## インストール

### Pythonスクリプトとして使用
```bash
git clone https://github.com/shirousuda/chatgpt_json2md.git
cd chatgpt_json2md
pip install -r requirements.txt
```

### 実行ファイルとして使用
1. [Releases](https://github.com/shirousuda/chatgpt_json2md/releases)から最新の`json2md.exe`をダウンロード
2. 任意のフォルダに配置

## 使い方

### Pythonスクリプトとして実行
1. ChatGPTの会話ログ（JSON形式）を`conversations.json`として保存
2. 必要に応じて`config.json`を編集（オプション）
3. スクリプトを実行：
```bash
python json2md.py
```

### 実行ファイルとして実行
1. ChatGPTの会話ログ（JSON形式）を`conversations.json`として保存
2. 必要に応じて`config.json`を編集（オプション）
3. `json2md.exe`をダブルクリックまたはコマンドラインから実行

変換されたMarkdownファイルは`output`ディレクトリに保存されます。

## 設定（config.json）

設定ファイルは任意です。設定ファイルが見つからない場合は、以下のデフォルト値が使用されます：

```json
{
    "user_name": "mr.774",
    "user_email": "",
    "features": {
        "show_statistics": true,
        "show_code_blocks": true,
        "show_links": true,
        "show_toc": true,
        "toc_threshold": 5,
        "show_message_metadata": true,
        "show_timestamps": true,
        "show_message_length": true,
        "show_tags": true,
        "use_language_tags": true,
        "use_keyword_tags": true,
        "use_custom_tags": true
    },
    "custom_tags": {
        "programming": ["code", "function", "class", "variable"],
        "error": ["error", "exception", "warning"],
        "question": ["how", "what", "why", "when", "where", "?"],
        "solution": ["solution", "answer", "fix", "resolve"]
    },
    "stopwords": {
        "english": [
            "the", "and", "is", "are", "was", "were", "be", "to", "of", "in", "on", "for", "with", "as", "by", "at", "an", "a", "it", "this", "that", "from", "or", "but", "not", "can", "will", "would", "should", "could", "has", "have", "had", "do", "does", "did", "so", "if", "then", "than", "which", "who", "whom", "what", "when", "where", "why", "how", "all", "any", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "only", "own", "same", "too", "very"
        ],
        "japanese": [
            "です", "ます", "こと", "それ", "これ", "あれ", "ため", "よう", "もの", "あと", "から", "まで", "ので", "でも", "また", "など", "その", "この", "あの", "そして", "しかし", "または", "ので", "なら", "ならば", "けど", "けれど", "けれども", "が", "に", "を", "で", "と", "や", "へ", "の", "も", "ね", "よ", "な", "か", "が", "は", "を", "に", "と", "で", "や", "から", "まで", "より", "へ", "の", "ね", "よ", "な", "か"
        ],
        "domain": [
            "質問", "回答", "会話", "内容", "例", "場合", "方法", "対応", "部分", "全体", "今回", "以上", "以下", "必要", "可能", "利用", "使用", "追加", "削除", "設定", "確認", "実行", "作成", "編集", "保存", "表示", "選択", "入力", "出力", "取得", "変更", "指定", "選択", "開始", "終了", "更新", "作業", "操作", "説明", "参考", "情報", "詳細", "注意", "結果", "理由", "目的", "手順", "注意点", "注意事項", "概要", "特徴"
        ]
    }
}
```

### ストップワードの設定

`stopwords`セクションでは、タグとして抽出しない単語を指定できます。以下の3つのカテゴリがあります：

1. **english**: 英語のストップワード（例：the, and, is など）
2. **japanese**: 日本語のストップワード（例：です、ます、こと など）
3. **domain**: ドメイン固有のストップワード（例：質問、回答、会話 など）

これらの単語は、キーワード抽出時に自動的に除外されます。必要に応じて、各カテゴリに独自のストップワードを追加できます。

設定ファイルをカスタマイズする場合は、上記のJSONを`config.json`として保存し、必要な値を変更してください。設定ファイルが見つからない場合は、デフォルト値が使用されます。

## 出力形式

生成されるMarkdownファイルには以下の要素が含まれます：

- タイトル
- タグ一覧
- ユーザー情報
- タイムスタンプ（作成日時、更新日時、エクスポート日時）
- 会話の統計情報
- コードブロック分析
- リンク一覧
- 目次
- 会話内容（プロンプトとレスポンス）

### ファイル名の形式

生成されるファイル名は以下の形式になります：

```
ChatGPT-{タイトル}-{YYYYMMDD_HHMMSS}.md
```

同じタイムスタンプの場合は連番が付与されます：

```
ChatGPT-{タイトル}-{YYYYMMDD_HHMMSS}_1.md
ChatGPT-{タイトル}-{YYYYMMDD_HHMMSS}_2.md
```

例：
- `ChatGPT-Obsidian使い方ガイド-20240315_143022.md`
- `ChatGPT-Obsidian使い方ガイド-20240315_143022_1.md`
- `ChatGPT-Pythonの基本-20240315_143156.md`

タイトルは最大50文字までに制限され、ファイル名に使用できない文字は自動的に除去されます。タイムスタンプは会話の作成日時から生成され、同じタイムスタンプの場合は連番が付与されることで一意のファイル名が保証されます。

## カスタマイズ

- タグの抽出ルールの調整
- カスタムタグの追加・変更
- 表示形式のカスタマイズ
- 目次の表示閾値の設定

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。 