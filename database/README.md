## 后台数据库更新
### 简介
该模块提供后台数据自动更新功能，为前台页面展示最新的数据提供支持。设置自动更新时间，程序自动执行，根据设置来更新最新的数据。

### 文件介绍
1. db\_summary.md  
	介绍数据库中各个表格的含义，以及字段简介，内容展示
2. manage\_server.py  
	更新主程序，该文件来启动各个小模块进行自动执行更新数据库
3. tasks库  
	该库存放各个更新程序

该程序仍然可以优化，提取基本模块，往后来人可以好好做，我应该是没时间做了，太多事情要做了。
以下是可以优化的几点：

1. 数据库操作使用orm
2. 提取更多公共模块
3. 更友善的输出结果 