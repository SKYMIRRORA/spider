# spider
## 爬虫数据收集
###  1、获取bv号
    spider/ex1_get_bv_nub.py
### 2、筛选没下载的bv号
    spider/ex27_undown.py
### 3、获取视屏
    spider/ex26_down_load_bvs.py
### 4、删除无效视频
    spider/ex20_delete_video.py
### 5、推理视频
    spider/ex4_inf_down_video.py
### 6、爬虫数据内部清洗
### 7、数据融合



#sudo apt install golang

go env -w GO111MODULE=on #启用Go Moledules
go env -w  GOPROXY=https://goproxy.io #使用官方代理
一次性运行FastestBibiliDownloader 程序入口在cmd/start-concurrent-engine.go，只需要
go run cmd/start-concurrent-engine.go -t (aid/bvid/upid) -v (id)

ex1_get_bvs 获取bv号

##更新get_urls
获取到的bv号直接添加到all_bvs




