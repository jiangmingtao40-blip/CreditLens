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
			<!-- Profile Header -->
			<view class="profile-header">
				<view class="avatar">
					<template v-if="isLogin && userInfo && userInfo.avatar">
						<image :src="userInfo.avatar" class="avatar-img"></image>
					</template>
					<template v-else>
						<view class="avatar-default">U</view>
					</template>
				</view>
				<view class="profile-info">
					<view class="profile-name">
						{{ isLogin ? (userInfo.nickname || '用户') : '请点击登录' }}
					</view>
					<view class="profile-vip-row">
						<view class="profile-vip-badge" v-if="isVip">VIP会员</view>
						<view class="profile-phone" v-if="isLogin && userInfo && userInfo.phone">
							{{ formatPhone(userInfo.phone) }}
						</view>
					</view>
				</view>
			</view>
			
			<!-- Menu Group -->
			<view class="menu-group">
				<view class="menu-item" @click="goCreditCheck">
					<view class="menu-icon-wrap">
						<view class="menu-icon credit-icon"></view>
					</view>
					<text class="menu-text">征信查询</text>
					<view class="menu-arrow">›</view>
				</view>
				<view class="menu-item" @click="goRecords">
					<view class="menu-icon-wrap">
						<view class="menu-icon history-icon"></view>
					</view>
					<text class="menu-text">历史记录</text>
					<view class="menu-arrow">›</view>
				</view>
				<view class="menu-item" @click="onClickService">
					<view class="menu-icon-wrap">
						<view class="menu-icon service-icon"></view>
					</view>
					<text class="menu-text">联系客服</text>
					<view class="menu-arrow">›</view>
				</view>
				<view class="menu-item" @click="goSettings">
					<view class="menu-icon-wrap">
						<view class="menu-icon settings-icon"></view>
					</view>
					<text class="menu-text">设置</text>
					<view class="menu-arrow">›</view>
				</view>
			</view>
			
			<!-- Menu Group 2 -->
			<view class="menu-group">
				<view class="menu-item" @click="goAbout">
					<view class="menu-icon-wrap">
						<view class="menu-icon about-icon"></view>
					</view>
					<text class="menu-text">关于我们</text>
					<view class="menu-arrow">›</view>
				</view>
				<view class="menu-item" @click="goHelp">
					<view class="menu-icon-wrap">
						<view class="menu-icon help-icon"></view>
					</view>
					<text class="menu-text">帮助与反馈</text>
					<view class="menu-arrow">›</view>
				</view>
			</view>
			
			<!-- Logout Button -->
			<button class="logout-btn" v-if="isLogin" @click="logout">
				退出登录
			</button>
		</scroll-view>
		
		<!-- Tab Bar -->
		<TabBar :current="4" @change="onTabChange"></TabBar>
	</view>
</template>

