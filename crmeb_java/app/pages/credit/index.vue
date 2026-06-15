<template>
	<view class="page">
		<!-- Status Bar -->
		<view class="status-bar">
			<text class="time">9:41</text>
			<view class="spacer"></view>
			<view class="battery"></view>
		</view>
		
		<!-- Content -->
		<scroll-view class="content" scroll-y>
			<!-- Hero Section -->
			<view class="hero">
				<view class="brand">信用解析</view>
				<view class="tagline">AI驱动的智能征信分析服务</view>
			</view>
			
			<!-- Quota Card -->
			<view class="quota-card">
				<view class="left">
					<view class="quota-label">免费查询次数</view>
					<view class="quota-count">{{ quotaInfo.freeCount }}</view>
				</view>
				<view class="quota-right">
					<view class="vip-badge" v-if="quotaInfo.isVip"><span>VIP</span></view>
					<view class="quota-price">¥{{ quotaInfo.pricePerQuery }}/次</view>
				</view>
			</view>
			
			<!-- Upload Button -->
			<button class="btn-primary" @click="goToUpload">
				<view class="btn-icon">
					<view class="icon-arrow-up"></view>
				</view>
				上传征信报告
			</button>
			
			<view class="hint-text">支持 JPG / PNG / PDF 格式，最大 20MB</view>
			
			<!-- Features Section -->
			<view class="section-title">核心功能</view>
			<view class="feature-row">
				<view class="feature-card">
					<view class="feature-icon purple">OCR</view>
					<view class="feature-name">OCR识别</view>
					<view class="feature-desc">精准提取文字</view>
				</view>
				<view class="feature-card">
					<view class="feature-icon purple">AI</view>
					<view class="feature-name">AI分析</view>
					<view class="feature-desc">深度报告解读</view>
				</view>
			</view>
			<view class="feature-row">
				<view class="feature-card">
					<view class="feature-icon purple">信</view>
					<view class="feature-name">信用评分</view>
					<view class="feature-desc">专业评级模型</view>
				</view>
				<view class="feature-card">
					<view class="feature-icon red">险</view>
					<view class="feature-name">风险提示</view>
					<view class="feature-desc">预警潜在风险</view>
				</view>
			</view>
			
			<!-- Process Section -->
			<view class="section-title">使用流程</view>
			<view class="process-row">
				<view class="step-item">
					<view class="step-circle">1</view>
					<view class="step-label">上传报告</view>
				</view>
				<view class="step-arrow">→</view>
				<view class="step-item">
					<view class="step-circle">2</view>
					<view class="step-label">智能识别</view>
				</view>
				<view class="step-arrow">→</view>
				<view class="step-item">
					<view class="step-circle">3</view>
					<view class="step-label">AI分析</view>
				</view>
				<view class="step-arrow">→</view>
				<view class="step-item">
					<view class="step-circle">4</view>
					<view class="step-label">查看报告</view>
				</view>
			</view>
			
			<!-- Security Badge -->
			<view class="security-badge">
				<view class="security-icon">✓</view>
				<text class="security-text">数据加密传输 · 隐私安全保障</text>
			</view>
		</scroll-view>
		
		<!-- Tab Bar -->
		<TabBar :current="0" @change="onTabChange"></TabBar>
	</view>
</template>

<script>
	import TabBar from '@/components/TabBar/index.vue';
	
	export default {
		components: {
			TabBar
		},
		data() {
			return {
				quotaInfo: {
					freeCount: 3,
					isVip: false,
					pricePerQuery: '9.9'
				}
			}
		},
		onLoad() {
			this.loadData();
		},
		methods: {
			loadData() {
				// 加载额度信息
				uni.request({
					url: 'http://localhost:20510/api/credit/quota',
					method: 'GET',
					success: (res) => {
						if (res.data.code === 200 && res.data.data) {
							this.quotaInfo = res.data.data;
						}
					},
					fail: () => {
						// 使用默认值
					}
				});
			},
			goToUpload() {
				uni.navigateTo({
					url: '/pages/credit/upload'
				});
			},
			onTabChange(index) {
				// Tab切换处理
			}
		}
	}
</script>

<style lang="scss" scoped>
page {
	background: #F8FAFC;
}

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
	flex-shrink: 0;
	
	.time {
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
	display: flex;
	flex-direction: column;
	gap: 24rpx;
	overflow-y: auto;
	-webkit-overflow-scrolling: touch;
}

