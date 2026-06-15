package com.zbkj.common.response.credit;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * VIP套餐响应
 */
@Data
public class VipPackageResponse implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 套餐ID
     */
    private Long id;

    /**
     * 套餐名称
     */
    private String name;

    /**
     * 有效天数
     */
    private Integer days;

    /**
     * 价格
     */
    private BigDecimal price;

    /**
     * 原价
     */
    private BigDecimal originalPrice;

    /**
     * 赠送查询次数
     */
    private Integer queryCount;

    /**
     * 描述
     */
    private String description;

    /**
     * 是否推荐
     */
    private Boolean isRecommend;
}
