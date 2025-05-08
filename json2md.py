import json
import os
import re
from datetime import datetime
from collections import defaultdict
import sys
from janome.tokenizer import Tokenizer

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_config(config_path='config.json'):
    """Load configuration with default values"""
    default_config = {
        "user_name": "mr.774",  # デフォルトユーザー名を設定
        "user_email": "",
        "features": {
            "show_statistics": True,
            "show_code_blocks": True,
            "show_links": True,
            "show_toc": True,
            "toc_threshold": 5,
            "show_message_metadata": True,
            "show_timestamps": True,
            "show_message_length": True,
            "show_tags": True,
            "use_language_tags": True,
            "use_keyword_tags": True,
            "use_custom_tags": True
        },
        "keyword_settings": {
            "min_frequency": 3,  # 最低出現回数
            "max_keywords": 5,   # 最大キーワード数
            "min_length": 2,     # 最小文字数
            "topK": 50          # キーワード候補の取得数
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
    
    try:
        # First try the local config file
        if os.path.exists(config_path):
            config_file_path = config_path
        else:
            # If not found, try the bundled config file
            config_file_path = get_resource_path(config_path)
        
        if os.path.exists(config_file_path):
            with open(config_file_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                if 'features' in user_config:
                    default_config['features'].update(user_config['features'])
                if 'custom_tags' in user_config:
                    default_config['custom_tags'].update(user_config['custom_tags'])
                if 'stopwords' in user_config:
                    default_config['stopwords'].update(user_config['stopwords'])
                if 'keyword_settings' in user_config:
                    default_config['keyword_settings'].update(user_config['keyword_settings'])
                default_config.update({k: v for k, v in user_config.items() 
                                    if k not in ['features', 'custom_tags', 'stopwords', 'keyword_settings']})
                print(f"Loaded configuration from {config_file_path}")
        else:
            print(f"Config file not found. Using default configuration with user: {default_config['user_name']}")
    except Exception as e:
        print(f"Warning: Could not load config file ({str(e)}). Using default configuration with user: {default_config['user_name']}")
    
    return default_config

def is_corrupted_text(text):
    """文字化けを検出する関数"""
    # 制御文字（0x00-0x1F）や不正なUnicode文字を検出
    control_chars = ''.join(map(chr, list(range(0, 32)) + list(range(127, 160))))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))
    
    # 文字化けの特徴的なパターン
    corruption_patterns = [
        r'[\ufffd\ufffe\uffff]',  # 不正なUnicode文字
        r'[\u0000-\u0008\u000B\u000C\u000E-\u001F]',  # 制御文字
        r'[\uD800-\uDFFF]',  # サロゲートペア
        r'[\uFFFD]',  # 置換文字
        r'[\uFFFE\uFFFF]',  # 不正なUnicode文字
    ]
    
    # 文字化けのパターンに一致するかチェック
    for pattern in corruption_patterns:
        if re.search(pattern, text):
            return True
    
    # 制御文字が含まれているかチェック
    if control_char_re.search(text):
        return True
    
    return False

def initialize_tokenizer():
    """janomeの初期化"""
    return Tokenizer()

def is_noun(word, tokenizer):
    """単語が名詞かどうかを判定"""
    tokens = list(tokenizer.tokenize(word))
    if tokens:
        # 名詞または未知語の場合を名詞として扱う
        pos = tokens[0].part_of_speech
        return pos.startswith('名詞') or pos.startswith('未知語')
    return False

def is_unnatural_tokenization(word, tokens):
    """形態素解析の結果が不自然かどうかを判定"""
    # デバッグ出力
    print(f"\n=== 不自然な分割の判定 ===")
    print(f"単語: {word}")
    print(f"分割結果: {' '.join([f'{t.surface}({t.part_of_speech})' for t in tokens])}")
    
    # 分割数が多すぎる場合
    if len(tokens) > len(word) / 2:  # 文字数の半分以上に分割されるのは不自然
        print(f"→ 分割数が多すぎます（{len(tokens)}分割）")
        return True
    
    # 1文字の分割が含まれる場合
    one_char_tokens = [t.surface for t in tokens if len(t.surface) == 1]
    if one_char_tokens:
        print(f"→ 1文字の分割が含まれています: {one_char_tokens}")
        return True
    
    # 品詞の並びが不自然な場合
    pos_sequence = [token.part_of_speech.split(',')[0] for token in tokens]
    if len(pos_sequence) >= 3:
        # 同じ品詞が3回以上連続するのは不自然
        for i in range(len(pos_sequence) - 2):
            if pos_sequence[i] == pos_sequence[i+1] == pos_sequence[i+2]:
                print(f"→ 同じ品詞が3回以上連続しています: {pos_sequence[i:i+3]}")
                return True
    
    print("→ 自然な分割と判定")
    return False

def extract_keywords(text, config=None, title=None):
    """Extract keywords from text using janome"""
    if not config:
        config = load_config()
    
    # デバッグ: タイトルの形態素解析結果を表示
    if title and 'ちゆかいゆ' in title:
        print("\n=== タイトルの形態素解析結果 ===")
        tokenizer = initialize_tokenizer()
        for token in tokenizer.tokenize(title):
            print(f"表層形: {token.surface}\t品詞: {token.part_of_speech}\t読み: {token.reading}")
        print("=== タイトルの形態素解析結果終了 ===\n")
        
        # ちゆかいゆの不自然な分割チェック
        print("\n=== ちゆかいゆの不自然な分割チェック ===")
        tokens = list(tokenizer.tokenize('ちゆかいゆ'))
        is_unnatural = is_unnatural_tokenization('ちゆかいゆ', tokens)
        print(f"判定結果: {'不自然な分割' if is_unnatural else '自然な分割'}")
        print("=== ちゆかいゆの不自然な分割チェック終了 ===\n")
    
    keyword_settings = config.get('keyword_settings', {})
    min_frequency = keyword_settings.get('min_frequency', 3)
    max_keywords = keyword_settings.get('max_keywords', 5)
    min_length = keyword_settings.get('min_length', 2)
    topK = keyword_settings.get('topK', 50)
    
    # デバッグ出力を有効にする
    debug = True
    
    # コードブロックを除外したテキストを取得
    text_without_code = re.sub(r'```[\s\S]*?```', '', text)
    
    # URLを除外したテキストを取得
    text_without_urls = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', text_without_code)
    
    # テキストの前処理
    # 1. 全角スペースを半角に変換
    text_without_urls = text_without_urls.replace('　', ' ')
    # 2. 連続するスペースを1つに
    text_without_urls = re.sub(r'\s+', ' ', text_without_urls)
    # 3. 記号の前後にスペースを追加
    text_without_urls = re.sub(r'([.,!?;:])', r' \1 ', text_without_urls)
    
    # ちゆかいゆの出現回数をチェック
    chiyukaiyu_count = text_without_urls.count('ちゆかいゆ')
    if debug and chiyukaiyu_count > 0:
        print(f"\n=== キーワード抽出デバッグ ===")
        print(f"ちゆかいゆの出現回数: {chiyukaiyu_count}")
        print(f"タイトル: {title}")
        if title and 'ちゆかいゆ' in title:
            print("ちゆかいゆはタイトルに含まれています（重み付け3倍）")
    
    # janomeで形態素解析
    tokenizer = initialize_tokenizer()
    tokens = tokenizer.tokenize(text_without_urls)
    
    if debug and chiyukaiyu_count > 0:
        print("\n形態素解析結果:")
        for token in tokens:
            if token.surface == 'ちゆかいゆ':
                print(f"  ちゆかいゆ: 品詞={token.part_of_speech}")
    
    # トークンを再度取得（イテレータは1回しか使えないため）
    tokens = tokenizer.tokenize(text_without_urls)
    word_freq = {}
    
    # 不自然な分割の単語を検出して追加
    if title and 'ちゆかいゆ' in title:
        word_freq['ちゆかいゆ'] = 3  # タイトルに含まれる場合は3回分
        if debug:
            print(f"  ちゆかいゆを不自然な分割として追加: 出現回数=3")
    
    for token in tokens:
        word = token.surface
        if len(word) >= min_length:
            # 名詞の場合、または未知語で不自然な分割の場合
            if token.part_of_speech.startswith('名詞'):
                # タイトルに含まれる単語は出現回数を3倍に
                if title and word in title:
                    word_freq[word] = word_freq.get(word, 0) + 3
                    if debug and word == 'ちゆかいゆ':
                        print(f"  ちゆかいゆをタイトルから検出: 重み付け後の出現回数={word_freq[word]}")
                else:
                    word_freq[word] = word_freq.get(word, 0) + 1
                    if debug and word == 'ちゆかいゆ':
                        print(f"  ちゆかいゆを本文から検出: 出現回数={word_freq[word]}")
    
    # 最低出現回数以上の単語のみを抽出し、出現回数でソート
    frequent_words = [(word, freq) for word, freq in word_freq.items() if freq >= min_frequency]
    frequent_words.sort(key=lambda x: (-x[1], x[0]))  # 出現回数の降順、同じ場合は単語の昇順
    frequent_words = [word for word, _ in frequent_words[:max_keywords]]  # 上位N件のみ
    
    if debug and chiyukaiyu_count > 0:
        print(f"\n最低出現回数({min_frequency}回)以上の単語:")
        for word, freq in sorted(word_freq.items(), key=lambda x: (-x[1], x[0])):
            if word == 'ちゆかいゆ':
                print(f"  ちゆかいゆ: {freq}回")
                if freq >= min_frequency:
                    print("  → 最低出現回数を満たしています")
                else:
                    print("  → 最低出現回数を満たしていません")
    
    # 英語の単語も抽出（最低出現回数以上出現するもののみ）
    eng_words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]{2,}\b', text_without_urls)
    eng_word_freq = {}
    for word in eng_words:
        # タイトルに含まれる単語は出現回数を3倍に
        if title and word in title:
            eng_word_freq[word] = eng_word_freq.get(word, 0) + 3
        else:
            eng_word_freq[word] = eng_word_freq.get(word, 0) + 1
    
    frequent_eng_words = [(word, freq) for word, freq in eng_word_freq.items() if freq >= min_frequency]
    frequent_eng_words.sort(key=lambda x: (-x[1], x[0]))  # 出現回数の降順、同じ場合は単語の昇順
    frequent_eng_words = [word for word, _ in frequent_eng_words[:max_keywords]]  # 上位N件のみ
    
    keywords = set(frequent_words + frequent_eng_words)
    
    # ストップワードの取得
    stopwords = set()
    if config and 'stopwords' in config:
        for lang in ['english', 'japanese', 'domain']:
            if lang in config['stopwords']:
                stopwords.update(config['stopwords'][lang])
    
    filtered = [
        k for k in keywords
        if len(k) >= min_length
        and k.lower() not in stopwords
        and not re.match(r'^https?://', k)
        and not re.match(r'^[\w\.-]+@[\w\.-]+$', k)
        and not re.match(r'^[!-/:-@\[-`{-~]+$', k)
        and not re.match(r'^[\d\.]+$', k)  # 数値のみのタグを除外（小数点を含む数値も除外）
        and not re.match(r'^#[\d\.]+$', k)  # #で始まる数値のみのタグを除外
        and not re.match(r'^turn\d+search\d+$', k)  # turnXsearchY形式の文字列を除外
        and not re.match(r'^[a-z]+\d+[a-z]+\d+$', k)  # 文字と数字が交互に現れるパターンを除外
        and not is_corrupted_text(k)  # 文字化けしているテキストを除外
    ]
    
    if debug and chiyukaiyu_count > 0:
        print("=== デバッグ終了 ===\n")
    
    return filtered

