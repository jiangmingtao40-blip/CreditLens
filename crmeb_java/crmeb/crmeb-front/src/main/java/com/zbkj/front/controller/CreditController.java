package com.zbkj.front.controller;

import com.zbkj.common.response.CreditQuotaResponse;
import com.zbkj.common.response.CreditCommissionResponse;
import com.zbkj.common.result.CommonResult;
import com.zbkj.common.service.credit.CreditUserService;
import com.zbkj.common.utils.CreditTokenUtil;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.annotation.RequestMethod;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

/**
 * 征信报告接口
 */
@Slf4j
@RestController("CreditFrontController")
@RequestMapping("api/credit")
@Api(tags = "征信报告")
public class CreditController {

    @Autowired
    private CreditUserService creditUserService;

    private Long getUserId(String token) {
        return CreditTokenUtil.getUserId(token);
    }

    /**
     * 获取用户额度信息
     * @return 额度信息
     */
    @ApiOperation(value = "获取用户额度信息")
    @RequestMapping(value = "/quota", method = RequestMethod.GET)
    public CommonResult<CreditQuotaResponse> getQuota(@RequestHeader(value = "Authorization", required = false) String token) {
        Long userId = getUserId(token);
        CreditQuotaResponse response = new CreditQuotaResponse();
        if (userId != null) {
            var user = creditUserService.getById(userId);
            if (user != null) {
                response.setFreeCount(user.getFreeCount());
                response.setIsVip(user.getIsVip() == 1);
                response.setVipExpireTime(user.getVipExpireTime());
            }
        } else {
            response.setFreeCount(0);
            response.setIsVip(false);
        }
        response.setPricePerQuery(new BigDecimal("9.90"));
        response.setTotalUsed(0);

        log.info("获取额度信息: userId={}, freeCount={}, isVip={}", userId, response.getFreeCount(), response.getIsVip());
        return CommonResult.success(response);
    }

    /**
     * 获取用户佣金信息
     * @return 佣金信息
     */
    @ApiOperation(value = "获取用户佣金信息")
    @RequestMapping(value = "/commission", method = RequestMethod.GET)
    public CommonResult<CreditCommissionResponse> getCommission() {
        // TODO: 从数据库或缓存获取真实数据
        // 目前返回模拟数据
        CreditCommissionResponse response = new CreditCommissionResponse();
        response.setTotalCommission(BigDecimal.ZERO);
        response.setAvailableCommission(BigDecimal.ZERO);
        response.setFrozenCommission(BigDecimal.ZERO);
        response.setTotalInvites(0);
        response.setTotalEarnings(BigDecimal.ZERO);
        
        log.info("获取佣金信息: totalCommission={}", response.getTotalCommission());
        return CommonResult.success(response);
    }

    /**
     * 创建支付订单
     * @return 订单信息
     */
    @ApiOperation(value = "创建支付订单")
    @RequestMapping(value = "/pay/create", method = RequestMethod.POST)
    public CommonResult<Map<String, Object>> createPayOrder() {
        // TODO: 实现真实的支付订单创建逻辑
        Map<String, Object> result = new HashMap<>();
        result.put("order_id", "CR" + System.currentTimeMillis());
        result.put("amount", new BigDecimal("9.90"));
        result.put("pay_sign", "mock_pay_sign_" + System.currentTimeMillis());
        
        log.info("创建支付订单: orderId={}", result.get("order_id"));
        return CommonResult.success(result);
    }

    /**
     * 查询支付状态
     * @param orderId 订单ID
     * @return 支付状态
     */
    @ApiOperation(value = "查询支付状态")
    @RequestMapping(value = "/pay/status/{orderId}", method = RequestMethod.GET)
    public CommonResult<Map<String, Object>> getPayStatus(@PathVariable String orderId) {
        // TODO: 实现真实的支付状态查询逻辑
        Map<String, Object> result = new HashMap<>();
        result.put("order_id", orderId);
        result.put("status", "pending");  // pending, paid, failed
        result.put("pay_time", null);
        
        log.info("查询支付状态: orderId={}, status={}", orderId, result.get("status"));
        return CommonResult.success(result);
    }
}
