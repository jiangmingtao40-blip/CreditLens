<template>
	<view class="page">
		<!-- Custom Nav Bar -->
		<view class="nav-bar">
			<view class="nav-back" @click="goBack">
				<svg viewBox="0 0 24 24" width="44rpx" height="44rpx">
					<path d="M15 19l-7-7 7-7" stroke="#1E293B" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</view>
			<text class="nav-title">会员中心</text>
			<view class="nav-placeholder"></view>
		</view>

		<scroll-view class="content" scroll-y>
			<!-- VIP 状态卡片 -->
			<view class="vip-card" :class="vipLevel">
				<view class="vip-card-top">
					<view class="vip-badge">
						<text class="vip-badge-text">{{ vipLevelText }}</text>
					</view>
					<view class="vip-expire" v-if="vipExpire">
						<text>到期日：{{ vipExpire }}</text>
					</view>
				</view>
				<view class="vip-card-bottom">
					<view class="vip-stat">
						<view class="vip-stat-num">{{ remainReports }}</view>
						<view class="vip-stat-label">剩余报告数</view>
					</view>
					<view class="vip-stat-divider"></view>
					<view class="vip-stat">
						<view class="vip-stat-num">{{ usedReports }}</view>
						<view class="vip-stat-label">已分析</view>
					</view>
					<view class="vip-stat-divider"></view>
					<view class="vip-stat">
						<view class="vip-stat-num">{{ vipDaysLeft }}</view>
						<view class="vip-stat-label">剩余天数</view>
					</view>
				</view>
			</view>

			<!-- 会员权益 -->
			<view class="section">
				<view class="section-title">会员权益</view>
				<view class="benefits-grid">
					<view class="benefit-item" v-for="(item, idx) in benefits" :key="idx">
						<view class="benefit-icon" :style="{ background: item.bg }">
							<text class="benefit-emoji">{{ item.icon }}</text>
						</view>
						<text class="benefit-name">{{ item.name }}</text>
						<text class="benefit-desc">{{ item.desc }}</text>
					</view>
				</view>
			</view>

			<!-- 套餐选择 -->
			<view class="section">
				<view class="section-title">选择套餐</view>
				<view class="package-list">
					<view
						class="package-card"
						v-for="(pkg, idx) in packages"
						:key="idx"
						:class="{ active: selectedPackage === idx }"
						@click="selectedPackage = idx"
					>
						<view class="package-tag" v-if="pkg.tag">{{ pkg.tag }}</view>
						<view class="package-name">{{ pkg.name }}</view>
						<view class="package-price">
							<text class="price-symbol">¥</text>
							<text class="price-num">{{ pkg.price }}</text>
							<text class="price-unit">/{{ pkg.unit }}</text>
						</view>
						<view class="package-original" v-if="pkg.originalPrice">
							<text>原价 ¥{{ pkg.originalPrice }}</text>
						</view>
						<view class="package-features">
							<view class="package-feature" v-for="(f, fi) in pkg.features" :key="fi">
								<svg viewBox="0 0 16 16" width="24rpx" height="24rpx">
									<path d="M4 8l3 3 5-6" stroke="#10B981" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
								<text>{{ f }}</text>
							</view>
						</view>
					</view>
				</view>
			</view>

			<!-- 支付按钮 -->
			<view class="pay-section">
				<button class="pay-btn" @click="handlePurchase">
					<text v-if="!isVip">立即开通 ¥{{ currentPrice }}</text>
					<text v-else>立即续费 ¥{{ currentPrice }}</text>
				</button>
				<view class="pay-hint">
					<text>支付即表示同意 <text class="link" @click="showService">服务协议</text></text>
				</view>
			</view>

			<!-- 底部间距 -->
			<view class="bottom-spacing"></view>
		</scroll-view>
	</view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getVipPackages, checkVipStatus, purchaseVip } from '@/api/credit'

const vipLevel = ref('none') // none / basic / premium / enterprise
const vipLevelText = ref('普通用户')
const vipExpire = ref('')
const remainReports = ref(3)
const usedReports = ref(0)
const vipDaysLeft = ref(0)
const isVip = ref(false)
const selectedPackage = ref(0)
const packages = ref<any[]>([])
const loading = ref(false)