/* Hero */
.hero {
	position: relative;
	background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #A855F7 100%);
	border-radius: 40rpx;
	padding: 72rpx 40rpx 56rpx;
	text-align: center;
	overflow: hidden;
	
	&::before {
		content: '';
		position: absolute;
		top: -60rpx;
		left: -60rpx;
		width: 180rpx;
		height: 180rpx;
		border-radius: 50%;
		background: rgba(255,255,255,0.08);
	}
	
	&::after {
		content: '';
		position: absolute;
		bottom: -120rpx;
		right: -60rpx;
		width: 260rpx;
		height: 260rpx;
		border-radius: 50%;
		background: rgba(255,255,255,0.05);
	}
}

.brand {
	position: relative;
	z-index: 1;
	font-size: 52rpx;
	font-weight: 700;
	color: #FFFFFF;
}

.tagline {
	position: relative;
	z-index: 1;
	font-size: 24rpx;
	color: rgba(255,255,255,0.7);
	margin-top: 12rpx;
}

/* Quota Card */
.quota-card {
	display: flex;
	align-items: center;
	background: #FFFFFF;
	border-radius: 28rpx;
	padding: 32rpx;
	gap: 32rpx;
	box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
}

.quota-card .left {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.quota-label {
	font-size: 22rpx;
	color: #64748B;
}

.quota-count {
	font-family: 'IBM Plex Sans', sans-serif;
	font-size: 68rpx;
	font-weight: 700;
	color: #6366F1;
	line-height: 1;
}

.quota-right {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	gap: 8rpx;
}

.vip-badge {
	background: #FEF3C7;
	border-radius: 8rpx;
	padding: 6rpx 12rpx;
	
	span {
		font-family: 'IBM Plex Sans', sans-serif;
		font-size: 20rpx;
		font-weight: 700;
		color: #D97706;
	}
}

.quota-price {
	font-size: 22rpx;
	color: #94A3B8;
}

/* Primary Button */
.btn-primary {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 100rpx;
	background: linear-gradient(90deg, #6366F1, #A855F7);
	border-radius: 50rpx;
	color: #FFFFFF;
	font-size: 30rpx;
	font-weight: 700;
	gap: 16rpx;
	border: none;
	padding: 0 40rpx;
	box-shadow: 0 8rpx 32rpx rgba(99,102,241,0.3);
	
	.btn-icon {
		width: 40rpx;
		height: 40rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.icon-arrow-up {
		width: 0;
		height: 0;
		border-left: 10rpx solid transparent;
		border-right: 10rpx solid transparent;
		border-bottom: 16rpx solid #FFFFFF;
	}
}

/* Hint Text */
.hint-text {
	font-size: 22rpx;
	color: #94A3B8;
	text-align: center;
}

/* Section Title */
.section-title {
	font-size: 34rpx;
	font-weight: 700;
	color: #1E293B;
}

/* Feature Cards */
.feature-row {
	display: flex;
	gap: 24rpx;
}

.feature-card {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	background: #FFFFFF;
	border-radius: 28rpx;
	padding: 24rpx 16rpx;
	gap: 4rpx;
	box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.04);
}

.feature-icon {
	width: 64rpx;
	height: 64rpx;
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 18rpx;
	font-weight: 700;
	
	&.purple {
		background: #EEF2FF;
		color: #6366F1;
	}
	
	&.red {
		background: #FEF2F2;
		color: #EF4444;
	}
}

.feature-name {
	font-size: 24rpx;
	font-weight: 600;
	color: #1E293B;
	margin-top: 8rpx;
}

.feature-desc {
	font-size: 20rpx;
	color: #94A3B8;
}

/* Process Steps */
.process-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 0 16rpx;
}

.step-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 12rpx;
}

.step-circle {
	width: 72rpx;
	height: 72rpx;
	border-radius: 50%;
	background: #6366F1;
	display: flex;
	align-items: center;
	justify-content: center;
	font-family: 'IBM Plex Sans', sans-serif;
	font-size: 28rpx;
	font-weight: 700;
	color: #FFFFFF;
}

.step-label {
	font-size: 20rpx;
	color: #64748B;
}

.step-arrow {
	font-size: 24rpx;
	color: #CBD5E1;
}

/* Security Badge */
.security-badge {
	display: flex;
	align-items: center;
	gap: 16rpx;
	background: #F0FDF4;
	border-radius: 24rpx;
	padding: 24rpx;
}

.security-icon {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: #10B981;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24rpx;
	font-weight: 700;
	color: #FFFFFF;
}

.security-text {
	font-size: 22rpx;
	color: #10B981;
}
</style>
