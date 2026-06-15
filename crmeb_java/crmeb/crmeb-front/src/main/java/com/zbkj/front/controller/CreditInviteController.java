package com.zbkj.front.controller;

import com.zbkj.common.result.CommonResult;
import com.zbkj.common.response.credit.InviteListResponse;
import com.zbkj.common.response.credit.InviteStatsResponse;
import com.zbkj.common.service.credit.CreditInviteService;
import com.zbkj.common.utils.CreditTokenUtil;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 征信邀请控制器
 */
@Slf4j
@RestController("CreditInviteFrontController")
@RequestMapping("api/credit/invite")
@Api(tags = "征信邀请")
public class CreditInviteController {

    @Autowired
    private CreditInviteService creditInviteService;

    private Long getUserId(String token) {
        return CreditTokenUtil.getUserId(token);
    }

    @ApiOperation(value = "获取邀请统计")
    @RequestMapping(value = "/stats", method = RequestMethod.GET)
    public CommonResult<InviteStatsResponse> getInviteStats(@RequestHeader("Authorization") String token) {
        log.info("获取邀请统计");
        
        try {
            Long userId = getUserId(token);
            if (userId == null) {
                return CommonResult.failed("登录已过期，请重新登录");
            }
            InviteStatsResponse response = creditInviteService.getInviteStats(userId);
            return CommonResult.success(response);
        } catch (Exception e) {
            log.error("获取邀请统计失败", e);
            return CommonResult.failed("获取失败: " + e.getMessage());
        }
    }

    @ApiOperation(value = "获取邀请列表")
    @RequestMapping(value = "/list", method = RequestMethod.GET)
    public CommonResult<InviteListResponse> getInviteList(
            @RequestHeader("Authorization") String token,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer limit) {
        
        log.info("获取邀请列表: page={}, limit={}", page, limit);
        
        try {
            Long userId = getUserId(token);
            if (userId == null) {
                return CommonResult.failed("登录已过期，请重新登录");
            }
            InviteListResponse response = creditInviteService.getInviteList(userId, page, limit);
            return CommonResult.success(response);
        } catch (Exception e) {
            log.error("获取邀请列表失败", e);
            return CommonResult.failed("获取失败: " + e.getMessage());
        }
    }
}
