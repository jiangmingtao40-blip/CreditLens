package com.zbkj.common.response.credit;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * 邀请统计响应
 */
@Data
public class InviteStatsResponse implements Serializable {
    private static final long serialVersionUID = 1L;

    private Integer totalInvited; // 累计邀请人数
    private Integer todayInvited; // 今日邀请人数
    private BigDecimal totalCommission; // 累计佣金
    private BigDecimal availableCommission; // 可用佣金
}
