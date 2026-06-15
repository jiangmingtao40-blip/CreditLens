<template>
	<view class="page">
		<!-- Status Bar -->
		<view class="status-bar">
			<text class="time">9:41</text>
			<view class="spacer"></view>
			<view class="battery"></view>
		</view>
		
		<!-- Header -->
		<view class="page-header">
			<text class="back-arrow" @click="goBack">←</text>
			<view class="page-title">分析结果</view>
			<view class="header-spacer"></view>
		</view>
		
		<!-- Content -->
		<scroll-view class="content" scroll-y>
			<!-- Score Card -->
			<view class="score-card">
				<view class="score-label">信用评分</view>
				<view class="score-value">{{ resultData.score }}</view>
				<view class="grade-badge">
					<span>{{ resultData.grade }}</span>
				</view>
			</view>
			
			<!-- Risk Level -->
			<view class="risk-card" :class="getRiskClass()">
				<view class="risk-icon">{{ resultData.riskLevel === 'low' ? '低' : resultData.riskLevel === 'medium' ? '中' : '高' }}</view>
				<view class="risk-info">
					<view class="risk-title">{{ resultData.riskTitle }}</view>
					<view class="risk-desc">{{ resultData.riskDesc }}</view>
				</view>
			</view>
			
			<!-- Personal Info Section -->
			<view class="section-title">基本信息</view>
			<view class="info-card">
				<view class="info-row">
					<view class="info-label">姓名</view>
					<view class="info-value">{{ resultData.name }}</view>
				</view>
				<view class="info-row">
					<view class="info-label">身份证号</view>
					<view class="info-value">{{ resultData.idCard }}</view>
				</view>
				<view class="info-row">
					<view class="info-label">查询时间</view>
					<view class="info-value">{{ resultData.queryTime }}</view>
				</view>
			</view>
			
			<!-- Credit Summary Section -->
			<view class="section-title">信贷概要</view>
			<view class="detail-card" :class="{ warn: resultData.overdueCount > 0 }">
				<view class="left">
					<view class="detail-title">信贷账户数</view>
					<view class="detail-value" :class="resultData.loanCount > 5 ? 'warning' : ''">{{ resultData.loanCount }}个</view>
				</view>
				<view class="detail-arrow">›</view>
			</view>
			<view class="detail-card" :class="{ warn: resultData.overdueCount > 0 }">
				<view class="left">
					<view class="detail-title">逾期账户数</view>
					<view class="detail-value" :class="resultData.overdueCount > 0 ? 'warning' : ''">{{ resultData.overdueCount }}个</view>
				</view>
				<view class="detail-arrow">›</view>
			</view>
			<view class="detail-card">
				<view class="left">
					<view class="detail-title">负债情况</view>
					<view class="detail-value" :class="resultData.debtRatio > 50 ? 'warning' : 'green'">{{ resultData.debtRatio }}%</view>
				</view>
				<view class="detail-arrow">›</view>
			</view>
			
			<!-- Risk Warnings Section -->
			<view class="section-title" v-if="resultData.warnings && resultData.warnings.length > 0">风险提示</view>
			<view class="warning-card" v-for="(warning, index) in resultData.warnings" :key="index">
				<view class="warning-icon">!</view>
				<view class="warning-text">{{ warning }}</view>
			</view>
			
			<!-- Action Buttons -->
			<view class="action-row">
				<button class="btn-outline" @click="shareReport">
					分享报告
				</button>
				<button class="btn-primary" @click="viewDetails">
					查看详情
				</button>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	import { getCachedHistory, getCreditResult } from '@/api/credit.js';

	export default {
		data() {
			return {
				resultData: {
					score: 685,
					grade: '良好',
					riskLevel: 'low',
					riskTitle: '信用良好',
					riskDesc: '您的信用状况良好，具备较强的金融业务办理能力',
					name: '未识别',
					idCard: '未识别',
					queryTime: new Date().toLocaleString('zh-CN'),
					loanCount: 0,
					overdueCount: 0,
					debtRatio: 0,
					warnings: [],
					personalInfo: {},
					creditRecords: {},
					overdueRecords: {}
				}
			}
		},
		onLoad(options) {
			const taskId = options.taskId || '';
			if (taskId) {
				this.loadResult(taskId);
			} else {
				// 如果没有taskId，尝试从缓存获取
				const history = getCachedHistory();
				if (history.length > 0) {
					const latest = history[0];
					this.loadResult(latest.taskId);
				}
			}
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			loadResult(taskId) {
				getCreditResult(taskId).then((result) => {
					if (result && result.status === 'completed') {
						this.parseResult(result);
					} else {
						console.error('获取结果失败:', result);
					}
				}).catch((err) => {
					console.error('获取结果失败:', err);
					// 尝试从缓存获取
					const cached = api.getCachedResult(taskId);
					if (cached) {
						this.parseResult(cached);
					}
				});
			},
			parseResult(data) {
				// 解析信用评分
				this.resultData.score = data.credit_score || 600;
				
				// 解析等级
				const score = this.resultData.score;
				if (score >= 800) this.resultData.grade = '优秀';
				else if (score >= 700) this.resultData.grade = '良好';
				else if (score >= 600) this.resultData.grade = '一般';
				else this.resultData.grade = '较差';
				
				// 解析风险等级
				const riskLevel = data.risk_level || '低';
				if (riskLevel.includes('低') || riskLevel.includes('优')) {
					this.resultData.riskLevel = 'low';
					this.resultData.riskTitle = '风险等级：低';
					this.resultData.riskDesc = '信用状况良好，无重大风险项';
				} else if (riskLevel.includes('中')) {
					this.resultData.riskLevel = 'medium';
					this.resultData.riskTitle = '风险等级：中';
					this.resultData.riskDesc = '存在一定风险，建议关注';
				} else {
					this.resultData.riskLevel = 'high';
					this.resultData.riskTitle = '风险等级：高';
					this.resultData.riskDesc = '风险较高，建议及时处理';
				}
				
				// 解析个人信息
				if (data.personal_info) {
					this.resultData.name = data.personal_info.name || '未识别';
					this.resultData.idCard = data.personal_info.id_number ? 
						data.personal_info.id_number.replace(/(\d{3})\d{11}(\d{4})/, '$1***********$2') : '未识别';
				}
				
				// 解析信贷记录
				if (data.credit_records) {
					const records = data.credit_records;
					this.resultData.loanCount = records.credit_cards || 0;
					this.resultData.creditRecords = records;
				}
				
				// 解析逾期记录
				if (data.overdue_records) {
					this.resultData.overdueCount = data.overdue_records.count || 0;
					this.resultData.overdueRecords = data.overdue_records;
				}
				
				// 解析风险预警
				if (data.risk_tips && data.risk_tips.length > 0) {
					this.resultData.warnings = data.risk_tips;
				}
				
				// 更新查询时间
				this.resultData.queryTime = new Date().toLocaleString('zh-CN');
			},
			getRiskClass() {
				const classes = {
					low: 'risk-low',
					medium: 'risk-medium',
					high: 'risk-high'
				};
				return classes[this.resultData.riskLevel] || 'risk-low';
			},
			shareReport() {
				uni.showToast({
					title: '分享功能开发中',
					icon: 'none'
				});
			},
			viewDetails() {
				uni.showToast({
					title: '详情页开发中',
					icon: 'none'
				});
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

/* Page Header */
.page-header {
	display: flex;
	align-items: center;
	height: 88rpx;
	padding: 0 24rpx;
	gap: 24rpx;
}

.back-arrow {
	font-size: 44rpx;
	font-weight: 600;
	color: #1E293B;
	font-family: 'IBM Plex Sans', sans-serif;
	line-height: 1;
}

.page-title {
	flex: 1;
	font-size: 36rpx;
	font-weight: 700;
	color: #1E293B;
	text-align: center;
}

.header-spacer {
	width: 48rpx;
}

/* Content */
.content {
	flex: 1;
	padding: 20rpx;
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

/* Score Card */
.score-card {
	background: linear-gradient(135deg, #6366F1, #A855F7);
	border-radius: 40rpx;
	padding: 48rpx;
	text-align: center;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 8rpx;
}

.score-label {
	font-size: 24rpx;
	color: rgba(255,255,255,0.7);
}

.score-value {
	font-family: 'IBM Plex Sans', sans-serif;
	font-size: 112rpx;
	font-weight: 700;
	color: #FFFFFF;
	line-height: 1;
}

.grade-badge {
	background: rgba(255,255,255,0.2);
	border-radius: 26rpx;
	padding: 8rpx 24rpx;
	
	span {
		font-size: 26rpx;
		font-weight: 700;
		color: #FFFFFF;
	}
}

/* Risk Card */
.risk-card {
	display: flex;
	align-items: center;
	background: #F0FDF4;
	border-radius: 28rpx;
	padding: 28rpx 32rpx;
	gap: 24rpx;
	
	&.risk-low {
		background: #F0FDF4;
		.risk-icon { background: #10B981; }
		.risk-title { color: #10B981; }
	}
	
	&.risk-medium {
		background: #FFF7ED;
		.risk-icon { background: #F59E0B; }
		.risk-title { color: #F59E0B; }
	}
	
	&.risk-high {
		background: #FEF2F2;
		.risk-icon { background: #EF4444; }
		.risk-title { color: #EF4444; }
	}
}

.risk-icon {
	width: 72rpx;
	height: 72rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	font-weight: 700;
	color: #FFFFFF;
	flex-shrink: 0;
}

.risk-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 4rpx;
}

.risk-title {
	font-size: 28rpx;
	font-weight: 600;
}

.risk-desc {
	font-size: 22rpx;
	color: #64748B;
}

/* Section Title */
.section-title {
	font-size: 34rpx;
	font-weight: 700;
	color: #1E293B;
	margin-top: 8rpx;
}

/* Info Card */
.info-card {
	background: #FFFFFF;
	border-radius: 24rpx;
	padding: 8rpx 0;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}

.info-row {
	display: flex;
	align-items: center;
	padding: 24rpx 32rpx;
	border-bottom: 1rpx solid #F1F5F9;
	
	&:last-child {
		border-bottom: none;
	}
}

.info-label {
	width: 160rpx;
	font-size: 26rpx;
	color: #64748B;
}

.info-value {
	flex: 1;
	font-size: 26rpx;
	color: #1E293B;
	font-weight: 500;
}

/* Detail Card */
.detail-card {
	display: flex;
	align-items: center;
	background: #FFFFFF;
	border-radius: 24rpx;
	padding: 28rpx 32rpx;
	gap: 12rpx;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
	
	.left {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 4rpx;
	}
	
	&.warn {
		background: #FFF7ED;
	}
}

.detail-title {
	font-size: 26rpx;
	font-weight: 600;
	color: #1E293B;
}

.detail-value {
	font-size: 24rpx;
	color: #94A3B8;
	
	&.green {
		color: #10B981;
	}
	
	&.warning {
		color: #F59E0B;
	}
}

.detail-arrow {
	font-size: 32rpx;
	color: #CBD5E1;
}

/* Warning Card */
.warning-card {
	display: flex;
	align-items: center;
	background: #FEF2F2;
	border-radius: 24rpx;
	padding: 24rpx;
	gap: 16rpx;
}

.warning-icon {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: #EF4444;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24rpx;
	font-weight: 700;
	color: #FFFFFF;
	flex-shrink: 0;
}

.warning-text {
	flex: 1;
	font-size: 24rpx;
	color: #64748B;
}

/* Action Buttons */
.action-row {
	display: flex;
	gap: 24rpx;
	margin-top: 16rpx;
}

.btn-outline {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	height: 96rpx;
	background: #FFFFFF;
	border: 3rpx solid #E2E8F0;
	border-radius: 48rpx;
	color: #64748B;
	font-size: 28rpx;
	font-weight: 600;
}

.btn-primary {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	height: 96rpx;
	background: linear-gradient(90deg, #6366F1, #A855F7);
	border-radius: 48rpx;
	color: #FFFFFF;
	font-size: 28rpx;
	font-weight: 700;
	border: none;
	box-shadow: 0 8rpx 32rpx rgba(99,102,241,0.3);
}
</style>
