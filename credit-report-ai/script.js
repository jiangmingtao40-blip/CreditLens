/* ===== User State ===== */
var userState = {
  isLoggedIn: false,
  userId: null,
  token: localStorage.getItem('credit_token') || '',
  nickname: '',
  avatar: '',
  phone: '',
  isVip: false,
  freeCount: 0,
  balance: 0,
  reports: [],
  consumes: []
};

// 如果有token，启动时自动恢复登录态
(function initAuth() {
  var savedToken = localStorage.getItem('credit_token');
  if (savedToken) {
    fetch(API_BASE + '/api/user/info', { headers: { 'token': savedToken } })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        if (data.id) {
          userState.isLoggedIn = true;
          userState.userId = data.id;
          userState.token = savedToken;
          userState.nickname = data.nickname || '用户';
          userState.phone = data.phone ? data.phone.slice(0,3)+'****'+data.phone.slice(-4) : '';
          userState.avatar = userState.nickname[0] || '用';
          userState.isVip = data.is_vip || false;
          userState.freeCount = data.free_queries || 0;
          userState.balance = data.balance || 0;
          refreshProfilePage();
          loadUserData();
        }
      })
      .catch(function() { /* token过期，忽略 */ });
  }
  refreshProfilePage();
})();

function loadUserData() {
  if (!userState.token) return;
  // 加载消费记录
  fetch(API_BASE + '/api/pay/consume-log', { headers: { 'token': userState.token } })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      if (data.items) {
        userState.consumes = data.items.map(function(item) { return { id: item.id, type: item.type, name: item.name, date: item.created_at, amount: item.amount }; });
      }
    }).catch(function() {});
  // 加载邀请统计
  fetch(API_BASE + '/api/invite/stats', { headers: { 'token': userState.token } })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      if (data.invite_count !== undefined) {
        userState.commission = data.total_commission || 0;
      }
    }).catch(function() {});
}

/* ===== Page Management ===== */
var pages = document.querySelectorAll('.page');
var pageMap = {0:'page-home',1:'page-upload',2:'page-results',3:'page-history',4:'page-profile',5:'page-progress',6:'page-login'};
var currentPage = 0;

function switchPage(idx) {
  if (idx === currentPage) return;
  var oldPage = document.getElementById(pageMap[currentPage]);
  var newPage = document.getElementById(pageMap[idx]);
  if (!oldPage || !newPage) return;
  oldPage.classList.remove('active');
  newPage.classList.add('active');
  currentPage = idx;
  var content = newPage.querySelector('.content');
  if (content) content.scrollTo(0, 0);
  updateTabBar(idx);
  if (idx === 4) refreshProfilePage();
}

function goToUpload() { switchPage(1); }
function goToProgress() { switchPage(5); }

/* ===== Tab Bar ===== */
function updateTabBar(idx) {
  var tabBars = document.querySelectorAll('.tab-bar-container');
  for (var i = 0; i < tabBars.length; i++) {
    var items = tabBars[i].querySelectorAll('.tab-item');
    for (var j = 0; j < items.length; j++) {
      items[j].classList.remove('active');
    }
  }
  // 首页=0, 历史=3, 上传=1, 结果=2, 我的=4
  var mapTab = {0:0, 3:1, 1:2, 2:3, 4:4};
  var tabIdx = mapTab[idx];
  if (tabIdx !== undefined && tabBars.length > 0) {
    for (var k = 0; k < tabBars.length; k++) {
      var item = tabBars[k].querySelectorAll('.tab-item')[tabIdx];
      if (item) item.classList.add('active');
    }
  }
}

/* ===== Toast ===== */
function toast(msg) {
  var el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(el._t);
  el._t = setTimeout(function() { el.classList.remove('show'); }, 1600);
}

/* ===== Detail Card Toggle ===== */
function toggleDetail(card) {
  var expand = card.querySelector('.expand');
  var arrow = card.querySelector('.detail-arrow');
  if (!expand || !arrow) return;
  // 直接切换 class，由 CSS 处理过渡动画和样式
  expand.classList.toggle('open');
  arrow.classList.toggle('rotated');
}

/* ===== 更新风险等级显示 ===== */
function updateRiskLevel(riskLevel) {
  var riskIcon = document.querySelector('.risk-icon');
  var riskTitle = document.querySelector('.risk-title');
  var riskDesc = document.querySelector('.risk-desc');
  
  if (!riskIcon || !riskTitle || !riskDesc) return;
  
  // 同时支持英文和中文风险等级
  var isLow = riskLevel && (riskLevel.includes('低') || riskLevel.includes('优') || riskLevel.includes('low'));
  var isMedium = riskLevel && (riskLevel.includes('中') || riskLevel.includes('medium'));
  
  if (isLow) {
    riskIcon.innerHTML = '<svg viewBox="0 0 20 20"><path d="M10 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zm-1-13l3 3-3 3-1.5-1.5L8 9l-3 3-1.5-1.5L7 9l-2-2 1.5-1.5L7 6l2-2 1.5 1.5L10 6l3-3 1.5 1.5L12 6l2 2-1.5 1.5L11 9l3-3 1.5 1.5L14 11l-3 3-1.5-1.5L11 11l-3 3-1.5-1.5L9 11l2-2-1.5-1.5L9 8l-2-2 1.5-1.5L9 6z" fill="#10B981"/></svg>';
    riskTitle.textContent = '风险等级：低风险';
    riskDesc.textContent = '信用状况良好，无重大风险项';
    riskIcon.style.backgroundColor = '#ECFDF5';
  } else if (isMedium) {
    riskIcon.innerHTML = '<svg viewBox="0 0 20 20"><path d="M10 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zm1-11h-2v6h2v-6zm0 8h-2v2h2v-2z" fill="#F59E0B"/></svg>';
    riskTitle.textContent = '风险等级：中风险';
    riskDesc.textContent = '存在一定风险，建议关注';
    riskIcon.style.backgroundColor = '#FFFBEB';
  } else {
    riskIcon.innerHTML = '<svg viewBox="0 0 20 20"><path d="M10 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zm1-11h-2v6h2v-6zm0 8h-2v2h2v-2z" fill="#EF4444"/></svg>';
    riskTitle.textContent = '风险等级：高风险';
    riskDesc.textContent = '风险较高，建议及时处理';
    riskIcon.style.backgroundColor = '#FEF2F2';
  }
}