<script>
	import Cache from '@/utils/cache';
	import { tokenIsExistApi } from '@/api/api.js';
	import { toLogin } from '@/libs/login.js';
	import { mapGetters } from "vuex";
	import TabBar from '@/components/TabBar/index.vue';

	export default {
		components: {
			TabBar
		},
		computed: mapGetters(['isLogin', 'uid']),
		data() {
			return {
				userInfo: {},
				isVip: false
			}
		},
		onLoad() {
			this.loadUserInfo();
		},
		onShow() {
			this.loadUserInfo();
		},
		methods: {
			async loadUserInfo() {
				try {
					const tokenIsExist = await tokenIsExistApi();
					if (this.isLogin && tokenIsExist.data) {
						this.$store.dispatch('USERINFO').then(res => {
							this.userInfo = res;
							this.isVip = res.vip || false;
						});
					} else {
						this.$store.commit("LOGOUT");
						this.$store.commit('UPDATE_LOGIN', '');
						this.$store.commit('UPDATE_USERINFO', {});
					}
				} catch (e) {
					console.error(e);
				}
			},
			
			formatPhone(phone) {
				if (!phone) return '';
				return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
			},
			
			openAuto() {
				toLogin();
			},
			
			goCreditCheck() {
				uni.switchTab({
					url: '/pages/credit/index'
				});
			},
			
			goRecords() {
				uni.navigateTo({
					url: '/pages/credit/records'
				});
			},
			
			onClickService() {
				uni.showModal({
					title: '联系客服',
					content: '客服电话：400-123-4567\n工作时间：9:00-18:00',
					showCancel: false
				});
			},
			
			goSettings() {
				uni.showToast({
					title: '设置功能开发中',
					icon: 'none'
				});
			},
			
			goAbout() {
				uni.showToast({
					title: '关于我们开发中',
					icon: 'none'
				});
			},
			
			goHelp() {
				uni.showToast({
					title: '帮助与反馈开发中',
					icon: 'none'
				});
			},
			
			logout() {
				uni.showModal({
					title: '提示',
					content: '确定要退出登录吗？',
					success: (res) => {
						if (res.confirm) {
							this.$store.commit("LOGOUT");
							this.$store.commit('UPDATE_LOGIN', '');
							this.$store.commit('UPDATE_USERINFO', {});
							this.userInfo = {};
							this.isVip = false;
						}
					}
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
}

/* Profile Header */
.profile-header {
	display: flex;
	align-items: center;
	background: linear-gradient(135deg, #6366F1, #A855F7);
	border-radius: 40rpx;
	padding: 32rpx;
	gap: 28rpx;
}

.avatar {
	width: 96rpx;
	height: 96rpx;
	border-radius: 50%;
	background: rgba(255,255,255,0.3);
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
	}
	
	.avatar-default {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
	}
}

.profile-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
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
	background: rgba(255,255,255,0.2);
	border-radius: 8rpx;
	padding: 4rpx 12rpx;
	font-size: 20rpx;
	font-weight: 700;
	color: #FFFFFF;
}

.profile-phone {
	font-size: 22rpx;
	color: rgba(255,255,255,0.7);
	font-family: 'IBM Plex Sans', sans-serif;
}

/* Menu Group */
.menu-group {
	background: #FFFFFF;
	border-radius: 28rpx;
	overflow: hidden;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}

.menu-item {
	display: flex;
	align-items: center;
	padding: 0 28rpx;
	height: 100rpx;
	cursor: pointer;
	border-bottom: 1rpx solid #F1F5F9;
	
	&:last-child {
		border-bottom: none;
	}
}

.menu-icon-wrap {
	width: 64rpx;
	height: 64rpx;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}

.menu-icon {
	width: 32rpx;
	height: 32rpx;
	border-radius: 8rpx;
	
	&.credit-icon {
		background: #EEF2FF;
		position: relative;
		
		&::before {
			content: '';
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			width: 16rpx;
			height: 16rpx;
			border: 3rpx solid #6366F1;
			border-radius: 4rpx;
		}
	}
	
	&.history-icon {
		background: #FEF3C7;
		border-radius: 50%;
		position: relative;
		
		&::before {
			content: '';
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			width: 12rpx;
			height: 12rpx;
			border: 3rpx solid #D97706;
			border-radius: 50%;
		}
	}
	
	&.service-icon {
		background: #F0FDF4;
		position: relative;
		
		&::before {
			content: '?';
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			font-size: 20rpx;
			font-weight: 700;
			color: #10B981;
		}
	}
	
	&.settings-icon {
		background: #F1F5F9;
		position: relative;
		
		&::before {
			content: '';
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			width: 16rpx;
			height: 16rpx;
			border: 3rpx solid #64748B;
			border-radius: 50%;
		}
	}
	
	&.about-icon {
		background: #EEF2FF;
		position: relative;
		
		&::before {
			content: 'i';
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			font-size: 18rpx;
			font-weight: 700;
			color: #6366F1;
			font-style: italic;
		}
	}
	
	&.help-icon {
		background: #FEF2F2;
		position: relative;
		
		&::before {
			content: '!';
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			font-size: 20rpx;
			font-weight: 700;
			color: #EF4444;
		}
	}
}

.menu-text {
	flex: 1;
	margin-left: 24rpx;
	font-size: 28rpx;
	color: #1E293B;
}

.menu-arrow {
	font-size: 32rpx;
	color: #CBD5E1;
}

/* Logout Button */
.logout-btn {
	height: 96rpx;
	background: #FFFFFF;
	border-radius: 48rpx;
	font-size: 28rpx;
	font-weight: 600;
	color: #EF4444;
	border: none;
	margin-top: 16rpx;
	margin-bottom: 120rpx;
}
</style>
