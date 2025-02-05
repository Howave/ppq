import json

from ppq.core import *


class GraphFormatSetting():
    def __init__(self) -> None:
        # 有一些平台不支持Constant Op，这个pass会尝试将 Constant Operation 的输入转变为 Parameter Variable
        # Some deploy platform does not support constant operation, 
        # this pass will convert constant operation into parameter variable(if can be done).
        self.format_constant_op = True
        
        # 融合Conv和Batchnorm，不开这个 pass 八成要崩
        # Fuse Conv and Batchnorm Layer. This pass is necessary and curicial.
        self.fuse_conv_bn       = True
        
        # 将所有的parameter variable进行分裂，使得每个variable具有至多一个输出算子，不开八成也要崩
        # Split all parameter variables, making all variable has at most 1 output operation. 
        # This pass is necessary and curicial.
        self.format_paramters   = True
        
        # 一个你必须要启动的 Pass
        # This pass is necessary and curicial.
        self.format_cast        = True
        
        # 尝试从网络中删除所有与输出无关的算子和 variable，注意有一些平台很无聊，
        # 喜欢把量化参数秃着写在网络里，在这种情况下开启这个选项就要崩了。
        # Remove all unnecessary operations and variables(which are not link to graph output) from current graph,
        # notice that some platfrom use unlinked variable as quantization parameters, do not set this as true if so.
        self.delete_isolate     = True


class SSDEqualizationSetting():
    def __init__(self) -> None:
        # Equalization 优化级别，目前只支持level 1，对应 Conv--Relu--Conv 和 Conv--Conv 的拉平
        # optimization level, only support level 1 for now
        # you shouldn't modify this
        self.opt_level            = 1
        
        # 在计算scale的时候，所有低于 channel_ratio * max(W) 的值会被裁减到 channel_ratio * max(W)
        # channel ratio used to calculate equalization scale
        # all values below this ratio of the maximum value of corresponding weight
        # will be clipped to this ratio when calculating scale
        self.channel_ratio        = 0.5

        # loss的降低阈值，优化后的loss低于 原来的loss * 降低阈值, 优化才会发生
        # optimized loss must be below this threshold of original loss for algo to take effect
        self.loss_threshold       = 0.8
        
        # 是否对权重进行正则化
        # whether to apply layer normalization to weights
        self.layer_norm           = False

        # 算法迭代次数，3次对于大部分网络足够
        # num of iterations, 3 would be enough for most networks
        # it takes about 10 mins for one iteration
        self.iteration            = 3


class EqualizationSetting():
    def __init__(self) -> None:
        # Equalization 优化级别，如果选成 1 则不进行多分支拉平，如果选成 2，则进行跨越 add, sub 的多分支拉平
        # 不一定哪一个好，你自己试试
        # optimization level of layerwise equalization
        # 1 - single branch equalization(can not cross add, sub)
        # 2 - multi branch equalization(equalization cross add, sub)
        # don't know which one is better, try it by yourself.
        self.opt_level            = 1
        
        # Equalization 迭代次数，试试 1，2，3，10，100
        # algorithm iteration times, try 1, 2, 3, 10, 100
        self.iterations           = 10
        
        # Equalization 权重阈值，试试 0.5, 2
        # 这是个十分重要的属性，所有小于该值的权重不会参与运算
        # value threshold of equalization, try 0.5 and 2
        # it is a curical setting of equalization, value below this threshold won't get included in this optimizition.
        self.value_threshold      = .5 # try 0.5 and 2, it matters.
        
        # 是否在 Equalization 中拉平 bias
        # whether to equalize bias as well as weight
        self.including_bias       = False
        self.bias_multiplier      = 0.5
        
        # 是否在 Equalization 中拉平 activation
        # whether to equalize activation as well as weight
        self.including_act        = False
        self.act_multiplier       = 0.5

        # 暂时没用
        # for now this is a useless setting.
        self.self_check           = False


class ChannelSplitSetting():
    def __init__(self) -> None:
        # 所有需要分裂的层的名字，Channel Split 会降低网络执行的性能，你必须手动指定那些层要被分裂
        # interested layer names on which channel split is desired
        self.interested_layers = []
        # 分裂方向 - 可以是向上分裂或者向下分裂，每个层都要给一个哦
        # search direactions of layers in interested_layers, can be 'down' or 'up', each layer has one.
        self.search_directions = []
        # 要分裂多少 channel，数值越高则越多 channel 会被分裂
        # ratio of newly added channels
        self.expand_ratio      =  0.1
        # 还没看，我也不知道是什么
        # value split ratio 
        self.split_ratio       =  0.5
        # 是否添加一个小偏移项用来使得量化后的结果尽可能与浮点对齐。
        # cancel out round effect
        self.grid_aware        =  True