/* ===== Responsive Scaling ===== */
var DESIGN_W = 375, DESIGN_H = 812;
function resize() {
  var ww = window.innerWidth, wh = window.innerHeight;
  var scale = Math.min(ww / DESIGN_W, wh / DESIGN_H);
  var wrap = document.getElementById('appWrapper');
  wrap.style.transform = 'scale(' + scale + ')';
  wrap.style.left = ((ww - DESIGN_W * scale) / 2) + 'px';
  wrap.style.top = ((wh - DESIGN_H * scale) / 2) + 'px';
}
window.addEventListener('resize', resize);
resize();

/* ===== API Configuration ===== */
var API_BASE = 'http://localhost:8081';  // Python 后端 FastAPI 地址

/* ===== File Upload (Demo Mode) ===== */
var currentTaskId = null;
var progressTimer = null;
var isDemoMode = false; // 关闭演示模式，使用真实后端API

var uploadZone = document.getElementById('uploadZone');
if (uploadZone) {
  uploadZone.addEventListener('click', function() {
    var input = document.createElement('input');
    input.type = 'file';
    input.accept = '.jpg,.jpeg,.png,.pdf';
    input.onchange = function(e) {
      var file = e.target.files[0];
      if (file) uploadFile(file);
    };
    input.click();
  });
  uploadZone.addEventListener('dragover', function(e) {
    e.preventDefault();
    uploadZone.style.borderColor = '#6366F1';
    uploadZone.style.background = '#EEF2FF';
  });
  uploadZone.addEventListener('dragleave', function() {
    uploadZone.style.borderColor = 'rgba(99,102,241,0.3)';
    uploadZone.style.background = '#F8FAFC';
  });
  uploadZone.addEventListener('drop', function(e) {
    e.preventDefault();
    uploadZone.style.borderColor = 'rgba(99,102,241,0.3)';
    uploadZone.style.background = '#F8FAFC';
    var file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  });
}

/* ===== 上传 -> 后端API 或 演示Fallback ===== */

function uploadFile(file) {
  toast('正在上传 ' + file.name + '...');
  userState.freeCount = Math.max(0, userState.freeCount - 1);
  var formData = new FormData();
  formData.append('file', file);

  fetch(API_BASE + '/api/ocr/upload', { method: 'POST', body: formData })
    .then(function(res) {
      if (!res.ok) throw new Error('上传失败: ' + res.status);
      return res.json();
    })
    .then(function(data) {
      if (!data.task_id) throw new Error('未获取到任务ID');
      currentTaskId = data.task_id;
      toast('上传成功，开始分析...');
      switchPage(5);
      startRealAnalysis(data.task_id);
    })
    .catch(function(err) {
      console.log('Backend unreachable, fallback to demo:', err.message);
      toast('后端未启动，使用演示模式...');
      currentTaskId = 'demo_' + Date.now();
      setTimeout(function() {
        switchPage(5);
        startDemoProgress();
      }, 600);
    });
}

function demoQuickUpload(fileName) {
  if (userState.freeCount <= 0) {
    toast('免费次数已用完，请先充值');
    return;
  }
  uploadFile({ name: fileName });
}

/* ===== 真实后端分析流程 ===== */

function startRealAnalysis(taskId) {
  console.log('=== 开始真实分析 ===', taskId);
  var statusEl = document.querySelector('.progress-status');
  var percentEl = document.getElementById('progressPercent');
  var timeEl = document.querySelector('.progress-time');
  if (statusEl) statusEl.textContent = '正在提取文字...';
  if (percentEl) percentEl.textContent = '5%';
  if (timeEl) timeEl.textContent = '预计剩余 00:20';
  updateProgressSteps(0);

  // 调用 analyze
  fetch(API_BASE + '/api/ocr/analyze/' + taskId, { method: 'POST' })
    .then(function(res) { 
      console.log('=== 分析响应状态 ===', res.status);
      return res.json(); 
    })
    .then(function(data) {
      console.log('=== 分析返回数据 ===', JSON.stringify(data, null, 2));
      if (data.status === 'completed') {
        // 直接完成，获取结果
        showRealResults(data);
      } else {
        // 轮询等待
        startResultPolling(taskId);
      }
    })
    .catch(function(err) {
      console.log('Analysis error, fallback to demo:', err.message);
      startDemoProgress();
    });
}

