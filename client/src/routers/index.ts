import { createRouter, createWebHistory, type RouteLocationNormalized, type NavigationGuardNext } from 'vue-router'
import { routes } from 'vue-router/auto-routes'

for (const route of routes) {
  if (route.path === '/recipes') {
    route.name = 'recipes'
    route.meta = { requiresAuth: true }
    route.beforeEnter = (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
      console.log(to, from)
      const isAuthenticated = JSON.parse(localStorage.getItem('authenticated') || 'false')
      const isTrial = to.query.trial === 'true' ? true : false
      console.log(isTrial)
      if (isAuthenticated || isTrial) {
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
