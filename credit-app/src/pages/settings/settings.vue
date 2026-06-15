<template>
	<view class="page">
		<!-- Custom Nav Bar -->
		<view class="nav-bar">
			<view class="nav-back" @click="goBack">
				<svg viewBox="0 0 24 24" width="44rpx" height="44rpx">
					<path d="M15 19l-7-7 7-7" stroke="#1E293B" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</view>
			<text class="nav-title">设置</text>
			<view class="nav-placeholder"></view>
		</view>

		<scroll-view class="content" scroll-y>
			<!-- 通知设置 -->
			<view class="section-title">通知设置</view>
			<view class="menu-group">
				<view class="menu-item">
					<text class="menu-label">分析完成通知</text>
					<switch :checked="notifyAnalysis" @change="onNotifyAnalysisChange" color="#6366F1"/>
				</view>
				<view class="menu-item">
					<text class="menu-label">报告生成提醒</text>
					<switch :checked="notifyReport" @change="onNotifyReportChange" color="#6366F1"/>
				</view>
				<view class="menu-item">
					<text class="menu-label">会员到期提醒</text>
					<switch :checked="notifyVip" @change="onNotifyVipChange" color="#6366F1"/>
				</view>
				<view class="menu-item">
					<text class="menu-label">活动推送</text>
					<switch :checked="notifyPromo" @change="onNotifyPromoChange" color="#6366F1"/>
				</view>
			</view>

			<!-- 隐私设置 -->
			<view class="section-title">隐私设置</view>
			<view class="menu-group">
				<view class="menu-item">
					<text class="menu-label">数据分析改进</text>
					<switch :checked="privacyAnalytics" @change="onPrivacyAnalyticsChange" color="#6366F1"/>
				</view>
				<view class="menu-item">
					<text class="menu-label">崩溃日志上报</text>
					<switch :checked="privacyCrash" @change="onPrivacyCrashChange" color="#6366F1"/>
				</view>
				<view class="menu-item" @click="showPrivacyPolicy">
					<text class="menu-label">隐私政策</text>
					<svg class="menu-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
				<view class="menu-item" @click="showServiceAgreement">
					<text class="menu-label">服务协议</text>
					<svg class="menu-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
			</view>

			<!-- 账号安全 -->
			<view class="section-title">账号安全</view>
			<view class="menu-group">
				<view class="menu-item" @click="changePassword">
					<text class="menu-label">修改密码</text>
					<svg class="menu-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
				<view class="menu-item" @click="manageDevices">
					<text class="menu-label">登录设备管理</text>
					<view class="menu-right">
						<text class="menu-hint">3台</text>
						<svg class="menu-arrow" viewBox="0 0 16 16">
							<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
						</svg>
					</view>
				</view>
				<view class="menu-item">
					<text class="menu-label">双重验证</text>
					<switch :checked="twoFactorAuth" @change="onTwoFactorChange" color="#6366F1"/>
				</view>
			</view>

			<!-- 存储管理 -->
			<view class="section-title">存储管理</view>
			<view class="menu-group">
				<view class="menu-item" @click="clearCache">
					<text class="menu-label">清除缓存</text>
					<view class="menu-right">
						<text class="menu-hint">{{ cacheSize }}</text>
						<svg class="menu-arrow" viewBox="0 0 16 16">
							<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
						</svg>
					</view>
				</view>
			</view>

			<!-- 底部间距 -->
			<view class="bottom-spacing"></view>
		</scroll-view>
	</view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const notifyAnalysis = ref(true)
const notifyReport = ref(true)
const notifyVip = ref(true)
const notifyPromo = ref(false)
const privacyAnalytics = ref(true)
const privacyCrash = ref(true)
const twoFactorAuth = ref(false)
const cacheSize = ref('12.8 MB')

// 从本地存储读取设置
onMounted(() => {
	notifyAnalysis.value = uni.getStorageSync('notify_analysis') !== false
	notifyReport.value = uni.getStorageSync('notify_report') !== false
	notifyVip.value = uni.getStorageSync('notify_vip') !== false
	notifyPromo.value = uni.getStorageSync('notify_promo') === true
	privacyAnalytics.value = uni.getStorageSync('privacy_analytics') !== false
	privacyCrash.value = uni.getStorageSync('privacy_crash') !== false
	twoFactorAuth.value = uni.getStorageSync('two_factor_auth') === true
	calculateCacheSize()
})

const onNotifyAnalysisChange = (e: any) => {
	notifyAnalysis.value = e.detail.value
	uni.setStorageSync('notify_analysis', e.detail.value)
}