def extract_tags_from_messages(messages, config):
    """Extract tags from conversation messages"""
    tags = set()
    
    # コードブロックの言語をタグとして追加
    if config['features']['use_language_tags']:
        for msg in messages:
            code_matches = re.finditer(r'```(\w*)\n', msg['text'])
            for match in code_matches:
                lang = match.group(1)
                if lang and lang != 'plaintext':
                    tags.add(f'lang:{lang}')
    
    # キーワードをタグとして追加
    if config['features']['use_keyword_tags']:
        # タイトルを取得
        title = None
        for msg in messages:
            if msg['role'] == 'user':
                title = msg['text'][:50].strip()
                title = title.replace('#', '').replace('*', '').replace('_', '').strip()
                break
        
        for msg in messages:
            keywords = extract_keywords(msg['text'], config=config, title=title)
            tags.update(keywords)
    
    # カスタムタグを追加
    if config['features']['use_custom_tags']:
        custom_tags = config.get('custom_tags', {})
        # カスタムタグの条件に基づいてタグを追加
        for tag, conditions in custom_tags.items():
            for msg in messages:
                if any(condition.lower() in msg['text'].lower() for condition in conditions):
                    tags.add(tag)
    
    return sorted(list(tags))

def convert_timestamp(timestamp):
    """Convert timestamp to readable date format"""
    return datetime.fromtimestamp(timestamp).strftime('%m/%d/%Y %H:%M')

