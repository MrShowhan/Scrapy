# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import  pymysql
from bilibili.items import BilibiliItem
from bilibili.items import VideoItem

class BilibiliPipeline(object):

    def open_spider(self, spider):
        """
        该方法用于创建数据库连接池对象并连接数据库
        """
        db = spider.settings.get('MYSQL_DB_NAME', 'bili')
        host = spider.settings.get('MYSQL_HOST', 'localhost')
        port  = spider.settings.get('MYSQL_PORT', 3306)
        user = spider.settings.get('MYSQL_USER', 'root')
        passwd = spider.settings.get('MYSQL_PASSWORD', '12593')

        self.db_conn  = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset='utf8')
        self.db_cur = self.db_conn.cursor()

    def process_item(self, item, spider):
        if isinstance(item,BilibiliItem):
            # 使用execute方法执行SQL语句
            sql = "create table if not exists bilibili(id int primary key auto_increment ,name char(20),basic_spacing text,following int," \
                  "follower int,view int,likes int,certification char(20),announcement longtext)"
            try:
                # 执行sql语句
                self.db_cur.execute(sql)
                self.insert_use_db(item)
                # 提交到数据库执行
                self.db_conn.commit()
                print('MySQLbilibili保存成功',item)
            except:
                self.db_conn.rollback()
                print('MySQLbilibili保存失败', item)

        elif isinstance(item, VideoItem):
            # 使用execute方法执行SQL语句
            sql = "create table if not exists video(id int primary key auto_increment ,author varchar(100),title varchar(100),introduction longtext,play int," \
                  "videotime varchar(100),comments int,link varchar(100))"
            try:
                # 执行sql语句
                self.db_cur.execute(sql)
                self.insert_video_db(item)
                # 提交到数据库执行
                self.db_conn.commit()
                print('MySQLview保存成功', item)
            except:
                self.db_conn.rollback()
                print('MySQLview保存失败', item)
        else:
            print('无法保存')

    def insert_use_db(self, item):
        """
        sql语句构造方法
        """
        values =(
            item['name'],
            item['basic_spacing'],
            item['following'],
            item['follower'],
            item['view'],
            item['likes'],
            item['certification'],
            item['announcement']
        )
        sql = 'INSERT INTO bilibili(name,basic_spacing,following,follower,view,likes,certification,announcement) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
        self.db_cur.execute(sql, values)

    def insert_video_db(self, item):
        """
        sql语句构造方法
        """
        values =(
            item['video_author'],
            item['video_title'],
            item['video_desc'],
            item['video_play'],
            item['video_length'],
            item['video_comment'],

            item['video_bvid'],
        )
        sql = 'INSERT INTO video(author,title,introduction,play,videotime,comments,link) VALUES(%s,%s,%s,%s,%s,%s,%s)'
        self.db_cur.execute(sql, values)

    def close_spider(self, spider):
        """
        该方法用于关闭数据库
        """
        self.db_conn.close()





# class BilibiliVideoPipeline(object):
#     def process_item(self, item, spider):
#         if isinstance(item,VideoItem):
#             print('video管道',item)
#

