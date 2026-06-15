package com.zbkj.common.response;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * 征信佣金响应
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
@ApiModel(value = "CreditCommissionResponse", description = "征信佣金响应对象")
public class CreditCommissionResponse implements Serializable {

    private static final long serialVersionUID = 1L;

    @ApiModelProperty(value = "累计佣金")
    private BigDecimal totalCommission;

    @ApiModelProperty(value = "可提现佣金")
    private BigDecimal availableCommission;

    @ApiModelProperty(value = "冻结佣金")
    private BigDecimal frozenCommission;

    @ApiModelProperty(value = "累计邀请人数")
    private Integer totalInvites;

    @ApiModelProperty(value = "累计收益")
    private BigDecimal totalEarnings;
}