def extract_all_messages(mapping):
    messages = []
    for msg in mapping.values():
        content = msg.get('message', {})
        if content:
            role = content.get('author', {}).get('role')
            parts = content.get('content', {}).get('parts', [])
            create_time = content.get('create_time', 0) or msg.get('create_time', 0)
            if role in ['user', 'assistant'] and parts:
                text = parts[0]
                if text and isinstance(text, str):
                    messages.append({
                        'role': role,
                        'text': text,
                        'create_time': create_time,
                        'length': len(text)
                    })
    messages.sort(key=lambda x: x['create_time'])
    return messages

def get_title(conversation, messages):
    title = conversation.get('title', '').strip()
    if not title and messages:
        for msg in messages:
            if msg['role'] == 'user':
                title = msg['text'][:50].strip()
                title = title.replace('#', '').replace('*', '').replace('_', '').strip()
                break
    if not title:
        title = 'Untitled Conversation'
    return title

def generate_filename(title, create_time):
    """Generate filename with timestamp"""
    # タイムスタンプを日付形式に変換
    timestamp = datetime.fromtimestamp(create_time).strftime('%Y%m%d_%H%M%S')
    # ファイル名に使用できない文字を除去
    safe_title = "".join(c for c in title if c.isalnum() or c in ('_', '-', '.'))
    # タイトルが長すぎる場合は切り詰める
    if len(safe_title) > 50:
        safe_title = safe_title[:50]
    
    # タイムスタンプを含むファイル名を生成
    return f"ChatGPT-{safe_title}-{timestamp}.md"