class AdvancedOptimizationSetting():
    def __init__(self) -> None:
        # 中间结果保存位置，可以选择 executor 或 cpu
        # executor - 将中间结果保存在 executor 的执行设备上(通常是cuda)
        # cpu - 将中间结果保存在 cpu memory 上
        # device to store all generated data.
        # executor - store data to executing device. (cuda)
        # cpu - store data to cpu memory.
        self.collecting_device    = 'executor' # executor or cpu
        
        # 每一轮迭代后是否校验优化结果，建议开启，延长执行时间，提升精度
        # whether to check optimization result after each iteration.
        self.check                = True
        
        # 偏移量限制，试试1, 2, 4
        # offset limitation used in this optimziation, try 1, 2, 4
        self.offset_limit         = 2.0
        
        # 对那些算子进行优化
        # optimizing operation types
        self.interested_types     = ['Gemm', 'Conv', 'ConvTranspose']
        
        # 迭代步长，必须控制在 0 ~ 0.5 之间
        # iteration step, must between 0 ~ 0.5
        self.step                 = 0.1
        
        # 是否执行 bias correction，推荐开启，延长执行时间，提升精度
        # whether to invoke bias correction procedure at the end of iteration
        self.correct_bias         = True
        
        # 最大尝试次数，延长执行时间，提升精度
        # max optmization trys.
        self.max_trys             = 8
        
        # 学习率，试试 3e-4, 1e-4, 5e-5, 1e-5
        # learning rate. try 3e-4, 1e-4, 5e-5, 1e-5
        self.lr                   = 1e-4


class ActivationQuantizationSetting():
    def __init__(self) -> None:
        # 激活值校准算法，不区分大小写，可以选择 minmax, kl, percentile, MSE
        # activation calibration method
        self.calib_algorithm = 'percentile'

        # 执行逐层激活值校准，延长执行时间，提升精度
        # whether to calibrate activation per - layer.
        self.per_layer_calibration = False

        # 激活值原地量化，设置为 True 且 USING_CUDA_KERNEL = True，则所有激活值原地量化，不产生额外显存
        # inplace quantization, if USING_CUDA_KERNEL = True, 
        # quantize all activations inplace, do not require extra memory.
        self.inplace_act_quantization = True


class ParameterQuantizationSetting():
    def __init__(self) -> None:
        # 参数校准算法，不区分大小写，可以选择 minmax, percentile(per-layer), kl(per-layer sym), MSE
        # parameter calibration method
        self.calib_algorithm = 'minmax'
        
        # 是否处理被动量化参数
        # whether to process passive parameters
        self.quantize_passive_parameter = True
        
        # 是否执行参数烘焙
        # whether to bake quantization on parameter.
        self.baking_parameter = True


class QuantizationFusionSetting():
    def __init__(self) -> None:
        # 一个你必须要启动的 Pass，修复所有算子上的定点错误
        # This pass is necessary and curicial, fix all quantization errors with your operation.
        self.refine_quantization = True
        
        # 一个你必须要启动的 Pass，删除无效定点。
        # PPQ 的定点过程与硬件设备一致，每一个算子都会尝试对它的输入和输出进行定点
        # 但在网络当中，当输入已经被上游算子进行了定点，则当前算子无需再对其输入进行定点
        # This pass is necessary and curicial, remove all unnecessary quantization from your graph.
        # PPQ executor quantizes each input tensor and output tensor of current operation.
        # however if input tensor has been quantized by upstream operations, then there is no need to quantize it again.
        self.remove_useless_quantization = True
        
        # conv - relu - add 联合定点
        # conv - relu - add joint quantization.
        # only gpu platform support this joint quantization optimization.
        self.fuse_conv_add = False
        
        # concat 联合定点
        # joint quantization with all concat inputs.
        self.fuse_concat   = False
        
        # computing operation - activation operation 联合定点
        # joint quantization with computing operations and following activations.
        self.fuse_activation = True
        
        # 省略被动算子的定点，保持算子前后定点信息一致
        # skip passive opeartion's input and output quantization, keep them with a same quantization scale and offset.
        self.fuse_passive_op = True


class TemplateSetting():
    """
    TemplateSetting 只是为了向你展示如何创建一个新的 Setting 并传递给相对应的 pass
        传递的过程在 ppq.quantization.quantizer.base.py 里面
   
    TemplateSetting just shows you how to create a setting class.
        parameter passing is inside ppq.quantization.quantizer.base.py

    Raises:
        TypeError: [description]

    Returns:
        [type]: [description]
    """
    def __init__(self) -> None:
        self.my_first_parameter = 'This Parameter just shows you how to create your own parameter.'


class Dispatching():
    def __init__(self, operation: str, platform: int) -> None:
        self.operation = operation
        self.platform  = platform


