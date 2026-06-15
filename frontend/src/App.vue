<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">IS</span>
        <div>
          <strong>雅思排课</strong>
          <span class="workspace-caption">教学主管工作台</span>
        </div>
      </div>
      <nav class="nav">
        <span class="nav-section-title">日常工作</span>
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/courses">排课管理</RouterLink>
        <RouterLink to="/daily-schedule">每日总课表</RouterLink>

        <span class="nav-section-title">资料与统计</span>
        <RouterLink to="/students">学生管理</RouterLink>
        <RouterLink to="/teachers">老师管理</RouterLink>
        <RouterLink to="/student-schedule">学生课表</RouterLink>
        <RouterLink to="/teacher-monthly">老师月度统计</RouterLink>

        <span class="nav-section-title">支持</span>
        <RouterLink to="/help">使用指南</RouterLink>
      </nav>
    </aside>

    <main class="main">
      <RouterView />
    </main>
  </div>
</template>