def extract_metadata(messages):
    """Extract metadata from messages"""
    if not messages:
        return {}
    
    total_messages = len(messages)
    total_chars = sum(msg['length'] for msg in messages)
    first_msg_time = messages[0]['create_time']
    last_msg_time = messages[-1]['create_time']
    duration = last_msg_time - first_msg_time
    
    # Extract code blocks and their languages
    code_blocks = []
    for msg in messages:
        code_matches = re.finditer(r'```(\w*)\n(.*?)```', msg['text'], re.DOTALL)
        for match in code_matches:
            lang = match.group(1) or 'plaintext'
            code = match.group(2)
            code_blocks.append({'language': lang, 'length': len(code)})
    
    # Extract links
    links = []
    for msg in messages:
        link_matches = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', msg['text'])
        for match in link_matches:
            links.append({'text': match.group(1), 'url': match.group(2)})
    
    return {
        'total_messages': total_messages,
        'total_chars': total_chars,
        'duration': duration,
        'code_blocks': code_blocks,
        'links': links
    }

def generate_toc(messages):
    """Generate table of contents for the conversation"""
    toc = "## Table of Contents\n\n"
    for i, msg in enumerate(messages, 1):
        if msg['role'] == 'user':
            # Use first line or first 50 chars as section title
            title = msg['text'].split('\n')[0][:50].strip()
            toc += f"{i}. [{title}](#section-{i})\n"
    return toc + "\n"

