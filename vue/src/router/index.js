import Vue from 'vue'
import Router from 'vue-router'
import HomePage from '@pages/HomePage'
import NewsPage from '@pages/News/NewsPage'
import NewsHome from '@pages/News/NewsHome'
import NewsArticle from '@pages/News/NewsArticle'
import MarketPage from '@pages/MarketPage'
import CommentPage from '@pages/Comment/CommentPage'
import SettingPage from '@pages/SettingPage'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: CommentPage,
      meta: { 
        ifShow: false
      }
    },
    {
      path: '/news',
      component: NewsHome,
      name: 'News',
      redirect: {name: 'NewList'},
      children: [
        {
          path: '/news/',
          name: 'NewsList',
          component: NewsPage,
        },
        {
          path: '/news/:article_id',
          name: 'NewsArticle',
          component: NewsArticle
        },
      ]
    },
    {
      path: '/commit',
      name: 'Commit',
      meta: { 
        ifShow: false
      },
      children: [
        {
          path: '/commit/write',
          name: 'writeArticle',
        },
        {
          path: '/commit/history',
          name: 'historyArticle',
        },
        {
          path: '/commit/history',
          name: 'collectionArticle',
        },
      ]
    },
    {
      path: '/setting/:userId',
      name: 'Setting',
      component: SettingPage,
      meta: {
        ifShow: false
      }
    },
    {
      path: '/market',
      name: 'Market',
      component: MarketPage,
      meta: { 
        ifShow: true
      }
    },
    {
      path: '/shop',
      name: 'Shop',
      component: HomePage,
      meta: { 
        ifShow: true
      }
    },
  ]
})

router.beforeEach((to,from,next)=>{
  
  next()
})


export default router