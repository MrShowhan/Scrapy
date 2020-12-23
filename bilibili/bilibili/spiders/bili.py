# -*- coding: utf-8 -*-
import scrapy
from bilibili.items import BilibiliItem
from bilibili.items import VideoItem
import json
import math
class BiliSpider(scrapy.Spider):
    name = 'bili'
    allowed_domains = ['bilibili.com']
    start_urls = ['https://api.bilibili.com/x/space/acc/info?mid=883968&jsonp=jsonp']

    def parse(self, response):
        item = BilibiliItem()
        result = json.loads(response.text)
        item['id'] = result.get('data').get('mid')
        item['name'] = result.get('data').get('name')
        item['basic_spacing'] = result.get('data').get('sign')
        item['certification'] = result.get('data').get('official').get('title')
        follower_url = 'https://api.bilibili.com/x/relation/stat?vmid={}&jsonp=jsonp'.format(item['id'])
        yield  scrapy.Request(follower_url,callback=self.relation_parse,meta={'item':item},priority=6)     #访问关注数和粉丝数网页

    def relation_parse(self,response):
        item = response.meta['item']
        result = json.loads(response.text)
        if int(result.get('data').get('follower')) > 1000:  #定义活跃用户，如果设置为Ture，则为全用户爬取
            item['following'] = result.get('data').get('following')
            item['follower'] = result.get('data').get('follower')
            upstat_url = 'https://api.bilibili.com/x/space/upstat?mid={}&jsonp=jsonp'.format(item['id'])
            yield  scrapy.Request(upstat_url,callback=self.space_parse,meta={'item':item},priority=7)           #访问播放量和点赞数网页
        #通过此up主的粉丝与关注列表，提取其他用户id进行遍历
        followings_url = 'https://api.bilibili.com/x/relation/followings?vmid={}&pn=1&ps=50&order=desc&jsonp=jsonp'.format(item['id'])
        yield scrapy.Request(followings_url,callback=self.get_other_id,meta={'id': item['id'],'referer':'followings'},priority=1)
        followers_url = 'https://api.bilibili.com/x/relation/followers?vmid={}&pn=1&ps=50&order=desc&jsonp=jsonp'.format(item['id'])
        yield scrapy.Request(followers_url, callback=self.get_other_id,meta={'id': item['id'], 'referer': 'followers'},priority=1)

    def space_parse(self,response):
        item = response.meta['item']
        result = json.loads(response.text)
        item['view'] = result.get('data').get('archive').get('view')
        item['likes'] = result.get('data').get('likes')
        notice_url = 'https://api.bilibili.com/x/space/notice?mid={}&jsonp=jsonp'.format(item['id'])
        yield scrapy.Request(notice_url, callback=self.notice_parse, meta={'item': item},priority=8)  # 访问公告网页

    def notice_parse(self, response):
        item = response.meta['item']
        result = json.loads(response.text)
        item['announcement'] = result.get('data')
        yield item
        video_url = 'https://api.bilibili.com/x/space/arc/search?mid={}&ps=50&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp'.format(item['id'])
        yield scrapy.Request(video_url, callback=self.video_parse, meta={'id': item['id']},priority=9)  # 访问视频连接网页


    def video_parse(self, response):
        data = json.loads(response.text)
        count = data.get('data').get('page').get('count')
        results = data.get('data').get('list').get('vlist')
        if count > 0 :
            for result in results:
                video_item = VideoItem()
                video_item['id']=response.meta['id']
                video_item['video_author']=result.get('author')
                video_item['video_title']=result.get('title')
                video_item['video_desc']=result.get('description')
                video_item['video_play']=result.get('play')
                video_item['video_length']=result.get('length')
                video_item['video_comment']=result.get('comment')
                bvid = result.get('bvid')
                video_item['video_bvid'] = 'https://www.bilibili.com/video/{}'.format(bvid)
                yield video_item
            if int(count) > 50:
                page = math.ceil(int(count)/50)
                id = response.meta['id']
                for i in range(2,page+1):
                    video_url = 'https://api.bilibili.com/x/space/arc/search?mid={}&ps=50&tid=0&pn={}&keyword=&order=pubdate&jsonp=jsonp'.format(
                        id,i)
                    yield scrapy.Request(video_url, callback=self.next_video_parse, meta={'id': id},priority=10)  # 翻页视频连接网页

    def next_video_parse(self, response):
        data = json.loads(response.text)
        results = data.get('data').get('list').get('vlist')
        for result in results:
            video_item = VideoItem()
            video_item['id'] = response.meta['id']
            video_item['video_author'] = result.get('author')
            video_item['video_title'] = result.get('title')
            video_item['video_desc'] = result.get('description')
            video_item['video_play'] = result.get('play')
            video_item['video_length'] = result.get('length')
            video_item['video_comment'] = result.get('comment')
            bvid = result.get('bvid')
            video_item['video_bvid'] = 'https://www.bilibili.com/video/{}'.format(bvid)
            yield video_item

    def get_other_id(self, response):
        id = response.meta['id']
        result = json.loads(response.text)
        total = int(result.get('data').get('total')) #获取总用户数量
        if total > 0:
            ids = result.get('data').get('list')
            for i in ids:
                other_id = i.get('mid')
                url = 'https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(other_id)
                yield scrapy.Request(url,callback=self.parse,priority=3)
            if total > 50 :
                page = math.ceil(int(total) / 50)
                if page > 5:
                    page = 5    #最大只能访问前5页
                for i in range(2, page + 1):
                    if response.meta['referer'] == 'followings':    #关注用户翻页
                        url = 'https://api.bilibili.com/x/relation/followings?vmid={}&pn={}&ps=50&order=desc&jsonp=jsonp'.format(
                            id, i)
                        yield scrapy.Request(url, callback=self.next_other_id, meta={'id': id},priority=2)  # 翻页
                    elif response.meta['referer'] == 'followers':   #粉丝用户翻页
                        url = 'https://api.bilibili.com/x/relation/followers?vmid={}&pn={}&ps=50&order=desc&jsonp=jsonp'.format(
                            id, i)
                        yield scrapy.Request(url, callback=self.next_other_id, meta={'id': id},priority=2)  # 翻页

    def next_other_id (self, response):
        result = json.loads(response.text)
        ids = result.get('data').get('list')
        for i in ids:
            other_id = i.get('mid')
            url = 'https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(other_id)
            yield scrapy.Request(url, callback=self.parse,priority=3)