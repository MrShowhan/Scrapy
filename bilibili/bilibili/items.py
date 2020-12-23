# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BilibiliItem(scrapy.Item):
    id = scrapy.Field()                #id
    name = scrapy.Field()               #账号名称
    basic_spacing = scrapy.Field()      #简介
    following = scrapy.Field()          #关注数量
    follower = scrapy.Field()           #粉丝数量
    view = scrapy.Field()               #播放量
    likes = scrapy.Field()              #点赞数
    certification = scrapy.Field()      #认证标签
    announcement = scrapy.Field()       #公告


class VideoItem(scrapy.Item):
    id = scrapy.Field()  # id
    video_author = scrapy.Field()    #作者昵称
    video_title = scrapy.Field()    # 视频标题
    video_desc = scrapy.Field()     # 视频简介
    video_bvid = scrapy.Field()     # 视频连接
    video_play = scrapy.Field()    #被播放次数
    video_length = scrapy.Field()     #视频时长
    video_comment = scrapy.Field()  #评论数


