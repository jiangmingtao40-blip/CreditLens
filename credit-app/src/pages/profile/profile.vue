<template>
	<view class="page">
		<!-- Status Bar -->
		<view class="status-bar">
			<text class="time">{{ currentTime }}</text>
			<view class="spacer"></view>
			<view class="battery"></view>
		</view>
		
		<!-- Content -->
		<scroll-view class="content" scroll-y>
			<!-- Profile Header -->
			<view class="profile-header" @click="handleHeaderClick">
				<view class="avatar">
					<text v-if="!userInfo.avatar">{{ userInfo.nickname?.[0] || '用' }}</text>
					<image v-else :src="userInfo.avatar" class="avatar-img"/>
				</view>
				<view class="profile-info">
					<view class="profile-name">{{ userInfo.nickname || '未登录用户' }}</view>
					<view class="profile-vip-row">
						<view class="profile-vip-badge" :class="vipClass">{{ vipText }}</view>
						<span class="profile-phone" v-if="userInfo.phone">{{ formatPhone(userInfo.phone) }}</span>
						<span class="profile-phone" v-else>点击登录</span>
					</view>
				</view>
				<svg class="header-arrow" viewBox="0 0 16 16">
					<path d="M6 4l4 4-4 4" stroke="rgba(255,255,255,0.7)" stroke-width="2" fill="none" stroke-linecap="round"/>
				</svg>
			</view>
			
			<!-- 统计卡片 -->
			<view class="stats-row">
				<view class="stat-item" @click="goToRecords">
					<view class="stat-num">{{ stats.reports }}</view>
					<view class="stat-label">我的报告</view>
				</view>
				<view class="stat-divider"></view>
				<view class="stat-item" @click="goToVipCenter">
					<view class="stat-num">{{ stats.vipDays }}</view>
					<view class="stat-label">VIP天数</view>
				</view>
				<view class="stat-divider"></view>
				<view class="stat-item" @click="goToInvite">
					<view class="stat-num">{{ stats.invites }}</view>
					<view class="stat-label">邀请好友</view>
				</view>
			</view>
			
			<!-- Menu Group 1 -->
			<view class="menu-group">
				<view class="menu-item" @click="goToVipCenter">
					<view class="menu-icon" style="background:#EEF2FF">
						<svg viewBox="0 0 20 20" width="36rpx" height="36rpx">
							<path d="M10 2l2.5 5 5.5.8-4 3.9.9 5.3L10 13.5 5.1 17l.9-5.3-4-3.9 5.5-.8z" stroke="#6366F1" stroke-width="1.2" fill="none" stroke-linejoin="round"/>
						</svg>
					</view>
					<span class="menu-text">会员中心</span>
					<view class="menu-right">
						<text class="menu-badge" v-if="!isVip">未开通</text>
						<svg class="menu-arrow" viewBox="0 0 16 16">
							<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
						</svg>
					</view>
				</view>
				<view class="menu-item" @click="goToRecords">
					<view class="menu-icon" style="background:#ECFDF5">
						<svg viewBox="0 0 20 20" width="36rpx" height="36rpx">
							<rect x="3" y="3" width="14" height="14" rx="2" stroke="#10B981" stroke-width="1.5" fill="none"/>
							<path d="M3 8h14M8 3v14" stroke="#10B981" stroke-width="1.5" fill="none"/>
						</svg>
					</view>
					<span class="menu-text">历史记录</span>
					<svg class="menu-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
				<view class="menu-item" @click="goToInvite">
					<view class="menu-icon" style="background:#FCE7F3">
						<svg viewBox="0 0 20 20" width="36rpx" height="36rpx">
							<circle cx="7" cy="7" r="3.5" stroke="#EC4899" stroke-width="1.5" fill="none"/>
							<circle cx="13" cy="7" r="3.5" stroke="#EC4899" stroke-width="1.5" fill="none"/>
							<path d="M2 17c0-3 2.5-5 5-5s5 2 5 5" stroke="#EC4899" stroke-width="1.5" fill="none" stroke-linecap="round"/>
							<path d="M12 12c2.5 0 5 2 5 5" stroke="#EC4899" stroke-width="1.5" fill="none" stroke-linecap="round"/>
						</svg>
					</view>
					<span class="menu-text">邀请有礼</span>
					<view class="menu-right">
						<text class="menu-hint">赚佣金</text>
						<svg class="menu-arrow" viewBox="0 0 16 16">
							<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
						</svg>
					</view>
				</view>
			</view>
			
			<!-- Menu Group 2 -->
			<view class="menu-group">
				<view class="menu-item" @click="goToSettings">
					<view class="menu-icon" style="background:#F0F9FF">
						<svg viewBox="0 0 20 20" width="36rpx" height="36rpx">
							<circle cx="10" cy="10" r="8" stroke="#0EA5E9" stroke-width="1.5" fill="none"/>
							<circle cx="10" cy="10" r="3" stroke="#0EA5E9" stroke-width="1.5" fill="none"/>
							<path d="M8 13l2-3h4" stroke="#0EA5E9" stroke-width="1.5" fill="none" stroke-linecap="round"/>
						</svg>
					</view>
					<span class="menu-text">设置</span>
					<svg class="menu-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
				<view class="menu-item" @click="showService">
					<view class="menu-icon" style="background:#F5F3FF">
						<svg viewBox="0 0 20 20" width="36rpx" height="36rpx">
							<circle cx="10" cy="8" r="4" stroke="#8B5CF6" stroke-width="1.5" fill="none"/>
							<path d="M4 18c0-3.3 2.7-6 6-6s6 2.7 6 6" stroke="#8B5CF6" stroke-width="1.5" fill="none" stroke-linecap="round"/>
							<path d="M15 3l2-2M17 1v4h-4" stroke="#8B5CF6" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</view>
					<span class="menu-text">联系客服</span>
					<svg class="menu-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
				<view class="menu-item" @click="goToAbout">
					<view class="menu-icon" style="background:#FFFBEB">
						<svg viewBox="0 0 20 20" width="36rpx" height="36rpx">
							<circle cx="10" cy="10" r="8" stroke="#F59E0B" stroke-width="1.5" fill="none"/>
							<path d="M10 7v7M10 5v.01" stroke="#F59E0B" stroke-width="2" fill="none" stroke-linecap="round"/>
						</svg>
					</view>
					<span class="menu-text">关于我们</span>
					<svg class="menu-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
			</view>
			
			<!-- Logout Button -->
			<button class="btn-danger" @click="handleLogout" v-if="isLoggedIn">退出登录</button>
			<button class="btn-primary" @click="handleLogin" v-else>微信登录</button>
			
			<!-- Bottom Spacing -->
			<view class="bottom-spacing"></view>
		</scroll-view>
		
		<!-- Tab Bar -->
		<TabBar :current="4" @change="onTabChange"></TabBar>
	</view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import TabBar from '@/components/TabBar/index.vue'