function startResultPolling(taskId) {
  var statusEl = document.querySelector('.progress-status');
  var percentEl = document.getElementById('progressPercent');
  var timeEl = document.querySelector('.progress-time');
  var startTime = Date.now();
  var lastStatus = '';
  var maxPolls = 30;

  updateProgressSteps(0);

  function poll() {
    fetch(API_BASE + '/api/ocr/result/' + taskId)
      .then(function(res) { return res.json(); })
      .then(function(data) {
        maxPolls--;
        var elapsed = Math.floor((Date.now() - startTime) / 1000);

        if (data.status === 'completed') {
          clearInterval(pollTimer);
          if (statusEl) statusEl.textContent = '分析完成！';
          if (percentEl) percentEl.textContent = '100%';
          if (timeEl) timeEl.textContent = '已用时 00:' + (elapsed < 10 ? '0' : '') + elapsed;
          updateProgressSteps(3);
          setTimeout(function() { showRealResults(data); }, 600);
          return;
        }

        if (data.status === 'failed' || maxPolls <= 0) {
          clearInterval(pollTimer);
          toast('分析失败，使用演示数据');
          startDemoProgress();
          return;
        }

        // 更新进度
        if (data.status !== lastStatus) {
          lastStatus = data.status;
          var stepIdx = data.status === 'uploaded' ? 0 : (data.status === 'processing' ? 1 : 2);
          updateProgressSteps(stepIdx);
          if (statusEl) statusEl.textContent = stepIdx === 0 ? '正在上传文件...' : (stepIdx === 1 ? 'OCR文字识别 + AI分析中...' : '生成分析报告...');
        }

        var progress = Math.min(95, 5 + elapsed * 3);
        if (percentEl) percentEl.textContent = progress + '%';
        var remaining = Math.max(1, Math.floor((95 - progress) / 3));
        if (timeEl) timeEl.textContent = '预计剩余 00:' + (remaining < 10 ? '0' : '') + remaining;
      })
      .catch(function() {
        // 网络错误忽略，继续轮询
      });
  }

  var pollTimer = setInterval(poll, 2000);
  poll(); // 立即第一次
  progressTimer = pollTimer;
}

function fetchResult(taskId) {
  fetch(API_BASE + '/api/ocr/result/' + taskId)
    .then(function(res) { return res.json(); })
    .then(function(data) {
      if (data.status === 'completed') {
        showRealResults(data);
      } else {
        toast('结果尚未就绪');
      }
    })
    .catch(function(err) {
      console.log('Fetch result error:', err.message);
      showDemoResults();
    });
}

function showRealResults(data) {
  console.log('=== 后端返回数据 ===', JSON.stringify(data, null, 2));
  switchPage(2);
  
  // 延迟填充数据，确保页面切换完成后DOM已加载
  setTimeout(function() {
    var scoreEl = document.querySelector('.score-value');
    var score = data.credit_score !== undefined && data.credit_score !== null ? data.credit_score : 0;
    if (scoreEl) scoreEl.textContent = score || 'N/A';

    var gradeEl = document.querySelector('.grade-badge span');
    if (gradeEl) {
      if (score >= 800) gradeEl.textContent = '优秀';
      else if (score >= 700) gradeEl.textContent = '良好';
      else if (score >= 600) gradeEl.textContent = '一般';
      else gradeEl.textContent = '暂无评级';
    }

    // 更新风险等级显示
    updateRiskLevel(data.risk_level);

    // 填充个人信息卡片（兼容 personal_info 和 personal 两种字段名）
    var personal = data.personal_info || data.personal || {};
    console.log('=== 个人信息数据 ===', personal);
    var idCard = personal.id_card || personal.id_number || '未识别';
    if (idCard && idCard.length >= 18) {
      idCard = idCard.replace(/(\d{3})\d{11}(\d{4})/, '$1***********$2');
    } else if (idCard && idCard.length === 4) {
      idCard = '***********' + idCard;
    }
    fillDetailCard('个人信息', [
      ['姓名', personal.name || '未识别'],
      ['身份证号', idCard],
      ['婚姻状况', personal.marriage || personal.marital_status || '未识别'],
      ['学历', personal.education || '未识别']
    ]);

    // 填充信贷记录卡片（兼容 credit_summary 和 credit 两种字段名）
    var credit = data.credit_summary || data.credit || {};
    var cards = credit.credit_cards || [];
    var loans = credit.loans || credit.mortgages || credit.other_loans || [];
    var totalCards = Array.isArray(cards) ? cards.length : (typeof cards === 'number' ? cards : 0);
    var totalLoans = Array.isArray(loans) ? loans.length : (typeof loans === 'number' ? loans : 0);
    fillDetailCard('信贷记录', [
      ['信用卡笔数', totalCards + '笔'],
      ['贷款笔数', totalLoans + '笔'],
      ['还款状态', credit.repayment_status || credit.status || '正常']
    ]);

    // 填充逾期记录卡片
    var overdue = data.overdue || {};
    var hasOverdue = overdue.has_overdue || data.has_overdue || false;
    var overdueDetails = overdue.details || data.overdue_details || '暂无逾期记录';
    fillDetailCard('逾期记录', [
      ['是否有逾期', hasOverdue ? '是' : '否'],
      ['详情', overdueDetails]
    ]);

    // 填充风险预警卡片
    var warnings = data.risk_warnings || [];
    var suggestions = data.suggestions || [];
    fillDetailCard('风险预警', [
      ['风险等级', data.risk_level || '未识别'],
      ['风险提示', warnings.length > 0 ? warnings.join('；') : '暂无'],
      ['优化建议', suggestions.length > 0 ? suggestions.join('；') : '暂无']
    ]);

    // 更新首页
    var quotaEl = document.querySelector('.quota-count');
    if (quotaEl) quotaEl.textContent = Math.max(0, userState.freeCount);

    // 写入历史
    var now = new Date();
    var dateStr = now.getFullYear() + '-' +
      String(now.getMonth() + 1).padStart(2, '0') + '-' +
      String(now.getDate()).padStart(2, '0') + ' ' +
      String(now.getHours()).padStart(2, '0') + ':' +
      String(now.getMinutes()).padStart(2, '0');
    userState.reports.unshift({
      id: userState.reports.length + 1,
      taskId: currentTaskId,
      name: '个人征信报告',
      date: dateStr,
      score: score
    });
    userState.consumes.unshift({
      id: userState.consumes.length + 1,
      type: 'query',
      name: '征信查询',
      date: dateStr,
      amount: -9.90
    });

    toast('分析完成');
  }, 300);
}

