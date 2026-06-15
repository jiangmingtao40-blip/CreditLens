package com.zbkj.common.response.credit;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

/**
 * 消费记录列表响应
 */
@Data
public class ConsumeListResponse implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 记录ID
     */
    private Long id;

    /**
     * 类型
     */
    private String type;

    /**
     * 类型描述
     */
    private String typeDesc;

    /**
     * 金额
     */
    private BigDecimal amount;

    /**
     * 描述
     */
    private String description;

    /**
     * 创建时间
     */
    private Date createTime;
}
