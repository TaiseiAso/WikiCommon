# coding: utf-8

"""Wikipediaコーパスに形態素解析、正規化処理、フィルタリング処理を施す"""
__author__ = "Aso Taisei"
__date__ = "11 Jun 2020"

import yaml
import os
import re
import sys
import unicodedata
import MeCab

class WikipediaCleaner:
    """Wikipediaコーパスに形態素解析、正規化処理、フィルタリング処理を施すクラス"""

    def __init__(self):
        """コンストラクタ"""
        # ファイルパス
        self.config_path = "./config.yml"
        self.wiki_dump_path = "./data/dumped.txt"
        self.wiki_clean_path = "./data/cleaned.txt"
        self.wiki_clean_part_path = "./data/cleaned-part.txt"
        self.wiki_clean_yaml_path = "./data/cleaned.yml"

        # 設定
        if not os.path.isfile(self.config_path):
            print("{}: cannot find".format(self.config_path))
            sys.exit(1)

        try:
            config = yaml.load(stream=open(self.config_path, 'r', encoding='utf-8'), Loader=yaml.SafeLoader)
        except:
            print("{}: file read error".format(self.config_path))
            sys.exit(1)

        filter = config['filter']
        self.need = filter['need']
        self.needless = filter['needless']
        self.dump = filter['dump']
        self.length = filter['length']
        self.output = config['output']

        # 分かち書きするモジュール
        self.tagger = MeCab.Tagger('-Ochasen')

    def isTagStart(self, line):
        """
        文が<docタグかどうかを判定する
        @param:str line 判定する文
        @return:bool 文が<docタグかどうか
        """
        return re.compile("^<doc").search(line)

    def isTagEnd(self, line):
        """
        文が</docタグかどうかを判定する
        @param:str line 判定する文
        @return:bool 文が</docタグかどうか
        """
        return re.compile("^</doc").search(line)

    def check(self, line):
        """
        テキストに不適切な情報が含まれていないかを判定
        @param text テキスト
        @return True: 適切、False: 不適切
        """
        # 英数字を含む
        #if re.compile("[a-zA-Z0-9]").search(line):
        #    return False
        return True

    def normalize(self, line):
        """
        文に正規化処理を施す
        読点ごとに分割されてリストが返される
        @param:str line 正規化する文
        @return:list[str] 正規化された文の集合
        """
        line = re.sub("[\(\[][^笑泣汗]*?[\)\]]", " ", line)
        line = re.sub("[^ぁ-んァ-ヶ一-龠々ー～〜、。!?,.a-zA-Z0-9]", " ", line)

        line = re.sub(",", "、", line)
        line = re.sub("\.", "。", line)
        line = re.sub("〜", "～", line)
        line = re.sub("、(\s*、)+|。(\s*。)+", "...", line)

        line = re.sub("!+", "！", line)
        line = re.sub("！(\s*！)+", "！", line)
        line = re.sub("\?+", "？", line)
        line = re.sub("？(\s*？)+", "？", line)

        line = re.sub("～(\s*～)+", "～", line)
        line = re.sub("ー(\s*ー)+", "ー", line)
        line = re.sub("っ(\s*っ)+", "っ", line)
        line = re.sub("ッ(\s*ッ)+", "ッ", line)
        line = re.sub("笑(\s*笑)+", "笑", line)
        line = re.sub("泣(\s*泣)+", "泣", line)
        line = re.sub("汗(\s*汗)+", "汗", line)

        line += "。"
        line = re.sub("[、。](\s*[、。])+", "。", line)

        line = re.sub("[。、！](\s*[。、！])+", "！", line)
        line = re.sub("[。、？](\s*[。、？])+", "？", line)
        line = re.sub("((！\s*)+？|(？\s*)+！)(\s*[！？])*", "!?", line)

        line = re.sub("、\s*([笑泣汗])\s*。", " \\1。", line)
        line = re.sub("(。|！|？|!\?)\s*([笑泣汗])\s*。", " \\2\\1", line)

        line = re.sub("、", " 、 ", line)
        line = re.sub("。", " 。\n", line)

        line = re.sub("(\.\s*)+", " ... ", line)
        line = re.sub("！", " ！\n", line)
        line = re.sub("？", " ？\n", line)
        line = re.sub("!\?", " !?\n", line)

        line = re.sub("\n(\s*[～ー])+", "\n", line)

        line = re.sub("^([\s\n]*[。、！？!?ー～]+)+", "", line)
        line = re.sub("(.+?)\\1{3,}", "\\1\\1\\1", line)

        return line.strip().split('\n')

    def parse(self, line):
        """
        文を形態素解析してノイズ除去する
        @param:str line 形態素解析する文
        @return:list[str] 形態素解析してノイズ除去された文
        @return:list[str] 対応する品詞
        """
        words, parts = [], []

        node = self.tagger.parseToNode(line)
        while node:
            feature = node.feature.split(',')
            if feature[0] == "BOS/EOS" or node.feature in [".", "..", "!", "?"]:
                node = node.next
                continue

            if feature[0] == "名詞":
                if feature[1] in ["一般", "固有名詞", "サ変接続", "形容動詞語幹"]:
                    token = "noun_main"
                elif feature[1] == "代名詞":
                    token = "pronoun"
                else:
                    token = "noun_sub"
            elif feature[0] == "動詞":
                if feature[1] == "自立":
                    token = "verb_main"
                else:
                    token = "verb_sub"
            elif feature[0] == "形容詞":
                if feature[1] == "自立":
                    token = "adjective_main"
                else:
                    token = "adjective_sub"
            elif feature[0] == "副詞":
                token = "adverb"
            elif feature[0] == "助詞":
                token = "particle"
            elif feature[0] == "助動詞":
                token = "auxiliary_verb"
            elif feature[0] == "接続詞":
                token = "conjunction"
            elif feature[0] == "接頭詞":
                token = "prefix"
            elif feature[0] == "フィラー":
                token = "filler"
            elif feature[0] == "感動詞":
                token = "impression_verb"
            elif feature[0] == "連体詞":
                token = "pre_noun"
            elif node.surface == "...":
                token = "three_dots"
            elif node.surface in ["。", "！", "？", "!?"]:
                token = "phrase_point"
            elif node.surface == "、":
                token = "reading_point"
            else:
                token = "other"

            words.append(node.surface)
            parts.append(token)
            node = node.next

        return words, parts

    def need_check(self, parts):
        """
        文が need filter を満たすかを判定する
        @param:list[str] parts 品詞列
        @return:bool 文が need filter を満たすかどうか
        """
        for part in self.need:
            if self.need[part] and part not in parts:
                return False
        return True

    def needless_check(self, parts):
        """
        文が needless filter を満たすかを判定する
        @param:list[str] parts 品詞列
        @return:bool 文が needless filter を満たすかどうか
        """
        for part in parts:
            if self.needless.get(part):
                return False
        return True

    def dump_filter(self, words, parts):
        """
        文の dump filter を満たす品詞の単語のみを抽出する
        @param:list[str] words 単語列
        @param:list[str] parts 対応する品詞列
        @return:list[str] 文の dump filter を満たす品詞の単語のみを抽出した文
        """
        dump_words, dump_parts = [], []
        for word, part in zip(words, parts):
            if self.dump.get(part):
                dump_words.append(word)
                dump_parts.append(part)
        return dump_words, dump_parts

    def length_check(self, words):
        """
        文が length filter を満たすかを判定する
        @param:list[str] words 単語列
        @return:bool 文が length filter を満たすかどうか
        """
        return self.length['min'] <= len(words) <= self.length['max']

    def clean(self):
        """Wikipediaコーパスに形態素解析、正規化処理、フィルタリング処理を施す"""
        # 例外処理
        error_flag = False
        if not os.path.isfile(self.wiki_dump_path):
            print("{}: cannot find".format(self.wiki_dump_path))
            error_flag = True

        try:
            f_out = open(self.wiki_clean_path, 'w', encoding='utf-8')
        except:
            print("{}: file write error".format(self.wiki_clean_path))
            error_flag = True
        if self.output['part']:
            try:
                f_out_part = open(self.wiki_clean_part_path, 'w', encoding='utf-8')
            except:
                print("{}: file write error".format(self.wiki_clean_part_path))
                error_flag = True
        if self.output['yaml']:
            try:
                f_out_yaml = open(self.wiki_clean_yaml_path, 'w', encoding='utf-8')
            except:
                print("{}: file write error".format(self.wiki_clean_yaml_path))
                error_flag = True

        if error_flag:
            sys.exit(1)

        # Wikipediaコーパスは一行ずつ読み取る
        with open(self.wiki_dump_path, 'r', encoding='utf-8') as f_in:
            line = f_in.readline()
            tmp_title, tmp_doc_words, tmp_doc_parts = "", [], [] # あるタイトルの記事を一時的に蓄積する
            save_line_count = 0 # 保存した文の数

            while line:
                # タグ情報ならば飛ばして次の文をタイトルとして取得する
                if self.isTagStart(line):   # <doc
                    line = f_in.readline()
                    while line == "\n":
                        line = f_in.readline()
                    if self.output['yaml']:
                        tmp_title = unicodedata.normalize('NFKC', line).strip()
                elif self.isTagEnd(line):   # </doc
                    line_count = len(tmp_doc_words)
                    if line_count > 0:
                        f_out.write('\n'.join([' '.join(words) for words in tmp_doc_words]) + '\n')
                        tmp_doc_words.clear()
                        if self.output['part']:
                            f_out_part.write('\n'.join([' '.join(parts) for parts in tmp_doc_parts]) + '\n')
                            tmp_doc_parts.clear()
                        if self.output['yaml']:
                            doc_id_list = set(range(save_line_count, save_line_count+line_count))
                            yaml.dump({tmp_title : doc_id_list}, f_out_yaml, encoding='utf-8', allow_unicode=True)
                        save_line_count += line_count
                elif line != "\n":
                    line = unicodedata.normalize('NFKC', line).strip()
                    if self.check(line):
                        splited_lines = self.normalize(line)
                        for splited_line in splited_lines:
                            words, parts = self.parse(splited_line)
                            # フィルタリング
                            if self.need_check(parts) and self.needless_check(parts):
                                dump_words, dump_parts = self.dump_filter(words, parts)
                                if self.length_check(dump_words):
                                    tmp_doc_words.append(dump_words)
                                    if self.output['part']:
                                        tmp_doc_parts.append(dump_parts)

                line = f_in.readline()

            print("sum of all wikipedia data: {}".format(save_line_count))

        f_out.close()
        if self.output['part']:
            f_out_part.close()
        if self.output['yaml']:
            f_out_yaml.close()

def clean():
    """Wikipediaコーパスに形態素解析、正規化処理、フィルタリング処理を施す"""
    wikipedia_cleaner = WikipediaCleaner()
    wikipedia_cleaner.clean()

if __name__ == '__main__':
    clean()