function fillDetailCard(title, rows) {
  console.log('=== fillDetailCard START === 标题:', title, ', 数据:', JSON.stringify(rows));
  // 找到对应卡片，修改展开区内容
  var cards = document.querySelectorAll('.detail-card');
  console.log('=== 找到卡片数量 ===', cards.length);
  
  if (cards.length === 0) {
    console.log('=== 警告：未找到任何 .detail-card 元素 ===');
    return;
  }
  
  var found = false;
  for (var i = 0; i < cards.length; i++) {
    // 兼容两种标题选择器：.detail-title 和 .detail-header span
    var h = cards[i].querySelector('.detail-title') || cards[i].querySelector('.detail-header span');
    var cardTitle = h ? h.textContent.trim() : '未找到';
    console.log('=== 卡片', i, '标题 ===', cardTitle);
    
    if (h && h.textContent.trim() === title) {
      console.log('=== 找到匹配的卡片 ===');
      var expand = cards[i].querySelector('.expand');
      console.log('=== 找到展开区域 ===', expand);
      
      if (!expand) {
        console.log('=== 警告：未找到 .expand 元素 ===');
        continue;
      }
      
      var html = '';
      for (var j = 0; j < rows.length; j++) {
        html += '<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f0f0f0;font-size:13px">'
          + '<span style="color:#64748b">' + rows[j][0] + '</span>'
          + '<span style="color:#1e293b;font-weight:500">' + rows[j][1] + '</span>'
          + '</div>';
      }
      console.log('=== 生成的HTML ===', html);
      expand.innerHTML = html;
      console.log('=== 已成功更新卡片内容 ===');
      found = true;
      break;
    }
  }
  
  if (!found) {
    console.log('=== 警告：未找到标题为 "' + title + '" 的卡片 ===');
  }
}

function updateProgressSteps(activeIdx) {
  var steps = document.querySelectorAll('.step-item-progress');
  for (var i = 0; i < steps.length; i++) {
    var icon = steps[i].querySelector('.icon');
    var span = steps[i].querySelector('span:last-child');
    if (!icon || !span) continue;
    if (i < activeIdx) { icon.textContent = '✓'; span.className = 'step-done'; }
    else if (i === activeIdx) { icon.textContent = '⟳'; span.className = 'step-active'; }
    else { icon.textContent = '○'; span.className = 'step-pending'; }
  }
}

/* ===== 演示模式Fallback（后端不可用时） ===== */

function startDemoProgress() {
  var percentEl = document.getElementById('progressPercent');
  var statusEl = document.querySelector('.progress-status');
  var timeEl = document.querySelector('.progress-time');
  var progress = 0;
  var elapsed = 0;
  var steps = [
    { threshold: 15, status: '正在上传文件...' },
    { threshold: 35, status: 'OCR文字识别中...' },
    { threshold: 60, status: 'AI智能解析中...' },
    { threshold: 85, status: '生成分析报告...' },
    { threshold: 100, status: '分析完成！' }
  ];
  var stepIdx = 0;

  if (timeEl) timeEl.textContent = '预计剩余 00:15';

  progressTimer = setInterval(function() {
    if (progress < 30) progress += Math.floor(Math.random() * 6) + 3;
    else if (progress < 60) progress += Math.floor(Math.random() * 4) + 2;
    else if (progress < 90) progress += Math.floor(Math.random() * 2) + 1;
    else progress += 0.5;
    if (progress > 99) progress = 100;

    if (percentEl) percentEl.textContent = Math.floor(progress) + '%';

    while (stepIdx < steps.length && progress >= steps[stepIdx].threshold) {
      if (statusEl) statusEl.textContent = steps[stepIdx].status;
      updateProgressSteps(stepIdx);
      stepIdx++;
    }

    elapsed++;
    if (timeEl) {
      var remaining = Math.max(0, 15 - Math.floor(elapsed / 2));
      timeEl.textContent = '预计剩余 00:' + (remaining < 10 ? '0' : '') + remaining;
    }

    if (progress >= 100) {
      clearInterval(progressTimer);
      if (statusEl) statusEl.textContent = '分析完成！';
      if (percentEl) percentEl.textContent = '100%';
      if (timeEl) timeEl.textContent = '已用时 00:' + (elapsed < 10 ? '0' : '') + Math.floor(elapsed / 2);
      updateProgressSteps(4);
      setTimeout(function() { showDemoResults(); }, 800);
    }
  }, 600);
}

