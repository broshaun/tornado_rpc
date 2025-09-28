# 微服务主服务

```当前服务用于转发至其它服务的服务```


### docker镜像编译
- docker build -t rpc:master .

### 正式环境部署镜像
- docker-compose up

### 正式环境停止镜像
- docker-compose down

### 配置
#### app/config 配置项目设定
- DEBUG=True 为开发环境
- EBUG=False 为生产环境
