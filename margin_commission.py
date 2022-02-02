import backtrader as bt


class MyCommission(bt.CommInfoBase):
    params = (
        ('stocklike', False),  # 指定为期货模式 Designated as futures mode
        ('margin_percent', 0.1),  # 保证金比例 Margin level
        ('margin', 2000),  # 保证金 margin
        ('special', False)
    )

    # 自定义交易费用计算方式 Custom transaction cost calculation
    def _getcommission(self, size, price, pseudoexec):
        # 手续费 所有品种默认手续费 万分之三 Handling charge: the default handling charge for all varieties is 0.03%
        if self.p.special:
            return abs(size) * 120
        return abs(size) * price * 0.0003 * self.p.mult

    # 自定义保证金计算方式 custom margin calculation
    def get_margin(self, price):
        return price * self.p.margin_percent * self.p.mult


# 回测以及实盘合约配置 backtest and real market  of contract configuration
# 特别注意 动力煤 手续费比较高 远远超过万分之三，每手120元，做了特殊处理，加了字段special
# 涉及到动力煤的策略 初始化 设置手续费以及保证金的时候需要注意
quote_dict = {
    # 螺纹
    'rb2205.SHFE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 热卷
    'hc2205.SHFE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 沥青
    'bu2206.SHFE': {
        'size': 10,
        'pricetick': 2,
        'margin_percent': 0.1
    },
    # 橡胶
    'ru2205.SHFE': {
        'size': 10,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 纸浆
    'sp2205.SHFE': {
        'size': 10,
        'pricetick': 2,
        'margin_percent': 0.09
    },
    # 线材
    'wr2202.SHFE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 黄金
    'au2206.SHFE': {
        'size': 1000,
        'pricetick': 0.02,
        'margin_percent': 0.08
    },
    # 白银
    'ag2206.SHFE': {
        'size': 15,
        'pricetick': 1,
        'margin_percent': 0.12
    },
    # 沪铜
    'cu2203.SHFE': {
        'size': 5,
        'pricetick': 10,
        'margin_percent': 0.1
    },
    # 沪铝
    'al2203.SHFE': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 沪锌
    'zn2203.SHFE': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 沪铅
    'pb2203.SHFE': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 沪镍
    'ni2203.SHFE': {
        'size': 1,
        'pricetick': 10,
        'margin_percent': 0.1
    },
    # 沪锡
    'sn2203.SHFE': {
        'size': 1,
        'pricetick': 10,
        'margin_percent': 0.1
    },
    # 燃油
    'fu2205.SHFE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 不锈钢
    'ss2203.SHFE': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 黄豆一号
    'a2203.DCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.12
    },
    # 塑料
    'l2205.DCE': {
        'size': 5,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 聚丙烯
    'pp2205.DCE': {
        'size': 5,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 鸡蛋
    'jd2205.DCE': {
        'size': 5,
        'pricetick': 1,
        'margin_percent': 0.09
    },
    # PVC 聚氯乙烯
    'v2205.DCE': {
        'size': 5,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 豆油
    'y2205.DCE': {
        'size': 10,
        'pricetick': 2,
        'margin_percent': 0.08
    },
    # 棕榈油
    'p2205.DCE': {
        'size': 10,
        'pricetick': 2,
        'margin_percent': 0.1
    },
    # 玉米
    'c2205.DCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.11
    },
    # 玉米淀粉
    'cs2203.DCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.07
    },
    # 焦炭
    'j2205.DCE': {
        'size': 100,
        'pricetick': 0.5,
        'margin_percent': 0.2
    },
    # 纤维板
    'fb2202.DCE': {
        'size': 10,
        'pricetick': 0.5,
        'margin_percent': 0.1
    },
    # 生猪
    'lh2203.DCE': {
        'size': 16,
        'pricetick': 5,
        'margin_percent': 0.15
    },
    # 焦煤
    'jm2205.DCE': {
        'size': 60,
        'pricetick': 0.5,
        'margin_percent': 0.2
    },
    # 铁矿石
    'i2205.DCE': {
        'size': 100,
        'pricetick': 0.5,
        'margin_percent': 0.12
    },
    # 豆粕
    'm2205.DCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.08
    },
    # 黄豆二号
    'b2203.DCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.09
    },
    # 乙二醇
    'eg2205.DCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.11
    },
    # 粳米
    'rr2203.DCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.06
    },
    # 苯乙烯
    'eb2203.DCE': {
        'size': 5,
        'pricetick': 1,
        'margin_percent': 0.12
    },
    # 液化气
    'pg2203.DCE': {
        'size': 20,
        'pricetick': 1,
        'margin_percent': 0.11
    },
    # PTA 精对苯二甲酸
    'TA205.CZCE': {
        'size': 5,
        'pricetick': 2,
        'margin_percent': 0.08
    },
    # 纯碱
    'SA205.CZCE': {
        'size': 20,
        'pricetick': 1,
        'margin_percent': 0.09
    },
    # 白糖
    'SR205.CZCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.07
    },
    # 棉花
    'CF205.CZCE': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 菜油
    'OI205.CZCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.08
    },
    # 动力煤
    'ZC205.CZCE': {
        'size': 100,
        'pricetick': 0.2,
        'margin_percent': 0.4,
        'special': True,
    },
    # 菜粕
    'RM205.CZCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.08
    },
    # 甲醇
    'MA205.CZCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.08
    },
    # 硅铁
    'SF205.CZCE': {
        'size': 5,
        'pricetick': 2,
        'margin_percent': 0.12
    },
    # 锰硅
    'SM205.CZCE': {
        'size': 5,
        'pricetick': 2,
        'margin_percent': 0.12
    },
    # 苹果
    'AP205.CZCE': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.08
    },
    # 红枣
    'CJ205.CZCE': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.18
    },
    # 尿素
    'UR205.CZCE': {
        'size': 20,
        'pricetick': 1,
        'margin_percent': 0.07
    },
    # 花生
    'PK205.CZCE': {
        'size': 5,
        'pricetick': 2,
        'margin_percent': 0.08
    },
    # 玻璃
    'FG205.CZCE': {
        'size': 20,
        'pricetick': 1,
        'margin_percent': 0.09
    },
    # 棉纱
    'CY205.CZCE': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 短纤
    'PF205.CZCE': {
        'size': 5,
        'pricetick': 2,
        'margin_percent': 0.08
    },

}