function showDemoResults() {
  switchPage(2);
  var demoData = { credit_score: 782, risk_level: '低风险' };
  var scoreEl = document.querySelector('.score-value');
  if (scoreEl) scoreEl.textContent = demoData.credit_score;

  var gradeEl = document.querySelector('.grade-badge span');
  if (gradeEl) gradeEl.textContent = '良好';

  var now = new Date();
  var dateStr = now.getFullYear() + '-' +
    String(now.getMonth() + 1).padStart(2, '0') + '-' +
    String(now.getDate()).padStart(2, '0') + ' ' +
    String(now.getHours()).padStart(2, '0') + ':' +
    String(now.getMinutes()).padStart(2, '0');
  userState.reports.unshift({
    id: userState.reports.length + 1,
    taskId: currentTaskId,
    name: '个人征信报告（演示）',
    date: dateStr,
    score: demoData.credit_score
  });
  userState.consumes.unshift({
    id: userState.consumes.length + 1,
    type: 'query',
    name: '征信查询',
    date: dateStr,
    amount: -9.90
  });

  var quotaEl = document.querySelector('.quota-count');
  if (quotaEl) quotaEl.textContent = Math.max(0, userState.freeCount);

  toast('分析完成（演示模式）');
}

function cancelProgress() {
  if (progressTimer) {
    clearInterval(progressTimer);
    progressTimer = null;
  }
  switchPage(0);
  toast('已取消分析');
}

/* ===== Modal System ===== */
function closeModal() {
  var overlay = document.getElementById('modalOverlay');
  if (overlay) overlay.classList.remove('open');
}
function openModal(title, bodyHTML, footerHTML) {
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalBody').innerHTML = bodyHTML;
  document.getElementById('modalFooter').innerHTML = footerHTML || '';
  document.getElementById('modalOverlay').classList.add('open');
}

/* ===== 我的报告 ===== */
function openMyReports() {
  if (!userState.isLoggedIn) { goToLogin(); return; }
  var html = '<div style="text-align:center;padding:20px;color:#94A3B8;">加载中...</div>';
  openModal('我的报告', html, '');
  
  fetch(API_BASE + '/api/pay/orders', { headers: { 'token': userState.token } })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      var orders = data.orders || [];
      var html = '';
      if (orders.length === 0) {
        html = '<div class="empty-state"><div class="empty-icon">📄</div><div class="empty-text">暂无报告记录</div></div>';
      } else {
        for (var i = 0; i < orders.length; i++) {
          var r = orders[i];
          html += '<div class="report-item">';
          html += '<div class="report-icon">📊</div>';
          html += '<div class="report-info"><div class="report-name">征信查询</div><div class="report-date">' + r.created_at + '</div></div>';
          html += '<div class="report-score" style="color:' + (r.status==='paid'?'#10B981':'#F59E0B') + '">' + r.status + '</div>';
          html += '</div>';
        }
      }
      document.getElementById('modalBody').innerHTML = html;
    })
    .catch(function() {
      document.getElementById('modalBody').innerHTML = '<div class="empty-state"><div class="empty-icon">📄</div><div class="empty-text">加载失败</div></div>';
    });
}

/* ===== 消费记录 ===== */
function openConsumeRecords() {
  if (!userState.isLoggedIn) { goToLogin(); return; }
  var html = '<div style="text-align:center;padding:20px;color:#94A3B8;">加载中...</div>';
  openModal('消费记录', html, '');
  
  fetch(API_BASE + '/api/pay/consume-log', { headers: { 'token': userState.token } })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      var items = data.items || [];
      var html = '';
      if (items.length === 0) {
        html = '<div class="empty-state"><div class="empty-icon">💰</div><div class="empty-text">暂无消费记录</div></div>';
      } else {
        for (var i = 0; i < items.length; i++) {
          var c = items[i];
          var amountClass = c.amount < 0 ? ' out' : '';
          var amountStr = (c.amount >= 0 ? '+' : '') + c.amount.toFixed(2);
          html += '<div class="consume-item">';
          html += '<div class="consume-icon">' + (c.amount < 0 ? '💳' : '💵') + '</div>';
          html += '<div class="consume-info"><div class="consume-name">' + c.name + '</div><div class="consume-date">' + c.created_at + '</div></div>';
          html += '<div class="consume-amount' + amountClass + '">' + amountStr + '</div>';
          html += '</div>';
        }
      }
      document.getElementById('modalBody').innerHTML = html;
    })
    .catch(function() {
      document.getElementById('modalBody').innerHTML = '<div class="empty-state"><div class="empty-icon">💰</div><div class="empty-text">加载失败</div></div>';
    });
}

