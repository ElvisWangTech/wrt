# wrt
WRT is a realtime translator using whisper.

## 待解决的问题：

- ~~想实现逐行实时显示~~
- 想优先用gpu运算  
- 想优化下transcribe方法，现在每30s一个片段有点卡  
- 想从本地加载模型，且加载过程不会卡住主程序  
- 想用pyinstaller打包，且包含模型，安装的时候直接装到~/.cache目录  
- 想提升预加载的速度  
- 导出文本还没有实现  

## bugs:  
- 再次运行signals没有捕获  
- 孤儿线程问题，需要在退出的时候退出所有线程
