package com.zbkj.front.controller;

import com.zbkj.common.result.CommonResult;
import com.zbkj.common.response.credit.VipPackageResponse;
import com.zbkj.common.service.credit.CreditVipService;
import com.zbkj.common.utils.CreditTokenUtil;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * VIP会员控制器
 */
@Slf4j
@RestController("CreditVipFrontController")
@RequestMapping("api/credit/vip")
@Api(tags = "VIP会员")
public class CreditVipController {

    @Autowired
    private CreditVipService creditVipService;

    /**
     * 获取VIP套餐列表
     */
    @ApiOperation(value = "获取VIP套餐列表")
    @RequestMapping(value = "/packages", method = RequestMethod.GET)
    public CommonResult<List<VipPackageResponse>> getVipPackages() {
        log.info("获取VIP套餐列表");
        
        try {
            List<VipPackageResponse> packages = creditVipService.getVipPackages();
            return CommonResult.success(packages);
        } catch (Exception e) {
            log.error("获取VIP套餐列表失败", e);
            return CommonResult.failed("获取失败: " + e.getMessage());
        }
    }

    /**
     * 购买VIP
     */
    @ApiOperation(value = "购买VIP")
    @RequestMapping(value = "/purchase", method = RequestMethod.POST)
    public CommonResult<String> purchaseVip(
            @RequestHeader("Authorization") String token,
            @RequestParam Long packageId) {
        
        log.info("购买VIP: packageId={}", packageId);
        
        try {
            Long userId = CreditTokenUtil.getUserId(token);
            if (userId == null) {
                return CommonResult.failed("登录已过期，请重新登录");
            }
            
            // TODO: 创建订单并调用支付
            
            boolean success = creditVipService.purchaseVip(userId, packageId);
            if (success) {
                return CommonResult.success("购买成功");
            } else {
                return CommonResult.failed("购买失败");
            }
        } catch (Exception e) {
            log.error("购买VIP失败", e);
            return CommonResult.failed("购买失败: " + e.getMessage());
        }
    }

    /**
     * 检查VIP状态
     */
    @ApiOperation(value = "检查VIP状态")
    @RequestMapping(value = "/check", method = RequestMethod.GET)
    public CommonResult<Boolean> checkVipStatus(@RequestHeader("Authorization") String token) {
        log.info("检查VIP状态");
        
        try {
            Long userId = CreditTokenUtil.getUserId(token);
            if (userId == null) {
                return CommonResult.failed("登录已过期，请重新登录");
            }
            
            boolean isVip = creditVipService.isVipValid(userId);
            return CommonResult.success(isVip);
        } catch (Exception e) {
            log.error("检查VIP状态失败", e);
            return CommonResult.failed("检查失败: " + e.getMessage());
        }
    }
}