/* ===== 推广佣金 ===== */
function openCommission() {
  if (!userState.isLoggedIn) { goToLogin(); return; }
  var html = '<div style="text-align:center;padding:20px;color:#94A3B8;">加载中...</div>';
  openModal('推广佣金', html, '');
  
  fetch(API_BASE + '/api/invite/stats', { headers: { 'token': userState.token } })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      var html = '<div style="text-align:center;padding:16px 0;">';
      html += '<div style="font-size:36px;margin-bottom:8px;">💎</div>';
      html += '<div style="font-size:28px;font-weight:700;color:#1E293B;font-family:\'IBM Plex Sans\',sans-serif;">¥' + (data.total_commission || 0).toFixed(2) + '</div>';
      html += '<div style="font-size:13px;color:#64748B;margin-top:4px;">可提现佣金</div>';
      html += '</div>';
      html += '<div style="background:#EEF2FF;border-radius:12px;padding:14px;margin-top:12px;">';
      html += '<div style="font-size:13px;color:#6366F1;font-weight:600;">已邀请 ' + (data.invite_count || 0) + ' 人</div>';
      html += '<div style="font-size:12px;color:#64748B;margin-top:4px;">每邀请1位好友完成首次查询，可得 ¥5.00 佣金</div>';
      html += '<div style="font-size:11px;color:#94A3B8;margin-top:8px;background:#F8FAFC;padding:8px;border-radius:8px;word-break:break-all;">邀请码：' + (data.invite_code || '') + '</div>';
      html += '</div>';
      var footer = '<button class="btn-primary" onclick="withdrawCommission()" style="width:100%;height:46px;border:none;border-radius:23px;background:linear-gradient(90deg,#6366F1,#A855F7);color:#fff;font-size:15px;font-weight:700;cursor:pointer;">立即提现</button>';
      document.getElementById('modalBody').innerHTML = html;
      document.getElementById('modalFooter').innerHTML = footer;
    })
    .catch(function() {
      document.getElementById('modalBody').innerHTML = '<div style="text-align:center;padding:20px;">加载失败</div>';
    });
}
function withdrawCommission() {
  closeModal();
  toast('提现申请已提交，预计1-3个工作日到账');
}

/* ===== 设置 ===== */
function openSettings() {
  var html = '';
  html += '<div class="settings-item" onclick="toast(\'修改手机号\')"><span class="settings-icon">📱</span><span class="settings-text">修改手机号</span><span class="settings-value">' + userState.phone + '</span><svg class="settings-arrow" viewBox="0 0 16 16"><path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none"/></svg></div>';
  html += '<div class="settings-item" onclick="toast(\'修改密码\')"><span class="settings-icon">🔒</span><span class="settings-text">修改密码</span><svg class="settings-arrow" viewBox="0 0 16 16"><path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none"/></svg></div>';
  html += '<div class="settings-item" onclick="toast(\'通知设置\')"><span class="settings-icon">🔔</span><span class="settings-text">通知设置</span><span class="settings-value">已开启</span><svg class="settings-arrow" viewBox="0 0 16 16"><path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none"/></svg></div>';
  html += '<div class="settings-item" onclick="toast(\'清除缓存\')"><span class="settings-icon">🗑️</span><span class="settings-text">清除缓存</span><span class="settings-value">2.3MB</span><svg class="settings-arrow" viewBox="0 0 16 16"><path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none"/></svg></div>';
  openModal('设置', html, '');
}

/* ===== 联系客服 ===== */
function openContact() {
  var html = '<div class="contact-card">';
  html += '<div class="contact-row"><span class="contact-icon">📞</span><span>客服电话：</span><span class="contact-value">400-123-4567</span></div>';
  html += '<div class="contact-row"><span class="contact-icon">💬</span><span>在线客服：</span><span class="contact-value">工作日 9:00-18:00</span></div>';
  html += '<div class="contact-row"><span class="contact-icon">📧</span><span>邮箱：</span><span class="contact-value">support@credit-ai.com</span></div>';
  html += '</div>';
  html += '<div style="text-align:center;padding:16px 0;font-size:12px;color:#94A3B8;">如有疑问请联系客服，我们将尽快为您解答</div>';
  openModal('联系客服', html, '');
}

/* ===== 关于我们 ===== */
function openAbout() {
  var html = '<div class="about-section">';
  html += '<div class="about-logo"><div class="about-logo-icon">🛡️</div><div class="about-logo-name">信用解析</div><div class="about-version">v1.0.0</div></div>';
  html += '<div class="about-desc">AI驱动的智能征信分析服务，基于DeepSeek大模型为您提供专业、快速的征信报告解读。</div>';
  html += '<div class="about-features">';
  html += '<div class="about-feature"><span class="about-dot"></span>PaddleOCR 高精度文字识别</div>';
  html += '<div class="about-feature"><span class="about-dot"></span>DeepSeek 大模型智能分析</div>';
  html += '<div class="about-feature"><span class="about-dot"></span>多维信用评分体系</div>';
  html += '<div class="about-feature"><span class="about-dot"></span>风险预警与优化建议</div>';
  html += '</div></div>';
  openModal('关于我们', html, '');
}

/* ===== 充值 ===== */
var selectedRecharge = null;
var rechargePackages = [];

