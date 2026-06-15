package com.zbkj.common.response;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * 支付状态响应
 */
@Data
public class PayStatusResponse implements Serializable {
    private static final long serialVersionUID = 1L;

    private String orderId;
    private Integer status; // 0-待支付 1-支付成功 2-支付失败 3-已取消
    private String statusText;
    private BigDecimal amount;
    private String payTime;
}