import { getUserInfo, checkVipStatus, logout as apiLogout } from '@/api/credit'

const currentTime = ref('')
const userInfo = reactive({
	nickname: '',
	phone: '',
	avatar: '',
})
const isLoggedIn = ref(false)
const isVip = ref(false)
const vipText = ref('普通用户')
const vipClass = ref('vip-none')
const stats = reactive({
	reports: 0,
	vipDays: 0,
	invites: 0,
})

const formatPhone = (phone: string) => {
	if (!phone || phone.length < 11) return phone
	return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const loadUserInfo = async () => {
	try {
		const res: any = await getUserInfo()
		if (res.code === 0 && res.data) {
			userInfo.nickname = res.data.nickname || '用户'
			userInfo.phone = res.data.phone || ''
			userInfo.avatar = res.data.avatar || ''
			isLoggedIn.value = true
		}
	} catch (error) {
		console.log('Java服务未启动，使用默认用户信息')
		userInfo.nickname = '游客用户'
		isLoggedIn.value = false
	}
}

const loadVipStatus = async () => {
	try {
		const res: any = await checkVipStatus()
		if (res.code === 0 && res.data) {
			isVip.value = res.data.isVip || false
			vipText.value = isVip.value ? 'VIP会员' : '普通用户'
			vipClass.value = isVip.value ? 'vip-active' : 'vip-none'
		}
	} catch (error) {
		console.log('Java服务未启动，使用默认VIP状态')
		isVip.value = false
		vipText.value = '普通用户'
		vipClass.value = 'vip-none'
	}
}

const loadRecords = async () => {
	try {
		const res: any = await checkVipStatus()
		if (res.code === 200 || res.code === 0) {
			const data = res.data || res
			isVip.value = data.isVip || false
			vipText.value = data.vipLevelText || (isVip.value ? 'VIP会员' : '普通用户')
			vipClass.value = isVip.value ? 'vip-active' : 'vip-none'
			stats.vipDays = data.daysLeft || 0
		}
	} catch (e) {
		isVip.value = false
		vipText.value = '普通用户'
		vipClass.value = 'vip-none'
	}
}

const loadStats = () => {
	try {
		const res: any = uni.getStorageSync('user_stats')
		if (res) {
			stats.reports = res.reports || 0
			stats.invites = res.invites || 0
		}
	} catch (e) {}
}

onMounted(() => {
	updateTime()
	setInterval(updateTime, 30000)
	loadUserInfo()
	loadVipStatus()
	loadStats()
})

const updateTime = () => {
	const now = new Date()
	const h = now.getHours().toString().padStart(2, '0')
	const m = now.getMinutes().toString().padStart(2, '0')
	currentTime.value = `${h}:${m}`
}

const goToVipCenter = () => {
	uni.navigateTo({ url: '/pages/vip-center/vip-center' })
}

const goToRecords = () => {
	uni.navigateTo({ url: '/pages/records/records' })
}

const goToInvite = () => {
	uni.showToast({ title: '邀请功能开发中', icon: 'none' })
}

const goToSettings = () => {
	uni.navigateTo({ url: '/pages/settings/settings' })
}

const goToAbout = () => {
	uni.navigateTo({ url: '/pages/about/about' })
}

const showService = () => {
	uni.showActionSheet({
		itemList: ['拨打客服电话 400-888-9999', '复制客服微信', '发送邮件'],
		success: (res) => {
			if (res.tapIndex === 0) {
				uni.makePhoneCall({ phoneNumber: '4008889999', fail: () => {} })
			} else if (res.tapIndex === 1) {
				uni.setClipboardData({
					data: 'CreditAI_KeFu',
					success: () => uni.showToast({ title: '微信号已复制', icon: 'success' })
				})
			} else if (res.tapIndex === 2) {
				uni.setClipboardData({
					data: 'support@credit-ai.com',
					success: () => uni.showToast({ title: '邮箱已复制', icon: 'success' })
				})
			}
		}
	})
}

const handleHeaderClick = () => {
	if (isLoggedIn.value) {
		uni.navigateTo({ url: '/pages/vip-center/vip-center' })
	} else {
		uni.navigateTo({ url: '/pages/login/login' })
	}
}

const handleLogin = () => {
	uni.navigateTo({ url: '/pages/login/login' })
}

const handleLogout = () => {
	uni.showModal({
		title: '确认退出',
		content: '退出登录后需要重新登录',
		success: async (res) => {
			if (res.confirm) {
				try {
					await apiLogout()
				} catch (e) {}
				uni.removeStorageSync('credit_token')
				uni.removeStorageSync('user_info')
				isLoggedIn.value = false
				userInfo.nickname = ''
				userInfo.phone = ''
				userInfo.avatar = ''
				uni.showToast({ title: '已退出登录', icon: 'success' })
			}
		}
	})
}

const onTabChange = (index: number) => {
	const routes = [
		'/pages/index/index',
		'/pages/records/records',
		'/pages/upload/upload',
		'/pages/result/result',
		'/pages/profile/profile'
	]
	if (routes[index]) {
		uni.navigateTo({ url: routes[index] })
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

/* Status Bar */
.status-bar {
	display: flex;
	align-items: center;
	height: 62rpx;
	padding: 0 48rpx;
	background: #F8FAFC;
	
	.time {
		font-family: 'IBM Plex Sans', sans-serif;
		font-size: 28rpx;
		font-weight: 600;
		color: #1E293B;
	}
	
	.spacer {
		flex: 1;
	}
	
	.battery {
		width: 48rpx;
		height: 24rpx;
		background: #CBD5E1;
		border-radius: 6rpx;
	}
}

/* Content */
.content {
	flex: 1;
	padding: 20rpx;
	overflow-y: auto;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

/* Profile Header */
.profile-header {
	display: flex;
	align-items: center;
	background: linear-gradient(135deg, #6366F1, #A855F7);
	border-radius: 40rpx;
	padding: 36rpx 32rpx;
	gap: 28rpx;
	position: relative;
	
	.avatar {
		width: 96rpx;
		height: 96rpx;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.3);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 40rpx;
		font-weight: 700;
		color: #FFFFFF;
		flex-shrink: 0;
		overflow: hidden;
		
		.avatar-img {
			width: 100%;
			height: 100%;
			border-radius: 50%;
		}
	}
	
	.profile-info {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 4rpx;
	}
	
	.profile-name {
		font-size: 32rpx;
		font-weight: 700;
		color: #FFFFFF;
	}
	
	.profile-vip-row {
		display: flex;
		align-items: center;
		gap: 12rpx;
	}
	
	.profile-vip-badge {
		background: rgba(255, 255, 255, 0.2);
		border-radius: 8rpx;
		padding: 4rpx 12rpx;
		font-size: 20rpx;
		font-weight: 700;
		color: #FFFFFF;
		
		&.vip-active {
			background: rgba(251, 191, 36, 0.3);
			color: #FBBF24;
		}
	}
	
	.profile-phone {
		font-size: 22rpx;
		color: rgba(255, 255, 255, 0.7);
		font-family: 'IBM Plex Sans', sans-serif;
	}
	
	.header-arrow {
		width: 32rpx;
		height: 32rpx;
		flex-shrink: 0;
	}
}

/* Stats Row */
.stats-row {
	display: flex;
	align-items: center;
	background: #FFFFFF;
	border-radius: 28rpx;
	padding: 28rpx 0;
	box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.04);
	
	.stat-item {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8rpx;
		
		.stat-num {
			font-size: 36rpx;
			font-weight: 800;
			color: #1E293B;
			font-family: 'DIN Alternate', 'IBM Plex Sans', sans-serif;
		}
		
		.stat-label {
			font-size: 22rpx;
			color: #94A3B8;
		}
	}
	
	.stat-divider {
		width: 1rpx;
		height: 48rpx;
		background: #F1F5F9;
	}
}

/* Menu Group */
.menu-group {
	display: flex;
	flex-direction: column;
	background: #FFFFFF;
	border-radius: 28rpx;
	box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.04);
	overflow: hidden;
	
	.menu-item {
		display: flex;
		align-items: center;
		padding: 0 28rpx;
		height: 108rpx;
		cursor: pointer;
		border-bottom: 1rpx solid #F1F5F9;
		
		&:last-child {
			border-bottom: none;
		}
		
		.menu-icon {
			width: 60rpx;
			height: 60rpx;
			border-radius: 16rpx;
			display: flex;
			align-items: center;
			justify-content: center;
			flex-shrink: 0;
		}
		
		.menu-text {
			flex: 1;
			margin-left: 20rpx;
			font-size: 28rpx;
			color: #1E293B;
			font-weight: 500;
		}
		
		.menu-right {
			display: flex;
			align-items: center;
			gap: 8rpx;
		}
		
		.menu-badge {
			font-size: 20rpx;
			color: #EF4444;
			background: #FEF2F2;
			padding: 4rpx 12rpx;
			border-radius: 8rpx;
		}
		
		.menu-hint {
			font-size: 22rpx;
			color: #94A3B8;
		}
		
		.menu-arrow {
			width: 28rpx;
			height: 28rpx;
			stroke: #94A3B8;
			flex-shrink: 0;
		}
	}
}

/* Buttons */
.btn-danger {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 92rpx;
	background: #FEF2F2;
	border-radius: 46rpx;
	color: #EF4444;
	font-size: 28rpx;
	font-weight: 600;
	border: none;
	margin-top: 8rpx;
	
	&::after {
		border: none;
	}
}

.btn-primary {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 92rpx;
	background: linear-gradient(135deg, #6366F1, #A855F7);
	border-radius: 46rpx;
	color: #FFFFFF;
	font-size: 28rpx;
	font-weight: 600;
	border: none;
	margin-top: 8rpx;
	
	&::after {
		border: none;
	}
}

/* Bottom Spacing */
.bottom-spacing {
	height: 140rpx;
}
</style>
