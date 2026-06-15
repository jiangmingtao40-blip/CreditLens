package com.zbkj.common.response.credit;

import lombok.Data;

import java.io.Serializable;
import java.util.Date;

/**
 * 报告列表响应
 */
@Data
public class ReportListResponse implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 报告ID
     */
    private Long id;

    /**
     * 任务ID
     */
    private String taskId;

    /**
     * 文件名
     */
    private String fileName;

    /**
     * 状态
     */
    private String status;

    /**
     * 信用评分
     */
    private Integer creditScore;

    /**
     * 风险等级
     */
    private String riskLevel;

    /**
     * 消费金额
     */
    private String costAmount;

    /**
     * 是否免费
     */
    private Boolean isFree;

    /**
     * 创建时间
     */
    private Date createTime;
}
