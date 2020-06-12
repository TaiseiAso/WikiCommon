# coding: utf-8

"""Wikipediaコーパスを解凍して記事のみを抽出し単一ファイルに出力する"""
__author__ = "Aso Taisei"
__date__ = "12 Mar 2020"

import os
import sys
import yaml

def dump():
    """Wikipediaコーパスを解凍して記事のみを抽出し単一ファイルに出力する"""
    # ファイルパス
    wiki_extractor_path = "./script/WikiExtractor.py"
    wiki_xml_path = "./data/jawiki-latest-pages-articles.xml.bz2"
    wiki_dump_path = "./data/dumped.txt"
    wiki_tmp_path = "./data/tmp/"

    # 例外処理
    error_flag = False
    if not os.path.isfile(wiki_extractor_path):
        print("{}: cannot find".format(wiki_extractor_path))
        error_flag = True
    if not os.path.isfile(wiki_xml_path):
        print("{}: cannot find".format(wiki_xml_path))
        error_flag = True
    if error_flag:
        sys.exit(1)

    # Wikipediaコーパスを解凍して全てのファイルを一時保存する
    os.system("python {} {} --output {}".format(wiki_extractor_path, wiki_xml_path, wiki_tmp_path))

    # 解凍したファイルを単一ファイルにまとめる
    os.system("find {} | grep wiki | awk \'{{system(\"cat \"$0\" >> {}\")}}\'".format(wiki_tmp_path, wiki_dump_path))

    # 一時保存したファイルを全て削除する
    os.system("rm -rf {}".format(wiki_tmp_path))

if __name__ == '__main__':
    dump()
