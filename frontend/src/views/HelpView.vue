<template>
  <section>
    <div class="page-header">
      <div>
        <h1>使用指南</h1>
        <p>按助教日常流程整理的操作入口和检查项。</p>
      </div>
    </div>

    <div class="guide-grid">
      <section class="panel">
        <div class="panel-header">
          <div>
            <h2>推荐工作流</h2>
            <p>从资料录入到导出课表</p>
          </div>
        </div>

        <ol class="workflow-list">
          <li>
            <strong>录入学生和老师</strong>
            <span>先在学生管理和老师管理中维护基础资料，避免排课时找不到人。</span>
          </li>
          <li>
            <strong>创建课程</strong>
            <span>在排课管理中选择学生、老师、日期和时间。保存前会自动检测双方冲突。</span>
          </li>
          <li>
            <strong>核对每日安排</strong>
            <span>每日总课表按时间排序，可直接复制提醒消息或导出 CSV。</span>
          </li>
          <li>
            <strong>查看个人和月度课表</strong>
            <span>学生课表用于发送给学生；老师月度统计用于月底核算课时。</span>
          </li>
        </ol>
      </section>

      <section class="panel">
        <div class="panel-header">
          <div>
            <h2>冲突规则</h2>
            <p>系统保存课程前自动检查</p>
          </div>
        </div>

        <div class="rule-box">
          <code>新课程开始时间 &lt; 已有课程结束时间</code>
          <span>并且</span>
          <code>新课程结束时间 &gt; 已有课程开始时间</code>
        </div>

        <p class="guide-note">
          例如已有课程 10:00-11:00，新课程 10:30-11:30 会冲突；新课程 11:00-12:00 不冲突。
        </p>
      </section>

      <section class="panel">
        <div class="panel-header">
          <div>
            <h2>常见检查</h2>
            <p>遇到问题时先看这里</p>
          </div>
        </div>

        <div class="check-list">
          <span>后端接口文档是否能打开：127.0.0.1:8000/docs</span>
          <span>前端地址是否为：localhost:5173</span>
          <span>删除学生或老师前，是否还有关联课程</span>
          <span>导出 CSV 前，是否已经选择日期、学生或老师</span>
        </div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <div>
            <h2>快捷入口</h2>
            <p>直接跳转到常用页面</p>
          </div>
        </div>

        <div class="quick-links">
          <RouterLink class="button button-primary" to="/courses">新增课程</RouterLink>
          <RouterLink class="button" to="/daily-schedule">每日总课表</RouterLink>
          <RouterLink class="button" to="/student-schedule">学生课表</RouterLink>
          <RouterLink class="button" to="/teacher-monthly">老师月度统计</RouterLink>
        </div>
      </section>
    </div>
  </section>
</template>
