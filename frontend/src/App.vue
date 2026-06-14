<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">IELTS</span>
        <strong>排课管理</strong>
      </div>
      <nav class="nav">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/students">学生管理</RouterLink>
        <RouterLink to="/teachers">老师管理</RouterLink>
        <RouterLink to="/courses">排课管理</RouterLink>
        <RouterLink to="/daily-schedule">每日总课表</RouterLink>
        <RouterLink to="/student-schedule">学生课表</RouterLink>
        <RouterLink to="/teacher-monthly">老师月度统计</RouterLink>
      </nav>
    </aside>

    <main class="main">
      <RouterView />
    </main>
  </div>
</template>
