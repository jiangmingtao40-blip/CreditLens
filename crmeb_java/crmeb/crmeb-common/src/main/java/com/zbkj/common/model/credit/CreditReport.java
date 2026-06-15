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
 * 征信报告实体类
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("credit_report")
public class CreditReport implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 报告ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 任务ID
     */
    private String taskId;

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 文件名
     */
    private String fileName;

    /**
     * 文件路径
     */
    private String filePath;

    /**
     * 文件大小(字节)
     */
    private Long fileSize;

    /**
     * 状态：uploaded/processing/completed/failed
     */
    private String status;

    /**
     * 信用评分
     */
    private Integer creditScore;

    /**
     * 风险等级：低风险/中风险/高风险
     */
    private String riskLevel;

    /**
     * 个人信息(JSON)
     */
    private String personalInfo;

    /**
     * 信贷记录(JSON)
     */
    private String creditRecords;

    /**
     * 逾期记录(JSON)
     */
    private String overdueRecords;

    /**
     * 查询记录(JSON)
     */
    private String queryRecords;

    /**
     * 公共记录(JSON)
     */
    private String publicRecords;

    /**
     * 风险提示(JSON数组)
     */
    private String riskTips;

    /**
     * 建议(JSON数组)
     */
    private String suggestions;

    /**
     * 错误信息
     */
    private String errorMessage;

    /**
     * OCR识别原文
     */
    private String ocrText;

    /**
     * AI分析原文
     */
    private String aiAnalysis;

    /**
     * 消费金额
     */
    private BigDecimal costAmount;

    /**
     * 是否免费：0否 1是
     */
    private Integer isFree;

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
