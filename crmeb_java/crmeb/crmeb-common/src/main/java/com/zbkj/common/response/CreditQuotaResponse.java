package com.zbkj.common.response;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

/**
 * 征信额度响应
 *  +----------------------------------------------------------------------
 *  | CRMEB [ CRMEB赋能开发者，助力企业发展 ]
 *  +----------------------------------------------------------------------
 *  | Copyright (c) 2016~2025 https://www.crmeb.com All rights reserved.
 *  +----------------------------------------------------------------------
 *  | Licensed CRMEB并不是自由软件，未经许可不能去掉CRMEB相关版权
 *  +----------------------------------------------------------------------
 *  | Author: CRMEB Team <admin@crmeb.com>
 *  +----------------------------------------------------------------------
 */
@Data
@ApiModel(value = "CreditQuotaResponse", description = "征信额度响应对象")
public class CreditQuotaResponse implements Serializable {

    private static final long serialVersionUID = 1L;

    @ApiModelProperty(value = "免费查询次数")
    private Integer freeCount;

    @ApiModelProperty(value = "是否为VIP用户")
    private Boolean isVip;

    @ApiModelProperty(value = "单次查询价格")
    private BigDecimal pricePerQuery;

    @ApiModelProperty(value = "已使用次数")
    private Integer totalUsed;

    @ApiModelProperty(value = "VIP过期时间")
    private Date vipExpireTime;
}
