---
name: Vue.js Dashboard Developer
description: |
  Membuat dan mengembangkan dashboard/admin panel menggunakan Vue 3 + Composition API.
  Gunakan skill ini ketika user meminta: "buat dashboard Vue", "admin panel Vue.js", 
  "Vue 3 frontend", "dashboard dengan chart", "integrasi API ke Vue", "Vue dashboard UI".
version: 1.1
last_updated: 2026-04-27
tags: [vue, vue3, dashboard, frontend, typescript, pinia]
---

# Skill: Vue.js Dashboard Developer

## Goal
Menghasilkan dashboard Vue 3 yang **modern, performant, maintainable**, dengan UI yang clean, state management yang tepat, routing yang baik, dan siap connect ke backend API.

## When to Use This Skill
- User minta dashboard/admin interface.
- Pembuatan halaman dengan sidebar, charts, tables, forms, authentication.
- Refactoring atau improvement Vue dashboard existing.
- Integrasi dengan API (Axios/Fetch + Pinia actions).
- Jangan gunakan jika hanya butuh halaman landing sederhana.

## Latest Stable & Best Practices (Update 2026)
- **Vue.js**: 3.5.x (Composition API + `<script setup>` adalah standard)
- **Build Tool**: Vite (paling cepat)
- **State Management**: **Pinia** (bukan Vuex)
- **Routing**: Vue Router 4
- **UI Library** (opsional): Element Plus, Naive UI, Vuetify, atau Tailwind + Headless UI
- **TypeScript**: Sangat direkomendasikan untuk dashboard besar
- **Styling**: Tailwind CSS 4 (atau scoped CSS + CSS Modules)
- Gunakan **feature-based / domain-driven structure**
- Lazy loading routes
- Composables untuk logic reusable (`useAuth`, `useTable`, `useApi`)

## Recommended Project Structure (2026 Best Practice)

```bash
src/
├── assets/                 # images, icons
├── components/             # shared UI (BaseButton, BaseTable, etc.)
├── composables/            # reusable logic (useApi, usePagination)
├── modules/                # feature-based (dashboard/, users/, reports/)
│   ├── dashboard/
│   │   ├── views/
│   │   ├── components/
│   │   └── store/
│   └── users/
├── layouts/                # DashboardLayout, AuthLayout
├── router/                 # index.ts + guards
├── stores/                 # Pinia stores (authStore, themeStore)
├── services/               # api client (axios instance)
├── utils/
├── views/                  # page-level components
├── App.vue
└── main.ts