function showRechargeModal() {
  if (!userState.isLoggedIn) { goToLogin(); return; }
  // 从后端拉套餐
  fetch(API_BASE + '/api/pay/packages')
    .then(function(res) { return res.json(); })
    .then(function(data) {
      rechargePackages = data.packages || [];
      renderRechargeGrid(rechargePackages);
    })
    .catch(function() {
      // fallback
      rechargePackages = [
        {id:1,name:'Single Query',price:9.90,queries:1,desc:'1次查询'},
        {id:2,name:'3-Pack',price:29.70,queries:3,desc:'3次查询'},
        {id:3,name:'5-Pack',price:59.00,queries:5,desc:'5次查询'},
        {id:4,name:'VIP Monthly',price:29.90,queries:-1,desc:'30天无限查询'}
      ];
      renderRechargeGrid(rechargePackages);
    });
  document.getElementById('rechargeOverlay').classList.add('open');
}

function renderRechargeGrid(packages) {
  var gridHTML = '';
  for (var i = 0; i < packages.length; i++) {
    var p = packages[i];
    var badge = '';
    if (p.queries >= 5) badge = '超值';
    else if (p.queries >= 3) badge = '推荐';
    else if (p.queries === -1) badge = 'VIP';
    gridHTML += '<div class="recharge-option" onclick="selectRecharge(' + i + ')" id="rechargeOpt' + i + '">';
    gridHTML += '<div class="recharge-price">¥' + p.price.toFixed(2) + '</div>';
    gridHTML += '<div class="recharge-count">' + (p.queries === -1 ? '30天无限' : p.queries + '次查询') + '</div>';
    if (badge) gridHTML += '<div class="recharge-badge">' + badge + '</div>';
    gridHTML += '</div>';
  }
  document.getElementById('rechargeGrid').innerHTML = gridHTML;
  selectedRecharge = null;
}

function selectRecharge(idx) {
  selectedRecharge = idx;
  for (var i = 0; i < rechargePackages.length; i++) {
    var el = document.getElementById('rechargeOpt' + i);
    if (el) el.classList.toggle('selected', i === idx);
  }
}

function closeRechargeModal() {
  document.getElementById('rechargeOverlay').classList.remove('open');
}

function doRecharge() {
  if (selectedRecharge === null) { toast('请选择充值套餐'); return; }
  var pkg = rechargePackages[selectedRecharge];
  if (!pkg) { toast('套餐无效'); return; }
  closeRechargeModal();
  toast('正在充值...');
  fetch(API_BASE + '/api/pay/recharge', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'token': userState.token },
    body: JSON.stringify({ package_id: pkg.id })
  })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      if (data.success) {
        userState.balance = data.balance;
        userState.freeCount = data.free_queries;
        userState.isVip = data.is_vip;
        loadUserData();
        refreshProfilePage();
        toast('充值成功！');
      } else {
        toast('充值失败: ' + (data.detail || '未知错误'));
      }
    })
    .catch(function(err) {
      toast('充值失败，请重试');
      console.error(err);
    });
}

/* ===== 登录流程 ===== */
function goToLogin() { switchPage(6); }
function goBackFromLogin() { switchPage(4); }
function onPhoneInput(input) {
  var val = input.value.replace(/\D/g, '');
  input.value = val;
  var codeBtn = document.getElementById('codeBtn');
  if (codeBtn) codeBtn.disabled = val.length !== 11;
}

var codeTimer = null;
var loginMode = 'code'; // 'code' | 'password'

function toggleLoginMode() {
  var pwRow = document.getElementById('passwordRow');
  var codeRow = document.getElementById('codeRow');
  var toggleLink = document.getElementById('toggleLoginMode');
  if (loginMode === 'code') {
    loginMode = 'password';
    if (codeRow) codeRow.style.display = 'none';
    if (pwRow) pwRow.style.display = 'block';
    if (toggleLink) toggleLink.textContent = '验证码登录';
  } else {
    loginMode = 'code';
    if (pwRow) pwRow.style.display = 'none';
    if (codeRow) codeRow.style.display = 'block';
    if (toggleLink) toggleLink.textContent = '密码登录';
  }
}

function sendVerifyCode() {
  var phoneInput = document.getElementById('phoneInput');
  if (!phoneInput || phoneInput.value.length !== 11) { toast('请输入正确的手机号'); return; }
  var codeBtn = document.getElementById('codeBtn');
  var count = 60;
  codeBtn.classList.add('counting');
  codeBtn.disabled = true;
  codeBtn.textContent = count + 's后重发';
  toast('验证码已发送（演示版：任意6位数字）');
  codeTimer = setInterval(function() {
    count--;
    if (count <= 0) {
      clearInterval(codeTimer);
      codeBtn.classList.remove('counting');
      codeBtn.disabled = false;
      codeBtn.textContent = '获取验证码';
    } else {
      codeBtn.textContent = count + 's后重发';
    }
  }, 1000);
}

function toggleAgree() {
  document.getElementById('agreeCheck').classList.toggle('checked');
}

