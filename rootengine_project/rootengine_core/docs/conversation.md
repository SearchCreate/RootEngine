
# 其他
变量名体现绝对属性，
文件名、目录名体现相对属性
在extra.type加"null"  
注意：  
记忆模块叫：Memory  
整个记忆模块的reif条目叫：conversation  
记忆模块的reif条目的内容(reif_content)骄傲：messages
# 简介

# 功能

# 类
## 属性
### 1、self.conversation
memory维护的对话条目
## 方法
### r__init__
初始化
### add

### delete

### validate（self）  ->  Ture

校验此时的的self.conversation是否符合格式
1. 先校验是否符合reif_entry
2. 再校验是否符合reif_content_conversation
3. 若校验成功 return Ture