# 证券市场用户交易行为的图像分析方法
在证劵交易所领域，曾经发生用户证券账号被盗事件，导致客户资产损失，例如：黑客获得了用户A的证券账号密码，利用多次的低买高卖将资产转移，本文中针对此类对敲欺诈的场景，采用将用户交易数据转换为点阵图片，利用Amazon SageMaker 图像分类算法ResNet 进行模型训练和推理，得到了很好的效果。这种将交易数据转换为图像分类的方式简化了通常的特征提取的复杂度，可以作为防欺诈或者交易行为特征识别的方式的新的尝试。

在此项目中主要展示了数据样本的制作过程的代码，以及通过lamba实现具体业务流程的实例。具体的模型训练引用公共的图像分类算法。

## License
This library is licensed under the MIT-0 License. See the LICENSE file.

## 环境准备
本机安装python3.9版本环境。并且提前准备如下几个依赖包的安装

python -m pip install requests
python -m pip install matplotlib
python -m pip install numpy
python -m pip install opencv-python

## 样本数据生成
1. 获取k线

执行K线生成脚本generateKline.py ，生成某日的K线数据，本案例从alphavantage获取美股最新的Coinbase 80条5分钟k线。免费APIkey请自行从alphavantage官网申请。

2. 生成黑客用户交易记录

执行脚本genRandomHackerTrades.py ，生成模拟黑客交易记录表格。模拟逻辑为：

    * 找到Top 10 的COIN的5分钟k线数据中超过5%波幅的k线数据。
    * 随机选择3-5个5分钟k线，生成低价买入的成交价格。生成高价卖出的成交价格。
    * 生成csv文件，分别存放到 ./buy/ 和./sell/目录。生成文件样例

3. 生成用户交易记录

执行脚本genNormal.py,生成模拟正常用户交易记录数据。在实际的证券交易所风控可获取实际用户数据生成记录。本案例中的模拟逻辑是：随机获取COIN的5分钟k线，生成1-2个买卖记录。

``` python
python genNormal.py
```
	
执行脚本genRandomHackerTrades.py 生成模拟的黑客交易记录数据。模拟逻辑是：获取COIN日k线中的top 10价格振幅最大的k线单元，然后随机从top10中选择3个单元，模拟生成低买高卖的点位。

``` python
python genRandomHackerTrades.py
```
4. 将交易记录转换为图像

``` python
python generateNormalImg.py
```


## 模型训练与发布
经过以上的步骤，在traindata目录下，我们获得了hacker 和normal 两个类别的图像训练数据。下面就可以采用Amazon Sagemaker的内置算法resNet 进行图像分类模型训练了。
我们采用图像分类算法来进行交易行为识别，在Amazon SageMaker 里面内置了resNet 图像分类算法。我们可以方便的采用此[算法示例](https://sagemaker-examples.readthedocs.io/en/latest/introduction_to_amazon_algorithms/imageclassification_caltech/Image-classification-lst-format-highlevel.html)的notebook完成训练过程。
1. 首先通过[im2rec.py](https://github.com/apache/incubator-mxnet/blob/master/tools/im2rec.py) 生成lst文件

``` python
 python ./im2rec.py my_data ./traindata --list --recursive --train-ratio .75 --exts .jpg
```

2. 将.lst文件与jpg文件上传到 S3 bucket的四个指定目录。

3.按照()[]的jpg文件图像分类的实例步骤进行训练和部署。

## 业务流程设计参考：
在证券交易所，可以选择合适的触发时机来触发用户是否有欺诈行为的推理过程。例如在每天用户出金时实时推理或者每天晚上批量推理的方式。 我们按照实时推理的方式实现如下的业务流程。
![](./img/businessProcess.png)

1. 业务测发送触发消息到AWS SQS，消息体接口中具备基本的用户id信息。
2. Lambda接收到SQS消息，从交易数据库获取用户的24小时交易信息，获取涉及的交易对的5分钟k线数据，生成此用户的交易行为图像，图像的格式也采用相同的处理：去掉k线显示；去掉x，y轴刻度显示；图像尺寸缩小到2.5英寸*2.1英寸，dpi=100。
3. 生成的用户交易图像 调用实时推理接口，我们就可以获得推理结果，此用户行为是否是欺诈行为，如果概率超过90%，我们写入风控表。

Lambda函数实现了SQS消息接收，图像生成，实时推理的过程，参考例程[imageClassify.py](./lambda/imageClassify.py)