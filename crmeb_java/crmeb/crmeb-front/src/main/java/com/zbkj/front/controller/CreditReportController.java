package com.zbkj.front.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.zbkj.common.model.credit.CreditReport;
import com.zbkj.common.result.CommonResult;
import com.zbkj.common.response.credit.ReportListResponse;
import com.zbkj.common.service.credit.CreditReportService;
import com.zbkj.common.utils.CreditTokenUtil;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 征信报告控制器
 */
@Slf4j
@RestController("CreditReportFrontController")
@RequestMapping("api/credit/report")
@Api(tags = "征信报告")
public class CreditReportController {

    @Autowired
    private CreditReportService creditReportService;

    /**
     * 获取报告列表
     */
    @ApiOperation(value = "获取报告列表")
    @RequestMapping(value = "/list", method = RequestMethod.GET)
    public CommonResult<IPage<ReportListResponse>> getReportList(
            @RequestHeader("Authorization") String token,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer limit) {
        
        log.info("获取报告列表: page={}, limit={}", page, limit);
        
        try {
            Long userId = CreditTokenUtil.getUserId(token);
            if (userId == null) {
                return CommonResult.failed("登录已过期，请重新登录");
            }
            
            IPage<ReportListResponse> response = creditReportService.getUserReportList(userId, page, limit);
            return CommonResult.success(response);
        } catch (Exception e) {
            log.error("获取报告列表失败", e);
            return CommonResult.failed("获取失败: " + e.getMessage());
        }
    }

    /**
     * 获取报告详情
     */
    @ApiOperation(value = "获取报告详情")
    @RequestMapping(value = "/detail/{taskId}", method = RequestMethod.GET)
    public CommonResult<CreditReport> getReportDetail(
            @RequestHeader("Authorization") String token,
            @PathVariable String taskId) {
        
        log.info("获取报告详情: taskId={}", taskId);
        
        try {
            CreditReport report = creditReportService.getByTaskId(taskId);
            if (report == null) {
                return CommonResult.failed("报告不存在");
            }
            return CommonResult.success(report);
        } catch (Exception e) {
            log.error("获取报告详情失败", e);
            return CommonResult.failed("获取失败: " + e.getMessage());
        }
    }

    /**
     * 删除报告
     */
    @ApiOperation(value = "删除报告")
    @RequestMapping(value = "/delete/{taskId}", method = RequestMethod.DELETE)
    public CommonResult<String> deleteReport(
            @RequestHeader("Authorization") String token,
            @PathVariable String taskId) {
        
        log.info("删除报告: taskId={}", taskId);
        
        try {
            CreditReport report = creditReportService.getByTaskId(taskId);
            if (report == null) {
                return CommonResult.failed("报告不存在");
            }
            
            report.setIsDeleted(1);
            creditReportService.updateById(report);
            
            return CommonResult.success("删除成功");
        } catch (Exception e) {
            log.error("删除报告失败", e);
            return CommonResult.failed("删除失败: " + e.getMessage());
        }
    }
}