const benefits = [
	{ icon: '📊', name: '无限报告', desc: 'VIP会员无限制', bg: '#EEF2FF' },
	{ icon: '⚡', name: '优先分析', desc: '插队优先处理', bg: '#FEF3C7' },
	{ icon: '📈', name: '深度分析', desc: 'AI详细解读', bg: '#ECFDF5' },
	{ icon: '📝', name: '报告对比', desc: '历史对比分析', bg: '#FCE7F3' },
	{ icon: '🔔', name: '逾期提醒', desc: '信用风险预警', bg: '#F0F9FF' },
	{ icon: '📞', name: '专属客服', desc: '1对1专属服务', bg: '#F5F3FF' },
]

const currentPrice = computed(() => {
	if (packages.value.length > 0 && selectedPackage.value < packages.value.length) {
		return packages.value[selectedPackage.value].price
	}
	return 0
})

onMounted(async () => {
	await Promise.all([loadVipStatus(), loadPackages()])
})

const loadVipStatus = async () => {
	try {
		const res: any = await checkVipStatus()
		if (res.code === 200 || res.code === 0) {
			const data = res.data || res
			isVip.value = data.isVip || false
			vipLevel.value = data.vipLevel || 'none'
			vipLevelText.value = data.vipLevelText || (isVip.value ? 'VIP会员' : '普通用户')
			vipExpire.value = data.expireDate || ''
			remainReports.value = data.remainReports ?? 3
			usedReports.value = data.usedReports ?? 0
			vipDaysLeft.value = data.daysLeft ?? 0
		}
	} catch (e) {
		console.log('VIP状态加载失败，使用默认值')
	}
}

const loadPackages = async () => {
	try {
		const res: any = await getVipPackages()
		if (res.code === 200 || res.code === 0) {
			const data = res.data || res
			if (Array.isArray(data) && data.length > 0) {
				packages.value = data.map((p: any) => ({
					name: p.name || '套餐',
					price: p.price || 0,
					unit: p.unit || '月',
					originalPrice: p.originalPrice || 0,
					tag: p.tag || '',
					features: p.features || []
				}))
				return
			}
		}
	} catch (e) {
		console.log('套餐加载失败，使用默认套餐')
	}
	// 默认套餐
	packages.value = [
		{
			id: 1,
			name: '月度会员',
			price: 29,
			unit: '月',
			originalPrice: 49,
			tag: '限时优惠',
			features: ['无限次报告分析', '优先处理队列', 'AI深度解读', '报告对比分析']
		},
		{
			id: 2,
			name: '年度会员',
			price: 199,
			unit: '年',
			originalPrice: 588,
			tag: '超值推荐',
			features: ['无限次报告分析', '优先处理队列', 'AI深度解读', '报告对比分析', '逾期风险预警', '专属客服']
		}
	]
}

const handlePurchase = async () => {
	if (packages.value.length === 0) return
	const pkg = packages.value[selectedPackage.value]
	
	uni.showModal({
		title: '确认购买',
		content: `确认购买 ${pkg.name}，金额 ¥${pkg.price}？`,
		success: async (res) => {
			if (res.confirm) {
				loading.value = true
				try {
					const result: any = await purchaseVip(pkg.id || selectedPackage.value + 1)
					if (result.code === 200 || result.code === 0) {
						const payData = result.data || result
						if (payData.payUrl) {
							// 跳转支付
							uni.showToast({ title: '正在跳转支付...', icon: 'none' })
						} else {
							uni.showToast({ title: '购买成功', icon: 'success' })
							await loadVipStatus()
						}
					} else {
						uni.showToast({ title: result.msg || '购买失败', icon: 'none' })
					}
				} catch (e: any) {
					uni.showToast({ title: e.message || '购买失败', icon: 'none' })
				} finally {
					loading.value = false
				}
			}
		}
	})
}

const showService = () => {
	uni.navigateTo({ url: '/pages/about/about?tab=service' })
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

/* VIP Card */
.vip-card {
	border-radius: 32rpx;
	padding: 36rpx;
	margin-bottom: 24rpx;
	position: relative;
	overflow: hidden;
	
	&.none {
		background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
	}
	&.basic {
		background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%);
	}
	&.premium {
		background: linear-gradient(135deg, #F59E0B 0%, #F97316 100%);
	}
	&.enterprise {
		background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
	}
	
	.vip-card-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 32rpx;
		
		.vip-badge {
			background: rgba(255,255,255,0.25);
			border-radius: 12rpx;
			padding: 8rpx 20rpx;
			
			.vip-badge-text {
				font-size: 26rpx;
				font-weight: 700;
				color: #FFFFFF;
			}
		}
		
		.vip-expire {
			font-size: 22rpx;
			color: rgba(255,255,255,0.8);
		}
	}
	
	.vip-card-bottom {
		display: flex;
		align-items: center;
		justify-content: space-around;
		
		.vip-stat {
			display: flex;
			flex-direction: column;
			align-items: center;
			
			.vip-stat-num {
				font-size: 40rpx;
				font-weight: 800;
				color: #FFFFFF;
				font-family: 'DIN Alternate', 'IBM Plex Sans', sans-serif;
			}
			
			.vip-stat-label {
				font-size: 20rpx;
				color: rgba(255,255,255,0.7);
				margin-top: 4rpx;
			}
		}
		
		.vip-stat-divider {
			width: 1rpx;
			height: 48rpx;
			background: rgba(255,255,255,0.3);
		}
	}
}

