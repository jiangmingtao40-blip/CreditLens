<template>
	<view class="credit-score-container">
		<!-- 评分环 -->
		<view class="score-ring">
			<view class="ring-bg">
				<text class="score-value">{{ score }}</text>
				<text class="score-label">信用评分</text>
			</view>
			<view class="score-info">
				<text class="level-text" :style="{ color: levelColor }">{{ levelName }}</text>
				<text class="range-text">满分100分</text>
			</view>
		</view>

		<!-- 风险提示 -->
		<view class="risk-section" v-if="tips && tips.length > 0">
			<view class="section-title">
				<text class="title-icon">&#9888;</text>
				<text>风险提示</text>
			</view>
			<view class="risk-list">
				<view class="risk-item" v-for="(tip, index) in tips" :key="index">
					<text class="risk-dot">&#8226;</text>
					<text class="risk-text">{{ tip }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		name: 'CreditScore',
		props: {
			score: {
				type: Number,
				default: 0
			},
			tips: {
				type: Array,
				default: () => []
			}
		},
		computed: {
			levelName() {
				if (this.score >= 80) return '优秀';
				if (this.score >= 60) return '良好';
				if (this.score >= 40) return '一般';
				return '较差';
			},
			levelColor() {
				if (this.score >= 80) return '#22c55e';
				if (this.score >= 60) return '#3b82f6';
				if (this.score >= 40) return '#f59e0b';
				return '#ef4444';
			}
		}
	}
</script>

<style scoped>
	.credit-score-container {
		padding: 30rpx;
	}

	.score-ring {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 40rpx 0;
	}

	.ring-bg {
		width: 200rpx;
		height: 200rpx;
		border-radius: 50%;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		box-shadow: 0 8rpx 30rpx rgba(102, 126, 234, 0.3);
	}

	.score-value {
		font-size: 72rpx;
		font-weight: bold;
		color: #fff;
		line-height: 1;
	}

	.score-label {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.8);
		margin-top: 10rpx;
	}

	.score-info {
		margin-left: 40rpx;
	}

	.level-text {
		font-size: 36rpx;
		font-weight: bold;
	}

	.range-text {
		font-size: 24rpx;
		color: #999;
		margin-top: 10rpx;
	}

	.risk-section {
		margin-top: 30rpx;
		background: #fff8f0;
		border-radius: 16rpx;
		padding: 24rpx;
		border-left: 6rpx solid #f59e0b;
	}

	.section-title {
		font-size: 28rpx;
		font-weight: bold;
		color: #333;
		margin-bottom: 16rpx;
	}

	.title-icon {
		margin-right: 8rpx;
	}

	.risk-list {
		padding-left: 10rpx;
	}

	.risk-item {
		display: flex;
		align-items: flex-start;
		padding: 8rpx 0;
		font-size: 26rpx;
		color: #666;
		line-height: 1.6;
	}

	.risk-dot {
		margin-right: 10rpx;
		color: #f59e0b;
		flex-shrink: 0;
	}

	.risk-text {
		flex: 1;
	}
</style>
