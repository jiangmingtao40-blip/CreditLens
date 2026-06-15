package com.zbkj.common.model.credit;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

/**
 * VIP套餐实体类
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("credit_vip_package")
public class CreditVipPackage implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 套餐ID
     */
    @TableId(value = "id", type = IdType.AUTO)
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
     * 排序
     */
    private Integer sort;

    /**
     * 状态：0下架 1上架
     */
    private Integer status;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 更新时间
     */
    private Date updateTime;

    /**
     * 是否删除：0否 1是
     */
    private Integer isDeleted;
}
