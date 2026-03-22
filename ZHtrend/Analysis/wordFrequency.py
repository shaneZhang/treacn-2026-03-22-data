# -*- coding: utf-8 -*-
import jieba.analyse
from ZHtrend.DB import db

if __name__ == "__main__":
    word = db.WFGetWord()
    word_list = []
    for i in word:
        word_list.append(i[0])
        word_list.append(i[1])
    seg_list = jieba.cut_for_search(" ".join(word_list))
    tags = jieba.analyse.extract_tags(" ".join(word_list), withWeight=True, topK=30000)
    db.WFUPloadWF(tags)
    print("已经成功生成词频。")
