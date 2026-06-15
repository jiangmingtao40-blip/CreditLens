package com.zbkj.common.service.credit;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.zbkj.common.dao.credit.CreditReportDao;
import com.zbkj.common.model.credit.CreditReport;
import com.zbkj.common.response.credit.ReportListResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/**
 * 征信报告服务
 */
@Slf4j
@Service
public class CreditReportService extends ServiceImpl<CreditReportDao, CreditReport> {

    /**
     * 分页查询用户报告列表
     */
    public IPage<ReportListResponse> getUserReportList(Long userId, Integer page, Integer limit) {
        Page<CreditReport> pageParam = new Page<>(page, limit);
        IPage<CreditReport> reportPage = baseMapper.selectPageByUserId(pageParam, userId);

        // 转换为响应对象
        IPage<ReportListResponse> responsePage = new Page<>(page, limit);
        responsePage.setTotal(reportPage.getTotal());
        responsePage.setPages(reportPage.getPages());

        List<ReportListResponse> records = new ArrayList<>();
        for (CreditReport report : reportPage.getRecords()) {
            ReportListResponse response = new ReportListResponse();
            BeanUtils.copyProperties(report, response);
            response.setIsFree(report.getIsFree() == 1);
            if (report.getCostAmount() != null) {
                response.setCostAmount(report.getCostAmount().toString());
            }
            records.add(response);
        }
        responsePage.setRecords(records);

        return responsePage;
    }

    /**
     * 根据任务ID获取报告
     */
    public CreditReport getByTaskId(String taskId) {
        return baseMapper.selectByTaskId(taskId);
    }

    /**
     * 保存报告
     */
    public boolean saveReport(CreditReport report) {
        return save(report);
    }

    /**
     * 更新报告状态
     */
    public boolean updateReportStatus(String taskId, String status) {
        CreditReport report = getByTaskId(taskId);
        if (report == null) {
            return false;
        }
        report.setStatus(status);
        return updateById(report);
    }
}
