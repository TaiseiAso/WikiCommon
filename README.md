# WikiCommon
2020/03/12~ Aso Taisei
Wikipediaを用いるCS17の日本語研究者のために簡単に使えるスクリプトを
***
## 概要
Wikipediaコーパスから大規模知識データベースを構築するためのスクリプト群

## 要件
- Linux系 (Linuxコマンドが使える環境)
    - find, grep, awk, cat, rm
- python3系
- pyyaml
- MeCab (辞書を mecab-ipadic-NEologd に更新することを推奨)

## 準備
- https://dumps.wikimedia.org/jawiki から jawiki-latest-pages-articles.xml.bz2 をダウンロードして ./data/ へ置く (時間がかかる)
- カレントディレクトリを ./WikiCommon に移動

## 手順
1. ./data/jawiki-latest-pages-articles.xml.bz2 を解凍して記事のみを抽出し単一ファイルに出力する (時間がかかる)
    ```
    $ python dump.py
    ```
    ./data/ に dumped.txt が出力される

2. ./data/dumped.txt に形態素解析、正規化処理、フィルタリング処理を施す
    ```
    $ python clean.py
    ```
    ./data/ に cleaned.txt または cleaned-part.txt または cleaned.yml が出力される

## 備考
- ./script/WikiExtractor.py は https://github.com/attardi/wikiextractor からダウンロードしたものです
- 各種設定の変更は ./config.yml を参照してください
- 各出力ファイルが必要なくなった場合は ./data/ にあるファイルを削除するだけで大丈夫です (jawiki-latest-pages-articles.xml.bz2 は再ダウンロードに時間がかかるので残しておくことを推奨します)
