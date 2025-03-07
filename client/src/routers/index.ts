import { createRouter, createWebHistory, type RouteLocationNormalized, type NavigationGuardNext } from 'vue-router'
import { routes } from 'vue-router/auto-routes'

for (const route of routes) {
  if (route.path === '/recipes') {
    route.meta = { requiresAuth: true }
    route.beforeEnter = (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
      console.log(to, from)
      const isAuthenticated = JSON.parse(localStorage.getItem('authenticated') || 'false')
      if (isAuthenticated) {
        next();
      } else {
        next('/login' ); 
      }
    };
  }
}

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router;