def format_message(msg, section_num, config):
    """Format a single message with metadata"""
    role = "User" if msg['role'] == 'user' else "Assistant"
    
    # Add section anchor for user messages
    if msg['role'] == 'user':
        header = f"## <a id='section-{section_num}'></a>Prompt:\n"
    else:
        header = "## Response:\n"
    
    # Add metadata based on config
    metadata_parts = []
    if config['features']['show_timestamps']:
        metadata_parts.append(convert_timestamp(msg['create_time']))
    if config['features']['show_message_length']:
        metadata_parts.append(f"{msg['length']} characters")
    
    metadata = f"*{role}"
    if metadata_parts:
        metadata += " • " + " • ".join(metadata_parts)
    metadata += "*\n\n"
    
    return header + metadata + msg['text'] + "\n\n"

def convert_to_markdown(conversation, config):
    messages = extract_all_messages(conversation.get('mapping', {}))
    title = get_title(conversation, messages)
    create_time = conversation.get('create_time', 0)
    update_time = convert_timestamp(conversation.get('update_time', 0))
    
    # Extract metadata and tags
    metadata = extract_metadata(messages)
    tags = extract_tags_from_messages(messages, config)
    
    # Start building markdown
    markdown = f"# {title}\n\n"
    
    # Add tags if enabled
    if config['features']['show_tags'] and tags:
        markdown += "### Tags\n\n"
        markdown += " ".join([f"#{tag}" for tag in tags]) + "\n\n"
    
    # Add user info from config
    user_name = config.get('user_name', 'Unknown User')
    user_email = config.get('user_email', '')
    if user_email:
        markdown += f"**User:** {user_name} ({user_email})  \n"
    else:
        markdown += f"**User:** {user_name}  \n"
    
    # Add timestamps
    markdown += f"**Created:** {convert_timestamp(create_time)}  \n"
    markdown += f"**Updated:** {update_time}  \n"
    markdown += f"**Exported:** {datetime.now().strftime('%m/%d/%Y %H:%M')}  \n\n"
    
    # Add conversation metadata if enabled
    if config['features']['show_statistics']:
        markdown += "### Conversation Statistics\n\n"
        markdown += f"- Total Messages: {metadata['total_messages']}\n"
        markdown += f"- Total Characters: {metadata['total_chars']}\n"
        markdown += f"- Duration: {metadata['duration']/3600:.1f} hours\n\n"
    
    # Add code blocks summary if enabled and available
    if config['features']['show_code_blocks'] and metadata['code_blocks']:
        markdown += "### Code Blocks\n\n"
        for block in metadata['code_blocks']:
            markdown += f"- {block['language']}: {block['length']} characters\n"
        markdown += "\n"
    
    # Add links summary if enabled and available
    if config['features']['show_links'] and metadata['links']:
        markdown += "### Links\n\n"
        for link in metadata['links']:
            markdown += f"- [{link['text']}]({link['url']})\n"
        markdown += "\n"
    
    # Add table of contents if enabled and threshold met
    if (config['features']['show_toc'] and 
        len(messages) >= config['features']['toc_threshold']):
        markdown += generate_toc(messages)
    
    # Add messages
    for i, msg in enumerate(messages, 1):
        markdown += format_message(msg, i, config)
    
    return markdown

def process_json_file(input_file, output_dir='output', config_path='config.json'):
    os.makedirs(output_dir, exist_ok=True)
    with open(input_file, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    config = load_config(config_path)
    for i, conversation in enumerate(conversations):
        messages = extract_all_messages(conversation.get('mapping', {}))
        title = get_title(conversation, messages)
        create_time = conversation.get('create_time', 0)
        filename = generate_filename(title, create_time)
        markdown_content = convert_to_markdown(conversation, config)
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"Created: {output_path}")

if __name__ == "__main__":
    input_file = "conversations.json"
    process_json_file(input_file) 