/* Section */
.section {
	margin-bottom: 24rpx;
}

.section-title {
	font-size: 30rpx;
	font-weight: 700;
	color: #1E293B;
	margin-bottom: 20rpx;
	padding-left: 8rpx;
}

/* Benefits Grid */
.benefits-grid {
	display: grid;
	grid-template-columns: 1fr 1fr 1fr;
	gap: 16rpx;
	
	.benefit-item {
		background: #FFFFFF;
		border-radius: 24rpx;
		padding: 24rpx 12rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8rpx;
		box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.04);
		
		.benefit-icon {
			width: 64rpx;
			height: 64rpx;
			border-radius: 16rpx;
			display: flex;
			align-items: center;
			justify-content: center;
			
			.benefit-emoji {
				font-size: 32rpx;
			}
		}
		
		.benefit-name {
			font-size: 22rpx;
			font-weight: 600;
			color: #1E293B;
		}
		
		.benefit-desc {
			font-size: 18rpx;
			color: #94A3B8;
			text-align: center;
		}
	}
}

/* Package List */
.package-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
	
	.package-card {
		background: #FFFFFF;
		border-radius: 28rpx;
		padding: 32rpx;
		position: relative;
		border: 3rpx solid #F1F5F9;
		box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.04);
		transition: all 0.2s;
		
		&.active {
			border-color: #6366F1;
			box-shadow: 0 4rpx 20rpx rgba(99,102,241,0.15);
		}
		
		.package-tag {
			position: absolute;
			top: 0;
			right: 32rpx;
			background: linear-gradient(135deg, #F59E0B, #F97316);
			color: #FFFFFF;
			font-size: 20rpx;
			font-weight: 600;
			padding: 4rpx 16rpx;
			border-radius: 0 0 12rpx 12rpx;
		}
		
		.package-name {
			font-size: 30rpx;
			font-weight: 700;
			color: #1E293B;
			margin-bottom: 12rpx;
		}
		
		.package-price {
			display: flex;
			align-items: baseline;
			gap: 2rpx;
			margin-bottom: 8rpx;
			
			.price-symbol {
				font-size: 28rpx;
				font-weight: 700;
				color: #6366F1;
			}
			
			.price-num {
				font-size: 56rpx;
				font-weight: 800;
				color: #6366F1;
				font-family: 'DIN Alternate', 'IBM Plex Sans', sans-serif;
				line-height: 1;
			}
			
			.price-unit {
				font-size: 24rpx;
				color: #94A3B8;
				margin-left: 4rpx;
			}
		}
		
		.package-original {
			font-size: 22rpx;
			color: #94A3B8;
			text-decoration: line-through;
			margin-bottom: 20rpx;
		}
		
		.package-features {
			display: flex;
			flex-direction: column;
			gap: 12rpx;
			
			.package-feature {
				display: flex;
				align-items: center;
				gap: 10rpx;
				font-size: 24rpx;
				color: #334155;
			}
		}
	}
}

/* Pay Section */
.pay-section {
	padding: 16rpx 0;
	
	.pay-btn {
		width: 100%;
		height: 96rpx;
		background: linear-gradient(135deg, #6366F1, #A855F7);
		border-radius: 48rpx;
		color: #FFFFFF;
		font-size: 32rpx;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
		border: none;
		letter-spacing: 2rpx;
		
		&::after {
			border: none;
		}
	}
	
	.pay-hint {
		text-align: center;
		margin-top: 16rpx;
		font-size: 22rpx;
		color: #94A3B8;
		
		.link {
			color: #6366F1;
		}
	}
}

/* Bottom Spacing */
.bottom-spacing {
	height: 140rpx;
}
</style>
