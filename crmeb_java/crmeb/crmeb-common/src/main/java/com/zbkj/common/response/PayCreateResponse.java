package com.zbkj.common.response;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * 支付创建响应
 */
@Data
public class PayCreateResponse implements Serializable {
    private static final long serialVersionUID = 1L;

    private String orderId;
    private BigDecimal amount;
    private String payUrl;
    private String qrCode;
    private Long expireTime;
}