const onNotifyReportChange = (e: any) => {
	notifyReport.value = e.detail.value
	uni.setStorageSync('notify_report', e.detail.value)
}

const onNotifyVipChange = (e: any) => {
	notifyVip.value = e.detail.value
	uni.setStorageSync('notify_vip', e.detail.value)
}

const onNotifyPromoChange = (e: any) => {
	notifyPromo.value = e.detail.value
	uni.setStorageSync('notify_promo', e.detail.value)
}

const onPrivacyAnalyticsChange = (e: any) => {
	privacyAnalytics.value = e.detail.value
	uni.setStorageSync('privacy_analytics', e.detail.value)
}

const onPrivacyCrashChange = (e: any) => {
	privacyCrash.value = e.detail.value
	uni.setStorageSync('privacy_crash', e.detail.value)
}

const onTwoFactorChange = (e: any) => {
	twoFactorAuth.value = e.detail.value
	uni.setStorageSync('two_factor_auth', e.detail.value)
	if (e.detail.value) {
		uni.showToast({ title: '请在账号安全中完成验证', icon: 'none' })
	}
}

const showPrivacyPolicy = () => {
	uni.navigateTo({ url: '/pages/about/about?tab=privacy' })
}

const showServiceAgreement = () => {
	uni.navigateTo({ url: '/pages/about/about?tab=service' })
}

const changePassword = () => {
	uni.showToast({ title: '密码修改功能开发中', icon: 'none' })
}

const manageDevices = () => {
	uni.showToast({ title: '设备管理功能开发中', icon: 'none' })
}

const calculateCacheSize = () => {
	// 模拟计算缓存大小
	try {
		const res = uni.getStorageInfoSync()
		const size = ((res.currentSize || 0) / 1024).toFixed(1)
		cacheSize.value = `${size} MB`
	} catch (e) {
		cacheSize.value = '12.8 MB'
	}
}

const clearCache = () => {
	uni.showModal({
		title: '确认清除',
		content: '清除缓存将删除本地临时文件，确认继续？',
		success: (res) => {
			if (res.confirm) {
				try {
					// 保留token和用户信息，清除其他缓存
					const token = uni.getStorageSync('credit_token')
					const userInfo = uni.getStorageSync('user_info')
					uni.clearStorageSync()
					if (token) uni.setStorageSync('credit_token', token)
					if (userInfo) uni.setStorageSync('user_info', userInfo)
					cacheSize.value = '0 MB'
					uni.showToast({ title: '缓存已清除', icon: 'success' })
				} catch (e) {
					uni.showToast({ title: '清除失败', icon: 'none' })
				}
			}
		}
	})
}

const goBack = () => {
	const pages = getCurrentPages()
	if (pages.length > 1) {
		uni.navigateBack()
	} else {
		uni.switchTab({ url: '/pages/profile/profile' })
	}
}
</script>

<style lang="scss" scoped>
.page {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background: #F8FAFC;
}

/* Nav Bar */
.nav-bar {
	display: flex;
	align-items: center;
	justify-content: space-between;
	height: 96rpx;
	padding: 0 20rpx;
	background: #FFFFFF;
	border-bottom: 1rpx solid #F1F5F9;
	flex-shrink: 0;
	
	.nav-back {
		width: 68rpx;
		height: 68rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.nav-title {
		font-size: 34rpx;
		font-weight: 700;
		color: #1E293B;
	}
	
	.nav-placeholder {
		width: 68rpx;
	}
}

/* Content */
.content {
	flex: 1;
	padding: 20rpx;
	overflow-y: auto;
}

/* Section Title */
.section-title {
	font-size: 26rpx;
	font-weight: 600;
	color: #94A3B8;
	margin: 24rpx 12rpx 12rpx;
}

/* Menu Group */
.menu-group {
	background: #FFFFFF;
	border-radius: 28rpx;
	box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.04);
	overflow: hidden;
	
	.menu-item {
		display: flex;
		align-items: center;
		padding: 0 28rpx;
		height: 100rpx;
		border-bottom: 1rpx solid #F1F5F9;
		
		&:last-child {
			border-bottom: none;
		}
		
		.menu-label {
			flex: 1;
			font-size: 28rpx;
			color: #1E293B;
		}
		
		.menu-right {
			display: flex;
			align-items: center;
			gap: 8rpx;
		}
		
		.menu-hint {
			font-size: 24rpx;
			color: #94A3B8;
		}
		
		.menu-arrow {
			width: 28rpx;
			height: 28rpx;
		}
	}
}

/* Bottom Spacing */
.bottom-spacing {
	height: 140rpx;
}
</style>