class DispatchingTable():
    def __init__(self) -> None:
        self.intro_0 = "Dispatching Table is a str -> TargetPlatform dictionary."
        self.intro_1 = "Any thing listed in this table will override the policy of PPQ dispatcher."
        self.intro_2 = "Example above shows you how to edit a valid dispatching table."
        self.attention = "All operation names that can not be found with your graph will be ignored."

        self.dispatchings = [
            Dispatching(operation='YOUR OEPRATION NAME', platform='TARGET PLATFORM(INT)'),
            Dispatching(operation='FP32 OPERATION NAME', platform=TargetPlatform.FP32.value),
            Dispatching(operation='SOI OPERATION NAME', platform=TargetPlatform.SHAPE_OR_INDEX.value),
            Dispatching(operation='DSP INT8 OPERATION NAME', platform=TargetPlatform.DSP_INT8.value),
            Dispatching(operation='TRT INT8 OPERATION NAME', platform=TargetPlatform.TRT_INT8.value),
            Dispatching(operation='NXP INT8 OPERATION NAME', platform=TargetPlatform.NXP_INT8.value),
            Dispatching(operation='PPL INT8 OPERATION NAME', platform=TargetPlatform.PPL_CUDA_INT8.value),
        ]
    
    def append(self, operation: str, platform: Union[int, TargetPlatform]):
        assert isinstance(platform, int) or isinstance(platform, TargetPlatform), (
            'Your dispatching table contains a invalid setting of operation {operation}, '
            'All platform setting given in dispatching table is expected given as int or TargetPlatform instance, '
            f'however {type(platform)} was given.'
        )
        if isinstance(platform, TargetPlatform): platform = platform.value
        self.dispatchings.append(Dispatching(operation, platform))


class QuantizationSetting():
    def __init__(self) -> None:
        # 子图切分与调度算法，可从 'aggresive', 'conservative', 'PPLNN' 中三选一，不区分大小写
        self.dispatcher                      = 'conservative'
        
        self.graph_format_setting            = GraphFormatSetting()
        
        # ssd with loss check equalization 相关设置
        # may take longer time(about 30min for default 3 iterations), but guarantee better result than baseline
        # should not be followed by a plain equalization when turned on
        self.ssd_equalization                = False
        self.ssd_setting                     = SSDEqualizationSetting()

        # layer wise equalizition 与相关配置
        self.equalization                    = True
        self.equalization_setting            = EqualizationSetting()
        
        # OCS channel split configuration
        self.channel_split                   = False
        self.channel_split_setting           = ChannelSplitSetting()

        # activation 量化与相关配置
        self.quantize_activation             = True
        self.quantize_activation_setting     = ActivationQuantizationSetting()

        # 参数量化与相关配置 
        self.quantize_parameter              = True
        self.quantize_parameter_setting      = ParameterQuantizationSetting()

        # 是否启动 advanced_optim 优化算法，该算法整合了 adaround 和 bias correction 算法的功能，
        self.advanced_optimization           = False
        self.advanced_optimization_setting   = AdvancedOptimizationSetting()

        # 量化融合相关配置
        self.fusion                          = True
        self.fusion_setting                  = QuantizationFusionSetting()
        
        # extension setting 只是一个空白的占位符，用来向你展示如何创建一个自定义的 setting 并传递参数。
        # extension setting shows you how to create a setting and pass parameter to passes.
        # see ppq.quantization.quantizer.base.py
        self.extension                       = False
        self.extension_setting               = TemplateSetting()

        # 程序签名
        self.version                         = PPQ_VERSION
        self.signature                       = PPQ_NAME
        
        # 算子调度表，你可以编辑它来手动调度算子。
        self.dispatching_table               = DispatchingTable()

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, 
                          sort_keys=True, indent=4, ensure_ascii=False)


class QuantizationSettingFactory:
    @ staticmethod
    def default_setting() -> QuantizationSetting:
        return QuantizationSetting()

    @ staticmethod
    def pplcuda_setting() -> QuantizationSetting:
        default_setting = QuantizationSetting()
        default_setting.equalization = False
        default_setting.fusion_setting.fuse_conv_add = True
        return default_setting

    @ staticmethod
    def dsp_setting() -> QuantizationSetting:
        default_setting = QuantizationSetting()
        default_setting.equalization = True
        default_setting.fusion_setting.fuse_conv_add = False
        return default_setting
    
    @ staticmethod
    def nxp_setting() -> QuantizationSetting:
        default_setting = QuantizationSetting()
        default_setting.equalization = False
        default_setting.fusion_setting.fuse_conv_add = False
        return default_setting

    @ staticmethod
    def from_json(json_str: str) -> QuantizationSetting:
        setting = QuantizationSetting()
        setting_dict = json.loads(json_str)
        
        if 'version' not in setting_dict:
            ppq_warning('Can not find a valid version from your json input, input might not be correctly parsed.')
        else:
            version = setting_dict['version']
            if version < PPQ_VERSION:
                ppq_warning(f'You are loading a json quantization setting created by PPQ of another version: '
                            f'({version}), input setting might not be correctly parsed. '
                            'And all missing attributes will set as default without warning.')
        
        if not isinstance(setting_dict, dict):
            raise TypeError('Can not load setting from json string, '
                            f'expect a dictionary deserialzed from json here, '
                            f'however {type(setting_dict)} was given.')
        
        for key, value in setting_dict.items():
            if key in setting.__dict__:
                setting.__dict__[key] = value
            else:
                ppq_warning(
                    f'Unexpected attribute ({key}) was found. '
                    'This might because you are using a setting generated by PPQ with another version. '
                    'We will continue setting loading progress, while this attribute will be skipped.')
        return setting
