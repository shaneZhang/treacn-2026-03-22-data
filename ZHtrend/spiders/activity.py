# -*- coding: utf-8 -*-
import os
import sys
import datetime
import scrapy
import re
from ZHtrend.DB import db


class ActivitySpider(scrapy.Spider):
    name = "activity"

    def start_requests(self):
        # db.SpiderActivityCreateDB()
        ids = db.SpiderActivityGetID()
        for i in ids:
            url = "https://www.zhihu.com/people/" + i[0] + "/answers"
            yield scrapy.Request(url=url, callback=lambda response, user_id=i[0]: self.parseAnswer(response, user_id))

    def parseAnswer(self, response, user_id):
        question = response.css(".ContentItem-title").re('href="(.*)">')
        question_count = len(question)
        for i in range(question_count + 1):
            url = "https://www.zhihu.com" + question[i]
            yield scrapy.Request(url=url, callback=lambda response, uid=user_id: self.parseQuestion(response, uid))

    def parseQuestion(self, response, user_id):
        test_dir = os.path.join(os.path.dirname(__file__), "test")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        filename = os.path.join(test_dir, user_id + "_.html")
        with open(filename, 'wb') as f:
            f.write(response.body)

        questionId = response.url.split("/")[-3]
        answerId = response.url.split("/")[-1]
        if not response.xpath('//*[@id="zh-question-title"]/h2/a').re(">\n(.*)\n</a>"):
            return
        title = response.xpath('//*[@id="zh-question-title"]/h2/a').re(">\n(.*)\n</a>")[0]
        total = response.css('.zh-answers-title').re(">查看全部 (.*) 个回答<")[0]
        approve = response.xpath('//*[@id="zh-question-answer-wrap"]/div/div[1]/button[1]/span[1]').re(">(.*)<")[0]

        content = response.css(".zm-editable-content").extract()[
            len(response.css(".zm-editable-content").extract()) - 1]
        posttime = ""
        if response.css('.answer-date-link').re('发布于 (.*)" target="_blank"'):
            posttime = response.css('.answer-date-link').re('发布于 (.*)" target="_blank"')[0]
        else:
            posttime = response.css('.answer-date-link').re('发布于 (.*)</a>')[0]
        edittime = posttime
        if response.xpath('//*[@id="zh-question-answer-wrap"]/div/div[4]/div/a[1]').re('编辑于 (.*)</a>'):
            edittime = \
                response.xpath('//*[@id="zh-question-answer-wrap"]/div/div[4]/div/a[1]').re(
                    '编辑于 (.*)</a>')[0]
        posttime = self.formatDate(posttime)
        edittime = self.formatDate(edittime)
        comment = 0
        if response.xpath('//*[@id="zh-question-answer-wrap"]/div/div[4]/div/a[2]').re("</i>(.*) 条评论"):
            comment = \
                response.xpath('//*[@id="zh-question-answer-wrap"]/div/div[4]/div/a[2]').re(
                    "</i>(.*) 条评论")[0]
        db.SpiderActivityInsert(
            user_id, questionId, answerId, title, total, approve, content, posttime, edittime, comment)
        os.remove(filename)

    def formatDate(self, pre):
        today = datetime.datetime.now()
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=2))
        ret = ""
        if re.search("昨天", pre):
            ret = yesterday.strftime("%Y-%m-%d ") + pre[4:] + ":00"
        elif re.search("[012][0-9]:[0-5][0-9]", pre):
            ret = today.strftime("%Y-%m-%d ") + pre[4:] + ":00"
        else:
            ret = pre + " 00:00:00"
        return ret
