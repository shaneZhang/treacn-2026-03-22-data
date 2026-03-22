# -*- coding: utf-8 -*-
import pymysql
from pymysql.converters import escape_string

# 注意：在Python 3中，建议使用pymysql而不是MySQLdb
# 需要先安装pymysql: pip install pymysql

conn = pymysql.connect(
    host="192.168.31.112",
    user="zhangyuqing",
    password="zhangyuqing",
    database="ZHTrend",
    use_unicode=True,
    charset="gbk",
    connect_timeout=3600
)


def AlgoGetQuestionIDs():
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT questionid FROM `answer` WHERE DATE_FORMAT(posttime,'%Y-%m-%d')=DATE_FORMAT(now(),'%Y-%m-%d')")
    ret = cursor.fetchall()
    cursor.close()
    return ret


def AlgoGetQuestionID(questionid):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM `answer` WHERE DATE_FORMAT(posttime,'%Y-%m-%d')=DATE_FORMAT(now(),'%Y-%m-%d') and questionid = %s",
        (questionid[0],))
    ret = cursor.fetchall()
    cursor.close()
    return ret


def AlgoGetFollowers(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT follower FROM `user` WHERE id = %s", (user_id,))
    ret = cursor.fetchall()
    cursor.close()
    return ret


def AlgoDropTable():
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS Trend_temp;")
    cursor.close()


def AlgoCreateTable():
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE Trend_temp (`questionid` varchar(255) NOT NULL, `rank` int NOT NULL, PRIMARY KEY (`questionid`));")
    cursor.close()


def AlgoInsertTable(allRank):
    cursor = conn.cursor()
    for i in allRank:
        cursor.execute("INSERT INTO Trend_temp VALUES (%s, %s)", (i[0], i[1]))
    conn.commit()
    cursor.close()


def AlgoSwitchTable(table):
    cursor = conn.cursor()
    cursor.execute("RENAME TABLE " + table + " to Trend_Old;")
    cursor.execute("RENAME TABLE Trend_temp to " + table + ";")
    cursor.execute("DROP TABLE IF EXISTS Trend_Old;")


def WFGetWord():
    cursor = conn.cursor()
    cursor.execute("SELECT description, profession FROM user;")
    ret = cursor.fetchall()
    cursor.close()
    return ret


def WFUPloadWF(tags):
    cursor = conn.cursor()
    for i in tags:
        sql = "INSERT INTO wordfrequency VALUES (%s, %s)"
        cursor.execute(sql, (i[0], i[1]))
    conn.commit()
    cursor.close()


def SITEGetTrend(date):
    # 使用参数化查询避免SQL注入
    sql = "SELECT DISTINCT title, answer.questionid, rank FROM trend_%s, answer WHERE trend_%s.questionid = answer.questionid ORDER BY rank DESC LIMIT 30;" % (
        date, date)
    try:
        site_conn = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            database="ZHTrend",
            use_unicode=True,
            charset="gbk",
            connect_timeout=3600
        )
        cursor = site_conn.cursor()
        cursor.execute(sql)
        title = cursor.fetchall()
        cursor.close()
        site_conn.close()
        return title
    except Exception:
        fail = [["没找到这一天的趋势数据", "#", "0"]]
        return fail


def SpiderActivityGetID():
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM `user` WHERE follower > 800 AND receivethank > 4000;")
    ret = cursor.fetchall()
    cursor.close()
    return ret


def SpiderActivityInsert(
        user_id, questionId, answerId, title, total, approve, content, posttime, edittime, comment):
    # 使用参数化查询
    content = escape_string(content)
    cursor = conn.cursor()
    params = {"user_id": user_id, "questionId": questionId, "answerId": answerId,
              "title": title, "total": total, "approve": approve}
    sql = """INSERT INTO answer VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, (
        params["user_id"], params["questionId"], params["answerId"],
        params["title"], params["total"], params["approve"],
        content, posttime, edittime, comment))
    conn.commit()
    cursor.close()


def SpiderActivityCreateDB():
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS answer;")
    cursor.execute("""CREATE TABLE `answer` (
    `id` VARCHAR(255) NOT NULL,
    `questionid` VARCHAR(255) NOT NULL,
    `answerid` VARCHAR(255) NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `total` INT NOT NULL,
    `approve` INT UNSIGNED ZEROFILL NOT NULL,
    `content` LONGTEXT NOT NULL,
    `posttime` DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
    `edittime` DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
    `comment` INT UNSIGNED ZEROFILL NOT NULL,
    PRIMARY KEY (`answerid`, `questionid`),
    CONSTRAINT `usertoanswer` FOREIGN KEY (`id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=gbk;
    """)
    cursor.close()


def SpiderUserCreateDB():
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS user;")
    cursor.execute("""CREATE TABLE `user` (
            `id` VARCHAR(255) NOT NULL UNIQUE,
            `name` VARCHAR(255) NULL,
            `description` VARCHAR(2047) NULL,
            `profession` VARCHAR(255) NULL,
            `sex` VARCHAR(255) NULL,
            `answer` INT UNSIGNED ZEROFILL NOT NULL,
            `share` INT UNSIGNED ZEROFILL NOT NULL,
            `question` INT UNSIGNED ZEROFILL NOT NULL,
            `collection` INT UNSIGNED ZEROFILL NOT NULL,
            `receiveupprove` INT UNSIGNED ZEROFILL NOT NULL,
            `receivethank` INT UNSIGNED ZEROFILL NOT NULL,
            `receivecollect` INT UNSIGNED ZEROFILL NOT NULL,
            `follower` INT UNSIGNED ZEROFILL NOT NULL,
            `following` INT UNSIGNED ZEROFILL NOT NULL,
            `spsonsorlive` INT UNSIGNED ZEROFILL NOT NULL,
            `interesttopic` INT UNSIGNED ZEROFILL NOT NULL,
            `interestcolumn` INT UNSIGNED ZEROFILL NOT NULL,
            `interestquestion` INT UNSIGNED ZEROFILL NOT NULL,
            `interestcollection` INT UNSIGNED ZEROFILL NOT NULL,
            PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=gbk;
            """)
    cursor.close()


def SpiderUserGetIDs():
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user;")
    ret = cursor.fetchall()
    cursor.close()
    return ret


def SpiderUserInsert(user_id, name, description, profession, sex, answer, share, question, collection,
                     receiveupprove,
                     receivethank, receivecollect, follower, following, spsonsorlive, interesttopic, interestcolumn,
                     interestquestion, interestcollection):
    cursor = conn.cursor()
    # 使用参数化查询和正确的字符串转义
    description = escape_string(description)
    profession = escape_string(profession)
    sql = """INSERT INTO user VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, (
        user_id, name, description, profession, sex, answer, share, question, collection,
        receiveupprove, receivethank, receivecollect, follower, following, spsonsorlive,
        interesttopic, interestcolumn, interestquestion, interestcollection
    ))
    conn.commit()
    cursor.close()