function handleLogin() {
  var phone = document.getElementById('phoneInput').value;
  var agreed = document.getElementById('agreeCheck').classList.contains('checked');
  if (phone.length !== 11) { toast('请输入正确的手机号'); return; }
  if (!agreed) { toast('请先同意用户协议'); return; }
  
  toast('登录中...');
  
  if (loginMode === 'password') {
    // 密码登录
    var pwd = document.getElementById('passwordInput').value;
    if (!pwd || pwd.length < 6) { toast('密码至少6位'); return; }
    fetch(API_BASE + '/api/user/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: phone, password: pwd })
    }).then(function(res) { return res.json(); })
      .then(onLoginSuccess)
      .catch(function(err) { toast('登录失败: ' + err.message); });
  } else {
    // 验证码登录 - 简化版：验证码任意6位，自动注册
    var code = document.getElementById('codeInput').value;
    if (code.length !== 6) { toast('请输入6位验证码'); return; }
    // 先尝试登录，失败则注册
    fetch(API_BASE + '/api/user/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: phone, password: '111111' })
    }).then(function(res) {
      if (res.status === 401) {
        // 注册
        return fetch(API_BASE + '/api/user/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone: phone, password: '111111', nickname: '用户' + phone.slice(-4) })
        }).then(function(r) { return r.json(); });
      }
      return res.json();
    }).then(onLoginSuccess)
      .catch(function(err) { toast('登录失败: ' + err.message); });
  }
}

function onLoginSuccess(data) {
  if (data.token) {
    userState.isLoggedIn = true;
    userState.token = data.token;
    userState.userId = data.user.id;
    userState.nickname = data.user.nickname;
    userState.phone = data.user.phone.slice(0,3) + '****' + data.user.phone.slice(-4);
    userState.avatar = data.user.nickname[0] || '用';
    userState.isVip = data.user.is_vip || false;
    userState.freeCount = data.user.free_queries || 0;
    userState.balance = data.user.balance || 0;
    localStorage.setItem('credit_token', data.token);
    loadUserData();
    refreshProfilePage();
    switchPage(0);
    toast('登录成功');
  } else {
    toast('登录失败: ' + (data.detail || '未知错误'));
  }
}

function handleWechatLogin() {
  toast('微信登录中...');
  setTimeout(function() {
    // 微信登录暂用演示模式
    fetch(API_BASE + '/api/user/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: '139' + String(Math.floor(Math.random()*90000000+10000000)), password: 'wxlogin', nickname: '微信用户' })
    }).then(function(res) { return res.json(); })
      .then(onLoginSuccess)
      .catch(function() {
        userState.isLoggedIn = true;
        userState.nickname = '微信用户';
        userState.avatar = '微';
        userState.phone = '未绑定';
        refreshProfilePage();
        switchPage(0);
        toast('微信登录成功');
      });
  }, 1000);
}

function handleLogout() {
  if (userState.token) {
    fetch(API_BASE + '/api/user/logout', {
      method: 'POST',
      headers: { 'token': userState.token }
    }).catch(function() {});
  }
  localStorage.removeItem('credit_token');
  userState.isLoggedIn = false;
  userState.token = '';
  userState.userId = null;
  userState.freeCount = 0;
  userState.balance = 0;
  userState.reports = [];
  userState.consumes = [];
  refreshProfilePage();
  toast('已退出登录');
}

/* ===== 个人中心刷新 ===== */
function refreshProfilePage() {
  var loggedIn = document.getElementById('profileLoggedIn');
  var loginEntry = document.getElementById('profileLoginEntry');
  var logoutBtn = document.getElementById('logoutBtn');
  var rechargeCard = document.getElementById('rechargeCard');

  if (userState.isLoggedIn) {
    if (loggedIn) loggedIn.style.display = 'flex';
    if (loginEntry) loginEntry.style.display = 'none';
    if (logoutBtn) logoutBtn.style.display = 'block';
    if (rechargeCard) rechargeCard.style.display = 'flex';
    var avatarEl = document.getElementById('profileAvatar');
    var nameEl = document.getElementById('profileName');
    var phoneEl = document.getElementById('profilePhone');
    var vipBadge = document.getElementById('profileVipBadge');
    var balanceEl = document.getElementById('profileBalance');
    var commissionBadge = document.getElementById('commissionBadge');
    if (avatarEl) avatarEl.textContent = userState.avatar;
    if (nameEl) nameEl.textContent = userState.nickname;
    if (phoneEl) phoneEl.textContent = userState.phone;
    if (vipBadge) vipBadge.style.display = userState.isVip ? 'inline-block' : 'none';
    if (balanceEl) balanceEl.textContent = '\u00a5 ' + userState.balance.toFixed(2);
    if (commissionBadge) commissionBadge.textContent = '\u00a5' + userState.commission.toFixed(2);
  } else {
    if (loggedIn) loggedIn.style.display = 'none';
    if (loginEntry) loginEntry.style.display = 'flex';
    if (logoutBtn) logoutBtn.style.display = 'none';
    if (rechargeCard) rechargeCard.style.display = 'none';
    var b = document.getElementById('profileBalance');
    if (b) b.textContent = '\u00a5 0.00';
    var c = document.getElementById('commissionBadge');
    if (c) c.textContent = '\u00a50.00';
  }
}

/* ===== 登录入口点击 ===== */
var loginEntryEl = document.getElementById('profileLoginEntry');
if (loginEntryEl) {
  loginEntryEl.addEventListener('click', function() { goToLogin(); });
}

/* ===== 初始化 ===== */
refreshProfilePage();