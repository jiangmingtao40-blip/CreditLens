package com.zbkj.front.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.zbkj.common.result.CommonResult;
import com.zbkj.common.response.credit.ConsumeListResponse;
import com.zbkj.common.service.credit.CreditConsumeService;
import com.zbkj.common.utils.CreditTokenUtil;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 消费记录控制器
 */
@Slf4j
@RestController("CreditConsumeFrontController")
@RequestMapping("api/credit/consume")
@Api(tags = "消费记录")
public class CreditConsumeController {

    @Autowired
    private CreditConsumeService creditConsumeService;

    /**
     * 获取消费记录列表
     */
    @ApiOperation(value = "获取消费记录列表")
    @RequestMapping(value = "/list", method = RequestMethod.GET)
    public CommonResult<IPage<ConsumeListResponse>> getConsumeList(
            @RequestHeader("Authorization") String token,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer limit) {
        
        log.info("获取消费记录列表: page={}, limit={}", page, limit);
        
        try {
            Long userId = CreditTokenUtil.getUserId(token);
            if (userId == null) {
                return CommonResult.failed("登录已过期，请重新登录");
            }
            
            IPage<ConsumeListResponse> response = creditConsumeService.getUserConsumeList(userId, page, limit);
            return CommonResult.success(response);
        } catch (Exception e) {
            log.error("获取消费记录列表失败", e);
            return CommonResult.failed("获取失败: " + e.getMessage());
        }
    }
}