# 主连合约配置 Main continuous contract configuration
zl_quote_dict = {
    # 螺纹
    'SHFE.rb': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 热卷
    'SHFE.hc': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 沥青
    'SHFE.bu': {
        'size': 10,
        'pricetick': 2,
        'margin_percent': 0.1
    },
    # 橡胶
    'SHFE.ru': {
        'size': 10,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 纸浆
    'SHFE.sp': {
        'size': 10,
        'pricetick': 2,
        'margin_percent': 0.09
    },
    # 线材
    'SHFE.wr': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 黄金
    'SHFE.au': {
        'size': 1000,
        'pricetick': 0.02,
        'margin_percent': 0.08
    },
    # 白银
    'SHFE.ag': {
        'size': 15,
        'pricetick': 1,
        'margin_percent': 0.12
    },
    # 沪铜
    'SHFE.cu': {
        'size': 5,
        'pricetick': 10,
        'margin_percent': 0.1
    },
    # 沪铝
    'SHFE.al': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 沪锌
    'SHFE.zn': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 沪铅
    'SHFE.pb': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 沪镍
    'SHFE.ni': {
        'size': 1,
        'pricetick': 10,
        'margin_percent': 0.1
    },
    # 沪锡
    'SHFE.sn': {
        'size': 1,
        'pricetick': 10,
        'margin_percent': 0.1
    },
    # 燃油
    'SHFE.fu': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 不锈钢
    'SHFE.ss': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 黄豆一号
    'DCE.a': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.12
    },
    # 塑料
    'DCE.l': {
        'size': 5,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 聚丙烯
    'DCE.pp': {
        'size': 5,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 鸡蛋
    'DCE.jd': {
        'size': 5,
        'pricetick': 1,
        'margin_percent': 0.09
    },
    # PVC 聚氯乙烯
    'DCE.v': {
        'size': 5,
        'pricetick': 1,
        'margin_percent': 0.1
    },
    # 豆油
    'DCE.y': {
        'size': 10,
        'pricetick': 2,
        'margin_percent': 0.08
    },
    # 棕榈油
    'DCE.p': {
        'size': 10,
        'pricetick': 2,
        'margin_percent': 0.1
    },
    # 玉米
    'DCE.c': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.11
    },
    # 玉米淀粉
    'DCE.cs': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.07
    },
    # 焦炭
    'DCE.j': {
        'size': 100,
        'pricetick': 0.5,
        'margin_percent': 0.2
    },
    # 纤维板
    'DCE.fb': {
        'size': 10,
        'pricetick': 0.5,
        'margin_percent': 0.1
    },
    # 生猪
    'DCE.lh': {
        'size': 16,
        'pricetick': 5,
        'margin_percent': 0.15
    },
    # 焦煤
    'DCE.jm': {
        'size': 60,
        'pricetick': 0.5,
        'margin_percent': 0.2
    },
    # 铁矿石
    'DCE.i': {
        'size': 100,
        'pricetick': 0.5,
        'margin_percent': 0.12
    },
    # 豆粕
    'DCE.m': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.08
    },
    # 黄豆二号
    'DCE.b': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.09
    },
    # 乙二醇
    'DCE.eg': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.11
    },
    # 粳米
    'DCE.rr': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.06
    },
    # 苯乙烯
    'DCE.eb': {
        'size': 5,
        'pricetick': 1,
        'margin_percent': 0.12
    },
    # 液化气
    'DCE.pg': {
        'size': 20,
        'pricetick': 1,
        'margin_percent': 0.11
    },
    # PTA 精对苯二甲酸
    'CZCE.TA': {
        'size': 5,
        'pricetick': 2,
        'margin_percent': 0.08
    },
    # 纯碱
    'CZCE.SA': {
        'size': 20,
        'pricetick': 1,
        'margin_percent': 0.09
    },
    # 白糖
    'CZCE.SR': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.07
    },
    # 棉花
    'CZCE.CF': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 菜油
    'CZCE.OI': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.08
    },
    # 动力煤
    'CZCE.ZC': {
        'size': 100,
        'pricetick': 0.2,
        'margin_percent': 0.4,
        'special': True,
    },
    # 菜粕
    'CZCE.RM': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.08
    },
    # 甲醇
    'CZCE.MA': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.08
    },
    # 硅铁
    'CZCE.SF': {
        'size': 5,
        'pricetick': 2,
        'margin_percent': 0.12
    },
    # 锰硅
    'CZCE.SM': {
        'size': 5,
        'pricetick': 2,
        'margin_percent': 0.12
    },
    # 苹果
    'CZCE.AP': {
        'size': 10,
        'pricetick': 1,
        'margin_percent': 0.08
    },
    # 红枣
    'CZCE.CJ': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.18
    },
    # 尿素
    'CZCE.UR': {
        'size': 20,
        'pricetick': 1,
        'margin_percent': 0.07
    },
    # 花生
    'CZCE.PK': {
        'size': 5,
        'pricetick': 2,
        'margin_percent': 0.08
    },
    # 玻璃
    'CZCE.FG': {
        'size': 20,
        'pricetick': 1,
        'margin_percent': 0.09
    },
    # 棉纱
    'CZCE.CY': {
        'size': 5,
        'pricetick': 5,
        'margin_percent': 0.1
    },
    # 短纤
    'CZCE.PF': {
        'size': 5,
        'pricetick': 2,
        'margin_percent': 0.08
    },
}
